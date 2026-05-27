# EdgeLLM 论文中文翻译与技术整理

原文题目：EdgeLLM: A Highly Efficient CPU-FPGA Heterogeneous Edge Accelerator for Large Language Models

出处：IEEE Transactions on Circuits and Systems-I: Regular Papers, Vol. 72, No. 7, July 2025

## 摘要译文

大语言模型在自然语言处理和图像处理任务中表现突出，但模型规模巨大、计算量高、显存带宽需求高，使其很难直接部署在资源受限的边缘设备上。本文提出 EdgeLLM，一个面向大语言模型推理的 CPU-FPGA 异构边缘加速器。系统使用混合精度处理单元阵列和分组脉动结构，同时支持 MHA 中的 FP16*FP16 运算和 FFN 中的 FP16*INT4 运算。为了降低带宽和存储压力，设计了 log-scale 结构化稀疏方案与块量化参数封装方法。为了减少不同算子之间的数据重排开销，提出统一数据并行格式，并配套端到端编译流程、动态 token 长度控制和指令流水隐藏机制。作者在 AMD Xilinx VCU128 FPGA 上部署 ChatGLM-6B / Qwen-7B 等模型，实验表明相对 NVIDIA A100-SXM4-80G GPU，EdgeLLM 在稀疏 GLM-6B 解码任务上达到 1.91 倍吞吐率和 7.55 倍能效；相对 FlightLLM 也有 10% 到 24% 左右的能效/利用率优势。

## 1. 研究背景与核心问题

LLM 推理中的主要瓶颈不是单一的乘法器数量，而是计算阵列、HBM/DDR 带宽、KV-cache 访问、动态 token 控制以及算子之间数据格式的一致性。传统 GPU 具有高吞吐，但功耗高，不适合边缘端部署；普通 FPGA 虽然能效高，但如果没有高效的数据布局和编译调度，容易被外部存储带宽限制。

作者将 LLM 中的主要算子分成两类：矩阵乘法和 MHA 相关算子连接到高带宽 HBM；LayerNorm、RMSNorm、RotaryEmbedding、非线性激活等通过定制 DMA 连接 DDR 与片上 BRAM。系统由 CPU 负责控制、调度与部分通用操作，FPGA 负责高吞吐矩阵和注意力计算。

## 2. 系统架构翻译

EdgeLLM 采用 CPU-FPGA 异构架构。CPU 侧负责运行服务端、接收请求、生成推理控制信息，并通过 PCIe 与 FPGA 交互。FPGA 侧包含 LLM 加速器、控制寄存器、FP16 加速核心、特征存储、权重存储、AXI 接口和 DMA 模块。高带宽权重访问放在 HBM，其他算子的输入输出和中间状态可以放在 DDR 或 BRAM。

图 2 所示架构的关键点是：MatMUL 和 MHA 是主要的带宽/计算热点，直接连接 HBM；其他低吞吐或控制型算子连接 DDR；KV-cache 的读写由 HBM 路径处理，从而降低 MHA 阶段由于历史 token 增长带来的数据搬移压力。

## 3. Roofline 带宽-计算平衡

图 3 使用 roofline 模型解释 EdgeLLM 的设计点。HBM 原始接口为 32 个 AXI 端口，每端口 256 bit/cycle，总共 8192 bit/cycle。为了充分利用 HBM，作者让 HBM-AXI 通信模块和 DMA 以计算模块的两倍频率工作，相当于给计算阵列提供 16384 bit/cycle 的有效数据服务能力。

在 FFN 层，权重为 INT4，计算并行度设置为 4096，因此每周期权重数据需求为：

```text
4096 * 4 bit = 16384 bit/cycle
```

在 MHA 层，KV-cache 为 FP16，计算并行度设置为 1024，因此每周期 KV-cache 数据需求为：

```text
1024 * 16 bit = 16384 bit/cycle
```

这两个核心路径都精确匹配 HBM 的 16384 bit/cycle 服务能力。作者认为这种设置使系统既不明显受 memory bound 限制，也不明显受 compute bound 限制，而是落在更高效的平衡点附近。

## 4. 混合精度 G-VSA 与 PE 翻译

