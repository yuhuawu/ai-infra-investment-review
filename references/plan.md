下面这个框架可以当作一个 **AI 基础设施股票组合的月度 review 模板**。它不是个性化投资建议，而是把公开市场里能买到的 AI 相关股票，按“谁受益、看什么指标、指标变化后怎么调仓”系统化。

---

## 0. 总原则：先看需求，再看瓶颈，最后看利润兑现

AI 产业链的股票投资，不能只按“谁最像 AI 公司”来买，而要按三件事判断：

**第一，需求是否继续扩张。**
主要看 Microsoft、Alphabet、Amazon、Meta、Oracle 等超大客户的资本开支、云收入、RPO/backlog、AI 收入或 token 使用量。比如 Microsoft 最新披露 AI business annual revenue run rate 超过 370 亿美元，Azure and other cloud services 增长 40%；Alphabet 披露 Google Cloud 一季度收入 200 亿美元、同比增长 63%，Cloud backlog 超过 4600 亿美元；Oracle 披露 RPO 达 5530 亿美元、同比增长 325%，且大部分增量与大型 AI 合同相关。([Source][1])

**第二，瓶颈在哪里。**
如果瓶颈在 GPU，NVIDIA/AMD/ASIC 受益；如果瓶颈在 HBM，Micron/SK Hynix/Samsung 受益；如果瓶颈在先进制程/封装，TSMC/ASML/设备厂受益；如果瓶颈转向电力、散热、网络和数据中心建设，Vertiv、Arista、光模块、服务器 OEM 会受益。NVIDIA 最新季度 Data Center 收入达 623 亿美元，TSMC 最新季度毛利率 66.2%、先进制程收入占比 74%，Vertiv 披露 AI 基建带动 backlog 达 150 亿美元、同比增长 109%。([NVIDIA Newsroom][2])

**第三，利润是否真的留下来。**
AI capex 增长不等于所有公司股价都涨。买方公司的自由现金流可能被压缩，供应商可能受益但估值已提前反映。因此每次 review 都要同时看：收入增速、毛利率、订单/backlog、资本开支、自由现金流、估值倍数和 EPS 预期修正。

---

# 1. 分层框架

我建议把 AI 基建股票分成 6 层，而不是简单分成“芯片、云、模型”。

| 层级                       | 角色        | 主要公开股票示例                                                 | 投资逻辑                                                                           |
| ------------------------ | --------- | -------------------------------------------------------- | ------------------------------------------------------------------------------ |
| L1：半导体设备、晶圆代工、先进封装       | 产能源头      | ASML、TSM、AMAT、LRCX、KLAC、ASX、BESI、Tokyo Electron          | AI 算力长期扩张最终要落到先进制程、EUV、CoWoS/先进封装、晶圆产能                                         |
| L2：加速器与 ASIC             | 算力核心      | NVDA、AMD、AVGO、MRVL、ARM、INTC                              | GPU/ASIC 是 AI capex 最大价值池之一；NVIDIA 是 GPU 主导，Broadcom/Marvell 是定制 ASIC 和高速互联受益者 |
| L3：HBM、DRAM、NAND、SSD、HDD | 算力和数据存储瓶颈 | MU、Samsung、SK Hynix、SNDK、WDC、STX                         | AI 训练/推理提高 HBM、server DRAM、enterprise SSD、nearline HDD 需求，周期性强但弹性大             |
| L4：网络、光模块、服务器、机柜、电力、散热   | 数据中心“铲子”  | ANET、CSCO、LITE、COHR、CIEN、DELL、HPE、SMCI、VRT、ETN、Schneider | 当 GPU 不再是唯一瓶颈，网络、电力、液冷、机柜、电源管理成为第二波受益者                                         |
| L5：云服务与 LLM 运营商          | 需求端 + 变现端 | MSFT、GOOGL、AMZN、ORCL、META、CRWV                           | 公开市场中纯 LLM 公司很少，大部分模型层收益被云厂商、广告平台和基础设施云吸收                                      |
| L6：现金/机会仓/对冲             | 风险管理      | 现金、短债、半导体 ETF、云 ETF                                      | AI 链条波动大，月度 review 后需要有弹药调仓                                                    |

