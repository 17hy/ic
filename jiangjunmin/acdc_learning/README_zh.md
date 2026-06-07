# AC-DC 拓扑学习与 ngspice 仿真教程

本文档配合论文：

`jiangjunmin/19.9_A_2.15W_120V_230Vac_to_5-to-12Vdc_Offline_Power_Converter_with_Full-Duty-Cycle_Input-Series_Dual-Branch_Converter_Achieving_1088mW_textcm3_and_87.2_Peak_Efficiency.pdf`

目标不是复现芯片级电路，而是把论文里提到的几类典型 AC-DC 实现方式拆成能跑的 ngspice 拓扑级模型。真实产品还需要安规、EMI、浪涌、隔离、器件 SOA、热设计、控制环路、驱动和版图寄生；这里先只看功率路径和关键约束。

## 运行方法

在当前目录运行：

```powershell
cd C:\Users\Guohu\Desktop\ngspice\jiangjunmin\acdc_learning
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_all.ps1
```

也可以单独运行某个 deck：

```powershell
ngspice -b -o 03_cap_drop_rectifier.log 03_cap_drop_rectifier.cir
python .\plot_results.py
```

每个 `.cir` 会生成同名 `.log` 和 `.csv`；`plot_results.py` 会生成同名 `.png` 波形图。

## 论文里的几类典型方案

论文背景部分把离线 AC-DC 大致分成以下几类：

1. 传统隔离 flyback/forward：市电整流成高压 DC，再通过变压器隔离降压。优点是安全隔离和成熟，缺点是磁件体积大，功率密度受限。
2. Direct AC-DC：把整流后的 325 V 级高压直接用 HV LDO 或 HV DC-DC 降到 3.3-12 V。优点是结构直接，缺点是电压转换比极端，效率和器件压力差。
3. Capacitor-drop AC-DC：用串联 X 电容承受大部分市电电压，整流后得到几十伏级 `VREC`。优点是非隔离、小体积，缺点是输出功率有限、轻载效率和储能电容体积受限。
4. Capacitor-drop + 固定比 SC：前级产生 `VREC`，后级用 1/N 开关电容降压。缺点是 `VOUT` 强依赖 `VREC/N`，所以为了压住 `VREC` 纹波，需要很大的 `CREC`。
5. 论文提出的 Capacitor-drop + ISDB：仍用电容降压前端，但后级改成输入串联、输出并联的双分支 buck 类结构。`CH/CL` 把 `VREC` 拆成 `+VREC/2` 和 `-VREC/2`，每个分支器件只承受半压，转换关系约为 `VOUT = D * VREC / 2`。

## 文件与结果

| 文件 | 学习重点 | 关键仿真结果 |
|---|---|---|
| `01_isolated_flyback_acdc.cir` | 传统隔离反激平均模型 | `325 V` 母线到 `11.94 V` 输出；估算开关应力约 `451 V` |
| `02_direct_rectifier_hv_buck.cir` | 直接高压 buck | `325 V` 到 `12.20 V`；输出纹波约 `43.9 mVpp`；开关承压约 `326 V` |
| `03_cap_drop_rectifier.cir` | X 电容降压整流前端 | `VREC` 平均 `60.57 V`，范围 `53.23-65.86 V`；X 电容 RMS 电压约 `202 V` |
| `04_cap_drop_fixed_ratio_sc_macro.cir` | 固定比 SC 需要大 `CREC` | `4.7 uF CREC` 时 `VOUT` 纹波 `2.27 Vpp`；`47 uF CREC` 时降到 `0.259 Vpp` |
| `05_isdb_dual_branch_converter.cir` | 本文 ISDB 后级 | `60 V -> 5 V` 得到 `4.990 V`；`30 V -> 12 V` 得到 `12.002 V`，且 D > 0.5 可重叠工作 |
| `06_isdb_balance_loop_macro.cir` | `VCH/VCL` 平衡思想 | 初始失配约 `11.90 V`，40 ms 后降到约 `0.40 V` |

