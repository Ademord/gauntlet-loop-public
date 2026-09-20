"""Replay existing local transcripts without rewriting the original results.

Usage (no model calls):
  python tools/paired_study/replay_measurements.py --output <derived.jsonl> --report <report.md>

Historical pilot/startup rows share filenames with later reruns. They are kept
but never assigned the rerun's transcript. Legacy binding checks result.usage,
cost, and turns against the original row; it is not a historical crypto attestation.
"""
import argparse
import json
import statistics
from pathlib import Path

try:
    from .telemetry import accepted_checks, file_identity, measure_result, parse_stream, sha256_bytes
except ImportError:
    from telemetry import accepted_checks, file_identity, measure_result, parse_stream, sha256_bytes

REPO = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = REPO / 'research/program/paired-study/results.jsonl'
LEGACY_FIELDS = ('total_tokens', 'cost_usd', 'reviews_used', 'critic_dispatches', 'accepted')


def _label(path):
    try:
        return Path(path).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return Path(path).name


def bind_transcript(row, result, transcript_bytes):
    """Do not attach today's rerun transcript to an earlier row at the same path."""
    if not isinstance(result, dict):
        return False, 'missing_result_event'
    recorded_hash = row.get('transcript_sha256')
    if recorded_hash:
        return sha256_bytes(transcript_bytes) == recorded_hash, 'recorded_transcript_sha256'
    keys = ('usage', 'total_cost_usd', 'num_turns')
    if not isinstance(row.get('usage'), dict) or not all(k in result for k in keys):
        return False, 'insufficient_legacy_binding_fields'
    matches = (row['usage'] == result['usage'] and row.get('cost_usd') == result['total_cost_usd']
               and row.get('num_turns') == result['num_turns'])
    return matches, 'legacy_result_usage+cost+num_turns'


def derive_rows(results_path, pairs_root):
    results_path, pairs_root = Path(results_path).resolve(), Path(pairs_root).resolve()
    source = results_path.read_bytes()
    source_hash = sha256_bytes(source)
    identities = {'replay': file_identity(__file__), 'telemetry': file_identity(Path(__file__).with_name('telemetry.py'))}
    rows = []
    for line_number, raw_line in enumerate(source.splitlines(), 1):
        if not raw_line.strip():
            continue
        original = json.loads(raw_line)
        row = dict(original)
        row['original_measurements'] = {key: original.get(key) for key in LEGACY_FIELDS}
        row.update(measure_result(None))  # corrected totals remain unknown unless evidence binds
        row['cost_usd'] = original.get('cost_usd')
        row['cost_usd_source'] = 'original_record_unreplayed'
        row['agent_task_dispatches'] = None
        row['reviews_used_is_verified'] = False
        row['reviews_used_source'] = original.get('reviews_used_source', 'legacy_self_report_or_dispatch_fallback')
        row['critic_dispatches_semantics'] = 'legacy_dispatch_count; reviewer role and completion are not inferred'
        row['accepted'] = accepted_checks(original)
        row['acceptance_source'] = 'original_recorded_checks_including_held_out; checks_not_rerun'
        provenance = {'source_results': _label(results_path), 'source_results_sha256': source_hash,
                      'source_line': line_number, 'source_line_sha256': sha256_bytes(raw_line),
                      'tools': identities}
        row['replay_provenance'] = provenance
        if original.get('pilot') or original.get('harness_failure'):
            row['replay_status'] = 'excluded_original_record'
            rows.append(row)
            continue
        transcript = (pairs_root / original['task_id'] / original['flag'] / f"arm{original['arm']}.transcript.jsonl").resolve()
        if not transcript.is_relative_to(pairs_root):
            raise ValueError('record resolves outside the supplied pairs directory')
        provenance['transcript'] = _label(transcript)
        if not transcript.is_file():
            row['replay_status'] = 'missing_transcript'
            rows.append(row)
            continue
        data = transcript.read_bytes()
        result, dispatches, tool_calls = parse_stream(data.decode('utf-8'))
        provenance['transcript_sha256'] = sha256_bytes(data)
        matched, method = bind_transcript(original, result, data)
        provenance['binding_method'] = method
        if not matched:
            row['replay_status'] = 'unmatched_transcript'
            rows.append(row)
            continue
        row.update(measure_result(result))
        row['agent_task_dispatches'] = dispatches
        row['observed_tool_calls'] = tool_calls
        row['replay_status'] = 'matched_transcript'
        rows.append(row)
    return rows, source_hash