其中，**L5 的“LLM 层”要特别处理**：公开市场里真正纯粹的 LLM 公司很少，大部分顶级模型公司仍是私有或被大厂绑定。因此，股票投资中能买到的 LLM 暴露，主要是 Microsoft/OpenAI 生态、Alphabet/Gemini、Amazon/Anthropic 与 Trainium、Meta/Llama、Oracle/OCI、CoreWeave 这类云或算力平台。CoreWeave 已于 2025 年在 Nasdaq 上市，但公司仍有较高增长、较高资本开支和净亏损特征，适合放在高风险小仓位里看。([investors.coreweave.com][3])

---

# 2. 每一层的月度观测指标与获取方式

## L1：设备、晶圆代工、先进封装

| 观察指标                           | 含义                 | 获取方式                           | 调仓含义                                   |
| ------------------------------ | ------------------ | ------------------------------ | -------------------------------------- |
| TSMC 月度营收                      | 最快的先进制程需求温度计       | TSMC investor relations 每月营收公告 | 连续 2–3 个月同比/环比强，通常利好 TSM、ASML、设备、GPU 链 |
| TSMC 毛利率、先进制程占比、capex guidance | 判断是否供不应求、先进节点是否满载  | TSMC 季报、earnings call          | 毛利率高且先进节点占比高，说明 AI/先进制程价格权强            |
| ASML EUV 订单、revenue、backlog    | 判断未来 1–3 年先进制程扩产强度 | ASML 季报、年报                     | EUV 订单强，偏中长期利好设备和代工                    |
| SEMI 设备销售、晶圆出货                 | 半导体资本开支周期指标        | SEMI、SIA/WSTS 数据               | 设备销售上行说明产能扩张，过热时也要警惕周期顶部               |

TSMC 是这层最重要的月度温度计，因为它披露月度营收。比如 TSMC 2026 年一季度营收同比增长 35.1%，3 月单月营收同比增长 45.2%；公司一季度毛利率 66.2%，3nm、5nm、7nm 等先进制程合计收入占比 74%。([台积电][4]) SEMI 的数据也很有用：2025 年全球半导体设备销售额同比增长 15% 至 1351 亿美元，增长由先进逻辑、内存和 AI 相关产能推动；SEMI 还披露 2026 年一季度全球硅晶圆出货同比增长 13.1%。([SEMI][5])

---

## L2：GPU、AI ASIC、互联芯片

| 观察指标                                                | 含义                | 获取方式                  | 调仓含义                               |
| --------------------------------------------------- | ----------------- | --------------------- | ---------------------------------- |
| NVIDIA Data Center revenue、gross margin、guidance    | GPU 主链景气度         | NVDA 季报、earnings call | 若数据中心收入继续高增且毛利稳定，维持/提高 GPU 权重      |
| AMD Data Center revenue、Instinct GPU ramp           | 第二 GPU 供应商是否拿份额   | AMD 季报                | 若 AMD AI GPU 增速快，可提高 AMD 权重但控制集中度  |
| Broadcom AI semiconductor revenue                   | 定制 ASIC、以太网交换芯片趋势 | AVGO 季报               | 若 ASIC 增长快，说明 hyperscaler 自研芯片路线增强 |
| Marvell data center revenue、custom silicon bookings | ASIC/互联长周期订单      | MRVL 季报               | 若订单强，可作为 NVDA 之外的分散暴露              |

这层要同时看 **GPU 继续强势** 和 **ASIC 是否分流**。NVIDIA 最新季度 Data Center 收入 623 亿美元，同比增长 75%，公司整体非 GAAP 毛利率约 75.2%。([NVIDIA Newsroom][2]) AMD 披露 2025 年 Data Center 收入 166 亿美元，同比增长 32%，由 EPYC 和 Instinct GPU ramp 推动。([Advanced Micro Devices, Inc.][6]) Broadcom 披露 AI semiconductor revenue 同比增长 74%，并预计下一季度 AI semiconductor revenue 同比翻倍至 82 亿美元，受定制 AI 加速器和 Ethernet AI switches 推动。([Broadcom Inc.][7]) Marvell 披露 2026 财年收入同比增长 42%，由强劲 AI 需求推动，并称数据中心业务和订单会带动 2027 财年逐季加速。([Marvell Technology, Inc.][8])

