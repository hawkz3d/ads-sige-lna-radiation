# SiGe HBT MMIC LNA 辐照损伤与电磁干扰协合效应 — ADS 工程

基于《基于 SiGe HBT 的 SiGe 微波单片低噪声放大器（MMIC LNA）光子、重离子
辐照损伤及电磁干扰协合效应研究》第 3、4 章，整理自原始 ADS 工作区的 SiGe
微波单片低噪声放大器辐照损伤与电磁干扰协合效应仿真工程。

## 项目结构

```
ads-sige-lna-radiation/
├── README.md                    # 本文件
├── docs/
│   └── thesis_notes.md          # 论文技术要点
├── netlist/
│   ├── bandgap_spice.net        # 带隙基准电路（Kuijk CMOS）
│   ├── lna_cascode.net          # LNA Cascode 电路网表
│   └── radiation_models.md      # 辐照 SPICE 参数表（论文表4-3）
├── ads_scripts/                 # ADS 自动化脚本
│   ├── create_bandgap.ael       #   ADS AEL 建图脚本：自动搭建 BandgapRef 原理图
│   ├── probe_pins.ael           #   AEL 探针坐标转储脚本
│   ├── run_bandgap.py           #   Win32 SendInput 向 ADS Command Line 发命令
│   ├── send_cmd.py              #   pywinauto 控制 ADS 界面发送 load 命令
│   ├── probe_server.py          #   探测 ADS CLI Server TCP 8000-8015
│   ├── test_pvm.py              #   PVM 与 ADS eesofg2p 进程通信测试
│   ├── test_ads_py.py           #   ADS Python API（ADSSim/Design/Component）探测
│   └── query_doc.py             #   查询 ADS 帮助文档数据库 ads.qch
└── simulation/
    ├── run_radiation_sweep.py   # 辐照参数扫描脚本
    ├── radiation_sweep.png      # 脚本生成的 S21/S11/NF 三工况对比图
    └── radiation_summary.csv    # 扫描结果 CSV
```

## 工程背景

论文第 3 章用 **Sentaurus TCAD** 对 0.18 μm SiGe BiCMOS HBT 建立辐照损伤模型
（TID 电离损伤 + DD 位移损伤），得到 β 退化、结电容变化等结论（详见
`docs/thesis_notes.md`）。第 4 章把这些退化映射到 **SPICE 模型参数**
（BF/RB/CJE/CJC/TF，见 `netlist/radiation_models.md`），在 **ADS** 中设计
0.7 GHz Cascode LNA 并仿真辐照前后及 EMI 协合效应下的 S 参数 / 噪声系数退化。

工程交付内容：

- `netlist/bandgap_spice.net` — LNA 偏置电路的带隙基准启动模块
- `ads_scripts/` — 上述电路的 ADS 自动化搭建与通信脚本
- `netlist/lna_cascode.net` — Cascode LNA 放大级电路
- `simulation/run_radiation_sweep.py` — 辐照损伤与 EMI 协合效应的参数扫描

## 使用说明

### 1. 带隙基准

`netlist/bandgap_spice.net` 是 Kuijk CMOS 带隙基准（VDD=5V，PNP 面积比 1:8，
PMOS 电流镜，理想运放增益 1e5，启动电流 1 μA），可直接用 ADS 的
**File → Import → SPICE Netlist** 导入，或任何 SPICE 兼容仿真器运行 `.OP`。

在 ADS 中搭建该原理图可使用 `ads_scripts/create_bandgap.ael`（将
`<ADS_WORKSPACE>` 替换为你的 ADS 工作区路径）：

```ael
load("<ADS_WORKSPACE>/create_bandgap", "SimCmd")
```

该脚本会在自定义库 `MyLibrary_lib` 下生成 `BandgapRef:schematic`，放置
BJT_PNP×2 / R×4 / MOSFET_PMOS×3 / OpAmpIdeal / V_DC / GROUND×3 / PIN×2
并完成全部连线。

### 2. LNA 辐照仿真

`netlist/lna_cascode.net` 给出 Cascode LNA 拓扑与参数化 NPN 模型。通过
`.param COND=NOM|TID|DD` 切换辐照工况（对应表4-3 参数）：

```spice
.param COND=TID    ; 总剂量效应工况
```

- 偏置：带隙基准启动 → 电流镜（Q1 镜像 / Q2 地通路 / Q3 基极补偿）
- 放大级：Q6 共射 + Q7 共基 Cascode
- EMI 注入点（论文 4.3.2）：`B` 节点预留，接入 −15 dBm / 500 MHz 正弦源
  + 结上瞬态电流源模拟整流效应

### 3. 参数扫描

`simulation/run_radiation_sweep.py` 用简化小信号模型（谐振负载 + β 比例
跨导），对 NOM/TID/DD 及 +EMI 五种工况做频率扫描：

```
COND    S21@0.7G  S11@0.7G   NF@0.7G
NOM       18.41     -0.03      1.17
TID       16.88     -0.05      1.99
DD        17.04     -0.03      1.49
```

TID 比 DD 退化更明显；耦合 EMI 后 S21 再降 3.2 dB（TID+EMI），
NF 恶化至 ~3.5 dB。运行：

```bash
python simulation/run_radiation_sweep.py
```

依赖：`numpy`（必选），`matplotlib`（可选，生成对比图）。

## 相关结论速览（论文 6.1）

1. 辐照使 HBT β 退化、结电容略增，退化集中于低偏置区；DD 效应轻于 TID。
2. LNA 增益下降、噪声增加、匹配恶化；EMI 协合进一步加剧退化
   （S21 相对辐照前衰减 > 3.2 dB）。
3. α 粒子注量增加 → S11/S22/S21/S12/线性度单调退化，与仿真趋势一致。
