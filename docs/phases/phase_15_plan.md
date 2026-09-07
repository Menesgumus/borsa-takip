# Phase 15: Backtest Engine

**Goal**: Scientifically test the performance of signals and decisions on historical data, rigorously avoiding look-ahead bias and simulating realistic costs.

## Tasks
1. **T01 - Data Models**
   - BacktestJob, BacktestResult, BacktestTrade.

2. **T02 - Execution Engine**
   - Implement ackend/app/services/backtest.py.
   - Event-safe data access (ensuring signal generation at time T only accesses data available at time T-1 or strictly prior).
   - Incorporate slippage and commission costs.

3. **T03 - Strict Bias Audit Rules**
   - Look-ahead audit: No future price accessed.
   - Publication timestamp audit: Only use fundamental/KAP data AFTER public release time.
   - Corporate action audit: Dividend and split adjustments correctly mapped.

4. **T04 - Metrics & UI**
   - Calculate CAGR, Max Drawdown, Sharpe/Sortino ratios.
   - Implement /backtests UI displaying the equity curve and benchmark comparison.
