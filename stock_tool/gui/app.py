import tkinter as tk
from tkinter import ttk, messagebox

from gui.config import (
    WINDOW_TITLE,
    WINDOW_SIZE,
    DEFAULT_TICKERS,
    PERIODS
)

from data.yahoo import fetch_stock_data
from analysis.recommender import recommend
from export.excel import export_to_excel
from gui.portfolio_window import PortfolioWindow
from gui.news_window import NewsWindow
from portfolio.model import Portfolio


class StockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.data = []
        self.portfolio = Portfolio()

        self._build_controls()
        self._build_table()
        self._build_buttons()
        self._build_status()

    def run(self):
        self.root.mainloop()

    # ---------- UI BUILD ----------

    def _build_controls(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Tickers:").pack(side="left")
        self.ticker_entry = ttk.Entry(frame, width=45)
        self.ticker_entry.pack(side="left", padx=5)
        self.ticker_entry.insert(0, ", ".join(DEFAULT_TICKERS))

        ttk.Label(frame, text="Period:").pack(side="left", padx=(10, 0))
        self.period_var = tk.StringVar(value=list(PERIODS.values())[2])

        self.period_box = ttk.Combobox(
            frame,
            textvariable=self.period_var,
            values=list(PERIODS.values()),
            state="readonly",
            width=8
        )
        self.period_box.pack(side="left", padx=5)

        ttk.Button(
            frame,
            text="Load Data",
            command=self.load_data
        ).pack(side="right")

    def _build_table(self):
        columns = (
            "Ticker",
            "Price",
            "Change %",
            "RSI",
            "Score",
            "Recommendation"
        )

        self.table = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        # --- row colors ---
        self.table.tag_configure("STRONG BUY", background="#d4f8d4")
        self.table.tag_configure("WATCH", background="#fff4cc")
        self.table.tag_configure("AVOID", background="#ffd6d6")

        self.table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

    def _build_buttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            frame,
            text="Show News",
            command=self.show_news
        ).pack(side="left")

        ttk.Button(
            frame,
            text="Add to Portfolio",
            command=self.add_to_portfolio
        ).pack(side="left", padx=(10, 0))

        ttk.Button(
            frame,
            text="Open Portfolio",
            command=self.open_portfolio
        ).pack(side="left", padx=(10, 0))

        ttk.Button(
            frame,
            text="Export to Excel",
            command=self.export_excel
        ).pack(side="right")

    def _build_status(self):
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w"
        ).pack(fill="x", side="bottom")

    # ---------- ACTIONS ----------

    def load_data(self):
        raw = self.ticker_entry.get()

        tickers = [
            t.strip().upper()
            for t in raw.split(",")
            if t.strip()
        ]

        if not tickers:
            messagebox.showwarning(
                "Input error",
                "Please enter at least one ticker."
            )
            return

        self.status_var.set("Loading data...")
        self.root.update_idletasks()

        period = self.period_var.get()
        stocks = fetch_stock_data(tickers, period)

        self.table.delete(*self.table.get_children())
        self.data.clear()

        for stock in stocks:
            score, recommendation = recommend(stock)

            row = (
                stock["ticker"],
                round(stock["price"], 2),
                round(stock["change"], 2),
                round(stock["rsi"], 1),
                score,
                recommendation
            )

            self.table.insert(
                "",
                "end",
                values=row,
                tags=(recommendation,)
            )

            self.data.append(row)

        self.status_var.set("Ready")

    def add_to_portfolio(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning(
                "Portfolio",
                "Select a stock first."
            )
            return

        values = self.table.item(selected, "values")
        ticker = values[0]
        price = float(values[1])

        self.portfolio.add(
            ticker=ticker,
            shares=1,
            price=price
        )

        messagebox.showinfo(
            "Portfolio",
            f"{ticker} added to portfolio (1 share)"
        )

    def open_portfolio(self):
        PortfolioWindow(self.root, self.portfolio)

    def show_news(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning(
                "News",
                "Select a stock first."
            )
            return

        ticker = self.table.item(selected, "values")[0]
        NewsWindow(self.root, ticker)

    def export_excel(self):
        if not self.data:
            messagebox.showinfo(
                "Export",
                "No data to export."
            )
            return

        export_to_excel(self.data)

        messagebox.showinfo(
            "Export",
            "Data exported successfully."
        )
