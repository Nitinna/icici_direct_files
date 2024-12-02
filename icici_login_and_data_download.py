import pandas as pd
from breeze_connect import BreezeConnect
from datetime import datetime, timedelta
import pdb

class TradingAPI:
    def __init__(self, api_key, api_secret, session_token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session_token = session_token
        self.breeze = None
        self._login()

    def _login(self):
        """Log in to the Breeze API."""
        try:
            self.breeze = BreezeConnect(api_key=self.api_key)
            self.breeze.generate_session(api_secret=self.api_secret,
                                         session_token=self.session_token)
            print("Login Successful")
        except Exception as e:
            print(f"Error in login: {e}")

    def get_historical_data(self, interval, from_date, to_date, stock_code, exchange_code, product_type):
        """Fetch historical data from Breeze API."""
        try:
            return self.breeze.get_historical_data_v2(
                interval=interval,
                from_date=from_date,
                to_date=to_date,
                stock_code=stock_code,
                exchange_code=exchange_code,
                product_type=product_type
            )
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None


def get_chunked_data(api, interval, start_date, end_date, stock_code, exchange_code, product_type):
    """Fetch data in chunks (1-day intervals) from start_date to end_date."""
    all_data = pd.DataFrame()

    start_dt = datetime.fromisoformat(start_date[:-1])  # Remove 'Z' and parse
    end_dt = datetime.fromisoformat(end_date[:-1])

    while start_dt < end_dt:
        # Calculate the next chunk's end date
        chunk_end_dt = min(start_dt + timedelta(days=1), end_dt)

        # Prepare date range for the chunk
        from_date = start_dt.isoformat() + ".000Z"
        to_date = chunk_end_dt.isoformat() + ".000Z"
        
        chunk_data = api.get_historical_data(
            interval=interval,
            from_date=from_date,
            to_date=to_date,
            stock_code=stock_code,
            exchange_code=exchange_code,
            product_type=product_type
        )

        if chunk_data:
            chunk_df = pd.DataFrame(chunk_data['Success'])
            all_data = pd.concat([all_data, chunk_df], ignore_index=True)
            print(start_date)

        start_dt = chunk_end_dt  # Move start date to the next day's start

    return all_data


def filter_and_format_data(all_data):
    """Filter data based on trading hours and format the dataframe."""
    all_data['datetime'] = pd.to_datetime(all_data['datetime'])
    all_data['time'] = all_data['datetime'].dt.strftime('%H:%M:%S')
    filtered_data = all_data.loc[(all_data['time'] >= '09:15:00') & (all_data['time'] <= '15:29:00')]
    filtered_data = filtered_data.drop(columns=['time'])

    return filtered_data[['datetime', 'stock_code', 'open', 'high', 'low', 'close']]


def get_day_data(interval, start_date, end_date, stock_code, exchange_code, product_type):
    """Fetch day data, chunked and filtered, for the given stock."""
    # Initialize the API
    api = TradingAPI(
        api_key="11624t3D88283O9_421622O70m411*33",
        api_secret="15772+0G7Pq%Zz790445AujU9T1x1356",
        session_token="49497503"
    )

    # Fetch data in chunks
    all_data = get_chunked_data(api, interval, start_date, end_date, stock_code, exchange_code, product_type)

    # Filter and format data
    filtered_data = filter_and_format_data(all_data)

    return filtered_data