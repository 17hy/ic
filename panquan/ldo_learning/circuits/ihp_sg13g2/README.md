# IHP SG13G2 器件级 LDO 模板

这个子目录放基于 IHP SG13G2 Open PDK 的器件级 LDO 模板。它不会被上级 `run_all.ps1` 默认执行，因为运行前必须先安装 IHP PDK 和 ngspice OSDI 模型。

## 为什么选 IHP SG13G2

论文使用 130 nm SiGe BiCMOS。公开可用、且最接近这个方向的是 IHP SG13G2 Open PDK：130 nm BiCMOS，包含 SiGe:C NPN HBT、1.2 V/3.3 V MOS、MIM 电容、无源器件和 ngspice/Xyce 模型。

## 需要的外部环境

推荐安装：

```powershell
git clone https://github.com/IHP-GmbH/IHP-Open-PDK.git C:\pdk\IHP-Open-PDK
```

然后按 IHP 文档安装 ngspice OSDI 模型。IHP 文档说明需要设置：

```powershell
$env:PDK_ROOT = "C:\pdk\IHP-Open-PDK"
$env:PDK = "ihp-sg13g2"
```

并让 ngspice 能加载：

```text
$PDK_ROOT/$PDK/libs.tech/ngspice/osdi/psp103.osdi
$PDK_ROOT/$PDK/libs.tech/ngspice/osdi/psp103_nqs.osdi
$PDK_ROOT/$PDK/libs.tech/ngspice/osdi/r3_cmc.osdi
$PDK_ROOT/$PDK/libs.tech/ngspice/osdi/mosvar.osdi
```

## 文件

- `ihp_sg13g2_device_level_ldo.cir`：使用 `sg13_hv_pmos`、`sg13_hv_nmos` 和 `npn13G2` 的器件级骨架。
- `run_ihp_examples.ps1`：检查环境变量并运行模板。

## 运行

```powershell
cd C:\Users\Guohu\Desktop\ngspice\panquan\ldo_learning\circuits\ihp_sg13g2
.\run_ihp_examples.ps1
```

这个模板是“可落地的器件级起点”，不是最终可流片 LDO。下一步需要用真实偏置、电流能力、PVT、Monte Carlo 和版图寄生继续校准。

