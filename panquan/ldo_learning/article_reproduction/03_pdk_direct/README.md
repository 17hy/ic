# 03 PDK 级直接法

这一类直接使用 IHP SG13G2 Open PDK 的器件模型。当前直跑版使用：

- `sg13_hv_pmos`：3.3 V HV PMOS pass 管，来自 IHP SG13G2 ngspice PDK。
- `Rtop/Rbot`：反馈分压，目标 `VOUT=3.1 V`。
- 行为级 XCEA/SSF 驱动：先保证真实 pass 管可以稳定直跑，并用于估算 PDK pass 管带来的 PSR。

运行脚本会优先使用已有环境变量：

```powershell
$env:PDK_ROOT = "C:\pdk\IHP-Open-PDK"
$env:PDK = "ihp-sg13g2"
```

如果没有设置，脚本会在本目录 `_pdk_cache/` 下 sparse clone IHP Open PDK 的 ngspice 模型。OSDI 模型优先使用当前 ngspice 发行包里的 `Spice64/lib/ngspice/*.osdi`。

运行：

```powershell
.\run.ps1
```

结果写入 `results/`。

