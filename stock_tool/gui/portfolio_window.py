import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf


class PortfolioWindow:
    def __init__(self, parent, portfolio):
        self.portfolio = portfolio

        self.window = tk.Toplevel(parent)
        self.window.title("My Portfolio")
        self.window.geometry("980x520")

        self._build_controls()
        self._build_table()
        self._build_summary()
        self.refresh()

    # ---------- CONTROLS ----------

    def _build_controls(self):
        frame = ttk.Frame(self.window)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            frame,
            text="Refresh",
            command=self.refresh
        ).pack(side="left")

        ttk.Button(
            frame,
            text="Remove selected",
            command=self.remove_selected
        ).pack(side="right")

    # ---------- TABLE ----------

    def _build_table(self):
        columns = (
            "Ticker",
            "Shares",
            "Avg Price",
            "Current Price",
            "Total Value",
            "Total P/L ($)",
            "P/L %",
            "Action"
        )

        self.table = ttk.Treeview(
            self.window,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=115)

        self.table.pack(fill="both", expand=True, padx=10, pady=5)

        self.table.tag_configure("profit", foreground="green")
        self.table.tag_configure("loss", foreground="red")

    # ---------- SUMMARY ----------

    def _build_summary(self):
        frame = ttk.Frame(self.window)
        frame.pack(fill="x", padx=10, pady=5)

        self.summary_var = tk.StringVar(value="Total value: 0 | Total P/L: 0 (0%)")

        ttk.Label(
            frame,
            textvariable=self.summary_var,
            anchor="w",
            font=("Segoe UI", 10, "bold")
        ).pack(fill="x")

    # ---------- LOGIC ----------

    def refresh(self):
        self.table.delete(*self.table.get_children())

        total_value = 0.0
        total_invested = 0.0

        for ticker, pos in self.portfolio.all().items():
            shares = pos["shares"]
            avg_price = pos["avg_price"]

            try:
                hist = yf.Ticker(ticker).history(period="1d")
                if hist.empty:
                    continue

                current_price = hist["Close"].iloc[-1]

                invested = shares * avg_price
                value = shares * current_price
                pl_value = value - invested
                pl_percent = (pl_value / invested) * 100 if invested else 0

                total_value += value
                total_invested += invested

                action = self._portfolio_action(
                    avg_price,
                    current_price,
                    pos.get("stop_loss_pct", 5),
                    pos.get("take_profit_pct", 15)
                )

                tag = "profit" if pl_value >= 0 else "loss"

                self.table.insert(
                    "",
                    "end",
                    values=(
                        ticker,
                        shares,
                        round(avg_price, 2),
                        round(current_price, 2),
                        round(value, 2),
                        round(pl_value, 2),
                        f"{pl_percent:.2f}%",
                        action
                    ),
                    tags=(tag,)
                )

            except Exception as e:
                print(f"Error loading {ticker}: {e}")

        self._update_summary(total_value, total_invested)

    def _update_summary(self, value, invested):
        pl = value - invested
        pl_pct = (pl / invested) * 100 if invested else 0

        self.summary_var.set(
            f"Total value: {value:.2f} | "
            f"Total P/L: {pl:.2f} ({pl_pct:.2f}%)"
        )

    def _portfolio_action(self, avg, current, sl, tp):
        if current <= avg * (1 - sl / 100):
            return "SELL (Stop-Loss)"
        if current >= avg * (1 + tp / 100):
            return "SELL (Take-Profit)"
        return "HOLD"

    def remove_selected(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Remove",
                "Please select a stock to remove."
            )
            return

        item = selected[0]
        ticker = self.table.item(item, "values")[0]

        if not messagebox.askyesno(
            "Confirm removal",
            f"Remove {ticker} from portfolio?"
        ):
            return

        self.portfolio.remove(ticker)
        self.refresh()