---

## L3：HBM、DRAM、NAND、SSD、HDD

| 观察指标                                      | 含义            | 获取方式                                               | 调仓含义                              |
| ----------------------------------------- | ------------- | -------------------------------------------------- | --------------------------------- |
| HBM 供需、价格、长期供货协议                          | AI 训练芯片的关键瓶颈  | Micron、SK Hynix、Samsung 季报；TrendForce/DRAMeXchange | HBM 供不应求时，上调内存权重                  |
| DRAM/NAND contract price                  | 判断内存周期上行还是见顶  | TrendForce、DRAMeXchange、公司 call                    | 价格连续上涨利好 MU、SK Hynix、Samsung、SNDK |
| Enterprise SSD / nearline HDD revenue、毛利率 | AI 数据存储需求是否扩散 | SNDK、WDC、STX 季报                                    | 存储从训练扩散到推理和数据湖时，SSD/HDD 受益        |
| Capex discipline                          | 判断供给是否过度扩张    | 存储公司季报                                             | 若价格上涨但 capex 失控，要降低周期顶部风险         |

这一层波动通常比云和代工更大，但在 AI 周期里弹性也更强。Seagate 最新季度披露收入 31.12 亿美元、非 GAAP 毛利率 47.0%，公司表示 AI 应用放大数据创造和存储需求，并给出下一季度收入 34.5 亿美元左右的指引。([希捷投资者关系][9]) Sandisk 已从 Western Digital 分拆并作为独立上市公司交易，定位中也提到 AI 相关机会。([Sandisk][10])

---

## L4：网络、光模块、服务器、电力、散热

| 观察指标                                               | 含义             | 获取方式                         | 调仓含义                                            |
| -------------------------------------------------- | -------------- | ---------------------------- | ----------------------------------------------- |
| Arista AI networking revenue、gross margin、guidance | AI 数据中心网络强度    | ANET 季报                      | 网络从 InfiniBand 向 Ethernet 扩散时，ANET/AVGO/MRVL 受益 |
| 光模块 backlog、800G/1.6T 订单                           | AI 集群互联需求      | LITE、COHR、CIEN 季报            | backlog 高且毛利率改善，上调光模块                           |
| 服务器 OEM backlog、毛利率                                | GPU 服务器交付和价格竞争 | DELL、HPE、SMCI 季报             | 收入强但毛利弱，说明议价能力有限                                |
| 电力、液冷、UPS、机柜订单                                     | 数据中心物理瓶颈       | VRT、ETN、Schneider、Siemens 季报 | AI capex 从芯片扩散到基建时，上调这一层                        |

Arista 2025 年全年收入同比增长 28.6%，并在指引中给出 2026 年一季度收入约 26 亿美元、非 GAAP 毛利率 62%–63%。([Arista Networks][11]) Vertiv 披露 2025 年四季度 organic orders 同比增长 252%，过去 12 个月订单同比增长 81%，book-to-bill 达 2.9 倍，backlog 达 150 亿美元、同比增长 109%，管理层将其归因于 AI infrastructure 需求。([Vertiv][12]) Lumentum 披露 Optical Communications backlog 超过 4 亿美元，并收到 CPO 相关的数亿美元增量订单。([Lumentum Investor Relations][13])

---

## L5：云、LLM、模型运营商