图 4 是本文硬件设计的核心。作者没有直接采用 TPU 风格的细粒度脉动阵列，因为 TPU 风格结构需要大量寄存器保存临时数据，功耗和面积较高。本文采用 group vector systolic array，输入特征和权重以按行方式传入 PE 阵列，可以降低临时寄存器和数据搬移开销。

混合精度 PE 同时支持两种模式：

```text
FFN: FP16 activation * INT4 weight
MHA: FP16 activation * FP16 KV-cache
```

在 FFN 中，模型权重量化为 INT4，但激活和部分比例因子仍保留 FP16，以降低精度损失。在 MHA 中，KV-cache 保持 FP16，以避免注意力计算精度显著下降。PE 的计算流程分为四级流水：

1. Stage 0：输入拆分，将 FP16 拆成符号、指数和尾数，将 INT4 拆成符号和值。
2. Stage 1：符号异或、指数比较、尾数乘法。
3. Stage 2：根据指数差进行对齐移位，之后通过加法树累加。
4. Stage 3：使用 LZA 和指数调整恢复 FP16 规格，乘以 scale，并送入积分/输出模块。

作者给出的验证结果是：本文 PE 在 FP16*INT4 模式下计算误差约 0.0472%，在 FP16*FP16 模式下误差约 0.0044%。ASIC 28 nm 估计面积为 71664 um^2，频率达到 1.11 GHz；相比 FP16 加法树 baseline 面积降低约 33.2%，相比 FP20 加法树 baseline 面积降低约 49.1%。

## 5. Log-scale 结构化稀疏翻译

图 5 是本文另一个核心。LLM 权重规模巨大，INT4 量化能降低带宽，但仍不足以完全解决边缘端带宽和存储问题。作者提出 log-scale structured sparse：每 8 个相邻数据块中至少包含 N 个零，非零元素数量按 1/2、1/4、1/8 等幂次结构变化。这样硬件能够通过时间展开微架构保持较高利用率，同时减少无效权重访问。

对于每 2048 个输入通道，作者将 scale、mask 和 weight 共同打包。由于 HBM AXI 端口宽度为 256 bit，scale 为 FP16，并且量化块大小为 128，因此 2048 个通道对应 256 bit 的 scale。不同稀疏度下的有效权重位宽如下：

```text
Dense: 4.125 bit
50% sparse: 3.125 bit, 性能提升约 1.32x
75% sparse: 1.875 bit, 性能提升约 2.2x
87.5% sparse: 1.125 bit, 性能提升约 3.67x
```

作者还设计了混合编码方案：低稀疏度时使用 one-hot 编码，高稀疏度时使用 address-in-block 编码。这样既能减少 mask 开销，也能保持硬件计算阵列在不同稀疏度下接近 100% 的计算效率。

## 6. 软件设计与统一数据格式翻译

图 6 将 ChatGLM-6B 的一个 LLM block 优化为 17 个硬件步骤。绿色模块表示 FP16*INT4 MatMUL，蓝色模块表示 HBM-KVcache，黄色模块表示与 KV-cache 相关的 FP16*FP16 MatMUL。作者强调，每个算子的输入输出都应尽量保持一致的数据结构，否则 transpose、reshape、attention 里的 K/V 访问会造成大量数据重排。

图 7 提出统一数据格式。文本激活原始形状为 `[token, CH]`，在加速器中重排为：

```text
[CH / Tout, token, Tout]
```

如果有 batch 或 head 维度，可扩展为：

```text
[B or H, CH / Tout, token, Tout]
```

这种格式使 AXI 读写宽度固定为 `Tout * 16`，与最小数据包一致，并让连续地址可以沿 width 维或 token 维顺序访问。其主要价值是减少 transpose 前后的数据搬移，使 MHA 和 FFN 之间的数据流更连续。

## 7. 编译部署与延迟隐藏翻译

图 8 展示编译和部署流程。编译器导入已经量化和稀疏化的 LLM，然后做动态控制、图变换和后端代码生成，最终输出权重文件、指令文件和运行时控制代码。动态 token 相关参数被编码为 DAG 表达式；如果可在编译期确定，就直接写入指令；否则生成运行时代码进行更新。

