from portfolio.storage import load_portfolio, save_portfolio


class Portfolio:
    def __init__(self):
        self.data = load_portfolio()

    def add(
        self,
        ticker: str,
        shares: int,
        price: float,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 15.0,
    ):
        ticker = ticker.upper()

        if ticker not in self.data:
            self.data[ticker] = {
                "shares": shares,
                "avg_price": price,
                "stop_loss_pct": stop_loss_pct,
                "take_profit_pct": take_profit_pct,
            }
        else:
            old = self.data[ticker]
            total_cost = (
                old["shares"] * old["avg_price"]
                + shares * price
            )
            total_shares = old["shares"] + shares

            old["shares"] = total_shares
            old["avg_price"] = total_cost / total_shares

        save_portfolio(self.data)

    def remove(self, ticker: str):
        ticker = ticker.upper()
        if ticker in self.data:
            del self.data[ticker]
            save_portfolio(self.data)

    def get(self, ticker: str):
        return self.data.get(ticker.upper())

    def all(self):
        return self.data