## 1. 传统隔离 flyback/forward

实际搭建方式通常是：

```text
230 Vac -> EMI/保护 -> 桥式整流 -> 高压 bulk 电容 -> flyback/forward 变压器 -> 次级整流滤波 -> 低压输出
```

`01_isolated_flyback_acdc.cir` 用 325 V DC 源代表整流后的 bulk bus，用平均反激关系表示变压器降压：

```text
VOUT ~= D / (1 - D) * (NS / NP) * VBUS
```

deck 中 `nps=10` 表示 `NP:NS = 10:1`，`duty=0.27`，所以输出约为 12 V。`BDRAIN` 用

```text
VDS ~= VBUS + (NP / NS) * VOUT
```

估算关断时的 MOSFET 电压应力。这个模型不设计磁芯、漏感、RCD/active clamp，只用于理解传统隔离方案为什么需要高压开关和变压器。

## 2. Direct AC-DC 高压 buck

搭建方式：

```text
230 Vac -> 桥式整流/bulk -> 高压开关 S -> 电感 L -> 输出电容 COUT -> 负载
                         -> 续流二极管/同步管
```

`02_direct_rectifier_hv_buck.cir` 直接从 325 V bus 降到 12 V。理想 buck 近似为：

```text
D ~= VOUT / VBUS
```

也就是 `12/325 ~= 3.7%`。这么小的占空比会带来很短的导通时间；开关、驱动、电感电流检测和最小 on-time 都会变难。仿真中为了补偿二极管和开关宏模型，固定 duty 调到了 `0.0295`，输出约 `12.20 V`。关键结论不是这个 duty 的精确值，而是 325 V 到 12 V 的转换比过大，器件承压仍是 325 V 级。

## 3. Capacitor-drop AC-DC 前端

搭建方式：

```text
230 Vac -> 串联 X 电容 CX -> 桥式整流 -> CREC -> 后级 DC-DC/负载
```

X 电容不是普通输出滤波电容，它串在交流输入中，利用容抗限制电流并承担大部分市电电压。论文给出的理想输出功率近似为：

```text
PREC = 4 * fLINE * VREC * CX * (sqrt(2) * VLINE - VREC)
```

在 `03_cap_drop_rectifier.cir` 中：

```text
VLINE = 230 Vrms
fLINE = 50 Hz
CX = 0.68 uF
RLOAD = 1.7 kOhm
CREC = 10 uF
```

仿真得到 `VREC ~= 60.57 V`，纹波约 `12.63 Vpp`。这个前端的直观理解是：想提高功率，要么增大 `CX`，要么提高 `VREC`；但增大 `CX` 会提高空载/轻载损耗，提高 `VREC` 又会增加后级降压压力。

## 4. Capacitor-drop + 固定比 SC

搭建方式：

```text
cap-drop rectifier -> CREC -> 1/N switched-capacitor converter -> COUT -> load
```

`04_cap_drop_fixed_ratio_sc_macro.cir` 把 SC 简化成：

```text
VOUT ~= VREC / N - IOUT * ROUT
```

这里 `N=10`。为了让前级看到合理负载，deck 中还放了一个等效输入电阻：

```text
RIN ~= N^2 * RLOAD
```

仿真同时比较 `CREC=4.7 uF` 和 `CREC=47 uF`：

```text
4.7 uF:  VREC ripple = 24.31 Vpp, VOUT ripple = 2.27 Vpp
47 uF:   VREC ripple = 2.77 Vpp,  VOUT ripple = 0.259 Vpp
```

这就是论文批评固定比 SC 的核心：如果后级只能按固定比例跟随 `VREC`，那前级 `VREC` 不能大幅波动，只能靠更大的 `CREC` 压纹波，体积就会上去。

## 5. 论文提出的 ISDB 后级

搭建方式可以按两个 buck 分支理解：

```text
          VREC_P
            |
           CH
            |
DC-DC GND --+---- Branch P: buck, switch node VSW1 = 0 or +VREC/2
            |
           CL
            |
          VREC_N

Branch P output inductor L1 -> VOUT
Branch N output inductor L2 -> VOUT
```