| 观察指标                                      | 含义            | 获取方式                    | 调仓含义                       |
| ----------------------------------------- | ------------- | ----------------------- | -------------------------- |
| Cloud revenue growth                      | AI 需求是否转化为云收入 | MSFT、GOOGL、AMZN、ORCL 季报 | 云收入加速，说明 capex 有变现路径       |
| RPO / backlog                             | 未来收入可见度       | 公司季报、10-Q、10-K          | RPO 快速增长利好云和上游供应商          |
| Cloud gross margin                        | AI 推理是否压缩利润   | 公司季报                    | 收入强但毛利下滑，需警惕 AI 算力成本过高     |
| AI revenue run-rate、token usage、API usage | LLM 使用量和商业化   | 公司披露、earnings call      | 使用量强且毛利可控，利好云/模型运营商        |
| Free cash flow after capex                | 买方公司股价核心      | cash flow statement     | capex 增长但 FCF 恶化，可能压制云公司估值 |

Microsoft 最新披露 Microsoft Cloud 收入 545 亿美元、同比增长 29%，Azure and other cloud services 增长 40%，但也提到由于 AI infrastructure investments 和 AI product usage，云毛利率有所下降。([Source][1]) Alphabet 披露 Google Cloud 收入 200 亿美元、同比增长 63%，Cloud backlog 超过 4600 亿美元，同时 Gemini API 每分钟处理超过 160 亿 tokens、环比增长 60%。([Q4 数据中心][14]) Oracle 披露 RPO 达 5530 亿美元，并表示大部分 RPO 增量与大型 AI 合同相关。([Oracle 投资者关系][15])

---

# 3. 基准资产配置占比

下面是一个 **AI 基础设施股票组合内部** 的基准配置，不代表全部个人资产都应投入 AI。它适合高波动、长期跟踪、愿意按月复盘的组合。

| 层级                       | 基准权重 | 子配置建议                                                                       |
| ------------------------ | ---: | --------------------------------------------------------------------------- |
| L1：代工、设备、先进封装            |  22% | TSM 10%–12%；ASML 4%–5%；AMAT/LRCX/KLAC/TEL 5%–6%；先进封装 1%–2%                  |
| L2：GPU、ASIC、互联芯片         |  28% | NVDA 14%–18%；AVGO 5%–6%；AMD 3%–4%；MRVL 2%–3%；ARM/INTC/其他 0%–2%              |
| L3：HBM、DRAM、NAND、SSD、HDD |  15% | MU 4%–6%；SK Hynix/Samsung 4%–6%；SNDK/WDC/STX 3%–5%                          |
| L4：网络、光模块、服务器、电力、散热      |  12% | ANET 3%–4%；VRT/ETN/Schneider 3%–4%；LITE/COHR/CIEN 2%–3%；DELL/HPE/SMCI 1%–2% |
| L5：云、LLM、模型运营商           |  18% | MSFT 4%–5%；GOOGL 4%–6%；AMZN 3%–5%；ORCL 2%–3%；META 1%–2%；CRWV ≤1%–2%         |
| L6：现金/机会仓                |   5% | 用于财报后、回撤后、估值错杀时加仓                                                           |

几个风控规则：

1. **单一股票上限**：除非你特别高 conviction，否则单只股票不超过组合 18%。NVIDIA 可以是最大仓位，但不建议无限集中。
2. **高杠杆/高客户集中公司上限**：例如 CoreWeave、部分服务器 OEM、单一客户依赖严重的公司，单只最好控制在 1%–3%。CoreWeave 2025 年收入高增长至 51 亿美元，但仍录得 12 亿美元净亏损，属于高增长高风险资产。([美国证券交易委员会][16])
3. **周期股上限**：内存、存储、服务器 OEM 的周期弹性很大，合计不宜超过 25%，除非你明确判断内存/存储周期仍在上行早期。
4. **云公司是“需求端锚”**：当上游估值过热时，云公司能降低组合波动；但如果 capex 过高而云毛利/FCF 下行，也要降低云公司权重。

---

# 4. 月度 review 打分表

每月给每一层打分，范围为 **-2 到 +2**。
不用因为单条新闻频繁交易，只有当某一层连续两个月分数变化，或权重偏离目标超过 5 个百分点，再调整。

