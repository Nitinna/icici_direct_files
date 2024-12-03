import talib
import icici_login_and_data_download as ic
import pandas as pd
import pandas_ta as ta
import datetime
import itertools
import pdb


# get data via icici api
df = ic.get_day_data(
    interval="30minute",
    start_date="2024-11-29T07:00:00.000Z",
    end_date="2024-12-02T15:00:00.000Z",
    stock_code="STABAN",
    exchange_code="NSE",
    product_type="cash"
)
pdb.set_trace()
# df = pd.read_csv('sbin.csv')

# Convert 'datetime' column to datetime objects
df['datetime'] = pd.to_datetime(df['datetime'])

# Function to run backtest for a given Supertrend period and multiplier
def run_backtest(period, multiplier):
    df_copy = df.copy()  # Make a copy of the original dataframe for each test
    df_copy.ta.supertrend(length=period, multiplier=multiplier, append=True)
    
    # Initialize variables for the backtest
    current_position = None
    trade_data = []
    trade_details = None
    
    for index, row in df_copy.iterrows():
        current_time = row['datetime']
        close = row['close']
        st_dir = row[f'SUPERTd_{period}_{multiplier}.0']

        trade_start_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
        trade_end_time = current_time.replace(hour=15, minute=15, second=0, microsecond=0)

        # Trading window
        if trade_start_time <= current_time <= trade_end_time:
            # Enter a long trade if Supertrend is 1 and no current position
            if st_dir == 1 and current_position is None:
                trade_details = {
                    'entry_time': current_time,
                    'entry_price': close,
                    'st_value_entry': st_dir,
                    'position': 'long'
                }
                current_position = 'long'
                print(f"Buy at {close} on {current_time}")

            # Enter a short trade if Supertrend is -1 and no current position
            elif st_dir == -1 and current_position is None:
                trade_details = {
                    'entry_time': current_time,
                    'entry_price': close,
                    'st_value_entry': st_dir,
                    'position': 'short'
                }
                current_position = 'short'
                print(f"Sell short at {close} on {current_time}")

            # Exit long trade when Supertrend turns -1
            elif st_dir == -1 and current_position == 'long':
                trade_details.update({
                    'exit_time': current_time,
                    'exit_price': close,
                    'st_value_exit': st_dir,
                    'pnl': close - trade_details['entry_price']
                })
                trade_data.append(trade_details)

                # Immediately enter the opposite position (new trade on the same candle)
                trade_details = {
                    'entry_time': current_time,
                    'entry_price': close,
                    'st_value_entry': st_dir,
                    'position': 'short'
                }
                current_position = 'short'
                print(f"Sell short at {close} on {current_time} (re-enter)")

            # Exit short trade when Supertrend turns 1
            elif st_dir == 1 and current_position == 'short':
                trade_details.update({
                    'exit_time': current_time,
                    'exit_price': close,
                    'st_value_exit': st_dir,
                    'pnl': trade_details['entry_price'] - close
                })
                trade_data.append(trade_details)

                # Immediately enter the opposite position (new trade on the same candle)
                trade_details = {
                    'entry_time': current_time,
                    'entry_price': close,
                    'st_value_entry': st_dir,
                    'position': 'long'
                }
                current_position = 'long'
                print(f"Buy at {close} on {current_time} (re-enter)")

        # Forced exit at the end of trading window
        if current_time >= trade_end_time and current_position is not None:
            trade_details.update({
                'exit_time': current_time,
                'exit_price': close,
                'st_value_exit': st_dir,
                'pnl': (close - trade_details['entry_price']) if current_position == 'long' else (trade_details['entry_price'] - close)
            })
            trade_data.append(trade_details)
            current_position = None
            print(f"Forced close at {close} on {current_time}")

    # Convert to DataFrame
    trade_df = pd.DataFrame(trade_data)
    return trade_df

# Define possible ranges for Supertrend parameters
period_range = range(5, 21)  # Period from 5 to 20
multiplier_range = [2, 3, 4, 5]  # Multiplier options

# Generate all combinations of period and multiplier
combinations = list(itertools.product(period_range, multiplier_range))

best_performance = None
best_params = None

# Loop through all parameter combinations
for period, multiplier in combinations:
    # print(f"Testing Supertrend with period={period} and multiplier={multiplier}...")
    
    # Run the backtest for this combination
    trade_df = run_backtest(period, multiplier)
    
    # Calculate performance metrics (for example, total profit)
    total_pnl = trade_df['pnl'].sum() if not trade_df.empty else 0
    print(f"Total Profit for period={period}, multiplier={multiplier}: {total_pnl}")

    # if period == 18:
        # pdb.set_trace()
    # Define the file path where you want to save the data
    csv_file_path = "trade_results.csv"

    # Create a new row to append
    new_row = {
        'period': period,
        'multiplier': multiplier,
        'pnl': total_pnl
    }

    # Check if the CSV file already exists to avoid overwriting headers
    try:
        # Try reading the CSV file to check if it exists
        trade_results_df = pd.read_csv(csv_file_path)
        # If file exists, append the new row without headers
        new_row_df = pd.DataFrame([new_row])
        new_row_df.to_csv(csv_file_path, mode='a', header=False, index=False)
    except FileNotFoundError:
        # If file doesn't exist, create a new file with headers
        trade_results_df = pd.DataFrame([new_row])
        trade_results_df.to_csv(csv_file_path, mode='w', header=True, index=False)

    # print(f"Updated CSV file with total PnL: {total_pnl}")
    
    # Compare with the best performance so far
    if best_performance is None or total_pnl > best_performance:
        best_performance = total_pnl
        best_params = (period, multiplier)

print(f"Best performing parameters: period={best_params[0]}, multiplier={best_params[1]} with total profit: {best_performance}")