`CH` 和 `CL` 串联在 `VREC` 两端，中点作为 DC-DC 的地。这样：

```text
VCH ~= VREC/2
VCL ~= VREC/2
VOUT ~= D * VREC / 2
```

相比普通 buck 从 `VREC` 降压，ISDB 每个开关节点只在 `0` 和 `VREC/2` 之间切换，器件耐压减半。相比固定比 SC，`D` 可以调节，所以 `VREC` 可以有更大纹波，不必强行用很大的 `CREC` 压平。

`05_isdb_dual_branch_converter.cir` 做了两个工况：

```text
Case A: VREC = 60 V, VOUT = 5 V, IOUT = 0.4 A
  D ~= 5 / 30 = 0.167
  仿真 VOUT = 4.990 V
  IL1 ~= 0.1996 A, IL2 ~= 0.1996 A

Case B: VREC = 30 V, VOUT = 12 V, IOUT = 0.18 A
  D ~= 12 / 15 = 0.8
  仿真 VOUT = 12.002 V
  这个 D > 0.5，对应论文图里的相位重叠/full-duty-cycle 能力
```

这说明 ISDB 的优势不是单纯“多一个电感”，而是同时满足：

```text
器件耐压: 约 VREC/2
转换比:   D/2
占空比:   可接近 1
输出电流: 两个分支并联分担
```

## 6. VCH/VCL 平衡环路

ISDB 的风险是 `CH` 和 `CL` 可能不均压。如果 `VCH > VCL`，论文的平衡环路会让 Branch P 多送一点功率，使 `CH` 放电更多，同时让 `CL` 恢复，直到两者接近相等。

`06_isdb_balance_loop_macro.cir` 没有复现论文里的误差放大器和 PWM ramp，只用一个行为电流表示这个趋势：

```text
mismatch = VCH - VCL
positive mismatch -> discharge CH, charge CL
```

仿真从：

```text
VCH = 36 V
VCL = 24 V
```

收敛到：

```text
VCH ~= 30.20 V
VCL ~= 29.80 V
```

这对应论文里的直观说法：平衡 `VCH/VCL` 的同时，也会帮助两个分支电感电流趋于均衡。

## 建议学习顺序

1. 先跑 `03_cap_drop_rectifier.cir`，看 X 电容如何把 230 Vac 变成几十伏 `VREC`。
2. 跑 `04_cap_drop_fixed_ratio_sc_macro.cir`，观察小 `CREC` 时 `VOUT` 为什么跟着 `VREC` 大幅波动。
3. 跑 `05_isdb_dual_branch_converter.cir`，看 `VREC/2`、`D/2` 和两个电感分流。
4. 跑 `06_isdb_balance_loop_macro.cir`，理解为什么 ISDB 必须有均压控制。
5. 最后对比 `01` 和 `02`，理解传统隔离方案和 direct HV buck 为什么在体积、耐压或占空比上吃亏。

## 可以自己改的参数

电容降压前端：

```spice
.param cx=0.68u
.param rload=1.7k
.param crec=10u
```

固定比 SC：

```spice
.param nratio=10
.param rload=13.3
.param rout=0.8
```

ISDB：

```spice
.param vrec_a=60
.param vtarget_a=5
.param iout_a=0.4
.param duty_a={(vtarget_a-iout_a/2*rdcr)/vinhalf_a}
```

修改后重新运行 `run_all.ps1` 即可。若只改某一个 deck，建议先单独跑对应 `.cir`，确认 `.log` 里没有 `Error` 或 `Timestep too small`。

## 安全提醒

这些电路都是离线高压或非隔离思路。仿真中的 `230 Vac`、`325 Vdc`、X 电容降压、direct AC-DC 都不能直接按 netlist 搭实物。实物必须考虑安规电容、保险、浪涌、爬电距离、放电电阻、接地、隔离等级、EMI 和触电风险。
