import random
import time

class MarketMaker:
    def __init__(self, initial_cash=10000, inventory=0, spread=0.1):
        self.cash = initial_cash       # Initial cash available for orders
        self.inventory = inventory     # Stock inventory held by market maker
        self.spread = spread           # Bid-ask spread (percentage)
        self.price = 100               # Starting price of the asset
        self.order_size = 10           # Number of stocks per order
    
    def get_bid_ask_prices(self):
        # Bid aur Ask prices calculate karte hain
        bid_price = self.price * (1 - self.spread / 2)
        ask_price = self.price * (1 + self.spread / 2)
        return round(bid_price, 2), round(ask_price, 2)
    
    def place_orders(self):
        bid_price, ask_price = self.get_bid_ask_prices()
        
        # Market maker apne buy aur sell orders place karta hai
        print(f"Placing order to buy {self.order_size} stocks at {bid_price} (Total: {bid_price * self.order_size})")
        print(f"Placing order to sell {self.order_size} stocks at {ask_price} (Total: {ask_price * self.order_size})")
        
        # Orders execute karte hain agar market price bid ya ask price ko hit kare
        self.execute_orders(bid_price, ask_price)
    
    def execute_orders(self, bid_price, ask_price):
        # Market price ko random fluctuation ke saath simulate karte hain
        market_price = random.uniform(bid_price - 5, ask_price + 5)  # Simulate market price
        print(f"Market price: {round(market_price, 2)}")
        
        # Agar market price bid price ke paas aata hai, toh buy karte hain
        if market_price <= bid_price:
            if self.cash >= bid_price * self.order_size:
                self.inventory += self.order_size
                self.cash -= bid_price * self.order_size
                print(f"Bought {self.order_size} stocks at {round(bid_price, 2)}. Cash remaining: {self.cash}, Inventory: {self.inventory}")
        
        # Agar market price ask price ko touch karta hai, toh sell karte hain
        elif market_price >= ask_price:
            if self.inventory >= self.order_size:
                self.inventory -= self.order_size
                self.cash += ask_price * self.order_size
                print(f"Sold {self.order_size} stocks at {round(ask_price, 2)}. Cash now: {self.cash}, Inventory: {self.inventory}")
        
    def update_market_price(self):
        # Market price ko randomly update karte hain
        self.price += random.uniform(-0.5, 0.5)
        self.price = round(self.price, 2)

def run_market_maker():
    mm = MarketMaker(initial_cash=10000, inventory=0, spread=0.1)
    
    for _ in range(100):  # 20 rounds ke liye simulation chalayenge
        print(f"\n--- Round {_ + 1} ---")
        mm.place_orders()  # Buy/sell orders place karte hain based on current market price
        mm.update_market_price()  # Market price ko update karte hain
        # time.sleep(.1)  # Simulate karte hain delay

if __name__ == "__main__":
    run_market_maker()
