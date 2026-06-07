#!/usr/bin/env python3
"""DSM/ISM analysis tool.

This script reads a binary relationship matrix, validates it, computes DSM/ISM
results, and writes a concise report plus an optional Graphviz DOT diagram.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


Matrix = List[List[int]]


@dataclass(frozen=True)
class ISMResult:
    labels: List[str]
    adjacency_matrix: Matrix
    reachability_matrix: Matrix
    levels: List[List[str]]
    driving_power: List[int]
    dependence_power: List[int]


def validate_matrix(matrix: Matrix, labels: Sequence[str]) -> None:
    """Validate that matrix is square, binary, and matches labels."""
    if not matrix:
        raise ValueError("matrix must not be empty")

    size = len(matrix)
    if len(labels) != size:
        raise ValueError(
            f"label count ({len(labels)}) must match matrix size ({size})"
        )

    for row_index, row in enumerate(matrix, start=1):
        if len(row) != size:
            raise ValueError(
                f"row {row_index} has {len(row)} values; expected {size}"
            )
        for col_index, value in enumerate(row, start=1):
            if value not in (0, 1):
                raise ValueError(
                    f"matrix value at row {row_index}, column {col_index} "
                    f"must be 0 or 1, got {value!r}"
                )


def add_self_reachability(matrix: Matrix) -> Matrix:
    result = [row[:] for row in matrix]
    for index in range(len(result)):
        result[index][index] = 1
    return result


def transitive_closure(matrix: Matrix) -> Matrix:
    """Compute reachability matrix with Warshall's algorithm."""
    closure = add_self_reachability(matrix)
    size = len(closure)
    for via in range(size):
        for source in range(size):
            if closure[source][via] == 0:
                continue
            for target in range(size):
                if closure[via][target] == 1:
                    closure[source][target] = 1
    return closure


def derive_levels(reachability: Matrix, labels: Sequence[str]) -> List[List[str]]:
    """Derive ISM hierarchy levels from top/result level to bottom/driver level."""
    remaining = set(range(len(labels)))
    levels: List[List[str]] = []

    while remaining:
        current_level = []
        for item in sorted(remaining):
            reachable = {idx for idx in remaining if reachability[item][idx] == 1}
            antecedent = {idx for idx in remaining if reachability[idx][item] == 1}
            if reachable.issubset(antecedent):
                current_level.append(item)

        if not current_level:
            unresolved = ", ".join(labels[idx] for idx in sorted(remaining))
            raise ValueError(f"could not derive ISM levels for: {unresolved}")

        levels.append([labels[idx] for idx in current_level])
        remaining.difference_update(current_level)

    return levels


def power_scores(reachability: Matrix) -> Tuple[List[int], List[int]]:
    driving_power = [sum(row) for row in reachability]
    dependence_power = [
        sum(reachability[row][column] for row in range(len(reachability)))
        for column in range(len(reachability))
    ]
    return driving_power, dependence_power


def analyze(labels: Sequence[str], matrix: Matrix) -> ISMResult:
    labels = list(labels)
    validate_matrix(matrix, labels)
    reachability = transitive_closure(matrix)
    levels = derive_levels(reachability, labels)
    driving, dependence = power_scores(reachability)
    return ISMResult(
        labels=labels,
        adjacency_matrix=[row[:] for row in matrix],
        reachability_matrix=reachability,
        levels=levels,
        driving_power=driving,
        dependence_power=dependence,
    )


def read_csv_matrix(path: Path) -> Tuple[List[str], Matrix]:
    """Read CSV where first row and first column contain labels."""
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        rows = list(csv.reader(csv_file))

    if len(rows) < 2:
        raise ValueError("CSV must contain a header row and at least one matrix row")

    labels = [cell.strip() for cell in rows[0][1:]]
    if not labels or any(not label for label in labels):
        raise ValueError("CSV header must contain non-empty element labels")

    matrix: Matrix = []
    row_labels: List[str] = []
    for line_number, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        row_labels.append(row[0].strip())
        try:
            matrix.append([int(cell.strip()) for cell in row[1:]])
        except ValueError as exc:
            raise ValueError(f"CSV line {line_number} contains a non-integer value") from exc

    if row_labels != labels:
        raise ValueError(
            "CSV row labels must match column labels in the same order; "
            f"got rows {row_labels!r} and columns {labels!r}"
        )

    validate_matrix(matrix, labels)
    return labels, matrix


