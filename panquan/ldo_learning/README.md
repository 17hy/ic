# LDO 设计学习目录

这个目录用于从浅到深学习 LDO（Low Dropout Regulator，低压差线性稳压器）的设计和仿真。这里的电路是教学级 ngspice 宏模型，不依赖具体 PDK，重点是理解架构、指标、瞬态和稳定性。

## 目录结构

- `tutorial_zh.md`：LDO 设计教程，按学习顺序展开。
- `circuits/ldo_macromodel.inc`：教学用 PMOS LDO 子电路。
- `circuits/01_operating_point.cir`：基本工作点。
- `circuits/02_line_regulation.cir`：输入电压扫描和 dropout 观察。
- `circuits/03_load_regulation.cir`：负载电流扫描。
- `circuits/04_load_step_transient.cir`：负载阶跃瞬态响应。
- `circuits/05_psrr_ac.cir`：电源纹波到输出的 AC 传递。
- `circuits/06_loop_gain_ac.cir`：线性化环路增益近似模型。
- `run_all.ps1`：在 Windows PowerShell 中一键运行所有 `.cir` 文件。

## 快速运行

在本目录执行：

```powershell
.\run_all.ps1
```

或者单独运行某个例子：

```powershell
cd .\circuits
ngspice -b 01_operating_point.cir
```

每个例子会在 `circuits/` 下生成对应的 `.csv` 数据文件。可以用 Excel、Python、Matlab 或 ngspice 的 plot 命令查看。

## 建议学习顺序

1. 先读 `tutorial_zh.md` 的第 1 到 3 节，理解 LDO 方框图、反馈分压和 dropout。
2. 运行 `01_operating_point.cir`，看 `VOUT`、`FB`、`GATE` 的直流关系。
3. 运行 `02_line_regulation.cir` 和 `03_load_regulation.cir`，观察输入电压、负载电流变化时输出何时失稳或进入 dropout。
4. 运行 `04_load_step_transient.cir`，看负载阶跃造成的下冲、恢复时间和输出电容影响。
5. 运行 `05_psrr_ac.cir`，理解输入纹波如何耦合到输出。
6. 运行 `06_loop_gain_ac.cir`，把误差放大器、pass 管、输出电容、反馈系数串起来看环路增益。