def summarize(rows):
    counted = [r for r in rows if not r.get('pilot') and not r.get('harness_failure')]
    matched = [r for r in counted if r['replay_status'] == 'matched_transcript']
    known = [r for r in matched if r['total_tokens'] is not None]
    summary = {'original_rows': len(rows), 'counted_rows': len(counted), 'matched_transcripts': len(matched),
               'known_model_usage_totals': len(known),
               'original_tokens_sum': sum(r['original_measurements'].get('total_tokens') or 0 for r in counted),
               'model_usage_tokens_sum_known_rows': sum(r['total_tokens'] for r in known),
               'reconciled_cost_rows': sum(r['cost_reconciles'] is True for r in matched),
               'cost_mismatch_rows': sum(r['cost_reconciles'] is False for r in matched),
               'accepted_original': sum(r['original_measurements'].get('accepted') is True for r in counted),
               'accepted_with_held_out': sum(r['accepted'] for r in counted),
               'flags': {}}
    for flag in sorted({r['flag'] for r in counted}):
        grouped = {}
        for row in known:
            if row['flag'] == flag:
                arms = grouped.setdefault(row['task_id'], {})
                if row['arm'] in arms:
                    raise ValueError(f'duplicate counted task/arm for {flag}: {row["task_id"]}/{row["arm"]}')
                arms[row['arm']] = row
        pairs = [arms for arms in grouped.values() if 'A' in arms and 'B' in arms]
        summary['flags'][flag] = {
            'complete_pairs_with_model_usage': len(pairs),
            'mean_total_tokens_A_minus_B': statistics.mean(p['A']['total_tokens'] - p['B']['total_tokens'] for p in pairs) if pairs else None,
        }
    return summary


def render_report(rows, summary, source_hash):
    lines = ['# Measurement replay', '', f'Original results SHA-256: `{source_hash}`.', '',
             'This report derives measurements from saved transcripts. It makes no model calls and does not rerun correctness checks. Original result rows remain unchanged.', '',
             f"Of {summary['original_rows']} original rows, {summary['counted_rows']} are counted. "
             f"{summary['matched_transcripts']} counted transcripts bind to their original rows; "
             f"{summary['known_model_usage_totals']} have complete modelUsage token categories.", '',
             '| Measurement | Value |', '| --- | ---: |',
             f"| Original counted token sum | {summary['original_tokens_sum']:,} |",
             f"| modelUsage token sum, known counted rows only | {summary['model_usage_tokens_sum_known_rows']:,} |",
             f"| Costs reconciled to result.total_cost_usd | {summary['reconciled_cost_rows']} |",
             f"| Cost mismatches | {summary['cost_mismatch_rows']} |",
             f"| Original / held-out-aware acceptance | {summary['accepted_original']} / {summary['accepted_with_held_out']} |", '',
             '| Flag | Complete pairs with modelUsage | Mean tokens A minus B |', '| --- | ---: | ---: |']
    for flag, stats in summary['flags'].items():
        mean = stats['mean_total_tokens_A_minus_B']
        lines.append(f"| {flag} | {stats['complete_pairs_with_model_usage']} | {mean:,.3f} |" if mean is not None
                     else f'| {flag} | 0 | unknown |')
    lines += ['', 'The corrected token sum uses inputTokens + outputTokens + cacheReadInputTokens + cacheCreationInputTokens across all result.modelUsage entries. result.usage is recorded separately. No lead/subagent semantics are inferred, and missing categories stay unknown. Cached input tokens are included; token count is not a dollar-equivalent cost.', '',
              'Each derived row records source line, source/line/transcript SHA-256, tool hashes, binding method, and original measurements. Legacy binding matches usage, cost and turns; it cannot retroactively prove the identity of an unsaved historical transcript. Excluded pilot/startup rows are not rebound to later reruns.', '',
              'Agent/Task calls are dispatch attempts, not verified critic reviews. Legacy review fields remain labeled unverified. Acceptance is recomputed from recorded suite, scope and held-out results; no test suite is rerun. These corrections do not establish a causal performance benefit.', '']
    unresolved = [r for r in rows if not r.get('pilot') and not r.get('harness_failure')
                  and (r['replay_status'] != 'matched_transcript' or r['total_tokens'] is None or r['cost_reconciles'] is not True)]
    if unresolved:
        lines += ['Unresolved measurements:', '']
        lines += [f"- {r['task_id']} / {r['flag']} / {r['arm']}: {r['replay_status']}, tokens {r['total_tokens_status']}, cost {r['cost_reconciliation_status']}." for r in unresolved]
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=DEFAULT_RESULTS)
    parser.add_argument('--pairs', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(argv)
    results = args.results.resolve()
    pairs = (args.pairs or results.parent / 'pairs').resolve()
    output, report = args.output.resolve(), args.report.resolve()
    if output == report or any(p == results or p.is_relative_to(pairs) for p in (output, report)):
        parser.error('derived outputs must be distinct and cannot overwrite original results or pair evidence')
    rows, source_hash = derive_rows(results, pairs)
    summary = summarize(rows)
    report_text = render_report(rows, summary, source_hash)
    if sha256_bytes(results.read_bytes()) != source_hash:
        raise SystemExit('REFUSED: source results changed during replay')
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows), encoding='utf-8')
    report.write_text(report_text, encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0 if (summary['known_model_usage_totals'] == summary['counted_rows']
                 and summary['reconciled_cost_rows'] == summary['counted_rows']) else 2


if __name__ == '__main__':
    raise SystemExit(main())