| 维度    | +1 / +2 信号                                                | -1 / -2 信号                        |
| ----- | --------------------------------------------------------- | --------------------------------- |
| 需求    | hyperscaler capex 上调；云收入/RPO 加速；AI run-rate 或 token 使用量上升 | capex 延后；RPO 放缓；云收入增长低于预期         |
| 供给瓶颈  | HBM、先进封装、电力、网络持续紧张                                        | 交期缩短、库存上升、价格下跌                    |
| 利润率   | 毛利率稳定或上升；增量收入落到利润                                         | 收入强但毛利率/FCF 恶化                    |
| 估值    | EPS 预期上修大于股价涨幅                                            | 股价涨幅远超 EPS 上修，forward multiple 过高 |
| 订单可见度 | backlog、book-to-bill、RPO 强                                | backlog 消化但新增订单弱                  |

对应调仓：

| 分数变化        | 操作                    |
| ----------- | --------------------- |
| 某层从 0 升至 +1 | 增加该层 2%–3%，资金来自现金或低分层 |
| 某层升至 +2     | 增加该层 4%–6%，但不得突破该层上限  |
| 某层从 +1 降至 0 | 不急于卖，观察一个月            |
| 某层降至 -1     | 降低 2%–3%              |
| 某层降至 -2     | 降低 5%–8%，尤其是周期股和高估值股  |

---

# 5. 如何把 “Meta 扩大 capex” 转化为收入、利润、股价影响

这个例子可以做成固定模板。核心不是猜“Meta 买了谁的芯片”，而是把新增 capex 拆成几个桶。

Meta 正式披露的 2026 年资本开支区间为 1150 亿至 1350 亿美元，公司称同比增长主要由 Meta Superintelligence Labs 和核心业务推动，并预计 2026 年 operating income 将高于 2025 年。([Meta][17]) 若按随后媒体报道的最新区间 1250 亿至 1450 亿美元做情景分析，则中位数相当于从 1250 亿美元升至 1350 亿美元，即 **新增约 100 亿美元 capex**；这个报道口径仍应以 Meta 后续正式文件为准。([雅虎财经][18])

## 5.1 先拆分新增 100 亿美元 capex

假设 Meta 新增 capex 为 **ΔCapex = 100 亿美元**，可以先按以下比例拆：

| 支出桶                   |    假设占比 |        金额 | 潜在受益公司                                   |
| --------------------- | ------: | --------: | ---------------------------------------- |
| GPU/AI 加速器系统          | 45%–55% | 45–55 亿美元 | NVDA、AMD、AVGO、MRVL、TSM 间接受益              |
| HBM/DRAM/NAND/SSD/HDD | 12%–18% | 12–18 亿美元 | MU、SK Hynix、Samsung、SNDK、WDC、STX         |
| 网络、交换机、光模块            |  8%–12% |  8–12 亿美元 | ANET、AVGO、MRVL、NVDA networking、LITE、COHR |
| 服务器、机柜、ODM/OEM        |  8%–12% |  8–12 亿美元 | DELL、HPE、SMCI、Quanta、Wiwynn、Foxconn      |
| 电力、散热、UPS、液冷、建筑       | 15%–25% | 15–25 亿美元 | VRT、ETN、Schneider、Siemens                |
| 设备/代工/封装              |    间接受益 | 不直接等于当期收入 | TSM、ASML、AMAT、LRCX、KLAC                  |

这个拆分的重点是：**Meta 的 100 亿美元 capex 不会全部变成 NVIDIA 收入**。一部分是建筑、电力、土地、网络、存储、服务器集成；一部分订单可能已经在供应商 backlog 中；还有一部分会跨多个季度确认收入。

---

## 5.2 公司层面的计算公式

对任何供应商，都可以用同一个公式：

[
\Delta Revenue_i =
\Delta Capex \times CategoryShare \times VendorShare_i \times RevenueCapture_i \times TimingFactor
]

然后：

[
\Delta EBIT_i =
\Delta Revenue_i \times IncrementalMargin_i
]

[
\Delta NetIncome_i =
\Delta EBIT_i \times (1 - TaxRate)
]

