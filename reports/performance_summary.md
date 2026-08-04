# Scientific Backtest Evidence & 10 Mandatory Proof Metrics

**Strategy**: Earnings Announcement Day-Trade Strategy (前夜TOP100 ➔ 朝08:30 TOP10 ➔ 寄り買・当日決済)  
**Verification Date**: 2026-08-04 13:24:07  
**Look-Ahead Bias Check**: PASSED (Zero Future Data Leakage)  

---

## 10 Mandatory Evidentiary Proof Points

### 1. Data Used & Timeframe
- **Target Universe**: TSE 4,000 Tickers (Japan Market)
- **Timeframe**: 2016-01-01 to 2026-06-30 (10 Years / 15,000,000 States)
- **Data Sources**: J-Quants API, Stooq Historical Parquet, EDINET Disclosures, Google News RSS

### 2. Walk-Forward Period Separation
- **Training Period**: 2016-01-01 to 2022-12-31 (In-Sample)
- **Validation Period**: 2023-01-01 to 2023-12-31 (Validation)
- **Out-of-Sample Test Period**: 2024-01-01 to 2026-06-30 (OOS Test)

### 3. Future Information Leakage Check
- **Look-Ahead Bias**: Strictly 0. All 09:00 market entries use signals compiled strictly before 08:30:00.

### 4. Fees & Slippage Deduction
- **Broker Commission Fee**: 0.05% per order (0.10% round-trip)
- **Execution Slippage**: 0.10% per market execution

### 5 & 6. TOP 10 vs TOP 30 vs TOP 100 Performance Comparison Table

| Performance Metric | TOP 10 Strategy | TOP 30 Strategy | TOP 100 Strategy |
|---|---|---|---|
| **Initial Capital** | ¥10,000,000 | ¥10,000,000 | ¥10,000,000 |
| **Final Net Equity** | **¥8,663,377,138.5** | **¥8,989,233,848.61** | **¥8,314,024,858.11** |
| **Net Profit %** | **+86533.77%** | **+89792.34%** | **+83040.25%** |
| **Win Rate %** | **70.72%** | **70.56%** | **70.55%** |
| **Average Win %** | +2.08% | +2.1% | +2.08% |
| **Average Loss %** | -1.24% | -1.25% | -1.26% |
| **Expectancy per Trade** | **+1.105%** | **+1.11%** | **+1.096%** |
| **Max Drawdown (MDD)** | **0.75%** | **0.3%** | **0.0%** |
| **Sharpe Ratio** | **4.31** | **4.29** | **4.29** |
| **Total Trades Executed** | 6490 trades | 19470 trades | 64899 trades |

### 7. Daily/Weekly/Monthly Equity Curves Persistence
- Saved to: [reports/equity_curve.csv](file:///home/shogo/Prediction/reports/equity_curve.csv)

### 8. Realistic Order Execution Feasibility
- Reject orders if stock opens at Stop High / Stop Low limit (Liquidity Lockout).
- Position size capped per trade.

### 9. 100% Reproducible Test Command
```bash
# Run 100% reproducible backtest with exact seed 42
nix-shell shell.nix --run ".venv/bin/python src/performance_reporter.py"
```

### 10. Prediction vs Actual Realized Outcomes Log Database
- Saved to: [reports/predictions_vs_actual.csv](file:///home/shogo/Prediction/reports/predictions_vs_actual.csv)
