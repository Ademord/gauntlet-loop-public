# Trusted static validation

[validation_bridge.py](../tools/validation_bridge.py) gives a worker one capability: parse a Python or JSON artifact and receive diagnostics bound to its bytes. It never imports or executes candidate code, runs a shell, writes candidate files or opens network connections. This is a limited development tool, not a general sandbox or independent task acceptance.

The [SVQ-001 qualification](../research/program/readiness/SVQ-001.json) verified five actual calls through native Claude Code: valid and invalid Python, valid and invalid JSON, and a rejected traversal path. [MAQ-001](../research/program/readiness/MAQ-001.json) remains blocked for arbitrary candidate-code execution. The static bridge does not change that result.

## Configure the capability

Use a trusted Python installation and keep the server, its configuration, controller records and independent acceptance material outside the worker's artifact root. Give the worker file access only to its intended workspace through the host's own controls. The bridge's root restriction applies to this tool; it does not restrict other tools a host exposes.

```text
python -I -B /absolute/path/to/validation_bridge.py --root /absolute/path/to/artifacts
```

The process serves newline-delimited MCP JSON-RPC on standard input/output. It supports protocol `2025-06-18`, initialization, ping, tool discovery and tool calls. Initialization returns the supported version when a client requests another version. Optional transport `_meta` is accepted; the tool's own arguments stay closed.

For an MCP-capable host, put actual machine paths in private configuration, for example a gitignored `*.local.json` file:

```json
{
  "mcpServers": {
    "gauntlet_validation": {
      "command": "/absolute/path/to/python",
      "args": [
        "-I", "-B", "/absolute/path/to/validation_bridge.py",
        "--root", "/absolute/path/to/artifacts"
      ]
    }
  }
}
```

Paths above are placeholders. Use the host's reviewed per-invocation tool configuration; the bridge does not install itself, alter permissions or authorize worker dispatch. Record the selected executable, bridge identity and configuration with the task.

The exposed tool is `validate_artifact`, with exactly two required arguments:

```json
{"path": "output/controller.py", "validator": "python_ast"}
```

Use `"validator": "json"` for JSON. A host may prefix the tool name with its MCP server name. Paths must be relative to the fixed root, using forward slashes. The tool rejects absolute, traversal, device and alternate-stream paths, symlinks and reparse ancestry. It checks the opened file's identity and location rather than trusting path resolution alone. Requests are limited to 64 KiB and files to 512 KiB; artifacts must use UTF-8, with an optional BOM.

## Interpret the result

The tool returns the same report as structured content and JSON text:

| Field | Meaning |
| --- | --- |
| `path`, `validator` | Requested artifact and parser |
| `file_sha256` | Hash of the raw file bytes actually read; `null` when reading is rejected |
| `tool_sha256` | Hash of the trusted bridge source at startup |
| `status` | `valid`, `invalid` or `rejected` |
| `diagnostics` | Actionable parser or read-rejection messages, with line/column where available |

`valid` means only that parsing succeeded. Python syntax may parse despite failing at runtime or doing the wrong thing. JSON parsing does not validate a task-specific schema; duplicate object keys and explicit non-finite values are rejected. Neither parser establishes functional correctness, safe execution, installability or user acceptance. The bridge does not execute test suites or the separate skill-frontmatter validator.

`invalid` means the readable artifact failed parsing. `rejected` means the tool declined the read, for example because the path or size was outside its contract. A rejected path has no file hash and is returned as a tool error. Revalidation is needed after an artifact changes; a report remains evidence only about its recorded bytes. Independent acceptance stays with the existing controller and [observer outcome API](OBSERVER.md).

## Qualification and limits

```text
python -B -m unittest discover -s tests -p test_validation_bridge.py -v
```

The recorded suite ran 13 tests: 12 passed and one symlink fixture was skipped because the host did not permit creating symlinks. Coverage includes the actual stdio lifecycle, protocol negotiation, transport metadata, valid/invalid controls, path and size rejections, hashes, and a candidate import/write sentinel that remained unexecuted. A separate attribute check exercises the reparse rejection branch; it does not replace the skipped native symlink test.

The native Claude Opus 5/xhigh smoke completed five tool calls in **13.344 seconds**, reporting **12,739 tokens** and **$0.0966585 API-equivalent usage**. Token totals include input, output, cache-read and cache-creation categories. Cash billing, preparation, evaluation and human effort remain unknown. This was one compatibility smoke with supplied fixtures, not a comparison or evidence that validation improves task delivery.

Preserve the narrow qualification: no arbitrary candidate execution, comprehensive filesystem security, descendant cleanup, browser/account access or full host tool coverage was established. The bridge reuses existing observation and accounting; it adds no scheduler, autonomous retries or performance claim.