最后估算股价影响：

[
\Delta MarketCap_i \approx \Delta NetIncome_i \times ForwardPE_i
]

[
StockImpact_i =
\frac{\Delta MarketCap_i}{CurrentMarketCap_i}
]

这里最关键的变量是：

* **CategoryShare**：新增 capex 有多少进入某个支出桶。
* **VendorShare**：这个桶里某家公司拿多少份额。
* **RevenueCapture**：整机 BOM 里多少会被这家公司确认为收入。
* **TimingFactor**：今年确认，还是未来 4–8 个季度确认。
* **IncrementalMargin**：增量收入能留下多少利润。
* **ForwardPE / CurrentMarketCap**：市场如何给新增利润定价。

---

## 5.3 NVIDIA 示例：新增 100 亿美元 Meta capex 的传导

假设：

* 新增 capex 中 50% 进入 AI 加速器系统；
* 其中 80% 使用 NVIDIA 生态；
* NVIDIA 在整机/系统 BOM 里的收入捕获率为 65%；
* 则 NVIDIA 增量收入约为：

[
100亿 \times 50% \times 80% \times 65%
= 26亿美元
]

NVIDIA 最新季度非 GAAP 毛利率约 75.2%，但增量净利润不能简单等于毛利，需要扣除 opex、税费和渠道因素。([NVIDIA Newsroom][2]) 假设增量税后利润率约 55%：

[
\Delta NetIncome_{NVDA}
\approx 26亿 \times 55%
= 14.3亿美元
]

股价影响用下面这个公式：

[
\Delta MarketCap
\approx 14.3亿美元 \times ForwardPE
]

如果市场按 30 倍 forward PE 给这部分新增利润定价：

[
\Delta MarketCap
\approx 429亿美元
]

如果 NVIDIA 当月市值为 X，则：

[
StockImpact
= 429亿 / X
]

例如，若 X 为 4 万亿美元，则理论股价影响约为 1.1%；若 X 为 5 万亿美元，则约为 0.9%。这只是单一客户、单一 capex 上调的情景，实际股价还取决于这笔订单是否已被市场预期、是否挤占其他客户供给、毛利率是否维持，以及全行业 capex 是否同步上调。

---

## 5.4 TSMC 示例：同一笔 capex 的间接受益

TSMC 不会直接拿到 Meta 的全部 capex，而是通过 NVIDIA/AMD/Broadcom/Marvell 的芯片订单间接受益。

假设：

* 新增 100 亿美元 capex 中 50% 是加速器系统；
* 芯片中可归因于先进制程/封装的部分占 15%；
* TSMC 相关份额为 85%；
* 则 TSMC 增量收入约为：

[
100亿 \times 50% \times 15% \times 85%
= 6.375亿美元
]

TSMC 一季度净利率约 50.5%，毛利率 66.2%。([台积电][19]) 若粗略按 50% 税后净利率估算：

[
\Delta NetIncome_{TSMC}
\approx 6.375亿 \times 50%
= 3.19亿美元
]

然后同样套用：

[
\Delta MarketCap
= \Delta NetIncome \times ForwardPE
]

这个估算通常比 NVIDIA 小，但 TSMC 的优势是：它不只受益于 Meta，而是受益于整个 AI 芯片生态的先进制程需求。

---

## 5.5 Vertiv / 电力散热示例：当瓶颈转向物理基础设施

如果新增 100 亿美元 capex 中 20% 用于电力、散热、UPS、液冷、数据中心物理基础设施：

[
100亿 \times 20%
= 20亿美元
]

假设 Vertiv 能拿到其中 10%–20%：

[
\Delta Revenue_{VRT}
= 2亿–4亿美元
]

Vertiv 这类公司的关键不只是单个客户订单，而是整个行业电力和散热 backlog 是否持续扩张。Vertiv 最新披露 backlog 达 150 亿美元、book-to-bill 2.9 倍，说明它是 AI capex 扩散到物理基础设施时的代表性受益者。([Vertiv][12])

---

