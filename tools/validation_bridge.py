"""One read-only MCP capability: parse Python/JSON artifacts without executing them.

This is a trusted static validator, not an arbitrary-code sandbox. The fixed
artifact root must exclude this server and its controller. No model calls,
subprocesses, network access, candidate imports or candidate writes occur here.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import sys

PROTOCOL = "2025-06-18"
MAX_REQUEST_BYTES = 64 * 1024
MAX_FILE_BYTES = 512 * 1024
TOOL_NAME = "validate_artifact"
REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class Rejected(ValueError):
    pass


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON object key")
            result[key] = value
        return result

    def invalid(_value):
        raise ValueError("Non-finite numbers are not JSON values")

    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)


def ordinary(path, directory=False):
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & REPARSE_POINT:
        raise Rejected("Symlinks and reparse points are not allowed")
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise Rejected("Expected an ordinary directory" if directory else "Expected an ordinary file")
    return info


def relative_parts(value):
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise Rejected("path must be a nonempty relative file path of at most 2048 characters")
    if value.startswith("/") or "\\" in value or PureWindowsPath(value).drive:
        raise Rejected("Use a relative path with forward slashes; absolute and drive paths are not allowed")
    parts = value.split("/")
    for part in parts:
        if (part in {"", ".", ".."} or ":" in part or part.endswith((" ", "."))
                or any(ord(char) < 32 for char in part)
                or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part)):
            raise Rejected("Empty, traversal, device and alternate-stream path components are not allowed")
    return parts


def windows_open(path, root):
    """Open the final component without following a reparse point; inspect its handle."""
    import ctypes
    from ctypes import wintypes
    import msvcrt

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                       ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL
    final = kernel.GetFinalPathNameByHandleW
    final.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    final.restype = wintypes.DWORD
    info_call = kernel.GetFileInformationByHandleEx
    info_call.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    info_call.restype = wintypes.BOOL

    class AttributeTag(ctypes.Structure):
        _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]

    # Read only; OPEN_EXISTING; OPEN_REPARSE_POINT. Deny shared writes/deletes
    # while parsing so the opened artifact cannot change underneath the report.
    handle = create(str(path), 0x80000000, 1, None, 3, 0x00200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise Rejected("Cannot open the artifact for a stable read")
    try:
        info = AttributeTag()
        if not info_call(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            raise Rejected("Cannot verify opened file attributes")
        if info.attributes & (REPARSE_POINT | 0x10):
            raise Rejected("Opened target is a reparse point or directory")
        buffer = ctypes.create_unicode_buffer(32768)
        length = final(handle, buffer, len(buffer), 0)
        if not length or length >= len(buffer):
            raise Rejected("Cannot verify opened file location")
        actual = buffer.value
        if actual.startswith("\\\\?\\UNC\\"):
            actual = "\\\\" + actual[8:]
        elif actual.startswith("\\\\?\\"):
            actual = actual[4:]
        normalized = os.path.normcase(os.path.normpath(actual))
        if (normalized != os.path.normcase(str(path))
                or os.path.commonpath([normalized, os.path.normcase(str(root))]) != os.path.normcase(str(root))):
            raise Rejected("Opened file does not match the permitted artifact path")
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        handle = None  # Descriptor owns the handle now.
        return descriptor
    finally:
        if handle is not None:
            close(handle)


def posix_open(root, parts):
    """Walk directory handles with O_NOFOLLOW instead of trusting path resolution."""
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise Rejected("This platform cannot enforce the required file-open checks")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(root, directory_flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
    finally:
        os.close(descriptor)


class Bridge:
    def __init__(self, root):
        root = Path(root)
        if not root.is_absolute():
            raise Rejected("--root must be an existing absolute directory")
        for ancestor in (root, *root.parents):
            ordinary(ancestor, directory=True)
        self.root = root.resolve(strict=True)
        server = Path(__file__).resolve(strict=True)
        if server.is_relative_to(self.root):
            raise Rejected("The trusted server must be outside the artifact root")
        self.root_identity = ordinary(self.root, directory=True)
        self.tool_sha256 = hashlib.sha256(server.read_bytes()).hexdigest()
        self.initialized = False

    def read_artifact(self, path):
        parts = relative_parts(path)
        current = self.root
        root_now = ordinary(current, directory=True)
        if (root_now.st_dev, root_now.st_ino) != (self.root_identity.st_dev, self.root_identity.st_ino):
            raise Rejected("Artifact root changed since server startup")
        for part in parts[:-1]:
            current /= part
            ordinary(current, directory=True)
        target = current / parts[-1]
        before = ordinary(target)
        if before.st_size > MAX_FILE_BYTES:
            raise Rejected(f"Artifact exceeds the {MAX_FILE_BYTES}-byte limit")
        descriptor = windows_open(target, self.root) if os.name == "nt" else posix_open(self.root, parts)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (not stat.S_ISREG(opened.st_mode)
                    or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
                raise Rejected("Artifact identity changed during opening")
            data = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        # Reject swapped ancestors as well as the final component.
        for ancestor in (self.root, *(self.root.joinpath(*parts[:i]) for i in range(1, len(parts)))):
            ordinary(ancestor, directory=True)
        final = ordinary(target)
        if (len(data) > MAX_FILE_BYTES or after.st_size != before.st_size
                or after.st_mtime_ns != before.st_mtime_ns
                or (final.st_dev, final.st_ino) != (opened.st_dev, opened.st_ino)):
            raise Rejected("Artifact changed while being read or exceeded the size limit")
        return data

    def validate_artifact(self, arguments):
        if (not isinstance(arguments, dict) or set(arguments) != {"path", "validator"}
                or not isinstance(arguments["path"], str)
                or arguments["validator"] not in ("python_ast", "json")):
            raise ValueError("Arguments must contain only path:string and validator:python_ast|json")
        result = {"path": arguments["path"], "validator": arguments["validator"],
                  "file_sha256": None, "tool_sha256": self.tool_sha256,
                  "status": "rejected", "diagnostics": []}
        try:
            data = self.read_artifact(arguments["path"])
        except (OSError, ValueError) as exc:
            message = str(exc) if isinstance(exc, Rejected) else "Artifact cannot be read as a permitted ordinary file"
            result["diagnostics"] = [{"code": "read_rejected", "message": message}]
            return result
        result["file_sha256"] = hashlib.sha256(data).hexdigest()
        try:
            text = data.decode("utf-8-sig")
            if arguments["validator"] == "python_ast":
                ast.parse(text, filename=arguments["path"], mode="exec")
            else:
                strict_json(text)
            result["status"] = "valid"
        except (SyntaxError, UnicodeDecodeError, ValueError, RecursionError, MemoryError) as exc:
            result["status"] = "invalid"
            message = getattr(exc, "msg", None) or str(exc)
            if isinstance(exc, (RecursionError, MemoryError)):
                message = "Artifact exceeds parser complexity limits; reduce nesting or size"
            result["diagnostics"] = [{"code": "parse_error", "message": message[:500],
                                      "line": getattr(exc, "lineno", None),
                                      "column": getattr(exc, "offset", None) or getattr(exc, "colno", None)}]
        return result

    def dispatch(self, request):
        if (not isinstance(request, dict) or request.get("jsonrpc") != "2.0"
                or set(request) - {"jsonrpc", "id", "method", "params"}
                or not isinstance(request.get("method"), str)
                or ("id" in request and request["id"] is not None and type(request["id"]) not in {str, int})):
            return rpc_error(None, -32600, "Invalid JSON-RPC request")
        identity = request.get("id")
        method = request["method"]
        params = request.get("params", {})
        if "id" not in request:
            return None  # Notifications, including notifications/initialized, have no reply.
        try:
            if not isinstance(params, dict):
                raise ValueError("params must be an object")
            if "_meta" in params:
                metadata = params["_meta"]
                if (not isinstance(metadata, dict)
                        or ("progressToken" in metadata and type(metadata["progressToken"]) not in {str, int})):
                    raise ValueError("_meta must be an object with a string or integer progressToken when present")
                params = {key: value for key, value in params.items() if key != "_meta"}
            if method == "initialize":
                if (set(params) != {"protocolVersion", "capabilities", "clientInfo"}
                        or not isinstance(params["protocolVersion"], str)
                        or not isinstance(params["capabilities"], dict)
                        or not isinstance(params["clientInfo"], dict)):
                    raise ValueError("initialize requires protocolVersion, capabilities and clientInfo")
                self.initialized = True
                result = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {"listChanged": False}},
                          "serverInfo": {"name": "gauntlet-static-validation", "version": "0.1.0"},
                          "instructions": "Read-only syntax validation. A valid parse is not runtime, functional or task acceptance."}
            elif method == "ping":
                if params:
                    raise ValueError("ping accepts no parameters")
                result = {}
            elif not self.initialized:
                return rpc_error(identity, -32000, "Initialize before using tools")
            elif method == "tools/list":
                if params:
                    raise ValueError("tools/list accepts no parameters")
                result = {"tools": [{"name": TOOL_NAME,
                          "description": "Parse a UTF-8 artifact under the fixed root as Python syntax or strict JSON. Never executes/imports its contents. Returns identity and diagnostics; syntax success is not functional acceptance.",
                          "inputSchema": {"type": "object", "additionalProperties": False,
                                          "required": ["path", "validator"],
                                          "properties": {"path": {"type": "string"},
                                                         "validator": {"type": "string", "enum": ["python_ast", "json"]}}},
                          "annotations": {"readOnlyHint": True, "destructiveHint": False,
                                          "idempotentHint": True, "openWorldHint": False}}]}
            elif method == "tools/call":
                if set(params) != {"name", "arguments"} or params.get("name") != TOOL_NAME:
                    raise ValueError("Only validate_artifact with name and arguments is supported")
                report = self.validate_artifact(params["arguments"])
                result = {"content": [{"type": "text", "text": json.dumps(report, ensure_ascii=True)}],
                          "structuredContent": report, "isError": report["status"] == "rejected"}
            else:
                return rpc_error(identity, -32601, "Method not found")
            return {"jsonrpc": "2.0", "id": identity, "result": result}
        except ValueError as exc:
            return rpc_error(identity, -32602, str(exc))


def rpc_error(identity, code, message):
    return {"jsonrpc": "2.0", "id": identity, "error": {"code": code, "message": message}}


def serve(bridge, source, destination):
    while True:
        line = source.readline(MAX_REQUEST_BYTES + 1)
        if not line:
            return
        if len(line) > MAX_REQUEST_BYTES:
            while not line.endswith(b"\n"):
                line = source.readline(MAX_REQUEST_BYTES + 1)
                if not line:
                    break
            response = rpc_error(None, -32700, "Request exceeds size limit")
        else:
            try:
                request = strict_json(line.decode("utf-8"))
                response = bridge.dispatch(request)
            except (ValueError, RecursionError):
                response = rpc_error(None, -32700, "Invalid JSON request")
            except Exception:
                response = rpc_error(None, -32603, "Static validator failed; no acceptance recorded")
        if response is not None:
            destination.write((json.dumps(response, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8"))
            destination.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Fixed absolute artifact directory; excludes server/controller")
    args = parser.parse_args(argv)
    try:
        bridge = Bridge(args.root)
    except (OSError, ValueError):
        print("Cannot establish the fixed ordinary artifact root; server did not start.", file=sys.stderr)
        return 2
    serve(bridge, sys.stdin.buffer, sys.stdout.buffer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
