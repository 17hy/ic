# 前五章 ngspice 教程

## 使用方式

每个 `.cir` 文件都可以单独运行。例如：

```powershell
cd C:\Users\Guohu\Desktop\ngspice\razavi_ngspice_tutorial\circuits\ch03
..\..\..\Spice64\bin\ngspice_con.exe -b -o ..\..\logs\ch03_01_cs_resistor_load.log ch03_01_cs_resistor_load.cir
```

更推荐使用根目录下的批量脚本：

```powershell
.\tools\run_all.ps1
```

## 第 2 章：MOS 器件物理基础

这一章对应 MOS 开关、I-V 曲线、跨导、沟道长度调制、体效应和器件电容。仿真重点是先把单个 MOS 管看成一个可测器件：

- `ch02_01_mos_switch_transfer.cir`：把 NMOS 当作开关，观察输入电压从低到高时输出如何从高电平拉低。
- `ch02_02_nmos_iv_family.cir`：扫描 `VDS` 和 `VGS`，得到线性区、饱和区和沟道长度调制趋势。
- `ch02_03_gm_ro_bias.cir`：从工作点提取 `gm` 和 `gds`，理解小信号模型。
- `ch02_04_body_effect.cir`：固定 `VGS/VDS`，扫 `VSB`，观察体效应造成的漏电流下降。
- `ch02_05_mos_gate_capacitance.cir`：用 AC 门电流估算等效输入电容。

## 第 3 章：单级放大器

本章的主线是负载和输入/输出端口位置如何改变增益、输出摆幅与输入/输出电阻。

- 共源级：从电阻负载开始，再换成二极管连接负载、理想电流源负载、PMOS 有源负载和线性区 MOS 负载。
- 源极负反馈：用源极电阻降低等效跨导，提高线性度。
- 源跟随器：观察接近 1 的电压增益和有限输出摆幅。
- 共栅级：从源端输入，得到较低输入电阻和非反相电压增益。
- 共源共栅与折叠共源共栅：提高输出电阻，牺牲电压余量。

## 第 4 章：差动放大器

差动对的网表都用受控源生成 `VCM +/- VDM/2`，因此可以直接扫差模输入或做 AC 差模/共模测试。

- `ch04_01_basic_diff_pair_dc.cir`：扫差模输入，观察电流在两支路之间转移。
- `ch04_02_diff_pair_ac_gain.cir`：差模小信号增益。
- `ch04_03_diff_pair_common_mode.cir`：共模输入到输出的转换，体现尾电流源有限输出电阻的影响。
- `ch04_04_source_degenerated_diff_pair.cir`：源极负反馈扩大线性输入范围。
- `ch04_05_mos_load_diff_pair.cir`：PMOS 电流源作为差动对负载。
- `ch04_06_current_mirror_load_diff_pair.cir`：电流镜负载把差动电流转成单端输出。
- `ch04_07_gilbert_cell_mixer.cir`：Gilbert 单元作为跨导级加开关级的组合。

## 第 5 章：电流镜与偏置技术

电流镜部分建议重点看输出电流随 `Vout` 的变化。曲线越平，输出电阻越大，电流源越理想。

- `ch05_01_basic_current_mirror.cir`：基本 NMOS 电流镜。
- `ch05_02_ratio_current_mirror.cir`：用宽长比复制或缩放电流。
- `ch05_03_cascode_current_mirror.cir`：共源共栅电流镜提高输出电阻。
- `ch05_04_low_voltage_cascode_mirror.cir`：用外加偏置观察低电压余量的共源共栅镜。
- `ch05_05_current_mirror_load_ota.cir`：五管 OTA/有源电流镜负载差动对。
- `ch05_06_bias_common_source.cir` 到 `ch05_09_bias_diff_pair.cir`：把电流镜用于不同放大器的偏置。

## 结果读取

`results/*.dat` 是文本表格。常见列包括扫描变量、节点电压、电源电流、器件电流以及 `gm/gds`。例如共源电阻负载的 DC 转移曲线在：

```text
results/ch03_01_cs_resistor_load_dc.dat
```

AC 结果中，输入源的 AC 幅度通常设为 1 或 1 mV；若输入设为 1，`vdb(out)` 就是以 dB 表示的电压增益。

也可以直接生成所有曲线图：

```powershell
python .\tools\plot_results.py
```

生成的 PNG 位于 `plots/`。
