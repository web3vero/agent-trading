Here is the complete implementation of the backtest for your strategy using the provided instructions. The code includes all necessary imports, the strategy class, entry/exit logic, risk management, and parameter optimization. It also includes Moon Dev-themed debug prints for easier debugging.

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np

# Clean and prepare the data
DATA_PATH = "{DATA_DIR}/BTC-USD-15m.csv"
data = pd.read_csv(DATA_PATH)

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Ensure proper column mapping
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Drop rows with missing values
data = data.dropna()

# Strategy Class
class TrendMomentumStrategy(Strategy):
    # Parameters for optimization
    sma_short_period = 50
    sma_long_period = 200
    rsi_period = 14
    atr_period = 14
    atr_multiplier = 1.5
    risk_per_trade = 0.01  # 1% risk per trade
    max_drawdown = 0.05  # 5% max drawdown
    take_profit_multiplier = 2
    stop_loss_multiplier = 1
    trailing_stop_multiplier = 0.5

    def init(self):
        # Calculate indicators
        self.sma_short = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_short_period)
        self.sma_long = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_long_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)

        # Debug prints 🌙
        print("🌙 Moon Dev Strategy Initialized! ✨")
        print(f"SMA Short: {self.sma_short_period}, SMA Long: {self.sma_long_period}")
        print(f"RSI Period: {self.rsi_period}, ATR Period: {self.atr_period}")
        print(f"ATR Multiplier: {self.atr_multiplier}, Risk per Trade: {self.risk_per_trade * 100}% 🚀")

    def next(self):
        # Check if we have enough data
        if len(self.data.Close) < max(self.sma_long_period, self.rsi_period, self.atr_period):
            return

        # Calculate position size based on risk management
        atr_value = self.atr[-1]
        stop_loss_distance = atr_value * self.stop_loss_multiplier
        position_size = (self.equity * self.risk_per_trade) / stop_loss_distance
        position_size = min(position_size, self.equity * 0.2)  # Max 20% allocation

        # Long Entry Conditions
        if (self.sma_short[-1] > self.sma_long[-1] and  # Uptrend
            self.rsi[-1] > 50 and self.rsi[-1] < 70 and  # Bullish momentum
            self.data.Close[-1] > self.sma_short[-1] and  # Price above SMA
            atr_value > self.atr_multiplier * np.mean(self.atr[-self.atr_period:])):  # Volatility filter

            # Calculate take profit and stop loss
            take_profit = self.data.Close[-1] + atr_value * self.take_profit_multiplier
            stop_loss = self.data.Close[-1] - atr_value * self.stop_loss_multiplier

            # Enter long position
            self.buy(size=position_size, sl=stop_loss, tp=take_profit)
            print(f"🌙 Long Entry Signal! ✨ Price: {self.data.Close[-1]}, TP: {take_profit}, SL: {stop_loss} 🚀")

        # Short Entry Conditions
        elif (self.sma_short[-1] < self.sma_long[-1] and  # Downtrend
              self.rsi[-1] < 50 and self.rsi[-1] > 30 and  # Bearish momentum
              self.data.Close[-1] < self.sma_short[-1] and  # Price below SMA
              atr_value > self.atr_multiplier * np.mean(self.atr[-self.atr_period:])):  # Volatility filter

            # Calculate take profit and stop loss
            take_profit = self.data.Close[-1] - atr_value * self.take_profit_multiplier
            stop_loss = self.data.Close[-1] + atr_value * self.stop_loss_multiplier

            # Enter short position
            self.sell(size=position_size, sl=stop_loss, tp=take_profit)
            print(f"🌙 Short Entry Signal! ✨ Price: {self.data.Close[-1]}, TP: {take_profit}, SL: {stop_loss} 🚀")

        # Trailing Stop Logic
        for trade in self.trades:
            if trade.is_long:
                trailing_stop = self.data.Close[-1] - atr_value * self.trailing_stop_multiplier
                trade.sl = max(trade.sl, trailing_stop)
            elif trade.is_short:
                trailing_stop = self.data.Close[-1] + atr_value * self.trailing_stop_multiplier
                trade.sl = min(trade.sl, trailing_stop)

        # Max Drawdown Check
        if self.equity < self.initial_equity * (1 - self.max_drawdown):
            print("🌙 Max Drawdown Reached! Stopping Trading for the Day. 🌙")
            self.position.close()

# Backtest Execution
bt = Backtest(data, TrendMomentumStrategy, cash=1_000_000, commission=0.001)

# Initial Backtest
stats = bt.run()
print(stats)
print(stats._strategy)
bt.plot()

# Parameter Optimization
optimization_params = {
    'sma_short_period': range(40, 60, 5),
    'sma_long_period': range(190, 210, 5),
    'rsi_period': range(12, 16, 1),
    'atr_period': range(12, 16, 1),
    'atr_multiplier': [1.4, 1.5, 1.6],
    'take_profit_multiplier': [1.8, 2.0, 2.2],
    'stop_loss_multiplier': [0.8, 1.0, 1.2],
    'trailing_stop_multiplier': [0.4, 0.5, 0.6]
}

optimized_stats = bt.optimize(**optimization_params, maximize='Return [%]')
print(optimized_stats)
bt.plot()
```

### Key Features:
1. **Indicators**: Uses TA-Lib for SMA, RSI, and ATR calculations.
2. **Entry/Exit Logic**: Implements long and short entry rules with take profit, stop loss, and trailing stop.
3. **Risk Management**: Calculates position size based on 1% risk per trade and enforces a 5% max drawdown.
4. **Parameter Optimization**: Optimizes key parameters using ranges for better performance.
5. **Moon Dev Debug Prints**: Includes themed debug prints for easier tracking of signals and strategy behavior.

### Execution Order:
1. Runs an initial backtest with default parameters.
2. Prints full stats and strategy details.
3. Shows the initial performance plot.
4. Runs parameter optimization.
5. Shows optimized results and final plot.

Let me know if you need further adjustments! 🌙✨🚀