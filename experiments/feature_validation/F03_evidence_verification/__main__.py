"""Minimal command-line interface; registered A/B/C only."""
import argparse
import json

from .verifier import verify


def main():
    parser = argparse.ArgumentParser(description='F03: execute a frozen reviewed version and verify a bounded output claim')
    parser.add_argument('--case', required=True, choices=['A', 'B', 'C'])
    parser.add_argument('--args', required=True, help='JSON positional arguments: [3] or [[-5,-2]]')
    parser.add_argument('--version', default='original')
    parser.add_argument('--source-hash', help='Expected registered source SHA256; mismatches block execution')
    parser.add_argument('--predict', help='JSON return value to verify; not arbitrary natural-language analysis')
    parser.add_argument('--statement', help='Original wording retained alongside the explicitly normalized output prediction')
    ns = parser.parse_args()
    try:
        args = json.loads(ns.args)
        claim = None
        if ns.predict is not None:
            claim = {'kind': 'output_equals', 'value': json.loads(ns.predict), 'args': args,
                     'text': ns.statement, 'origin': 'CLI_user_explicit_output_predicate'}
        elif ns.statement is not None:
            claim = {'kind': 'non_executable', 'text': ns.statement, 'origin': 'CLI_unparsed_statement'}
    except json.JSONDecodeError as exc:
        parser.error('Use valid JSON: ' + str(exc))
    result = verify(ns.case, args, source_version=ns.version, expected_source_hash=ns.source_hash, claim=claim)
    print(json.dumps({k: result[k] for k in ['case_id', 'source_version', 'source_hash', 'input_legal',
          'allowed_to_execute', 'actual_output', 'reference_output', 'matches_reference', 'verification',
          'error_reason', 'elapsed_ms', 'evidence_files']}, ensure_ascii=False, indent=2))
    return 0 if result['execution_success'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
