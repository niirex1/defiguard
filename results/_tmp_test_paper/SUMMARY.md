# DeFiGuard paper artifacts

## Tables

### Table 2

| protocol_type                     |   protocols |   incidents |   median_contracts_per_attack |
|:----------------------------------|------------:|------------:|------------------------------:|
| AMMs / DEXes                      |          10 |          18 |                             4 |
| Lending / borrowing               |           8 |          16 |                             5 |
| Stablecoins                       |           4 |           7 |                             6 |
| Yield aggregators                 |           6 |          11 |                             5 |
| Liquid staking                    |           3 |           5 |                             4 |
| Other DeFi (derivatives, options) |           5 |           9 |                             5 |
| Total                             |          36 |          66 |                             5 |

### Table 4

| Method                    |   RCA |   ETD |   APC |   FPR |
|:--------------------------|------:|------:|------:|------:|
| David et al. [10]         |  0.4  |  0.09 |  0.42 |   4   |
| DeFiGuard (Full)          |  0.97 |  0.74 |  0.94 |   3.2 |
| DeFiGuard (protocol-only) |  0.63 |  0.36 |  0.67 |   3   |
| GPTScan [29]              |  0.41 |  0.11 |  0.44 |   3.9 |
| LLM-SmartAudit (BA) [33]  |  0.47 |  0.18 |  0.5  |   3.1 |
| LLM-SmartAudit (TA) [33]  |  0.51 |  0.21 |  0.53 |   3.3 |
| Mythril [23]              |  0.33 |  0.05 |  0.39 |   4.8 |
| Oyente [20]               |  0.21 |  0.01 |  0.28 |   5.3 |
| PropertyGPT [19]          |  0.45 |  0.15 |  0.47 |   3.4 |
| Securify [32]             |  0.29 |  0.03 |  0.34 |   4.1 |
| VeriSmart [28]            |  0.26 |  0.02 |  0.31 |   3.7 |

### Table 5

| Method                    |   Atomic |   Multi-block |
|:--------------------------|---------:|--------------:|
| DeFiGuard (full)          |     0.58 |          0.39 |
| DeFiGuard (protocol-only) |     0.51 |          0.33 |
| GPTScan [29]              |     0.29 |          0.1  |
| LLM-SmartAudit (TA) [33]  |     0.35 |          0.17 |
| Mythril [23]              |     0.18 |          0.04 |
| PropertyGPT [19]          |     0.32 |          0.13 |

### Table 6

| Method                   |   RCA |   ETD |
|:-------------------------|------:|------:|
| David et al. [10]        |  0.32 |  0.1  |
| DeFiGuard (Full)         |  0.95 |  0.55 |
| GPTScan [29]             |  0.3  |  0.08 |
| LLM-SmartAudit (TA) [33] |  0.37 |  0.14 |
| PropertyGPT [19]         |  0.34 |  0.11 |

### Table 7

| Method                   |   Latency_median_min |   Latency_95th_min |   Tokens_median_k |   Tokens_95th_k |
|:-------------------------|---------------------:|-------------------:|------------------:|----------------:|
| DeFiGuard (full)         |                   36 |                 59 |               240 |             390 |
| LLM-SmartAudit (TA) [33] |                   18 |                 37 |               180 |             310 |

### Table 8

| Variant           |   RCA |   ETD |
|:------------------|------:|------:|
| Single-agent      |  0.55 |  0.29 |
| No economic agent |  0.61 |  0.33 |
| DeFiGuard (full)  |  0.95 |  0.54 |

## Figures

- Figure 1 (left/right): fig1_left_detection_by_vector.png, fig1_right_apc_distribution.png
- Figure 5: fig5_rca_by_vector.png
- Figure 6: fig6_runtime_breakdown.png
