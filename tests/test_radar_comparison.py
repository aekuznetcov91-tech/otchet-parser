"""Radar dates and comparison semantics on synthetic and current snapshot data."""
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RadarComparisonTest(unittest.TestCase):
    def test_comparable_periods(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node is required')
        result = subprocess.run([node, 'tests/radar_comparison.cjs'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
