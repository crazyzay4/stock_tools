import yfinance as yf


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def fetch_stock_data(tickers, period="1mo"):
    results = []

    # --- unified fix for short periods ---
    if period in ("1d", "5d", "1mo"):
        calc_period = "3mo"
    else:
        calc_period = period

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        hist_calc = stock.history(period=calc_period)
        hist_view = stock.history(period=period)

        if hist_calc.empty or hist_view.empty:
            continue

        close_calc = hist_calc["Close"]
        close_view = hist_view["Close"]

        # --- indicators (from calc_period) ---
        if len(close_calc) < 50:
            continue

        price = close_view.iloc[-1]
        prev = close_view.iloc[0]
        change = ((price - prev) / prev) * 100

        sma20 = close_calc.rolling(20).mean().iloc[-1]
        sma50 = close_calc.rolling(50).mean().iloc[-1]
        rsi = calculate_rsi(close_calc).iloc[-1]

        info = stock.info
        dividend = (info.get("dividendYield") or 0) * 100

        results.append({
            "ticker": ticker,
            "price": float(price),
            "change": float(change),
            "dividend": float(dividend),
            "sma20": float(sma20),
            "sma50": float(sma50),
            "rsi": float(rsi)
        })

    return results
