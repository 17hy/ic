# Digital Integrated Circuits 2nd - Chapter 7

## 文件说明

- `text/chapter7_raw.txt`：由 `4.pdf` 提取的第7章原始文字。
- `pages_png/`：由 `4.pdf` 渲染的第7章书页图像，共 44 页。
- `ngspice_reproduction/`：基于 ngspice 的第7章代表性时序电路复现实验。

## 第7章结构（Designing Sequential Logic Circuits）

1. `7.1 Introduction`
- 组合逻辑只依赖当前输入，时序逻辑还依赖历史状态。
- 同步时序系统由组合逻辑和寄存器构成。
- 关键时序指标：`tc-q`、`tsetup`、`thold`、逻辑最大延时、污染延时、最小时钟周期。

2. `7.2 Static Latches and Registers`
- `7.2.1 The Bistability Principle`：交叉耦合反相器通过正反馈形成两个稳定状态和一个亚稳态。
- `7.2.2 SR Flip-Flops`：通过 set/reset 控制双稳态单元。
- `7.2.3 Multiplexer-Based Latches`：用传输门或多路选择器构造电平敏感锁存器。
- `7.2.4 Master-Slave Edge-Triggered Register`：两个互补相位锁存器级联形成边沿触发寄存器。
- `7.2.5 Low-Voltage Static Latches`：低电压下传输门、反馈保持与噪声裕量更难设计。

3. `7.3 Dynamic Latches and Registers`
- 动态寄存器依赖电容暂存电荷，面积和速度较好，但需要周期性刷新。
- 重点结构：动态传输门寄存器、`C2MOS`、`TSPCR`。
- 主要风险：时钟重叠、泄漏、电荷共享、输入/时钟斜率过慢。

4. `7.4 Alternative Register Styles`
- 脉冲寄存器用短脉冲打开锁存窗口，能降低寄存器开销。
- Sense-amplifier register 用再生放大器提升小信号采样速度，常用于高速路径。

5. `7.5 Pipelining`
- 插入寄存器或锁存器缩短组合逻辑路径，提高吞吐率。
- 锁存器流水线支持 time borrowing，但需要严格处理 race 和时钟相位。
- `NORA-CMOS` 将动态逻辑和 `C2MOS` 锁存器组合，用规则避免竞争。

6. `7.6 Non-Bistable Sequential Circuits`
- Schmitt trigger：有滞回阈值，适合清理慢输入或带噪输入。
- Monostable：一个稳定态，用作 pulse generator。
- Astable：无稳定态，典型例子是 ring oscillator。

7. `7.7` - `7.9`
- 选择时钟策略时要综合速度、功耗、鲁棒性、时钟复杂度和设计验证难度。

## 核心知识要点

- 时序电路正确性的核心不是只看逻辑功能，而是满足 setup/hold 和 clock-to-Q 约束。
- 正反馈带来状态保持，也带来亚稳态；寄存器输入靠近采样边沿时会出现解析时间不确定。
- 静态锁存器可靠，动态锁存器速度/面积更优但依赖时钟和电荷保持。
- 主从寄存器把电平敏感锁存器变成边沿触发行为，代价是时钟负载和传播延时增加。
- Schmitt trigger 的两个切换阈值构成 hysteresis，可以抑制输入噪声导致的多次翻转。
- Ring oscillator 的频率主要由级数和单级传播延时决定：级数越多或负载越大，频率越低。

## 仿真图表

在 `ngspice_reproduction/plots` 生成：

- `fig7_bistable_regeneration.png`：交叉耦合反相器从亚稳附近再生到稳定状态。
- `fig7_tg_latch_waveforms.png`：传输门锁存器的透明/保持行为。
- `fig7_schmitt_hysteresis.png`：Schmitt trigger 的滞回传输曲线和慢输入整形。
- `fig7_ring_oscillator.png`：五级 CMOS 环形振荡器波形和频率估计。

运行方法见 [ngspice_reproduction/README.md](C:/Users/Guohu/Desktop/ngspice/digital/Digital_Integrated_Circuits_2nd_Chapter7/ngspice_reproduction/README.md)。
