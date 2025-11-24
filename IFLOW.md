# IFLOW.md - Network Optimization Python Code (netoptim)

## 项目概述

`netoptim` 是一个用于网络优化的 Python 代码库，基于 PyScaffold 4.5 创建。该项目主要解决参数化网络问题，包括网络流优化和最优矩阵缩放等。项目依赖于一些专门的库，如 `ellalgo`（椭球算法优化库）、`digraphx`（有向图处理）和 `mywheel`（工具库）。

核心功能包括：
- `NetworkOracle`：用于解决参数化网络问题的 oracle 类，通过寻找负圈来评估约束满足性
- `OptScalingOracle`：用于最优矩阵缩放问题的 oracle 类，实现 Orlin 和 Rothblum (1985) 提出的算法

## 项目结构

```
netoptim/
├── src/netoptim/           # 源代码目录
│   ├── __init__.py
│   ├── network_oracle.py   # 网络 oracle 实现
│   ├── optscaling_oracle.py # 最优缩放 oracle 实现
│   └── py.typed
├── tests/                  # 测试文件目录
├── requirements/           # 依赖文件目录
│   ├── default.txt
│   ├── test.txt
│   └── doc.txt
├── pyproject.toml          # 项目构建配置
├── setup.cfg               # 项目配置
├── README.md               # 项目说明
└── ...
```

## 依赖

- `luk036/ellalgo` - 椭球优化算法库
- `luk036/mywheel` - 工具库
- `luk036/digraphx` - 有向图处理库
- `networkx` - 网络分析库
- `numpy` - 数值计算库
- `icecream` - 调试输出库

## 构建和运行

### 安装依赖

```bash
pip install -r requirements/default.txt
pip install -r requirements/test.txt  # 测试依赖
```

### 运行测试

```bash
pytest                    # 运行所有测试
pytest tests/ -v          # 运行测试并显示详细信息
pytest --cov=netoptim     # 运行测试并生成覆盖率报告
```

### 使用示例

```python
from netoptim.network_oracle import NetworkOracle
from unittest.mock import Mock

# 创建图结构
gra = {
    "v1": {"v2": {"w": 3}, "v3": {"w": 4}},
    "v2": {"v1": {"w": -2}, "v3": {"w": 1}},
    "v3": {"v1": {"w": -3}, "v2": {"w": -2}},
}

u = {"v1": 0, "v2": 0, "v3": 0}
oracle = Mock()
oracle.eval.side_effect = lambda e, x: e["w"] - x
oracle.grad.side_effect = lambda e, x: -1

network = NetworkOracle(gra, u, oracle)
result = network.assess_feas(1)
```

## 开发约定

- 代码遵循 PEP 8 编码风格
- 使用 pytest 进行单元测试
- 项目使用语义化版本控制
- 通过 `setup.cfg` 配置项目选项和测试参数
- 使用 `flake8` 进行代码风格检查