## 5.6 对 Meta 自己的影响：不是收入立即增加，而是 FCF 和折旧压力

对 Meta 本身，新增 100 亿美元 capex 的影响分两步：

**第一步：当年自由现金流减少。**

[
\Delta FCF \approx -100亿美元
]

这会压制短期自由现金流估值。

**第二步：未来折旧增加。**

假设数据中心资产平均 5 年折旧：

[
Annual\ D&A
= 100亿 / 5
= 20亿美元/年
]

Meta 给出的 2026 年税率区间为 13%–16%。([Meta][17]) 若按 15% 税率估算，税后利润压力约为：

[
20亿 \times (1 - 15%)
= 17亿美元/年
]

所以 Meta 股价是否受益，要看 AI 投资能否带来至少超过这部分折旧和机会成本的广告效率、用户增长、模型能力或新收入。如果只是 capex 上升但 revenue/operating income 没有对应上修，市场通常会降低估值；如果 capex 上升同时广告收入、AI engagement、operating income guidance 都上修，才是正面组合。

---

# 6. 实际月度操作模板

每个月固定做 5 步：

**第一步：更新需求端。**
记录 MSFT、GOOGL、AMZN、META、ORCL、CRWV 的 capex、RPO、cloud revenue、cloud gross margin、FCF。若 capex 上调且云收入/RPO 同步加速，说明上游需求真实；若 capex 上调但云毛利和 FCF 恶化，说明买方承压。

**第二步：更新算力端。**
记录 NVDA Data Center、AMD Data Center、AVGO AI semiconductor、MRVL data center/custom silicon。若 NVIDIA 强、Broadcom/Marvell 也强，说明 GPU 与 ASIC 都在扩张；若 ASIC 强而 NVIDIA 毛利承压，说明 hyperscaler 自研路线开始影响利润池。

**第三步：更新供给瓶颈。**
看 TSMC 月度营收、先进制程占比、ASML EUV 订单、SEMI 设备数据、HBM/DRAM/NAND 价格。若 TSMC、HBM、ASML 同时强，说明瓶颈仍在上游。

**第四步：更新第二波基建。**
看 ANET、LITE、COHR、VRT、DELL、HPE、SMCI 的订单、backlog、毛利率。若这些公司订单强，说明 AI capex 从“买 GPU”扩散到“建完整数据中心”。

**第五步：用分数调仓。**
不要因为一家公司一句话调仓，而要看整条链是否同步变化：

| 情景                              | 组合动作                            |
| ------------------------------- | ------------------------------- |
| Capex 上调 + 云收入/RPO 上调 + 上游毛利稳定  | 加 L1/L2/L4，尤其 GPU、ASIC、代工、网络、电力 |
| Capex 上调 + 云毛利/FCF 恶化           | 减 L5 中 capex 压力大的公司，保留高议价供应商    |
| HBM/SSD 价格上行 + 存储公司毛利率改善        | 加 L3，但设止盈纪律                     |
| TSMC 月度营收放缓 + NVDA 指引弱 + 存储价格转跌 | 降低 L1/L2/L3，转向现金或高质量云           |
| 电力/散热 backlog 强，但 GPU 增速放缓      | 降 GPU 集中度，加 L4                  |
| AI 收入增长但 capex intensity 下降     | 加 L5，因为云厂商经营杠杆开始释放              |

---

## 最后，把这个框架压缩成一句话

**月度 review 时，不要问“AI 还火不火”，而要问：capex 谁在花、订单谁在拿、毛利谁守住、现金流谁受压、估值是否已经反映。**

用这个框架，Meta 扩大 capex 这类新闻就不会只是“利好 AI”四个字，而可以被拆成：NVIDIA/AMD/ASIC 可能拿多少收入，TSMC/HBM/网络/电力分别分到多少，供应商利润能增加多少，最后再用 EPS 修正和估值倍数推回股价影响。

[1]: https://news.microsoft.com/source/2026/04/29/microsoft-cloud-and-ai-strength-fuels-third-quarter-results/ "Microsoft Cloud and AI strength fuels third quarter results - Source"
[2]: https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026 "NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2026 | NVIDIA Newsroom"
[3]: https://investors.coreweave.com/overview/default.aspx "
	CoreWeave - Investor Relations
