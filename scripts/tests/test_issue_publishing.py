"""Exercise publishing against a fake gh; never sends a network request."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class IssuePublishingTest(unittest.TestCase):
    def test_preserves_every_issue_body_including_newlines_and_letter_n(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            folder = Path(directory)
            fake = folder / 'gh'
            fake.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
if args[:2] == ['issue', 'list']:
    print('[]')
    if '--jq' in args:
        # Real --jq output is empty when there are no issues.
        pass
elif args[:2] == ['issue', 'create']:
    if '--body-file' in args:
        path = args[args.index('--body-file') + 1]
        body = sys.stdin.read() if path == '-' else Path(path).read_text()
    else:
        body = args[args.index('--body') + 1]
    with open(os.environ['ISSUE_CAPTURE'], 'a') as output:
        output.write(json.dumps({'title': args[args.index('--title') + 1], 'body': body}) + '\\n')
''')
            fake.chmod(0o755)
            capture = folder / 'captured.jsonl'
            result = subprocess.run(['bash', 'scripts/create-sprint0-issues.sh'], cwd=ROOT,
                                    env={**os.environ, 'PATH': str(folder) + os.pathsep + os.environ['PATH'],
                                         'ISSUE_CAPTURE': str(capture)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            actual = [json.loads(line) for line in capture.read_text().splitlines()]
            self.assertEqual(actual, json.loads((ROOT / 'scripts/issue-data.json').read_text()))


if __name__ == '__main__':
    unittest.main()
