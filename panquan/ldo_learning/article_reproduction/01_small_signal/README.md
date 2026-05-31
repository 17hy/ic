# 01 小信号等效法

这一类使用 `paper_dual_loop_ldo.inc` 的线性小信号模型：

```text
VIN ripple -> feedthrough -> VOUT ripple
VOUT ripple -> XCEA slow loop correction
VOUT ripple -> SSF fast-loop correction
VOUT ripple -> RLOAD || (ESR + COUT)
```

文件：

- `small_signal_dual_loop_psr.cir`：PSR 曲线，比较 conventional/worst/typ/best。
- `small_signal_sawtooth_noise.cir`：25 mVpp、1 MHz 锯齿供电噪声。
- `small_signal_power_bounce.cir`：普通慢环和双环 LDO 的 power-bounce 对比。

运行：

```powershell
.\run.ps1
```

结果写入 `results/`。

