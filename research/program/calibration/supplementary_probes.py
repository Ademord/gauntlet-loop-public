"""Offline post-run checks of concrete findings; never replace frozen primary scores."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def cases():
    chain = [{'id': str(i), 'depends_on': [str(i + 1)] if i < 2999 else [], 'status': 'done'}
             for i in range(3000)]
    cycle = copy.deepcopy(chain)
    cycle[-1]['depends_on'] = ['0']
    return [
        {'id': 'duration-overflow', 'task': 'c004-duration-parser', 'function': 'parse_duration',
         'input_description': 'PT followed by 400 nines and H', 'args': ['PT' + '9' * 400 + 'H'],
         'expected': 'unknown', 'selection': 'Concrete overflow reported by the reviewer and self-check.'},
        {'id': 'duration-nonbreaking-space', 'task': 'c004-duration-parser', 'function': 'parse_duration',
         'input_description': '1 followed by U+00A0 and hour', 'args': ['1\u00a0hour'],
         'expected': 3600, 'selection': 'Post-run inspection of the self-check re.ASCII edit; contract permits whitespace and constrains only digits to ASCII.'},
        {'id': 'scheduler-deep-chain', 'task': 'c006-ready-scheduler', 'function': 'ready_tasks',
         'input_description': '3000 done tasks: id i depends on i+1; last has no dependency; capacity 1',
         'args': [chain, 1], 'expected': [], 'selection': 'Recursion-depth issue reported by reviewer and self-check; no input-size ceiling in public contract.'},
        {'id': 'scheduler-deep-cycle', 'task': 'c006-ready-scheduler', 'function': 'ready_tasks',
         'input_description': 'Same 3000 done tasks, with final task depending on id 0; capacity 1',
         'args': [cycle, 1], 'expected_exception': 'ValueError',
         'selection': 'Cycle-detection correction claimed in final stage messages; contract requires ValueError even for done tasks.'},
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    assert (run / 'completion.json').exists(), 'Finish model generation before supplementary evaluation.'
    results = []
    for case in cases():
        row = {key: value for key, value in case.items() if key != 'args'}
        row['results'] = []
        for arm in ('baseline', 'self_check', 'review', 'reference'):
            path = (HERE / 'tasks' / case['task'] / 'oracle/solution.py' if arm == 'reference'
                    else run / 'artifacts' / case['task'] / arm / 'solution.py')
            spec = importlib.util.spec_from_file_location('probe_' + arm, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            try:
                actual = getattr(module, case['function'])(*copy.deepcopy(case['args']))
                observation = {'actual': actual, 'passed': 'expected_exception' not in case and actual == case['expected']}
            except Exception as exc:
                observation = {'exception': type(exc).__name__, 'passed': type(exc).__name__ == case.get('expected_exception')}
            row['results'].append({'arm': arm, 'source': path.relative_to(ROOT).as_posix(),
                                   'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **observation})
        results.append(row)
    output = {'classification': 'Supplementary post-run findings, selected after reading stage summaries/patches; no primary-score changes or population inference.',
              'recursion_limit': sys.getrecursionlimit(), 'cases': results}
    (run / 'supplementary-findings.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({r['id']: {x['arm']: x for x in r['results']} for r in results}, indent=2))


if __name__ == '__main__':
    main()
