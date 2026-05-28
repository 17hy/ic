# LDO 设计教程：从浅到深

## 1. LDO 是什么

LDO 是一种线性稳压器。它把较高且可能有纹波的输入电压 `VIN` 调成较稳定的输出电压 `VOUT`。典型结构包括：

- 基准源 `VREF`：提供稳定参考电压，例如 1.2 V。
- 误差放大器：比较 `VREF` 和反馈电压 `FB`。
- pass 管：通常是 PMOS 或 PNP，串在 `VIN` 和 `VOUT` 之间，调节输出电流。
- 反馈分压：把 `VOUT` 按比例送回误差放大器。
- 输出电容：改善瞬态响应和环路稳定性。
- 负载：由 `VOUT` 供电的后级电路。

最常见的反馈关系是：

```text
VOUT = VREF * (1 + RTOP / RBOT)
```

本目录的例子取 `VREF = 1.2 V`，`RTOP = 400 kOhm`，`RBOT = 600 kOhm`，因此目标输出约为：

```text
VOUT = 1.2 * (1 + 400k / 600k) = 2.0 V
```

## 2. 先理解 DC 工作点

运行：

```powershell
cd .\circuits
ngspice -b 01_operating_point.cir
```

重点看：

- `v(vout)` 是否接近 2.0 V。
- `v(fb)` 是否接近 1.2 V。
- `v(gate)` 是否低于 `VIN`。PMOS pass 管的源极接 `VIN`，栅极越低，导通越强。

如果负载电流变大，pass 管需要更强导通，PMOS 栅极会被拉得更低。

## 3. Dropout：为什么输入不能太低

LDO 不是开关电源，它靠 pass 管线性压降工作。当 `VIN` 太接近 `VOUT` 时，pass 管已经全开也无法继续维持输出，LDO 进入 dropout。

粗略理解：

```text
VIN(min) ~= VOUT + VDROP
VDROP ~= ILOAD * RDS(on)
```

对于 MOS pass 管：

- 加大 pass 管宽度可以降低 `RDS(on)`，减小 dropout。
- 但宽度越大，栅电容越大，误差放大器更难驱动，环路更容易变慢或不稳定。

运行：

```powershell
ngspice -b 02_line_regulation.cir
```

查看 `02_line_regulation.csv`。当 `VIN` 从低扫到高时，`VOUT` 会先跟着 `VIN` 上升，然后进入稳定的 2.0 V 区域。

## 4. Load regulation：负载变化时输出偏移

负载调整率描述负载电流变化导致的输出变化：

```text
Load regulation = Delta VOUT / Delta ILOAD
```

理想 LDO 在负载变化时输出不变；实际 LDO 由于有限环路增益、pass 管输出电阻、误差放大器能力有限，输出会有偏移。

运行：

```powershell
ngspice -b 03_load_regulation.cir
```

查看 `03_load_regulation.csv`。随着负载电流升高，输出会略有下降；如果 pass 管能力不够，下降会明显变大。

## 5. 负载阶跃瞬态

数字电路、SerDes、PLL 等负载经常快速改变电流。LDO 输出会出现：

- 下冲：负载突然变大，输出电容先供电，`VOUT` 瞬间下降。
- 恢复：误差放大器调节 pass 管，输出回到目标值。
- 过冲：负载突然变小，pass 管来不及关小，输出短暂升高。

运行：

```powershell
ngspice -b 04_load_step_transient.cir
```

可以尝试修改：

- `cout`：输出电容。更大通常下冲更小，但环路极点更低。
- `esr`：输出电容 ESR。适当 ESR 会引入零点，有时能改善稳定性。
- `fp_ea`：误差放大器主极点。越高环路越快，但相位裕度可能变差。
- `wpass`：pass 管宽度。越大 dropout 越小，但栅电容和寄生更大。

## 6. PSRR：输入纹波抑制

PSRR 描述输入电源纹波传到输出的程度。这里用 AC 仿真设置：

```text
VIN = 3.3 V DC + 1 V AC
```

因此 `vdb(vout)` 就是从输入纹波到输出纹波的传递增益，单位 dB。数值越低，输入纹波越不容易传到输出。常见写法也会把 PSRR 定义为：

```text
PSRR(dB) = -20 * log10(|VOUT_ripple / VIN_ripple|)
```

运行：

```powershell
ngspice -b 05_psrr_ac.cir
```

低频 PSRR 主要由环路增益决定；高频时环路跟不上，pass 管寄生和输出电容会主导。

## 7. 环路稳定性

LDO 是反馈系统。一个简化环路可以写成：

```text
T(s) = AEA(s) * GPASS(s) * ZOUT(s) * beta
```

其中：

- `AEA(s)`：误差放大器增益。
- `GPASS(s)`：pass 管小信号跨导。
- `ZOUT(s)`：输出节点阻抗，受负载、电容、ESR、pass 管输出电阻影响。
- `beta`：反馈系数，`beta = RBOT / (RTOP + RBOT)`。

关键极点和零点：

```text
pout ~= 1 / (2*pi*Rout*Cout)
zesr ~= 1 / (2*pi*ESR*Cout)
```

运行：

```powershell
ngspice -b 06_loop_gain_ac.cir
```

查看 `06_loop_gain_ac.csv`。找到环路增益穿越 0 dB 的频率，再看该频率附近的相位。教学上可以用下面的经验判断：

- 0 dB 穿越频率太低：瞬态慢。
- 0 dB 穿越频率太高：容易吃掉相位裕度。
- 相位裕度太小：负载阶跃后容易振铃甚至震荡。

## 8. 从宏模型走向真实设计

真实芯片设计时，还需要继续深入：

- 设计 bandgap 或使用外部参考源。
- 设计误差放大器：输入共模范围、输出摆幅、噪声、失调、静态电流。
- 设计 pass 管尺寸：dropout、电流能力、安全工作区、栅电容。
- 做稳定性补偿：输出电容范围、ESR 范围、负载范围、PVT corner。
- 做保护电路：限流、短路保护、热关断、软启动、欠压锁定。
- 做版图：大电流金属、电源地回流、基准噪声隔离、ESD 和 latch-up。

建议你在掌握这些宏模型后，再用具体 CMOS PDK 把误差放大器和 PMOS pass 管换成晶体管级电路。

