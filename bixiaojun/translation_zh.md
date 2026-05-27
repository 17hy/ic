# A 2 x 500Gb/s Monolithic Silicon-Photonic DWDM PAM-4 Transceiver in 45nm CMOS SOI - 中文翻译与技术整理

原文：Ziang Xu, Yalong Lin, Jinxuan Jin, Zhenkai Ye, Dacheng Xu, Aolin Xu, Chaodi Sheng, Binwen Hong, Xiaojun Bi，ISSCC 2026 Session 23.3。

说明：本文档为技术翻译与整理，不逐字复刻排版；参考文献仅保留与背景相关的信息，不逐条翻译。

## 标题

一款 45nm CMOS SOI 单片集成 2 x 500Gb/s 硅光 DWDM PAM-4 收发器

## 摘要

本文提出一款 45nm CMOS SOI 单片集成 2 x 5 波长 DWDM 微环收发器，实现 2 x 500Gb/s 总速率，即每通道 100Gb/s PAM-4。该收发器包含低噪声 TIA 与 Q-tamed CTLE、高速微环调制器（MRM）驱动器，以及基于 PWM、插入损耗（IL）可调的波长锁定电路。V-groove 耦合器和 PSR-to-CRR 接收前端实现低耦合损耗和紧密波长间隔。通过电光协同设计，端到端 loopback 中每通道 100Gb/s 时能效低于 2.5pJ/b。

## 背景与挑战

AI 和机器学习推动数据中心带宽需求快速增长，需要短距、高密度、低能耗光互连。硅光通过单片集成光子器件和电子电路，可以去除 pad 与 wire-bond 寄生，并支持光纤到芯片直接耦合。已有单片微环收发器证明了该路线的潜力，但单通道速率仍主要停留在 64Gb/s NRZ 或 40Gb/s PAM-4，难以满足 800G 与未来 1.6T 模块。

PAM-4 微环收发器能提升带宽密度与能效，但存在四个关键问题：

1. 微环调制器 MRM 在不同插入损耗点工作时，需要在带宽、线性度和光调制幅度 OMA 之间折中，以适应动态应用需求。
2. 更密集的 WDM 要求更窄波长间隔。尖锐的 MRR/CRR 滤波器能降低串扰，但会限制解复用后的带宽。
3. MRR 谐振会随温度漂移，需要主动稳定；多通道波长锁定中，监测光电二极管 MPD 电流也存在通道间失配。
4. 收发链路中的 CTLE 存在功耗、补偿能力和频率响应之间的基本折中。

## 系统架构

图 23.3.1 给出系统框图。本文实现 2 x 5 波长单片 DWDM 微环收发器，每个波长支持 100Gb/s PAM-4。TX 端使用半径 7.5um、预对准 0.054um 的微环，FSR 为 9.267nm，通道间隔 1.853nm，约 324GHz。RX 端使用 V-groove 耦合器、片上偏振分束旋转器 PSR、耦合环谐振器 CRR 滤波器和双探测器 PD，以增强串扰抑制并支持更紧密通道间隔。

每个通道都集成片上 WLL 电路，使 TX MRM 与 RX CRR 都能工作在目标波长点，而不需要额外片外控制逻辑。

## TIA 与 Q-tamed CTLE

图 23.3.2 给出 TIA 架构。TIA 用于 112Gb/s PAM-4 接收，采用低噪声、带宽增强结构。跨阻级 TIS 使用较大的反馈电阻获得高前端增益和低输入等效噪声，但这会加重后续均衡设计约束。

传统 CTLE 有两个问题：源退化 CTLE 通过牺牲增益换取峰化，超过 30GHz 后扩展性较差；电感峰化 CTLE 存在峰化幅度与响应形状之间的折中，高峰化会降低峰化频率并提高 Q 值，使时域眼图变差。

本文提出级联 Q-tamed CTLE。CTLE 采用两级 Gm-ZT 拓扑和串联电感峰化（CTLE1 + CTLE2），并在两级之间加入 Q-tamed path（QTP）塑形频率响应。QTP 由低 Q 被动电感和基于 Gm 的有源电感混合实现。它把原本同在 41GHz 的 CTLE1/CTLE2 谐振峰分裂开，增强 10-30GHz 中频增益，并降低整体 Q 值。

结果是 Q-tamed CTLE 获得 6.1dB 基线增益和 41GHz 处 12.4dB 峰化。在相同输出摆幅下，时域仿真眼高提升 60%，眼宽提升 30%。TIA 测得跨阻增益 62dBΩ、带宽 43.5GHz、输入等效噪声 3.14uArms，功耗 67mW。

## MRM PAM-4 驱动器

图 23.3.3 给出 MRM 驱动器架构。驱动器包含三级前置放大器、电平移位器和主驱动器。前置放大器把单端 MSB/LSB 输入转为差分信号，提供增益和均衡，并使用并联峰化与负电容技术，使带宽超过 30GHz。

