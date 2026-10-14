"""
Keep the README, the landing page and example.py in sync with the code.

Every Python block in README.md and the Quick Start snippet in index.html is
executed, example.py is run, and the advertised chord/scale counts are checked.
"""

import html
import inspect
import os
import re
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

from midigen import CHORD_TYPES, Scale

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
INDEX = ROOT / "index.html"
EXAMPLE = ROOT / "example.py"


def readme_python_blocks():
    return re.findall(
        r"```python\n(.*?)```", README.read_text(encoding="utf-8"), flags=re.S
    )


def index_code_blocks():
    blocks = re.findall(
        r"<pre><code>(.*?)</code></pre>", INDEX.read_text(encoding="utf-8"), flags=re.S
    )
    return [html.unescape(re.sub(r"<[^>]+>", "", block)) for block in blocks]


def distinct_scale_count():
    patterns = set()
    for name, method in inspect.getmembers(Scale, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        pitches = method(60)
        patterns.add(tuple(p - pitches[0] for p in pitches))
    return len(patterns)


def run_snippet(code, label):
    """Execute a code snippet in an empty temp dir with warnings as errors."""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                exec(compile(code, label, "exec"), {"__name__": "__docs__"})
        finally:
            os.chdir(cwd)


@unittest.skipUnless(README.exists(), "README.md not available (installed package)")
class TestReadme(unittest.TestCase):
    def test_every_python_block_runs(self):
        blocks = readme_python_blocks()
        self.assertGreaterEqual(len(blocks), 8)
        for i, code in enumerate(blocks):
            with self.subTest(block=i, first_line=code.splitlines()[0]):
                run_snippet(code, f"README.md python block {i}")

    def test_chord_type_count(self):
        match = re.search(
            r"\*\*(\d+) chord types\*\*", README.read_text(encoding="utf-8")
        )
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), len(CHORD_TYPES))

    def test_scale_type_count(self):
        match = re.search(
            r"\*\*(\d+) scale types\*\*", README.read_text(encoding="utf-8")
        )
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), distinct_scale_count())


@unittest.skipUnless(INDEX.exists(), "index.html not available (installed package)")
class TestLandingPage(unittest.TestCase):
    def test_quick_start_runs(self):
        blocks = index_code_blocks()
        self.assertTrue(blocks)
        for i, code in enumerate(blocks):
            with self.subTest(block=i):
                run_snippet(code, f"index.html code block {i}")

    def test_scale_list_matches_library(self):
        text = INDEX.read_text(encoding="utf-8")
        tags = re.findall(r'<span class="scale-tag">([^<]+)</span>', text)
        self.assertEqual(len(tags), distinct_scale_count(), tags)
        for count in re.findall(r"(\d+)\+? Scales", text):
            self.assertEqual(int(count), distinct_scale_count())


@unittest.skipUnless(EXAMPLE.exists(), "example.py not available (installed package)")
class TestExampleScript(unittest.TestCase):
    def test_example_runs_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-W", "error", str(EXAMPLE)],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "PYTHONPATH": str(ROOT)},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                sorted(p.name for p in Path(tmp).glob("*.mid")),
                ["arpeggio.mid", "drums.mid", "melody_and_chord.mid", "song.mid"],
            )


if __name__ == "__main__":
    unittest.main()
