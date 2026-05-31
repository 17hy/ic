# 02 大信号宏晶体管法

这一类使用 `paper_ldo_xcea_ssf_macro.inc`。它不是 PDK 模型，但已经包含大信号 PMOS pass 管和可观察内部节点：

- `vin`
- `vout`
- `fb`
- `gate`
- `xcea`
- `ssf`

文件：

- `large_signal_xcea_ssf_psr.cir`：大信号工作点 + AC PSR。
- `large_signal_xcea_ssf_transient.cir`：25 mVpp 供电锯齿 + 负载扰动瞬态。

运行：

```powershell
.\run.ps1
```

结果写入 `results/`。

