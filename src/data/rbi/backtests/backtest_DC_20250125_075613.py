Below is the implementation of the backtest for the described strategy. The code includes all the necessary components, such as imports, strategy class, entry/exit logic, risk management, and parameter optimization. It also includes Moon Dev-themed debug prints for better visualization and debugging.

---

### Backtest Implementation

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder
from backtesting.test import SMA, RSI, ATR

# Data Preparation
DATA_PATH = "{DATA_DIR}/BTC-USD-15m.csv"

# Clean and preprocess data
data = pd.read_csv(DATA_PATH)
data.columns = data.columns.str.strip().str.lower()  # Clean column names
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])  # Drop unnamed columns

# Map columns to required format
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Ensure proper datetime format
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Strategy Class
class MoonDevTrendMomentumStrategy(Strategy):
    # Parameters
    ema_period = 200  # 200-period EMA for trend
    rsi_period = 14  # 14-period RSI for momentum
    atr_period = 14  # 14-period ATR for stop loss and take profit
    volume_period = 20  # 20-period average volume
    risk_per_trade = 0.01  # Risk 1% of capital per trade
    max_daily_loss = 0.03  # Stop trading after 3% daily loss
    max_daily_trades = 5  # Maximum 5 trades per day
    take_profit_multiplier = 1.5  # Take profit at 1.5x ATR
    stop_loss_multiplier = 1.0  # Stop loss at 1x ATR
    trailing_stop_multiplier = 0.5  # Trailing stop at 0.5x ATR
    time_exit_hours = 4  # Exit trade after 4 hours if no target hit

    def init(self):
        # Calculate indicators
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.avg_volume = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_period)

        # Track daily metrics
        self.daily_trades = 0
        self.daily_pnl = 0

    def next(self):
        # Reset daily metrics at the start of a new day
        if self.data.index[-1].hour == 0 and self.data.index[-1].minute == 0:
            self.daily_trades = 0
            self.daily_pnl = 0

        # Check for maximum daily loss
        if self.daily_pnl <= -self.max_daily_loss * self.equity:
            print("🌙✨ Moon Dev Alert: Daily loss limit reached! Stopping trading for the day. 🌙✨")
            return

        # Check for maximum daily trades
        if self.daily_trades >= self.max_daily_trades:
            print("🌙✨ Moon Dev Alert: Maximum daily trades reached! Stopping trading for the day. 🌙✨")
            return

        # Entry Logic
        if not self.position:
            # Long Entry Conditions
            if (self.data.Close[-1] > self.ema[-1] and  # Price above 200 EMA
                self.rsi[-1] > 50 and self.rsi[-2] < self.rsi[-1] and  # RSI above 50 and rising
                self.data.Volume[-1] > self.avg_volume[-1] and  # Volume above average
                self.data.Close[-1] > self.data.Open[-1] and  # Bullish engulfing pattern
                self.data.Close[-2] < self.data.Open[-2]):
                print("🌙✨ Moon Dev Signal: Long Entry! 🚀")
                self.entry_price = self.data.Close[-1]
                self.stop_loss = self.entry_price - self.atr[-1] * self.stop_loss_multiplier
                self.take_profit = self.entry_price + self.atr[-1] * self.take_profit_multiplier
                self.buy(size=self.calculate_position_size(self.stop_loss))
                self.daily_trades += 1

            # Short Entry Conditions
            elif (self.data.Close[-1] < self.ema[-1] and  # Price below 200 EMA
                  self.rsi[-1] < 50 and self.rsi[-2] > self.rsi[-1] and  # RSI below 50 and falling
                  self.data.Volume[-1] > self.avg_volume[-1] and  # Volume above average
                  self.data.Close[-1] < self.data.Open[-1] and  # Bearish engulfing pattern
                  self.data.Close[-2] > self.data.Open[-2]):
                print("🌙✨ Moon Dev Signal: Short Entry! 🚀")
                self.entry_price = self.data.Close[-1]
                self.stop_loss = self.entry_price + self.atr[-1] * self.stop_loss_multiplier
                self.take_profit = self.entry_price - self.atr[-1] * self.take_profit_multiplier
                self.sell(size=self.calculate_position_size(self.stop_loss))
                self.daily_trades += 1

        # Exit Logic
        if self.position:
            # Take Profit or Stop Loss
            if (self.position.is_long and (self.data.Close[-1] >= self.take_profit or self.data.Close[-1] <= self.stop_loss)) or \
               (self.position.is_short and (self.data.Close[-1] <= self.take_profit or self.data.Close[-1] >= self.stop_loss)):
                print("🌙✨ Moon Dev Signal: Exit Trade! 🌙")
                self.position.close()
                self.daily_pnl += self.position.pl

            # Trailing Stop
            if self.position.is_long:
                self.stop_loss = max(self.stop_loss, self.data.Close[-1] - self.atr[-1] * self.trailing_stop_multiplier)
            elif self.position.is_short:
                self.stop_loss = min(self.stop_loss, self.data.Close[-1] + self.atr[-1] * self.trailing_stop_multiplier)

            # Time-Based Exit
            if len(self.data) - self.position.entry_bar >= self.time_exit_hours * 4:  # 4 hours in 15-minute bars
                print("🌙✨ Moon Dev Signal: Time-Based Exit! 🌙")
                self.position.close()
                self.daily_pnl += self.position.pl

    def calculate_position_size(self, stop_loss):
        risk_amount = self.equity * self.risk_per_trade
        distance = abs(self.data.Close[-1] - stop_loss)
        return risk_amount / distance

# Backtest Execution
bt = Backtest(data, MoonDevTrendMomentumStrategy, cash=10000, commission=0.001, slippage=0.001)

# Initial Backtest
stats = bt.run()
print(stats)
print(stats._strategy)
bt.plot()

# Parameter Optimization
optimization_results = bt.optimize(
    ema_period=range(180, 220, 10),
    rsi_period=range(10, 20, 2),
    atr_period=range(10, 20, 2),
    take_profit_multiplier=[1.2, 1.5, 1.8],
    stop_loss_multiplier=[0.8, 1.0, 1.2],
    maximize='Return [%]'
)

print(optimization_results)
bt.plot()
```

---

### Explanation of Key Components

1. **Data Preparation**:
   - The data is cleaned and preprocessed to match the required format for backtesting.
   - Columns are renamed and formatted to ensure compatibility with the `backtesting` library.

2. **Strategy Class**:
   - The `MoonDevTrendMomentumStrategy` class implements the strategy logic.
   - Indicators (EMA, RSI, ATR, and Volume) are calculated using `talib` functions wrapped in `self.I()`.
   - Entry and exit rules are implemented in the `next()` method.

3. **Risk Management**:
   - Position sizing is calculated based on the risk percentage and stop loss distance.
   - Daily loss limits and maximum daily trades are enforced.

4. **Backtest Execution**:
   - The initial backtest is run with default parameters.
   - Optimization is performed on key parameters to maximize returns.

5. **Moon Dev-Themed Debug Prints**:
   - Debug prints are added to provide clear signals and alerts during backtesting.

---

### Next Steps
1. Run the initial backtest to evaluate the strategy's performance.
2. Optimize the parameters to improve results.
3. Analyze the performance metrics (win rate, average profit/loss, drawdowns) to refine the strategy further.

Let me know if you need further assistance! 🌙✨🚀