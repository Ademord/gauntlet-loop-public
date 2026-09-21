"""Exercise the actual MCP stdio process; candidate code must never execute."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools/validation_bridge.py"
spec = importlib.util.spec_from_file_location("validation_bridge", SCRIPT)
bridge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge_module)


def request(identity, method, params=None):
    row = {"jsonrpc": "2.0", "id": identity, "method": method}
    if params is not None:
        row["params"] = params
    return row


def initialize():
    return request(1, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                      "clientInfo": {"name": "fixture", "version": "1"}})


def call(identity, path, validator="python_ast", **extra):
    return request(identity, "tools/call", {"name": "validate_artifact",
                   "arguments": {"path": path, "validator": validator, **extra}})


class ValidationBridgeTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="gauntlet-static-bridge-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "artifacts"
        self.root.mkdir()
        (self.root / "valid.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
        (self.root / "invalid.py").write_text("def answer(\n", encoding="utf-8")
        (self.root / "valid.json").write_text('{"answer":42}', encoding="utf-8")
        (self.root / "invalid.json").write_text('{"answer":}', encoding="utf-8")

    def communicate(self, rows, root=None):
        payload = b"".join((row if isinstance(row, bytes) else json.dumps(row).encode()) + b"\n" for row in rows)
        process = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), "--root", str(root or self.root)],
                                 input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=15, cwd=self.base)
        return process, [json.loads(line) for line in process.stdout.splitlines()]

    def reports(self, rows):
        process, replies = self.communicate([initialize(), *rows])
        self.assertEqual(0, process.returncode, process.stderr.decode())
        self.assertEqual(b"", process.stderr)
        return replies[1:]

    def test_actual_stdio_handshake_notification_list_ping_and_call(self):
        process, replies = self.communicate([
            initialize(), {"jsonrpc": "2.0", "method": "notifications/initialized"},
            request(2, "ping"), request(3, "tools/list"), call(4, "valid.py"),
        ])
        self.assertEqual(0, process.returncode, process.stderr.decode())
        self.assertEqual([1, 2, 3, 4], [row["id"] for row in replies])
        self.assertEqual("2025-06-18", replies[0]["result"]["protocolVersion"])
        self.assertEqual({}, replies[1]["result"])
        tools = replies[2]["result"]["tools"]
        self.assertEqual(["validate_artifact"], [tool["name"] for tool in tools])
        self.assertFalse(tools[0]["inputSchema"]["additionalProperties"])
        self.assertEqual({"path", "validator"}, set(tools[0]["inputSchema"]["required"]))
        report = replies[3]["result"]["structuredContent"]
        self.assertEqual("valid", report["status"])
        self.assertEqual(hashlib.sha256((self.root / "valid.py").read_bytes()).hexdigest(), report["file_sha256"])
        self.assertEqual(hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), report["tool_sha256"])
        self.assertEqual(report, json.loads(replies[3]["result"]["content"][0]["text"]))

    def test_valid_and_invalid_artifacts_have_actionable_diagnostics(self):
        replies = self.reports([call(2, "valid.py"), call(3, "invalid.py"),
                                call(4, "valid.json", "json"), call(5, "invalid.json", "json")])
        reports = [row["result"]["structuredContent"] for row in replies]
        self.assertEqual(["valid", "invalid", "valid", "invalid"], [row["status"] for row in reports])
        for index in (1, 3):
            self.assertEqual(1, reports[index]["diagnostics"][0]["line"])
            self.assertTrue(reports[index]["diagnostics"][0]["message"])
            self.assertEqual(64, len(reports[index]["file_sha256"]))

    def test_transport_metadata_is_supported_but_tool_arguments_stay_closed(self):
        opening = initialize()
        opening["params"]["_meta"] = {"progressToken": "initialize-1"}
        validating = call(4, "valid.py")
        validating["params"]["_meta"] = {"progressToken": 4, "fixture/context": {"purpose": "test"}}
        bad_argument = call(5, "valid.py", command="must still be rejected")
        bad_argument["params"]["_meta"] = {}
        process, replies = self.communicate([
            opening, request(2, "ping", {"_meta": {}}),
            request(3, "tools/list", {"_meta": {"progressToken": "list"}}),
            validating, bad_argument, request(6, "ping", {"_meta": []}),
            request(7, "ping", {"_meta": {"progressToken": True}}),
        ])
        self.assertEqual(0, process.returncode, process.stderr.decode())
        self.assertTrue(all("result" in reply for reply in replies[:4]))
        self.assertEqual("valid", replies[3]["result"]["structuredContent"]["status"])
        self.assertEqual([-32602] * 3, [reply["error"]["code"] for reply in replies[4:]])

    def test_ast_never_imports_or_executes_candidate_and_changes_no_files(self):
        sentinel = self.base / "executed.txt"
        (self.root / "payload.py").write_text(
            "import this_module_does_not_exist\n"
            f"open({str(sentinel)!r}, 'w').write('executed')\n"
            "raise RuntimeError('must not execute')\n", encoding="utf-8")
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}
        reply = self.reports([call(2, "payload.py")])[0]
        self.assertEqual("valid", reply["result"]["structuredContent"]["status"])
        self.assertFalse(sentinel.exists())
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.root.iterdir()})

    def test_absolute_traversal_device_and_stream_paths_rejected(self):
        outside = self.base / "outside.py"
        outside.write_text("secret = 42\n", encoding="utf-8")
        paths = [str(outside), "../outside.py", "sub/../../outside.py", "./valid.py",
                 "C:relative.py", "C:/outside.py", "//server/share/a.py", "sub\\a.py",
                 "NUL", "valid.py:stream", "valid.py.", "sub//a.py"]
        replies = self.reports([call(index + 2, path) for index, path in enumerate(paths)])
        for path, reply in zip(paths, replies):
            with self.subTest(path=path):
                report = reply["result"]["structuredContent"]
                self.assertEqual("rejected", report["status"])
                self.assertIsNone(report["file_sha256"])
                self.assertTrue(reply["result"]["isError"])
        self.assertEqual("secret = 42\n", outside.read_text())

    def test_regular_nested_file_is_allowed_and_missing_or_directory_denied(self):
        (self.root / "sub").mkdir()
        (self.root / "sub/ok.json").write_text("[1,2,3]", encoding="utf-8")
        replies = self.reports([call(2, "sub/ok.json", "json"), call(3, "missing.py"), call(4, "sub")])
        self.assertEqual(["valid", "rejected", "rejected"],
                         [reply["result"]["structuredContent"]["status"] for reply in replies])

    def test_symlink_file_and_symlink_ancestor_are_denied_when_supported(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "secret.py").write_text("value = 1", encoding="utf-8")
        try:
            (self.root / "link.py").symlink_to(outside / "secret.py")
            (self.root / "linked").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Host does not permit symlink fixtures: {type(exc).__name__}")
        replies = self.reports([call(2, "link.py"), call(3, "linked/secret.py")])
        self.assertTrue(all(reply["result"]["structuredContent"]["status"] == "rejected" for reply in replies))

    def test_reparse_attribute_is_rejected_without_following(self):
        # The Windows attribute guard also covers junction/reparse variants that
        # do not identify as S_IFLNK. This fake represents lstat's trusted result.
        class Info:
            st_mode = 0o100644
            st_file_attributes = 0x400
        class PathFixture:
            def lstat(self):
                return Info()
        with self.assertRaises(bridge_module.Rejected):
            bridge_module.ordinary(PathFixture())

    def test_file_and_transport_size_limits_preserve_connection(self):
        (self.root / "big.py").write_bytes(b"#" * (bridge_module.MAX_FILE_BYTES + 1))
        replies = self.reports([call(2, "big.py"), b" " * (bridge_module.MAX_REQUEST_BYTES + 1),
                                call(3, "valid.py")])
        self.assertEqual("rejected", replies[0]["result"]["structuredContent"]["status"])
        self.assertEqual(-32700, replies[1]["error"]["code"])
        self.assertEqual("valid", replies[2]["result"]["structuredContent"]["status"])

    def test_unknown_tool_command_argument_validator_and_fields_are_denied(self):
        replies = self.reports([
            request(2, "tools/call", {"name": "run_command", "arguments": {}}),
            call(3, "valid.py", command="echo unsafe"), call(4, "valid.py", "python_exec"),
            request(5, "tools/call", {"name": "validate_artifact", "arguments": {"path": "valid.py"}}),
            request(6, "tools/call", {"name": "validate_artifact", "arguments": {"path": "valid.py", "validator": "python_ast"}, "command": "ignored?"}),
            request(7, "resources/list"),
        ])
        self.assertEqual([-32602, -32602, -32602, -32602, -32602, -32601],
                         [reply["error"]["code"] for reply in replies])

    def test_malformed_json_duplicate_keys_and_invalid_rpc_are_rejected(self):
        replies = self.reports([b"{", b'{"jsonrpc":"2.0","id":2,"id":3,"method":"ping"}',
                                {"jsonrpc": "2.0", "id": True, "method": "ping"},
                                request(4, "ping", {"unexpected": True}), call(5, "valid.py")])
        self.assertEqual([-32700, -32700, -32600, -32602], [reply["error"]["code"] for reply in replies[:4]])
        self.assertEqual("valid", replies[4]["result"]["structuredContent"]["status"])

    def test_bom_invalid_utf8_strict_json_and_complexity_are_reported(self):
        (self.root / "bom.py").write_bytes(b"\xef\xbb\xbfvalue = 1\n")
        (self.root / "bad-utf8.py").write_bytes(b"\xff")
        (self.root / "nan.json").write_text("NaN", encoding="utf-8")
        (self.root / "duplicate.json").write_text('{"a":1,"a":2}', encoding="utf-8")
        (self.root / "deep.py").write_text("(" * 2000 + "1" + ")" * 2000, encoding="utf-8")
        replies = self.reports([call(2, "bom.py"), call(3, "bad-utf8.py"),
                                call(4, "nan.json", "json"), call(5, "duplicate.json", "json"),
                                call(6, "deep.py")])
        self.assertEqual(["valid", "invalid", "invalid", "invalid", "invalid"],
                         [reply["result"]["structuredContent"]["status"] for reply in replies])

    def test_tools_require_initialization_and_root_excludes_server(self):
        process, replies = self.communicate([request(1, "tools/list")])
        self.assertEqual(0, process.returncode)
        self.assertEqual(-32000, replies[0]["error"]["code"])
        process, replies = self.communicate([], root=SCRIPT.parent)
        self.assertEqual(2, process.returncode)
        self.assertEqual([], replies)


if __name__ == "__main__":
    unittest.main()
