"""Indexed research plans and evidence. Standard library; never dispatches model calls."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = Path('research/program')
QUESTIONS = ('claim', 'comparator', 'stop_rule', 'losses_to_check', 'cost', 'next_decision')
STATES = {'reuse', 'verified_scope', 'partial', 'open', 'deferred', 'rejected', 'superseded'}
QUEUES = {'ready', 'blocked', 'deferred', 'closed'}
KINDS = {'documentation', 'engineering', 'calibration', 'deterministic_audit', 'performance'}
CLAIM_ID = re.compile(r'M-\d{3,}')
EXPERIMENT_ID = re.compile(r'EXP-[A-Z0-9]+(?:-[A-Z0-9]+)*')
AUDIT_SCOPE = 'Inventory source pointers and proposed probe records only; no rule removal or performance adoption.'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def invalid(value):
        raise ValueError(f'Non-finite JSON number: {value}')
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=invalid)


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    try:
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(payload)
    except FileExistsError as exc:
        raise ValueError(f'Refusing to overwrite {path.name}') from exc


def repo_path(root, value, must_exist=True):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError(f'Invalid repository-relative path: {value!r}')
    rel = Path(value)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError(f'Path escapes repository: {value}')
    result = (root / rel).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes repository: {value}')
    if must_exist and not result.is_file():
        raise ValueError(f'Missing artifact: {value}')
    return result


def experiment_dir(root, experiment_id):
    if not isinstance(experiment_id, str) or not EXPERIMENT_ID.fullmatch(experiment_id):
        raise ValueError('Invalid experiment ID')
    return repo_path(root, (PROGRAM / 'experiments' / experiment_id).as_posix(), False)


def load_catalog(root):
    return read(root / PROGRAM / 'MILESTONES-50.json')


def load_evidence(root):
    return read(root / PROGRAM / 'evidence.json')['evidence']


def finite_number(value, unknown=False):
    return (value is None and unknown) or (type(value) in (int, float)
            and math.isfinite(value) and value >= 0)


def concrete_text(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in {'todo', 'tbd', 'unknown'}


def source_issues(root, catalog, source_id, today=None):
    today = today or date.today()
    source = catalog['sources'].get(source_id)
    if source is None:
        return [f'Unknown source {source_id}']
    issues = []
    if source.get('review_status', 'active') != 'active':
        issues.append(f'{source_id}: source is {source.get("review_status")}')
    if source.get('review_after_days') is not None:
        checked = date.fromisoformat(source.get('checked_date', catalog['checked_date']))
        if (today - checked).days > source['review_after_days']:
            issues.append(f'{source_id}: source review due; last checked {checked}')
    return issues


def evidence_issues(root, item, catalog, today=None):
    issues = []
    if item.get('review_status', 'active') != 'active':
        issues.append(f'{item["id"]}: evidence is {item.get("review_status")}')
    for artifact in item.get('artifacts', []):
        try:
            if file_hash(repo_path(root, artifact['path'])) != artifact['sha256']:
                issues.append(f'{item["id"]}: hash changed: {artifact["path"]}')
        except ValueError as exc:
            issues.append(str(exc))
    for source_id in item.get('source_ids', []):
        issues.extend(source_issues(root, catalog, source_id, today))
    return issues


def plan_errors(plan):
    errors = []
    if plan.get('schema_version') != 1 or not EXPERIMENT_ID.fullmatch(str(plan.get('id', ''))):
        errors.append('Invalid plan schema/ID')
    if not isinstance(plan.get('claim_ids'), list) or not plan['claim_ids']:
        errors.append('Plan requires claim_ids')
    if not isinstance(plan.get('questions'), dict) or any(k not in plan['questions'] for k in QUESTIONS):
        errors.append('Plan requires all six investor questions')
    if not isinstance(plan.get('metrics'), list) or not isinstance(plan.get('inputs'), list):
        errors.append('Plan requires metrics and inputs lists')
    if not isinstance(plan.get('prerequisites'), list):
        errors.append('Plan requires prerequisite records')
    else:
        for prerequisite in plan['prerequisites']:
            if type(prerequisite.get('satisfied')) is not bool or not prerequisite.get('id'):
                errors.append('Invalid prerequisite')
            if not isinstance(prerequisite.get('evidence_ids'), list) or not prerequisite.get('reason'):
                errors.append('Prerequisite requires evidence_ids and a reason')
            if not concrete_text(prerequisite.get('required_scope')):
                errors.append('Prerequisite requires an explicit required_scope')
    budget = plan.get('budget', {})
    if not finite_number(budget.get('model_execution_usd')):
        errors.append('Plan model_execution_usd must be a finite nonnegative number')
    for key in ('preparation_minutes', 'evaluation_minutes', 'human_minutes'):
        if key not in budget or not finite_number(budget[key], unknown=True):
            errors.append(f'Invalid budget {key}; use null for unknown')
    if not isinstance(plan.get('execution'), dict) or not plan['execution'].get('kind'):
        errors.append('Plan requires execution.kind')
    return errors


def result_errors(result, frozen):
    errors = []
    if result.get('schema_version') != 1 or result.get('experiment_id') != frozen['snapshot']['plan']['id']:
        errors.append('Result schema/experiment mismatch')
    if result.get('freeze_sha256') != frozen['sha256']:
        errors.append('Result does not bind the frozen plan')
    for key in ('outcomes', 'losses', 'exclusions', 'costs', 'decision', 'next_decision', 'limitations'):
        if key not in result:
            errors.append(f'Result missing {key}')
    if not isinstance(result.get('outcomes'), dict) or not result.get('outcomes'):
        errors.append('Result requires observed outcomes')
    if not isinstance(result.get('losses'), list) or not isinstance(result.get('exclusions'), list):
        errors.append('Result losses/exclusions must be explicit lists')
    costs = result.get('costs', {})
    for key in ('model_execution_usd', 'preparation_usd', 'evaluation_usd', 'research_usd', 'human_minutes'):
        if key not in costs or not finite_number(costs[key], unknown=True):
            errors.append(f'Invalid/missing actual cost {key}; unknown is null')
    decision = result.get('decision', {})
    if decision.get('outcome') not in {'reuse', 'adopt', 'reject', 'defer', 'inconclusive'}:
        errors.append('Result requires a recognized decision')
    if not decision.get('scope') or not result.get('limitations') or not result.get('next_decision'):
        errors.append('Result requires decision scope, limitations and next decision')
    if frozen['snapshot']['plan']['execution']['kind'] == 'inventory_audit':
        if result.get('evidence_kind') != 'deterministic_audit' or decision.get('outcome') not in {'reuse', 'reject', 'inconclusive'}:
            errors.append('Inventory audit cannot adopt a performance claim')
        outcomes = result.get('outcomes', {})
        if not isinstance(outcomes, dict):
            outcomes = {}
        for key in ('entries_checked', 'pointer_errors', 'native_behavior_probes_executed', 'model_calls'):
            if type(outcomes.get(key)) is not int or outcomes[key] < 0:
                errors.append(f'Inventory audit requires nonnegative integer {key}')
        if not finite_number(outcomes.get('audit_seconds')):
            errors.append('Inventory audit requires finite nonnegative audit_seconds')
        entry_ids = frozen['snapshot'].get('inventory_entry_ids')
        if not isinstance(entry_ids, list) or outcomes.get('entries_checked') != len(entry_ids):
            errors.append('Inventory entries_checked must match the frozen inventory')
        if outcomes.get('native_behavior_probes_executed') != 0 or outcomes.get('model_calls') != 0 or costs.get('model_execution_usd') != 0:
            errors.append('Inventory audit executes zero native behavior probes and zero model calls/cost')
        if isinstance(result.get('losses'), list) and outcomes.get('pointer_errors') != len(result['losses']):
            errors.append('Inventory pointer_errors must match disclosed losses')
        if outcomes.get('pointer_errors', 0) and decision.get('outcome') == 'reuse':
            errors.append('Inventory with pointer errors cannot be reused')
        if decision.get('scope') != AUDIT_SCOPE:
            errors.append('Inventory audit requires the inventory-only decision scope')
    return errors


def validate(root, today=None):
    errors, warnings = [], []
    try:
        catalog = load_catalog(root)
        evidence = load_evidence(root)
        claims = catalog['milestones']
        by_id = {c['claim_id']: c for c in claims}
        by_evidence = {e['id']: e for e in evidence}
        if len(by_id) != len(claims) or len({c['id'] for c in claims}) != len(claims):
            errors.append('Duplicate milestone ID')
        if len(by_evidence) != len(evidence):
            errors.append('Duplicate evidence ID')
        for source_id, source in catalog['sources'].items():
            if not source.get('title') or not source.get('url'):
                errors.append(f'Incomplete source {source_id}')
            interval = source.get('review_after_days')
            if interval is not None and (type(interval) is not int or interval <= 0):
                errors.append(f'Invalid source review interval {source_id}')
            else:
                warnings.extend(source_issues(root, catalog, source_id, today))
        for claim in claims:
            cid = claim['claim_id']
            if not CLAIM_ID.fullmatch(cid) or int(cid[2:]) != claim['id']:
                errors.append(f'Invalid milestone ID {cid}')
            for field in ('milestone', 'claim', 'comparator', 'advance_or_stop', 'losses_to_disclose', 'allowance', 'next_decision'):
                if not isinstance(claim.get(field), str) or not claim[field].strip():
                    errors.append(f'{cid}: missing {field}')
            workflow = claim['workflow']
            if workflow.get('state') not in STATES or workflow.get('queue') not in QUEUES:
                errors.append(f'{cid}: invalid state/queue')
            if type(workflow.get('priority')) is not int or not workflow.get('scope'):
                errors.append(f'{cid}: priority/scope required')
            for dependency in workflow.get('depends_on', []):
                if dependency not in by_id:
                    errors.append(f'{cid}: unknown dependency {dependency}')
            for eid in claim['evidence_ids']:
                if eid not in by_evidence:
                    errors.append(f'{cid}: unknown evidence {eid}')
                elif cid not in by_evidence[eid]['claim_ids']:
                    errors.append(f'{cid}: evidence {eid} does not name this scope')
            if workflow.get('state') in {'reuse', 'verified_scope'} and not claim['evidence_ids']:
                errors.append(f'{cid}: completed scope requires evidence')
            if workflow.get('state') == 'verified_scope' and not any(
                    by_evidence.get(eid, {}).get('kind') in {'engineering', 'deterministic_audit'} for eid in claim['evidence_ids']):
                errors.append(f'{cid}: verified scope requires engineering evidence')
            for part in ('research_support', 'codex', 'claude_code'):
                for source_id in claim[part]['sources']:
                    if source_id not in catalog['sources']:
                        errors.append(f'{cid}: unknown source {source_id}')
            for eid in claim['experiment_ids']:
                if not (experiment_dir(root, eid) / 'plan.json').is_file():
                    errors.append(f'{cid}: missing experiment {eid}')
        visiting, seen = set(), set()
        def visit(cid):
            if cid in visiting:
                errors.append(f'Dependency cycle at {cid}')
                return
            if cid in seen or cid not in by_id:
                return
            visiting.add(cid)
            for dependency in by_id[cid]['workflow'].get('depends_on', []):
                visit(dependency)
            visiting.remove(cid)
            seen.add(cid)
        for cid in by_id:
            visit(cid)
        for item in evidence:
            date.fromisoformat(item['observed_on'])
            if not isinstance(item.get('establishes'), list) or not item['establishes'] or not all(concrete_text(s) for s in item['establishes']):
                errors.append(f'{item["id"]}: evidence requires explicit establishes scopes')
            if item.get('kind') not in KINDS or not item.get('scope') or not item.get('limitations'):
                errors.append(f'{item["id"]}: evidence needs kind, scope and limitations')
            if not item.get('artifacts') and not item.get('source_ids'):
                errors.append(f'{item["id"]}: evidence has no resolvable support')
            if any(cid not in by_id for cid in item['claim_ids']):
                errors.append(f'{item["id"]}: unknown claim')
            for artifact in item.get('artifacts', []):
                try:
                    repo_path(root, artifact['path'])
                    if not re.fullmatch('[a-f0-9]{64}', artifact['sha256']):
                        errors.append(f'{item["id"]}: invalid SHA256')
                except ValueError as exc:
                    errors.append(str(exc))
            warnings.extend(evidence_issues(root, item, catalog, today))
        plans = list((root / PROGRAM / 'experiments').glob('*/plan.json'))
        for path in plans:
            plan = read(path)
            errors.extend(f'{path.parent.name}: {e}' for e in plan_errors(plan))
            if plan['id'] != path.parent.name:
                errors.append('Experiment directory/ID mismatch')
            for cid in plan.get('claim_ids', []):
                if cid not in by_id:
                    errors.append(f'{plan["id"]}: unknown claim {cid}')
                elif plan['id'] not in by_id[cid]['experiment_ids']:
                    errors.append(f'{plan["id"]}: missing reverse experiment link on {cid}')
            for value in plan.get('inputs', []):
                try:
                    repo_path(root, value)
                except ValueError as exc:
                    errors.append(str(exc))
            for prerequisite in plan.get('prerequisites', []):
                for eid in prerequisite.get('evidence_ids', []):
                    if eid not in by_evidence:
                        errors.append(f'{plan["id"]}: unknown prerequisite evidence {eid}')
            frozen_path = path.parent / 'frozen.json'
            if frozen_path.exists():
                frozen = read(frozen_path)
                if digest(frozen['snapshot']) != frozen['sha256']:
                    errors.append(f'{plan["id"]}: frozen snapshot hash mismatch')
                result_path = path.parent / 'result.json'
                if result_path.exists():
                    errors.extend(f'{plan["id"]}: {e}' for e in result_errors(read(result_path), frozen))
            elif (path.parent / 'result.json').exists():
                errors.append(f'{plan["id"]}: result without frozen plan')
        return {'errors': sorted(set(errors)), 'warnings': sorted(set(warnings)),
                'milestones': len(claims), 'evidence': len(evidence), 'experiments': len(plans)}
    except (KeyError, TypeError, ValueError, OSError) as exc:
        errors.append(f'Invalid program data: {exc}')
        return {'errors': sorted(set(errors)), 'warnings': sorted(set(warnings))}


def material_errors(root, path, catalog):
    material = read(repo_path(root, path))
    errors, ids = [], set()
    entries = material.get('entries', [])
    if not entries:
        errors.append('Inventory has no entries')
    for source_path, expected in material.get('source_files', {}).items():
        if file_hash(repo_path(root, source_path)) != expected:
            errors.append(f'Inventory source file changed: {source_path}')
    for entry in entries:
        eid = entry['id']
        if eid in ids:
            errors.append(f'Duplicate inventory entry {eid}')
        ids.add(eid)
        skill = entry['skill']
        lines = repo_path(root, skill['path']).read_text(encoding='utf-8').splitlines()
        start, end = skill['line_start'], skill['line_end']
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            errors.append(f'{eid}: invalid line range')
            continue
        excerpt = '\n'.join(lines[start - 1:end])
        if hashlib.sha256(excerpt.encode()).hexdigest() != skill['lines_sha256']:
            errors.append(f'{eid}: skill clause changed')
        if skill['excerpt'] not in excerpt or hashlib.sha256(skill['excerpt'].encode()).hexdigest() != skill['excerpt_sha256']:
            errors.append(f'{eid}: excerpt does not match source')
        if not entry.get('source_ids'):
            errors.append(f'{eid}: no native support source')
        for source_id in entry.get('source_ids', []):
            errors.extend(source_issues(root, catalog, source_id))
        if entry.get('recommended_action') not in {'keep', 'consider_removal', 'needs_probe'}:
            errors.append(f'{eid}: invalid proposed action')
        if entry.get('overlap_classification') not in {'native_primitive', 'mixed', 'gauntlet_policy'}:
            errors.append(f'{eid}: invalid overlap classification')
        probe = entry.get('discriminating_probe')
        if not isinstance(probe, dict):
            errors.append(f'{eid}: discriminating_probe must be a record')
        else:
            for field in ('setup', 'pass_condition'):
                if not concrete_text(probe.get(field)):
                    errors.append(f'{eid}: probe requires concrete {field}')
            for field, minimum in (('variants', 2), ('faults', 1), ('metrics', 1)):
                values = probe.get(field)
                if not isinstance(values, list) or len(values) < minimum or not all(concrete_text(v) for v in values):
                    errors.append(f'{eid}: probe requires at least {minimum} concrete {field}')
        if entry.get('probe_status') != 'not_run' or not concrete_text(entry.get('risk')):
            errors.append(f'{eid}: missing probe/risk or unsubstantiated probe status')
    return material, errors


def snapshot(root, plan):
    catalog = load_catalog(root)
    claims = [{k: v for k, v in c.items() if k not in {'workflow', 'evidence_ids', 'experiment_ids'}}
              for c in catalog['milestones'] if c['claim_id'] in plan['claim_ids']]
    evidence_ids = {eid for p in plan['prerequisites'] for eid in p['evidence_ids']}
    evidence = [e for e in load_evidence(root) if e['id'] in evidence_ids]
    source_ids = {sid for c in claims for part in ('research_support', 'codex', 'claude_code') for sid in c[part]['sources']}
    paths = set(plan['inputs'])
    inventory_entry_ids = []
    for item in evidence:
        paths.update(a['path'] for a in item.get('artifacts', []))
        source_ids.update(item.get('source_ids', []))
    if plan['execution']['kind'] == 'inventory_audit':
        paths.add(plan['execution']['material'])
        material = read(repo_path(root, plan['execution']['material']))
        inventory_entry_ids = [entry['id'] for entry in material['entries']]
        for entry in material['entries']:
            paths.add(entry['skill']['path'])
            source_ids.update(entry['source_ids'])
    return {'plan': plan, 'claims': claims, 'evidence': evidence,
            'inventory_entry_ids': inventory_entry_ids,
            'driver': {'path': 'tools/program.py', 'sha256': file_hash(Path(__file__).resolve())},
            'sources': {sid: catalog['sources'][sid] for sid in sorted(source_ids)},
            'inputs_sha256': {p: file_hash(repo_path(root, p)) for p in sorted(paths)}}


def readiness(root, experiment_id):
    report = validate(root)
    if report['errors']:
        return report['errors']
    directory = experiment_dir(root, experiment_id)
    try:
        plan = read(directory / 'plan.json')
        issues = plan_errors(plan)
        catalog, evidence = load_catalog(root), {e['id']: e for e in load_evidence(root)}
        for question in QUESTIONS:
            value = plan['questions'].get(question)
            if not isinstance(value, str) or not value.strip() or value.strip().lower() in {'todo', 'tbd', 'unknown'}:
                issues.append(f'Unspecified investor question: {question}')
        if not plan['metrics'] or not plan['inputs']:
            issues.append('Concrete metrics and inputs required')
        for prerequisite in plan['prerequisites']:
            if not prerequisite['satisfied']:
                issues.append(f'{prerequisite["id"]}: {prerequisite["reason"]}')
            elif not prerequisite['evidence_ids']:
                issues.append(f'{prerequisite["id"]}: satisfied prerequisite requires scoped evidence')
            elif not any(prerequisite['required_scope'] in evidence[eid]['establishes'] for eid in prerequisite['evidence_ids']):
                issues.append(f'{prerequisite["id"]}: evidence does not establish required scope {prerequisite["required_scope"]}')
            for eid in prerequisite['evidence_ids']:
                issues.extend(evidence_issues(root, evidence[eid], catalog))
        if plan['execution']['kind'] != 'inventory_audit':
            issues.append('External execution is not implemented by this tool; qualify a runner separately')
        else:
            if plan['budget']['model_execution_usd'] != 0:
                issues.append('Inventory audit must have a zero model-execution budget')
            _, failures = material_errors(root, plan['execution']['material'], catalog)
            issues.extend(failures)
        current = snapshot(root, plan)
        for sid in current['sources']:
            issues.extend(source_issues(root, catalog, sid))
        frozen_path = directory / 'frozen.json'
        if frozen_path.exists() and digest(current) != read(frozen_path)['sha256']:
            issues.append('Frozen inputs changed; create an amended experiment ID, do not overwrite the prior plan')
        return sorted(set(issues))
    except (KeyError, TypeError, ValueError, OSError) as exc:
        return [f'Cannot prepare experiment: {exc}']


def freeze(root, experiment_id):
    issues = readiness(root, experiment_id)
    if issues:
        raise ValueError('; '.join(issues))
    directory = experiment_dir(root, experiment_id)
    frozen = snapshot(root, read(directory / 'plan.json'))
    path = directory / 'frozen.json'
    write_new(path, {'schema_version': 1, 'frozen_at': datetime.now(timezone.utc).isoformat(),
                     'sha256': digest(frozen), 'snapshot': frozen})
    return path


def record(root, experiment_id, result):
    directory = experiment_dir(root, experiment_id)
    frozen = read(directory / 'frozen.json')
    if digest(frozen['snapshot']) != frozen['sha256']:
        raise ValueError('Frozen snapshot hash mismatch')
    errors = result_errors(result, frozen)
    if errors:
        raise ValueError('; '.join(errors))
    write_new(directory / 'result.json', result)


def run_inventory(root, experiment_id):
    directory = experiment_dir(root, experiment_id)
    if not (directory / 'frozen.json').is_file():
        raise ValueError('Freeze the plan before running')
    if (directory / 'result.json').exists():
        raise ValueError('Result already exists; no overwrite or automatic retry')
    issues = readiness(root, experiment_id)
    if issues:
        raise ValueError('; '.join(issues))
    started = time.monotonic()
    frozen = read(directory / 'frozen.json')
    material, errors = material_errors(root, frozen['snapshot']['plan']['execution']['material'], load_catalog(root))
    result = {'schema_version': 1, 'experiment_id': experiment_id, 'freeze_sha256': frozen['sha256'],
              'recorded_at': datetime.now(timezone.utc).isoformat(), 'evidence_kind': 'deterministic_audit',
              'outcomes': {'entries_checked': len(material['entries']), 'pointer_errors': len(errors),
                           'native_behavior_probes_executed': 0, 'model_calls': 0,
                           'audit_seconds': time.monotonic() - started},
              'losses': errors, 'exclusions': [],
              'costs': {'model_execution_usd': 0, 'preparation_usd': None, 'evaluation_usd': None,
                        'research_usd': None, 'human_minutes': None},
              'decision': {'outcome': 'reject' if errors else 'reuse',
                           'scope': AUDIT_SCOPE},
              'next_decision': 'Choose one candidate, then qualify the configured native control before any removal comparison.',
              'limitations': ['No live native behavior was tested.', 'Instruction savings and delivery gains are unmeasured.',
                              'Preparation, research, evaluation and human cost remain unknown.']}
    record(root, experiment_id, result)
    return result


def next_items(root):
    report = validate(root)
    if report['errors']:
        raise ValueError('; '.join(report['errors']))
    catalog = load_catalog(root)
    evidence = {e['id']: e for e in load_evidence(root)}
    claims = {c['claim_id']: c for c in catalog['milestones']}
    ready = []
    def fresh_scope(cid):
        item = claims[cid]
        return not any(evidence_issues(root, evidence[e], catalog) for e in item['evidence_ids']) and all(
            fresh_scope(d) for d in item['workflow'].get('depends_on', []))
    for claim in claims.values():
        workflow = claim['workflow']
        if workflow['queue'] != 'ready':
            continue
        # Dependencies order research work only. Experiment prerequisites always require scoped evidence.
        if any(claims[d]['workflow']['state'] not in {'reuse', 'verified_scope', 'rejected', 'superseded'}
               for d in workflow.get('depends_on', [])):
            continue
        if not fresh_scope(claim['claim_id']):
            continue
        ready.append(claim)
    return sorted(ready, key=lambda c: (c['workflow']['priority'], c['claim_id']))


def new_plan(root, experiment_id, claim_ids):
    catalog = load_catalog(root)
    claims = {c['claim_id']: c for c in catalog['milestones']}
    if not claim_ids or any(c not in claims for c in claim_ids):
        raise ValueError('Choose existing milestone IDs')
    directory = experiment_dir(root, experiment_id)
    plan = {'schema_version': 1, 'id': experiment_id, 'status': 'draft', 'claim_ids': claim_ids,
            'questions': dict.fromkeys(QUESTIONS, None), 'metrics': [], 'inputs': [],
            'prerequisites': [{'id': 'specific-treatment-and-controls', 'required_scope': 'specific-treatment-and-controls',
                               'satisfied': False, 'evidence_ids': [],
                               'reason': 'Define actual treatment, controls, scope and execution method.'}],
            'execution': {'kind': 'external'},
            'budget': {'model_execution_usd': 0, 'preparation_minutes': None, 'evaluation_minutes': None, 'human_minutes': None}}
    write_new(directory / 'plan.json', plan)
    for cid in claim_ids:
        claims[cid]['experiment_ids'].append(experiment_id)
    (root / PROGRAM / 'MILESTONES-50.json').write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return directory / 'plan.json'


def render(root, check=False):
    report = validate(root)
    if report['errors']:
        raise ValueError('; '.join(report['errors']))
    catalog = load_catalog(root)
    lines = ['# Research program', '', '<!-- Generated by tools/program.py render; edit the JSON records. -->', '',
             'Start here. Claims live in [MILESTONES-50.json](MILESTONES-50.json); observations in [evidence.json](evidence.json).',
             'Native availability, engineering verification and performance evidence are separate. No native performance advantage is inferred from a checkmark.', '',
             '```text', 'python tools/program.py validate', 'python tools/program.py next',
             'python tools/program.py show M-031', 'python tools/program.py readiness EXP-031-033-002',
             'python tools/program.py render --check', '```', '',
             'See [WORKFLOW.md](WORKFLOW.md) for preparing, freezing and recording a bounded experiment.',
             'The [full matrix](MILESTONES-50.md) includes research and native support. Inspect the [twelve proposed probes](materials/native-overlap.json)',
             'and the [first removal proposal](materials/OVL-001/change.json) for concrete testing material.',
             'Commands in this tool do not dispatch models. Historical [calibration](calibration/DECISION.md), [backlog](backlog.md),',
             '[feature inventory](feature-inventory.json) and [research/native review](RESEARCH-NATIVE-50.md) retain their own scopes.', '',
             '## Next eligible research work', '']
    for item in next_items(root):
        lines.append(f'- **{item["claim_id"]}** {item["milestone"]}: {item["next_decision"]}')
    lines += ['', '## Experiments', '', '| Plan | Stage | Linked milestones | Records |', '| --- | --- | --- | --- |']
    for path in sorted((root / PROGRAM / 'experiments').glob('*/plan.json')):
        plan = read(path)
        stage = 'recorded' if (path.parent / 'result.json').exists() else 'frozen' if (path.parent / 'frozen.json').exists() else 'draft'
        records = ' / '.join(f'[{name}](experiments/{plan["id"]}/{name}.json)' for name in ('frozen', 'result') if (path.parent / f'{name}.json').exists()) or 'None yet'
        lines.append(f'| [{plan["id"]}](experiments/{plan["id"]}/plan.json) | {stage} | {", ".join(plan["claim_ids"])} | {records} |')
    lines += ['', '## Evidence index', '', '| ID | Kind | Established scope |', '| --- | --- | --- |']
    for item in load_evidence(root):
        lines.append(f'| {item["id"]} | {item["kind"]} | {item["scope"]} |')
    lines += ['', '## Milestone index', '', '| ID | Milestone | Evidence state | Queue | Evidence / experiments |', '| --- | --- | --- | --- | --- |']
    for c in catalog['milestones']:
        lines.append(f'| {c["claim_id"]} | {c["milestone"]} | {c["workflow"]["state"]} | {c["workflow"]["queue"]} | {len(c["evidence_ids"])} / {len(c["experiment_ids"])} |')
    detail = ['# Fifty indexed research milestones', '',
              '<!-- Generated by tools/program.py render; edit MILESTONES-50.json. -->', '',
              'Use the [program index](README.md) and [workflow](WORKFLOW.md). The [source review](RESEARCH-NATIVE-50.md) records dated support and limits.',
              'Research support, native availability, scoped engineering evidence and demonstrated performance are separate axes.',
              'G and the L/S/B/Q proposed allowances are defined in [WORKFLOW.md](WORKFLOW.md). Actual unknown costs stay null in result records.', '',
              '| ID | Milestone | Research | Codex native | Claude Code native | Evidence state / scope | Exact claim | Comparator | Stop / advance | Losses to disclose | Proposed allowance | Next decision |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    def refs(ids):
        return ' '.join('[' + sid + ']' for sid in ids)
    for c in catalog['milestones']:
        cells = [c['claim_id'], c['milestone'], c['research_support']['label'] + ' ' + refs(c['research_support']['sources']),
                 c['codex']['support'] + ' ' + refs(c['codex']['sources']),
                 c['claude_code']['support'] + ' ' + refs(c['claude_code']['sources']),
                 c['workflow']['state'] + ': ' + c['workflow']['scope'], c['claim'], c['comparator'],
                 c['advance_or_stop'], c['losses_to_disclose'], c['allowance'], c['next_decision']]
        detail.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in cells) + ' |')
    detail += [''] + [f'[{sid}]: {source["url"]}' for sid, source in catalog['sources'].items()]
    outputs = {'README.md': '\n'.join(lines) + '\n', 'MILESTONES-50.md': '\n'.join(detail) + '\n'}
    for filename, output in outputs.items():
        target = root / PROGRAM / filename
        if check:
            if not target.exists() or target.read_text(encoding='utf-8') != output:
                raise ValueError(f'Generated {filename} is stale; run render')
        else:
            target.write_text(output, encoding='utf-8', newline='\n')
    return root / PROGRAM / 'README.md'


def main(argv=None):
    # Windows pipe encodings may otherwise reject the catalog's Unicode labels.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('validate')
    commands.add_parser('next')
    listing = commands.add_parser('list')
    listing.add_argument('--state', choices=sorted(STATES))
    show = commands.add_parser('show')
    show.add_argument('claim_id')
    for action in ('readiness', 'freeze', 'run'):
        sub = commands.add_parser(action)
        sub.add_argument('experiment_id')
    create = commands.add_parser('prepare')
    create.add_argument('experiment_id')
    create.add_argument('claim_ids', nargs='+')
    save = commands.add_parser('record')
    save.add_argument('experiment_id')
    save.add_argument('result_file', type=Path)
    rendering = commands.add_parser('render')
    rendering.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == 'validate':
            result = validate(root)
            print(json.dumps(result, indent=2))
            return 1 if result['errors'] else 0
        if args.command == 'readiness':
            issues = readiness(root, args.experiment_id)
            print(json.dumps({'ready': not issues, 'blockers': issues}, indent=2))
            return 1 if issues else 0
        if args.command in {'next', 'list'}:
            claims = next_items(root) if args.command == 'next' else load_catalog(root)['milestones']
            for c in claims:
                if args.command == 'list' and args.state and c['workflow']['state'] != args.state:
                    continue
                print(f'{c["claim_id"]}  {c["workflow"]["state"]:15}  {c["milestone"]}')
            return 0
        if args.command == 'show':
            result = next((c for c in load_catalog(root)['milestones'] if c['claim_id'] == args.claim_id), None)
            if result is None:
                raise ValueError('Unknown milestone')
        elif args.command == 'freeze':
            result = str(freeze(root, args.experiment_id).relative_to(root))
        elif args.command == 'run':
            result = run_inventory(root, args.experiment_id)
        elif args.command == 'prepare':
            result = str(new_plan(root, args.experiment_id, args.claim_ids).relative_to(root))
        elif args.command == 'record':
            record(root, args.experiment_id, read(args.result_file))
            result = 'Recorded; milestone adoption is a separate scoped decision.'
        else:
            result = str(render(root, args.check).relative_to(root))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
