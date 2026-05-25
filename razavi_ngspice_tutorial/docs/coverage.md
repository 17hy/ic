# 覆盖表

本表按正文可仿真的电路拓扑组织。原书中的物理剖面图、波形示意图、纯等效小信号图和数学推导图不复制原图；它们被合并到相应 testbench 中验证。

| 章节 | 正文主题 | 网表 |
|---|---|---|
| 2.1 | MOSFET 开关 | `circuits/ch02/ch02_01_mos_switch_transfer.cir` |
| 2.2 | MOS I-V 特性族 | `circuits/ch02/ch02_02_nmos_iv_family.cir` |
| 2.2-2.4 | gm、gds、ro 小信号参数 | `circuits/ch02/ch02_03_gm_ro_bias.cir` |
| 2.3 | 体效应 | `circuits/ch02/ch02_04_body_effect.cir` |
| 2.4 | MOS 输入电容 | `circuits/ch02/ch02_05_mos_gate_capacitance.cir` |
| 3.3 | 共源级，电阻负载 | `circuits/ch03/ch03_01_cs_resistor_load.cir` |
| 3.3 | 共源级，二极管连接负载 | `circuits/ch03/ch03_02_cs_diode_connected_load.cir` |
| 3.3 | 共源级，理想电流源负载 | `circuits/ch03/ch03_03_cs_current_source_load.cir` |
| 3.3 | 共源级，PMOS 有源负载 | `circuits/ch03/ch03_04_cs_pmos_active_load.cir` |
| 3.3 | 共源级，线性区 MOS 负载 | `circuits/ch03/ch03_05_cs_triode_load.cir` |
| 3.3 | 带源极负反馈的共源级 | `circuits/ch03/ch03_06_cs_source_degeneration.cir` |
| 3.4 | 源跟随器 | `circuits/ch03/ch03_07_source_follower.cir` |
| 3.5 | 共栅级 | `circuits/ch03/ch03_08_common_gate.cir` |
| 3.6 | 共源共栅级 | `circuits/ch03/ch03_09_cascode_stage.cir` |
| 3.6.1 | 折叠式共源共栅 | `circuits/ch03/ch03_10_folded_cascode_stage.cir` |
| 4.2 | 基本差动对，大信号转移 | `circuits/ch04/ch04_01_basic_diff_pair_dc.cir` |
| 4.2 | 基本差动对，小信号增益 | `circuits/ch04/ch04_02_diff_pair_ac_gain.cir` |
| 4.3 | 共模响应 | `circuits/ch04/ch04_03_diff_pair_common_mode.cir` |
| 4.2.3 | 源极负反馈差动对 | `circuits/ch04/ch04_04_source_degenerated_diff_pair.cir` |
| 4.4 | MOS 负载差动对 | `circuits/ch04/ch04_05_mos_load_diff_pair.cir` |
| 4.4/5.3 | 电流镜负载差动对 | `circuits/ch04/ch04_06_current_mirror_load_diff_pair.cir` |
| 4.5 | Gilbert 单元 | `circuits/ch04/ch04_07_gilbert_cell_mixer.cir` |
| 5.1 | 基本电流镜 | `circuits/ch05/ch05_01_basic_current_mirror.cir` |
| 5.1 | 比例电流镜 | `circuits/ch05/ch05_02_ratio_current_mirror.cir` |
| 5.2 | 共源共栅电流镜 | `circuits/ch05/ch05_03_cascode_current_mirror.cir` |
| 5.2 | 低压余量共源共栅镜 | `circuits/ch05/ch05_04_low_voltage_cascode_mirror.cir` |
| 5.3 | 有源电流镜负载 / 五管 OTA | `circuits/ch05/ch05_05_current_mirror_load_ota.cir` |
| 5.4 | 共源级偏置 | `circuits/ch05/ch05_06_bias_common_source.cir` |
| 5.4 | 共栅级偏置 | `circuits/ch05/ch05_07_bias_common_gate.cir` |
| 5.4 | 源跟随器偏置 | `circuits/ch05/ch05_08_bias_source_follower.cir` |
| 5.4 | 差动对偏置 | `circuits/ch05/ch05_09_bias_diff_pair.cir` |
