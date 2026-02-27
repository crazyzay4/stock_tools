from analysis.news import get_news_with_sentiment


def recommend(stock: dict):
    """
    Market recommendation (NOT portfolio action)

    Returns:
        score (0–100),
        recommendation: STRONG BUY / WATCH / AVOID
    """

    score = 50

    # ---- Price momentum ----
    change = stock.get("change", 0)
    score += max(min(change, 10), -10)

    # ---- RSI ----
    rsi = stock.get("rsi", 50)
    if rsi < 30:
        score += 12
    elif rsi > 70:
        score -= 12

    # ---- News sentiment (soft influence) ----
    news = get_news_with_sentiment(stock["ticker"])
    if news:
        avg_sentiment = sum(n["sentiment"] for n in news) / len(news)
        score += avg_sentiment * 4

    # ---- Clamp ----
    score = int(max(0, min(100, score)))

    # ---- Market recommendation ----
    if score >= 70:
        recommendation = "STRONG BUY"
    elif score >= 45:
        recommendation = "WATCH"
    else:
        recommendation = "AVOID"

    return score, recommendation