图 9 是推理阶段延迟隐藏机制。普通模式下，主机线程需要等待推理完成后再更新下一步指令；延迟隐藏模式下，主机在线程等待加速器计算时提前更新后续指令。作者采用预配置寄存器模式和辅助路径，将序列化算子指令从片上 DDR 通过 AXI 送入 buffer，主机只需写入地址、有效算子数等少量配置。这样动态控制更新时间可以被加速器计算时间覆盖，只在第一次推理前需要完整更新指令。

## 8. 实验结果翻译

实验平台为 AMD Xilinx VCU128。FPGA 资源包括约 1303K LUT、2607K FF、9024 DSP、2016 BRAM，并配备 8GB HBM，标称带宽 460 GB/s。MatMUL 和 HBM 相关路径运行在 280 MHz，其他算子约 140 MHz。

作者给出 HBM 利用率计算示例：GLM-6B 的 Wq 在 decode 阶段输入形状为 `(token, 4096)`，权重矩阵为 `(4096, 4096)`，当 token=1 时，理想操作时间为：

```text
4096 * 4096 * 4 bit / 8192 bit/cycle * 3.571 ns = 29.25 us
```

实际测得时间约 38.5 us，因此 HBM 带宽利用率为：

```text
29.25 us / 38.5 us = 75.97%
```

各 MatMUL 层利用率大多在 70% 到 80% 之间，平均约 75%。在 dense GLM-6B 中，当 decode token 小于 512 时，速度约保持在 90 token/s；随着 token 增长，MHA 延迟因 KV-cache 和注意力长度增加而上升。FFN 延迟基本不随 decode 长度变化。

稀疏策略 3 的 GLM-6B 首个 decode 延迟约 10.8 ms，峰值速度约 85.8 token/s，功耗约 56.86 W。相对 A100-SXM4-80G GPU，吞吐率约为 1.91 倍，能效约为 7.55 倍。DDR-only 系统在 decode 阶段速度约为 HBM 系统的 25%，说明解码阶段的矩阵-向量乘法强依赖高带宽存储。

## 9. 局限性翻译

作者指出，不同模型中的 RotaryEmbedding 等算子差异明显。为每个模型定制专用算子可以获得更高效率，但可移植性较差；把这类算子放在 CPU 或通用 ElementWise 单元上更通用，但性能较低。另外，当前系统中的一些 temporal-mode 算子仍按顺序执行，未来可以通过算子级并行进一步提高吞吐。

## 10. 我认为本文最核心的三个点

第一，EdgeLLM 的核心不是单个乘法器，而是让 FFN 的 FP16*INT4 和 MHA 的 FP16*FP16 两条最重路径都匹配 HBM 的有效带宽。4096*4 与 1024*16 都等于 16384 bit/cycle，这是系统级平衡设计。

第二，log-scale 稀疏把算法稀疏性变成硬件可预测的数据包格式，避免 GPU 上常见的不规则稀疏访问开销。它的价值不只是减少权重位数，而是让不同稀疏度下仍能保持高计算效率。

第三，统一数据格式和指令延迟隐藏解决的是部署问题。很多加速器论文只强调 PE 峰值算力，但 LLM 推理的实际瓶颈往往在 KV-cache、transpose、host 控制和动态 token 变化。本文把这些系统问题纳入设计，因此实验结果更接近端到端推理。

## 11. 本次 ngspice 仿真选取的核心对象

由于本文是 FPGA/体系结构论文，不是模拟集成电路论文，所以本次仿真采用行为级电路模型：用电压表示吞吐、位宽、延迟和收益，用电容积分表示带宽供需失衡时的 backlog 增长。仿真对象包括：

1. Roofline/HBM 平衡模型：验证 FFN 与 MHA 的数据需求是否匹配 16384 bit/cycle HBM 服务能力。
2. 混合精度 PE 模型：抽象比较 FP16*INT4 和 FP16*FP16 模式的误差、面积、功耗和带宽需求。
3. Log-scale 稀疏模型：验证不同稀疏度下有效 bit-width 和理论性能提升。
4. 指令流水延迟隐藏模型：估算 host 指令更新时间被 accelerator 计算时间覆盖后的端到端延迟收益。
