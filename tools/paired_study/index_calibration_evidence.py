"""Index local calibration evidence without rewriting append-only observations.

Pilot 01/02 recorded transcript_sha256 over LF-normalized UTF-8 text, while
Windows wrote CRLF files. Preserve those hashes and bind the actual saved bytes
in a derived sidecar. This command is offline and makes no model calls.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build_index(run):
    events_path = run / 'events.jsonl'
    events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines()]
    records = []
    for event in events:
        if event['event'] != 'completed':
            continue
        relative = 'private/' + event['task_id'] + '-' + event['stage'] + '.transcript.jsonl'
        path = run / relative
        raw_hash = sha(path.read_bytes())
        text_hash = sha(path.read_text(encoding='utf-8').encode('utf-8'))
        encoding = event.get('transcript_sha256_encoding', 'normalized-utf8-text')
        if encoding not in ('file-bytes', 'normalized-utf8-text'):
            raise ValueError('Unknown transcript hash encoding: ' + encoding)
        expected = raw_hash if encoding == 'file-bytes' else text_hash
        if event['transcript_sha256'] != expected:
            raise ValueError('Transcript does not match the original observation: ' + relative)
        records.append({
            'task_id': event['task_id'], 'stage': event['stage'], 'path': relative,
            'recorded_sha256': event['transcript_sha256'],
            'recorded_hash_encoding': encoding,
            'file_bytes_sha256': raw_hash, 'normalized_utf8_text_sha256': text_hash,
            'recorded_hash_verified': True,
        })
    return {
        'schema': 1, 'events_file_bytes_sha256': sha(events_path.read_bytes()),
        'scope': 'Completed calls with locally retained private transcripts; no source observations changed.',
        'transcripts': records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    index = build_index(args.run)
    (args.run / 'evidence-index.json').write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'verified_transcripts': len(index['transcripts'])}))


if __name__ == '__main__':
    main()