"
[4]: https://pr.tsmc.com/english/news/3294 "TSMC March 2026 Revenue Report"
[5]: https://www.semi.org/en/SEMI-Reports-Global-Semiconductor-Equipment-Billings-Reached-135-Billion-in-2025 "SEMI Reports Global Semiconductor Equipment Billings Reached $135 Billion in 2025, Up 15% Year-on-Year | SEMI"
[6]: https://ir.amd.com/news-events/press-releases/detail/1276/amd-reports-fourth-quarter-and-full-year-2025-financial-results "AMD Reports Fourth Quarter and Full Year 2025 Financial Results :: Advanced Micro Devices, Inc. (AMD)"
[7]: https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-fourth-quarter-and-fiscal-year-2025 "Broadcom Inc. Announces Fourth Quarter and Fiscal Year 2025 Financial Results and Quarterly Dividend | Broadcom Inc."
[8]: https://investor.marvell.com/news-events/press-releases/detail/1011/marvell-technology-inc-reports-fourth-quarter-and-fiscal-year-2026-financial-results "Marvell Technology, Inc. Reports Fourth Quarter and Fiscal Year 2026 Financial Results | Marvell Technology, Inc. (MRVL)"
[9]: https://investors.seagate.com/news/news-details/2026/Seagate-Technology-Reports-Fiscal-Third-Quarter-2026-Financial-Results/ "
	Seagate - Seagate Technology Reports Fiscal Third Quarter 2026 Financial Results
"
[10]: https://www.sandisk.com/en-ae/company/newsroom/press-releases/2025/sandisk-celebrates-nasdaq-listing-after-completing-separation "Sandisk Celebrates Nasdaq Listing After Completing Separation from Western Digital | Sandisk"
[11]: https://www.arista.com/en/company/news/press-release/23416-pr-20260212 "Arista Networks, Inc. Reports Fourth Quarter and Year End 2025 Financial Results  - Arista"
[12]: https://investors.vertiv.com/news/news-details/2026/Vertiv-Reports-Strong-Fourth-Quarter-with-Organic-Orders-Growth-of-252-and-Diluted-EPS-Growth-of-200-Adjusted-Diluted-EPS-37/default.aspx "
	Vertiv Holdings Co. - Vertiv Reports Strong Fourth Quarter with Organic Orders Growth of 252% and Diluted EPS Growth of 200% (Adjusted Diluted EPS +37%)
"
[13]: https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Second-Quarter-of-Fiscal-Year-2026-Financial-Results/default.aspx "
	Lumentum - Lumentum Announces Second Quarter of Fiscal Year 2026 Financial Results
"
[14]: https://s206.q4cdn.com/479360582/files/doc_financials/2026/q1/2026q1-alphabet-earnings-release.pdf "GOOG Exhibit 99.1 Q1 2026"
[15]: https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Fiscal-Year-2026-Third-Quarter-Financial-Results/default.aspx "
	Oracle - Oracle Announces Fiscal Year 2026 Third Quarter Financial Results
"
[16]: https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm?ref=wheresyoured.at "crwv-20251231"
[17]: https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Fourth-Quarter-and-Full-Year-2025-Results/default.aspx "
	Meta - Meta Reports Fourth Quarter and Full Year 2025 Results
"
[18]: https://finance.yahoo.com/sectors/technology/article/meta-stock-sinks-after-q1-earnings-as-company-raises-2026-ai-spending-forecast-to-125-billion-145-billion-160136308.html?utm_source=chatgpt.com "Meta stock sinks after Q1 earnings as company raises ..."
[19]: https://investor.tsmc.com/english/encrypt/files/encrypt_file/qr/phase4_reports/2026-04/bd8eb0403902fdea59a2f5e390e48d010b50edc9/1Q26%20EarningsRelease_WoG.pdf "1Q26 EarningsRelease_WoG"

