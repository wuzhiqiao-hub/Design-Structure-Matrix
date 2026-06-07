import tempfile
import unittest
from pathlib import Path

from DSMzuoye import analyze, read_csv_matrix, validate_matrix


class DSMISMTests(unittest.TestCase):
    def test_analyze_chain_structure(self):
        labels = ["A", "B", "C"]
        matrix = [
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0],
        ]

        result = analyze(labels, matrix)

        self.assertEqual(
            result.reachability_matrix,
            [
                [1, 1, 1],
                [0, 1, 1],
                [0, 0, 1],
            ],
        )
        self.assertEqual(result.levels, [["C"], ["B"], ["A"]])
        self.assertEqual(result.driving_power, [3, 2, 1])
        self.assertEqual(result.dependence_power, [1, 2, 3])

    def test_validate_rejects_non_square_matrix(self):
        with self.assertRaisesRegex(ValueError, "expected 2"):
            validate_matrix([[0, 1], [1]], ["A", "B"])

    def test_validate_rejects_non_binary_value(self):
        with self.assertRaisesRegex(ValueError, "must be 0 or 1"):
            validate_matrix([[0, 2], [1, 0]], ["A", "B"])

    def test_read_csv_matrix(self):
        csv_text = ",A,B\nA,0,1\nB,0,0\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "matrix.csv"
            path.write_text(csv_text, encoding="utf-8")

            labels, matrix = read_csv_matrix(path)

        self.assertEqual(labels, ["A", "B"])
        self.assertEqual(matrix, [[0, 1], [0, 0]])

    def test_read_csv_rejects_mismatched_labels(self):
        csv_text = ",A,B\nA,0,1\nC,0,0\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.csv"
            path.write_text(csv_text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "row labels must match"):
                read_csv_matrix(path)


if __name__ == "__main__":
    unittest.main()
