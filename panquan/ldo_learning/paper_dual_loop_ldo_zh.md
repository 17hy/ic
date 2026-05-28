# 论文 B 节 LDO 复现笔记

对应论文：

`A 4 x 224 Gb/s Single-Ended PAM-4 Transceiver Front-End With Noise Suppression Technique and Cascaded Equalizers in 130-nm SiGe BiCMOS`

本笔记针对论文第 II-B 节 `Proposed LDOs for S2D Converter and D2S Driver`，把其中的 LDO 思路整理成可仿真的 ngspice 教学模型。这里不是晶体管级复刻，因为论文没有给出完整器件尺寸、偏置电流、SiGe/CMOS 模型卡和版图寄生；本目录复现的是该节的系统级行为。

## 1. 论文这一节的 LDO 目标

论文里的 S2D converter 和 D2S driver 是单端/伪差分高速接口，电源噪声会直接污染信号。评估板上的 dc-dc 转换器在最差条件下会产生约 `25 mVpp`、`1 MHz` 的锯齿纹波，因此片上 LDO 需要提供高 PSR。

论文给出的关键目标和结果包括：

- LDO 给 S2D converter 和 D2S driver 供电。
- LDO 采用双环结构：XCEA 慢环 + SSF 快环。
- 输出端有 `200 pF` 电容，主极点位于输出端。
- pass 管栅极是非主极点位置，SSF 通过降低该节点阻抗，避免栅极极点靠近输出主极点。
- 1 MHz PSR 在最差角仍优于 `-40 dB`。
- 典型 Monte Carlo 中 1 MHz PSR 均值约 `-43.9 dB`，标准差约 `0.72 dB`。
- 面对 `25 mVpp`、`1 MHz` 供电锯齿噪声，TX/RX 前端输出噪声约为 `0.2 mVpp` 和 `0.02 mVpp`。
- 在 RX 前端 `300 mVpp` 输入激励下，双环 LDO 将 supply power bounce 从约 `88 mVpp` 降到约 `5 mVpp`。
- LDO 隔离共享电源网络后，可显著降低片上通道间串扰；论文图中给出 56 GHz 处约 `51 dB` 改善。

## 2. 双环 LDO 的直觉

普通 LDO 主要依赖误差放大器慢环：

```text
VOUT -> feedback -> error amplifier -> pass gate -> VOUT
```

慢环适合保证 DC 输出电压和低频 PSR，但高速电路的负载电流变化很快，pass 管栅极电容又大。如果只有慢环，栅极节点可能成为麻烦的非主极点，输出阻抗也会在高速下升高。

论文加入 SSF 快环后，可以把直觉理解成：

```text
slow loop: 用高增益 XCEA 确保低频精度和低频 PSR
fast loop: 用 SSF 快速感知/驱动 pass 管栅极，降低栅极阻抗和输出动态阻抗
```

这个做法的重点不是把 LDO 带宽无限做高，而是在输出主极点和 pass 栅极极点之间保持清楚的极点分离，同时让高速负载扰动有一条快速电流跟踪路径。

## 3. 本目录中的复现文件

新增文件：

- `circuits/paper_dual_loop_ldo.inc`：论文启发的双环 LDO 小信号宏模型。
- `circuits/07_paper_dual_loop_psr.cir`：复现 Fig. 4(b) 风格的 PSR 曲线，比较普通慢环和双环 worst/typ/best。
- `circuits/08_paper_sawtooth_noise.cir`：复现 `25 mVpp`、`1 MHz` 锯齿供电纹波被 LDO 抑制后的输出噪声。
- `circuits/09_paper_power_bounce.cir`：复现 Fig. 6(a) 风格的 power-bounce 抑制，比较慢环和双环。

运行：

```powershell
cd C:\Users\Guohu\Desktop\ngspice\panquan\ldo_learning
.\run_all.ps1
```

## 4. 宏模型说明

`paper_dual_loop_ldo.inc` 使用小信号等效电路：

```text
VIN ripple -> feedthrough gm -> VOUT ripple node
VOUT ripple -> slow low-pass loop -> correction current
VOUT ripple -> fast SSF-like loop -> correction current
VOUT ripple node -> RLOAD || (ESR + COUT)
```

主要参数：

- `cout=200p`：对应论文的输出电容。
- `gfeed`：输入电源纹波直接耦合到输出的等效强度。
- `gm_slow`、`fp_slow`：XCEA 慢环等效跨导和带宽。
- `gm_fast`、`fp_fast`：SSF 快环等效跨导和带宽。
- `rload`：被供电高速前端的等效负载。

普通慢环 LDO 令 `gm_fast=0`。论文启发的双环 LDO 给出有限的 `gm_fast` 和较高 `fp_fast`，用来模拟 SSF 快速驱动 pass 管栅极、降低动态输出阻抗的效果。

## 5. 可以做的学习实验

当前参数下，`run_all.ps1` 的新增仿真结果大致为：

- `07_paper_dual_loop_psr.cir`：1 MHz PSR 为 conventional `-37.1 dB`、worst `-40.3 dB`、typical `-43.9 dB`、best `-48.7 dB`。
- `08_paper_sawtooth_noise.cir`：`25 mVpp` 输入锯齿噪声下，TX/RX 输出噪声代理约为 `0.20 mVpp` 和 `0.02 mVpp`。
- `09_paper_power_bounce.cir`：普通慢环约 `92 mVpp`，双环约 `5.4 mVpp`，用于复现论文 Fig. 6(a) 的量级。

1. 在 `07_paper_dual_loop_psr.cir` 中把 `gm_fast` 改成 0，看 1 MHz 到高频段的 PSR 如何变差。
2. 把 `cout=200p` 改成 `100p` 或 `500p`，观察 PSR 高频拐点和 power-bounce 波形。
3. 把 `fp_slow` 调低，观察普通慢环对 1 MHz sawtooth 的抑制能力下降。
4. 把 `fp_fast` 调低，观察 power-bounce 抑制不再明显。
5. 把 `rload` 从 `31` 改为 `15`，模拟更重负载，观察输出阻抗需求变得更严格。

## 6. 和真实芯片设计的差距

本复现模型适合学习论文方法，但不能用于版图或流片判断。真实设计还必须包含：

- XCEA 的晶体管级开环增益、输入共模范围、输出摆幅和噪声。
- SSF 的偏置、线性范围、栅极驱动能力和稳定性。
- PMOS pass 管尺寸、寄生电容、dropout、电迁移和热限制。
- 200 pF 片上电容的版图寄生和 ESR/ESL。
- PVT、Monte Carlo、封装、电源网格和高速前端负载的真实寄生。