电平移位器使用堆叠反相器，在 0-VDDL 与 VDDL-VDDH 两个电压域产生满摆幅输出，以支持高摆幅驱动。主驱动器把两个 NRZ 信号组合成 PAM-4。输出端用串联峰化电感与可调并联电阻形成 R+L CTLE，在把差分摆幅降到 2.5Vppd 的同时扩展输出带宽。片上 bias-T 提供直流偏置，使驱动器可直接连接到 MRM 的阳极与阴极。

## 波长锁定 WLL 电路

图 23.3.4 给出 WLL 电路概念。前端包含 MPD 电流 Iph 放大器，该放大器由 6bit 数字信号自动调节增益，以补偿 WDM 系统中不同通道的 MPD 电流失配，以及输入光功率和光路损耗变化。这样可以让 Iph 与后续电路动态输入范围最佳匹配。

A/D 转换采用 1bit bang-bang ADC，减少相对 SAR ADC 的硬件开销。

IL 可调锁定流程如下：

1. 系统进入 SWEEP & ADJUST 模式，先调节 Iph 放大器增益，使 Iph 峰值与 IL 参考 DAC 匹配，此时参考 DAC 初始化为 Vmax。
2. 之后通过片上 SPI 将 DAC 输入码改为 VIL。目标插入损耗由下式定义：

```text
Desired IL = 1 - VIL / Vmax
```

3. 控制环路调节微环热调谐，使 Iph 对应电压匹配 VIL，从而把谐振点锁定到指定 IL 工作点。

该方案同时适用于 TX MRM 和 RX CRR 的 WLL，能针对不同 IL 点处理 MRM 的带宽、线性度和 OMA 折中。热控制 DAC 通过 PWM 把有效位数扩展到 14bit，相比此前使用 delta-sigma 调制模块，面积和复杂度更低。输出驱动级可提供超过 15mA 热调谐电流。

## WLL 的两个创新点

1. IL 可调目标锁定，而不是只锁峰值或固定斜率点。电路先通过 sweep/gain adjust 自动匹配 MPD 峰值和 Vmax，再由 VIL 设置目标插入损耗，因此可以把 MRM 或 CRR 锁到 6dB、3dB、1.5dB 或接近峰值等不同工作点。这直接服务于 MRM 的带宽、线性度和 OMA 动态折中。

2. 低硬件开销的多通道片上锁定实现。它结合 6bit MPD 自动增益控制、1bit bang-bang ADC 和 14bit PWM 热 DAC，既能处理通道间 MPD 电流和光路损耗失配，又避免传统 SAR ADC 或 delta-sigma 热调谐 DAC 的面积/复杂度开销，并可同时用于 TX MRM 与 RX CRR。

## 测量结果

TX 在 50GBaud PAM-4 下实现 100Gb/s，工作于 -6.2dB IL 点时，消光比 4.82dB，RLM 为 0.99，并使用 MSB/LSB skew 优化。RX 在五个通道中实现 112Gb/s PAM-4，BER = 2.4e-4 限值下灵敏度为 -5.3dBm。端到端 TRX 能效低于 2.5pJ/b。

WLL 测试显示，复位后电路进入 SWEEP & ADJUST 模式，然后进入锁定与 bang-bang 热调谐。通过配置不同 IL 点，微环可锁定到 6dB、3dB、1.5dB 和接近谐振峰等位置。约 40C 环境热扰动下，热稳定功能得到验证。TX MRM 热调谐效率为 0.3nm/mW，CRR 为 0.42nm/mW；调谐范围分别为 5.5nm 和超过 7nm。整个 WLL 功耗为 26.7mW，其中控制部分仅 7.9mW。

相比已有 MRM TRX，本文在单片集成条件下实现 100Gb/s PAM-4 单通道速率和低于 2.5pJ/b 的端到端能效，同时在带宽密度和单根光纤总带宽方面表现领先。

芯片采用 45nm CMOS SOI 工艺，集成 10 通道驱动器、TIA、光子器件和 V-groove 耦合器。单个 TX 通道面积为 400um x 550um，单个 RX 通道面积为 400um x 535um。TX/RX 单个 WLL 面积分别为 0.063/0.15mm2。TX/RX 总体能效分别为 1.82pJ/b 和 0.6pJ/b。

## 关键图题翻译

图 23.3.1：2 x 5 通道单片微环 DWDM 收发器框图。

图 23.3.2：基于级联 Q-tamed CTLE 的 TIA 架构。

图 23.3.3：MRM 驱动器架构。

图 23.3.4：波长调谐电路原理图与概念。

图 23.3.5：测量结果。

图 23.3.6：性能总结和对比。

图 23.3.7：芯片显微照片与 TRX 功耗分解。
