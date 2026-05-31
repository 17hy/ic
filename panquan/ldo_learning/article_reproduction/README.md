# 论文 LDO ngspice 复现分类

这个目录把论文第 II-B 节 LDO 复现分为三类：

- `01_small_signal`：小信号等效法。复现 PSR 曲线、25 mVpp/1 MHz 锯齿噪声、power-bounce 抑制量级。
- `02_large_signal`：大信号宏晶体管法。包含 PMOS pass 管、反馈、XCEA-like 慢环、SSF-like 快环和 200 pF 输出电容。
- `03_pdk_direct`：PDK 级直接法。使用 IHP SG13G2 Open PDK 的 `sg13_hv_pmos` 真实器件模型作为 pass 管。

运行全部：

```powershell
.\run_all_reproduction.ps1
```

每个子目录的结果都会写到自己的 `results/` 目录。

