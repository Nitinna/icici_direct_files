import talib
import icici_login_and_data_download as ic
import pdb
import pandas as pd


df = ic.get_day_data(
    interval="1minute",
    start_date="2024-01-01T07:00:00.000Z",
    end_date="2024-11-29T15:00:00.000Z",
    stock_code="STABAN",
    exchange_code="NSE",
    product_type="cash"
)

pdb.set_trace()

# apply sma indicatior on data
df['SMA'] = talib.MA(df['close'], timeperiod=20, matype=0)
df = df.dropna(subset=['SMA'])


# Initialize variables
trading = False
trade_data = []  # Store completed trade details

for index, row in df.iterrows():
    current_time = row['datetime']
    sma = row['SMA']
    close = row['close']

    trade_start_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0)
    trade_end_time = current_time.replace(hour=15, minute=15, second=0, microsecond=0)

    # Trading window
    if trade_start_time <= current_time <= trade_end_time:
        # Buy Condition: Enter the trade if no position is open
        if close > sma and not trading:
            trade_details = {
                'entry_time': current_time,
                'entry_price': close
            }
            trading = True
            print(f"Buy at {close} on {current_time}")

        # Sell Condition: Exit the trade if a position is open
        elif close < sma and trading:
            trade_details.update({
                'exit_time': current_time,
                'exit_price': close,
                'pnl': close - trade_details['entry_price']
            })
            trade_data.append(trade_details)
            trading = False
            print(f"Sell at {close} on {current_time}")

    # Forced exit at the end of trading window
    if current_time >= trade_end_time and trading:
        trade_details.update({
            'exit_time': current_time,
            'exit_price': close,
            'pnl': close - trade_details['entry_price']
        })
        trade_data.append(trade_details)
        trading = False
        print(f"Forced sell at {close} on {current_time}")

# Convert to DataFrame
trade_df = pd.DataFrame(trade_data)
pdb.set_trace()
print(trade_df)