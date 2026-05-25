# Razavi 前五章 ngspice 教程

这个目录把当前文件夹中的拉扎维《模拟 CMOS 集成电路设计》前 5 章正文内容整理成可运行的 ngspice 教程。为了避免复制教材原图，教程按“可仿真的电路拓扑”重建网表，并用章节主题对应原书正文：MOS 器件、单级放大器、差动放大器、电流镜与偏置。

## 快速运行

在 PowerShell 中执行：

```powershell
cd C:\Users\Guohu\Desktop\ngspice\razavi_ngspice_tutorial
.\tools\run_all.ps1
```

仿真输出会写到 `results/`，每个电路的 ngspice 日志写到 `logs/`。

生成曲线图：

```powershell
python .\tools\plot_results.py
```

图片会写到 `plots/`。

## 目录

- `models/educational_cmos.inc`：统一的教学 MOS 模型卡。
- `circuits/ch02`：MOS 开关、I-V、gm、ro、体效应、电容。
- `circuits/ch03`：共源、源跟随、共栅、共源共栅、折叠共源共栅。
- `circuits/ch04`：基本差动对、共模响应、源极负反馈、有源负载、Gilbert 单元。
- `circuits/ch05`：基本/比例/共源共栅电流镜、五管 OTA 与偏置电路。
- `docs/tutorial.md`：按章节组织的教程说明。
- `docs/coverage.md`：正文电路拓扑与网表的对应表。
- `tools/plot_results.py`：把 `results/*.dat` 批量画成 PNG。

## 建模边界

这些网表使用 Level 1 MOS 教学模型，适合观察工作区、增益趋势、输出电阻、共模/差模行为和偏置关系。它不是某个真实工艺 PDK，不能用于版图前精确设计。若后续要提高精度，可以把 `models/educational_cmos.inc` 替换为 BSIM/PDK 模型，其他网表结构不用大改。
