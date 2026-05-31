# 论文 LDO 三类 ngspice 复现结果

运行命令：

```powershell
cd C:\Users\Guohu\Desktop\ngspice\panquan\ldo_learning\article_reproduction
.\run_all_reproduction.ps1
```

## 01 小信号等效法

目录：`01_small_signal`

结果：

- 1 MHz PSR：
  - conventional：`-37.0912 dB`
  - worst：`-40.3122 dB`
  - typical：`-43.9118 dB`
  - best：`-48.7341 dB`
- 25 mVpp、1 MHz 锯齿电源噪声：
  - LDO residual ripple：约 `0.655 mVpp`
  - TX output noise proxy：约 `0.200 mVpp`
  - RX output noise proxy：约 `0.020 mVpp`
- power-bounce：
  - conventional slow loop：约 `92.2 mVpp`
  - dual loop：约 `5.36 mVpp`

## 02 大信号宏晶体管法

目录：`02_large_signal`

结果：

- DC 工作点：
  - `VOUT = 3.099981 V`
  - `FB = 1.199993 V`
  - `GATE = 2.715867 V`
  - `XCEA = 0.584133 V`
- 1 MHz PSR：`-53.1959 dB`
- 25 mVpp 供电锯齿 + 负载扰动瞬态：
  - `VOUT max = 3.11350 V`
  - `VOUT min = 3.08948 V`
  - `GATE max = 2.72853 V`
  - `GATE min = 2.69781 V`

## 03 PDK 级直接法

目录：`03_pdk_direct`

使用 IHP SG13G2 Open PDK 的 `sg13_hv_pmos` 真实 HV PMOS pass 管。运行脚本会自动 sparse clone IHP ngspice 模型到 `_pdk_cache/`，并加载本机 ngspice 自带的 PSP OSDI 模型。

结果：

- DC 工作点：
  - `VOUT = 3.099433 V`
  - `FB = 1.199781 V`
  - `GATE = 2.202725 V`
  - `EA = 1.097275 V`
- 1 MHz PSR：`-48.9020 dB`

## 说明

这三类模型的用途不同：

- 小信号等效法：最快，适合复现论文图 4/5/6 的量级。
- 大信号宏晶体管法：能观察 `gate/fb/xcea/ssf` 等内部节点，适合学习环路和瞬态。
- PDK 级直接法：真实使用 IHP SG13G2 pass 器件，适合后续替换成全器件 XCEA、SSF 和 MIM 电容。

