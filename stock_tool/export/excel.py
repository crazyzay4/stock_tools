import pandas as pd
from datetime import datetime


def export_to_excel(data):
    df = pd.DataFrame(
        data,
        columns=["Ticker", "Price", "Change %", "Dividend %", "Score"]
    )

    filename = f"stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)