def format_matrix(labels: Sequence[str], matrix: Matrix) -> str:
    label_width = max(6, max(len(label) for label in labels))
    lines = [" " * (label_width + 1) + " ".join(f"{label:>{label_width}}" for label in labels)]
    for label, row in zip(labels, matrix):
        values = " ".join(f"{value:>{label_width}}" for value in row)
        lines.append(f"{label:>{label_width}} {values}")
    return "\n".join(lines)


def build_report(result: ISMResult) -> str:
    lines = [
        "DSM/ISM 分析报告",
        "=" * 23,
        "",
        "系统元素：",
        ", ".join(result.labels),
        "",
        "原始 DSM 邻接矩阵：",
        format_matrix(result.labels, result.adjacency_matrix),
        "",
        "可达矩阵：",
        format_matrix(result.labels, result.reachability_matrix),
        "",
        "ISM 层级划分（先显示顶层/结果层）：",
    ]

    for index, level in enumerate(result.levels, start=1):
        lines.append(f"第 {index} 层：{', '.join(level)}")

    lines.extend(["", "驱动力与依赖力："])
    for label, driving, dependence in zip(
        result.labels, result.driving_power, result.dependence_power
    ):
        lines.append(
            f"- {label}：驱动力 = {driving}，依赖力 = {dependence}"
        )

    top_level = result.levels[0] if result.levels else []
    bottom_level = result.levels[-1] if result.levels else []
    lines.extend(
        [
            "",
            "结果解释：",
            f"- 顶层/结果因素：{', '.join(top_level)}",
            f"- 底层/驱动因素：{', '.join(bottom_level)}",
            "- 驱动力越高，通常表示该因素对整个系统的影响越强。",
            "- 依赖力越高，通常表示该因素越容易受到其他因素影响。",
        ]
    )
    return "\n".join(lines) + "\n"


def write_dot(result: ISMResult, path: Path) -> None:
    level_by_label = {
        label: level_index
        for level_index, level in enumerate(result.levels, start=1)
        for label in level
    }
    lines = [
        "digraph ISM {",
        '  graph [rankdir=BT, labelloc="t", label="ISM hierarchy"];',
        '  node [shape=box, style="rounded,filled", fillcolor="#f7f7f7"];',
        '  edge [color="#555555"];',
    ]

    for label in result.labels:
        lines.append(f'  "{label}" [xlabel="L{level_by_label[label]}"];')

    for source_index, source in enumerate(result.labels):
        for target_index, target in enumerate(result.labels):
            if source_index != target_index and result.adjacency_matrix[source_index][target_index]:
                lines.append(f'  "{source}" -> "{target}";')

    for level in result.levels:
        same_rank = " ".join(f'"{label}"' for label in level)
        lines.append(f"  {{ rank=same; {same_rank}; }}")

    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def default_example() -> Tuple[List[str], Matrix]:
    labels = ["需求", "设计", "采购", "制造", "测试"]
    matrix = [
        [0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
    ]
    return labels, matrix


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="分析 DSM 矩阵并推导 ISM 层级结构。"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="CSV 输入文件。第一行和第一列应包含元素标签。",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("dsm_ism_report.txt"),
        help="文本报告输出路径。默认：dsm_ism_report.txt",
    )
    parser.add_argument(
        "--dot",
        type=Path,
        default=Path("ism_graph.dot"),
        help="Graphviz DOT 输出路径。使用 --dot '' 可跳过生成图文件。",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    if args.input:
        labels, matrix = read_csv_matrix(args.input)
    else:
        labels, matrix = default_example()

    result = analyze(labels, matrix)
    report = build_report(result)
    args.output.write_text(report, encoding="utf-8")

    if str(args.dot):
        write_dot(result, args.dot)

    print(report)
    print(f"报告已写入：{args.output}")
    if str(args.dot):
        print(f"Graphviz DOT 图文件已写入：{args.dot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
