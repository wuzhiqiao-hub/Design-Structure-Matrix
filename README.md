# DSM/ISM 分析程序

这个程序用于分析系统元素之间的影响关系。它读取 DSM 关系矩阵，计算 ISM 可达矩阵和层级结构，并输出文字报告与 Graphviz 图文件。

## 功能

- 支持从 CSV 文件读取关系矩阵
- 支持 `0/1` 二值矩阵，也支持 `0` 到 `1` 之间的连续关系强度
- 自动校验矩阵是否为空、是否为方阵、数值是否位于 `[0, 1]`
- 自动计算可达矩阵；连续矩阵使用 max-min 可达闭包
- 按阈值自动划分 ISM 层级
- 输出每个元素的驱动力和依赖力
- 生成文本报告
- 生成 Graphviz `.dot` 关系图文件

## 运行

打开交互界面：

```bash
open index.html
```

交互界面支持设置任务数量、编辑每个任务名称、填写 `0` 到 `1` 的关系强度、查看层级图、可达矩阵、完整过程矩阵、CSV 和报告。

打开独立应用：

```bash
open dist/DSM-ISM.app
```

Windows 便携版位于：

```text
dist/windows/DSM-ISM-Windows.zip
```

在 Windows 中解压后，双击 `DSM-ISM.vbs` 或 `DSM-ISM.cmd` 即可运行。

重新生成 macOS 应用包：

```bash
python3 scripts/build_macos_app.py
```

重新生成 Windows 便携版：

```bash
python3 scripts/build_windows_portable.py
```

使用示例数据：

```bash
python3 DSMzuoye.py
```

使用 CSV 输入：

```bash
python3 DSMzuoye.py -i example_matrix.csv -o report.txt --dot ism_graph.dot
```

使用连续关系强度，并指定层级阈值：

```bash
python3 DSMzuoye.py -i example_matrix.csv -t 0.6
```

## CSV 格式

第一行是列标签，第一列是行标签，行标签必须和列标签顺序一致。

```csv
,任务1,任务2,任务3,任务4,任务5
任务1,0,0.8,0,0,0
任务2,0,0,0.7,0.9,0
任务3,0,0,0,0.6,0
任务4,0,0,0,0,0.8
任务5,0,0,0,0,0
```

矩阵含义：第 `i` 行第 `j` 列表示元素 `i` 对元素 `j` 的影响强度。`0` 表示没有影响，`1` 表示最强影响，中间小数表示连续强度。二值 `0/1` 输入仍然可用。

## 连续矩阵说明

连续矩阵的可达关系使用 max-min 规则：

- 一条路径的强度取路径上最弱关系的值
- 多条路径连接同一对元素时，取最强路径的值
- 层级划分和 DOT 图默认只使用强度大于等于 `0.5` 的关系
- 可以通过 `-t` 或 `--threshold` 调整阈值，例如 `-t 0.7`

## 输出说明

- `dsm_ism_report.txt`：分析报告
- `ism_graph.dot`：Graphviz 图文件

如果本机安装了 Graphviz，可以把 `.dot` 文件转成 PNG：

```bash
dot -Tpng ism_graph.dot -o ism_graph.png
```

## 结果理解

- 顶层因素：更像结果或表层因素，受其他因素影响较多
- 底层因素：更像驱动因素，对系统影响更深
- 驱动力越高，说明该因素能到达或影响的因素越多
- 依赖力越高，说明该因素被其他因素到达或影响得越多
- 连续矩阵中，驱动力和依赖力是可达强度的加总，不再只是数量计数
