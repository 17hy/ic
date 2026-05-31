# LDO 晶体管级与真实器件级建模路线

这里把 LDO 学习目录扩展成两条更接近论文和真实工艺的路线。

## 1. 论文结构完整宏模型

文件：

- `circuits/paper_ldo_xcea_ssf_macro.inc`
- `circuits/10_paper_xcea_ssf_macro_psr.cir`
- `circuits/11_paper_xcea_ssf_macro_transient.cir`

这个模型包含：

- `Mpass` PMOS pass 管。
- `Rtop/Rbot` 反馈分压，`VREF=1.2 V`，`VOUT=3.1 V`。
- XCEA-like 慢环，负责 DC 调节和低频 PSR。
- SSF-like 快环，负责快速负载扰动和高频动态输出阻抗。
- `200 pF` 输出电容，对应论文第 II-B 节的输出主极点设计。
- pass gate 电容、输出 ESR、rail clamp 和内部观测节点。

它不是 PDK 器件模型，但已经是大信号 LDO 模型，支持 `.op`、`.ac`、`.tran`。相比 `paper_dual_loop_ldo.inc` 的小信号模型，它更适合观察：

- pass 管 gate 电压如何调节。
- `FB` 如何锁定到 `VREF`。
- `VIN` 锯齿噪声如何变成 `VOUT` 小纹波。
- 慢环和快环对动态扰动的分工。

当前默认参数运行结果：

- DC：`VOUT ~= 3.10 V`，`FB ~= 1.20 V`。
- `10_paper_xcea_ssf_macro_psr.cir`：1 MHz PSR 约 `-53 dB`。
- `11_paper_xcea_ssf_macro_transient.cir`：`25 mVpp` 供电锯齿加小负载扰动下，`VOUT` 约在 `3.089 V` 到 `3.114 V` 之间变化。

## 2. 真实器件级模型：IHP SG13G2

文件：

- `circuits/ihp_sg13g2/README.md`
- `circuits/ihp_sg13g2/ihp_sg13g2_device_level_ldo.cir`
- `circuits/ihp_sg13g2/run_ihp_examples.ps1`

选择 IHP SG13G2 的原因：

- 论文是 130 nm SiGe BiCMOS。
- IHP SG13G2 Open PDK 是公开可用的 130 nm BiCMOS PDK。
- 它提供 SiGe:C NPN HBT、1.2 V/3.3 V MOS、MIM 电容、无源器件和 ngspice/Xyce 模型。

模板里已经使用这些器件名：

```spice
Xmpass vout gate vin vin sg13_hv_pmos ...
Xmn_fb nfb fb tail 0 sg13_hv_nmos ...
Xmn_ref nref vref tail 0 sg13_hv_nmos ...
Qssf vin ssf_base ssf_emit 0 npn13G2 Nx=4
```

IHP 器件接口来自 PDK 的 xschem/ngspice 模型：

- `sg13_hv_pmos` / `sg13_hv_nmos` pin order：`d g s b`
- `npn13G2` pin order：`c b e substrate`

## 3. 为什么 IHP 模板不放进默认 run_all

IHP MOS 使用 PSP OSDI 模型。运行前必须安装 PDK 并让 ngspice 加载 OSDI：

```text
psp103.osdi
psp103_nqs.osdi
r3_cmc.osdi
mosvar.osdi
```

如果没有这个环境，ngspice 会报 unknown model 或无法找到 `.lib`。所以 IHP 模板放在 `circuits/ihp_sg13g2/` 子目录中，避免默认 `run_all.ps1` 失败。

## 4. 下一步建议

1. 先用 `10/11` 调通论文结构和指标。
2. 安装 IHP SG13G2 PDK 后，运行 `ihp_sg13g2_device_level_ldo.cir`。
3. 逐步替换：
   - 理想电流源 -> MOS/HBT 偏置电路。
   - 理想输出电容 -> `cap_cmim` 或 RF MIM 电容阵列。
   - 简化 SSF -> 论文结构中更接近的 super-source-follower。
   - 单 corner -> TT/SS/FF + 温度 + `0.9VCC/VCC/1.1VCC`。
4. 做 Monte Carlo：先 PSR@1MHz，再做输出阻抗和 load-step。

## 5. 边界

没有论文的完整器件尺寸、偏置电流、版图寄生和作者使用的 PDK 模型时，不能声称完全复刻论文芯片。这里的目标是：

- 结构上贴近论文。
- 指标上复现论文量级。
- 工艺上提供可迁移到开放 130 nm SiGe BiCMOS PDK 的起点。

