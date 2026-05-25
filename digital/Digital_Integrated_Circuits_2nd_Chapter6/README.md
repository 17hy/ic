# Digital Integrated Circuits 2nd - Chapter 6

## 文件说明

- `text/chapter6_raw.txt`：由 `3.pdf` 提取的原始文字。
- `ngspice_reproduction/`：第6章代表性电路的 ngspice 复现工程（网表自动生成、批跑、数据与图表）。

## 第6章结构（Designing Combinational Logic Gates in CMOS）

1. `6.1 Introduction`
- 组合逻辑与时序逻辑区别。
- 门级实现的核心指标：面积、速度、能耗、鲁棒性。

2. `6.2 Static CMOS Design`
- `6.2.1 Complementary CMOS`：PUN/PDN 对偶构造法，NAND/NOR 实现规则。
- `6.2.2 Ratioed Logic`：Pseudo-NMOS、DCVSL 等，器件数减少但有静态功耗与逻辑电平折衷。
- `6.2.3 Pass-Transistor Logic`：强0/强1问题、阈值损失、传输门修复思路。

3. `6.3 Dynamic CMOS Design`
- `6.3.1` 动态逻辑基本原理（预充/评估两相）。
- `6.3.2` 速度与功耗对比静态 CMOS 的优势与代价。
- `6.3.3` 失效机理：泄漏、电荷共享、噪声敏感、时钟耦合。
- `6.3.4` 级联方法：Domino 等约束与设计规则。

4. `6.4 Perspectives`
- 逻辑风格选型：按性能、面积、功耗和鲁棒性折中。
- 低电压设计下的风格变化与可靠性挑战。

5. `6.5 Summary` / `6.6 To Probe Further`
- 总结静态、比率、动态三大路线的适用边界与参考文献。

## 知识要点

- 互补 CMOS 的本质是 PDN/PUN 对偶网络，稳态无直流短路路径。
- 复杂门延时与噪声裕量受输入模式影响，不能只看“所有输入短接”场景。
- 比率逻辑减少晶体管数，但引入静态电流与逻辑电平退化风险。
- 动态逻辑速度高、面积小，但对时钟、泄漏、噪声、级联约束更敏感。
- 逻辑风格没有绝对最优，必须结合目标（频率、能效、面积、PVT 鲁棒）选型。

## 仿真图表（对应本章主题）

在 `ngspice_reproduction/plots` 生成：

- `fig6_static_cmos_nand_vtc.png`：静态 CMOS NAND 在不同输入模式下的 VTC。
- `fig6_static_cmos_nand_delay.png`：静态 CMOS NAND 瞬态响应与传播延时。
- `fig6_ratioed_pseudo_nmos.png`：Pseudo-NMOS 的传输特性与静态电流。
- `fig6_dynamic_nand_waveforms.png`：动态 NAND 的预充/评估时序波形。

运行方法见 [ngspice_reproduction/README.md](C:/Users/Guohu/Desktop/ngspice/digital/Digital_Integrated_Circuits_2nd_Chapter6/ngspice_reproduction/README.md)。
