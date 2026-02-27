import tkinter as tk
from tkinter import ttk
from analysis.news import get_news_with_sentiment


class NewsWindow:
    def __init__(self, parent, ticker):
        self.ticker = ticker

        self.window = tk.Toplevel(parent)
        self.window.title(f"News — {ticker}")
        self.window.geometry("900x400")

        self._build_table()
        self.load_news()

    def _build_table(self):
        columns = ("Sentiment", "Title", "Source")

        self.table = ttk.Treeview(
            self.window,
            columns=columns,
            show="headings"
        )

        self.table.heading("Sentiment", text="Sentiment")
        self.table.heading("Title", text="Title")
        self.table.heading("Source", text="Source")

        self.table.column("Sentiment", width=80, anchor="center")
        self.table.column("Title", width=650, anchor="w")
        self.table.column("Source", width=150, anchor="center")

        self.table.tag_configure("pos", foreground="green")
        self.table.tag_configure("neg", foreground="red")
        self.table.tag_configure("neu", foreground="gray")

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

    def load_news(self):
        self.table.delete(*self.table.get_children())

        news = get_news_with_sentiment(self.ticker)

        if not news:
            self.table.insert(
                "",
                "end",
                values=("0", "No news available", ""),
                tags=("neu",)
            )
            return

        for item in news:
            sentiment = item["sentiment"]

            if sentiment > 0:
                tag = "pos"
            elif sentiment < 0:
                tag = "neg"
            else:
                tag = "neu"

            self.table.insert(
                "",
                "end",
                values=(
                    sentiment,
                    item["title"],
                    item["publisher"]
                ),
                tags=(tag,)
            )
