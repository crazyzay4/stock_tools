import yfinance as yf

POSITIVE_WORDS = [
    "growth", "profit", "beats", "record",
    "strong", "upgrade", "surge", "gain"
]

NEGATIVE_WORDS = [
    "loss", "miss", "drop", "weak",
    "downgrade", "fall", "decline", "lawsuit"
]


def analyze_sentiment(text: str) -> int:
    text = text.lower()
    score = 0

    for w in POSITIVE_WORDS:
        if w in text:
            score += 1

    for w in NEGATIVE_WORDS:
        if w in text:
            score -= 1

    return score


def get_news_with_sentiment(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news or []
    except Exception:
        return []

    results = []

    for item in news[:5]:
        title = item.get("title", "")
        if not title:
            continue

        sentiment = analyze_sentiment(title)

        results.append({
            "title": title,
            "publisher": item.get("publisher", ""),
            "sentiment": sentiment
        })

    return results
