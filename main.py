# region imports
from AlgorithmImports import *
import math
import pandas as pd
# endregion

class MomentumLowVolComposite(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2012, 1, 1)
        self.set_end_date(2025, 12, 31)
        self.set_cash(100000)

        self.spy = self.add_equity("SPY", Resolution.DAILY).symbol
        self.set_benchmark(self.spy)

        self.universe_settings.resolution = Resolution.DAILY

        self.coarse_count = 500
        self.top_n = 20
        self.momentum_lookback = 252      # about 12 months
        self.skip_recent = 21             # skip last month
        self.vol_lookback = 126           # about 6 months
        self.min_price = 10
        self.min_dollar_volume = 1e7

        self.selected_symbols = []
        self.last_rebalance_month = -1

        self.add_universe(self.coarse_selection)

    def coarse_selection(self, coarse):
        # Rebalance only once per month, but let coarse run daily
        if self.time.month == self.last_rebalance_month:
            return Universe.UNCHANGED

        # Liquid, reasonably priced universe
        coarse = [c for c in coarse
                  if c.has_fundamental_data
                  and c.price is not None
                  and c.price > self.min_price
                  and c.dollar_volume > self.min_dollar_volume]

        coarse = sorted(coarse, key=lambda c: c.dollar_volume, reverse=True)[:self.coarse_count]
        symbols = [c.symbol for c in coarse]

        if len(symbols) == 0:
            self.debug(f"{self.time.date()} no coarse symbols")
            return Universe.UNCHANGED

        lookback = self.momentum_lookback + self.skip_recent + 5
        history = self.history(symbols, lookback, Resolution.DAILY)

        if history.empty:
            self.debug(f"{self.time.date()} empty history")
            return Universe.UNCHANGED

        scores = []

        for symbol in symbols:
            try:
                hist = history.loc[symbol]
            except KeyError:
                continue

            if "close" not in hist.columns:
                continue

            prices = hist["close"].dropna()
            if len(prices) < lookback - 2:
                continue

            # 12-1 momentum: from t-12m to t-1m, skipping the most recent month
            p_now_minus_1m = prices.iloc[-self.skip_recent]
            p_12m_ago = prices.iloc[-(self.momentum_lookback + self.skip_recent)]
            if p_12m_ago <= 0:
                continue
            momentum = p_now_minus_1m / p_12m_ago - 1

            # 6m realized vol on daily returns
            rets = prices.pct_change().dropna()
            if len(rets) < self.vol_lookback:
                continue
            vol = rets.iloc[-self.vol_lookback:].std() * np.sqrt(252)
            if pd.isna(vol) or vol <= 0:
                continue

            scores.append((symbol, momentum, vol))

        if len(scores) < self.top_n:
            self.debug(f"{self.time.date()} not enough scored symbols: {len(scores)}")
            return Universe.UNCHANGED

        df = pd.DataFrame(scores, columns=["symbol", "mom", "vol"]).set_index("symbol")

        # Rank-based normalization is robust
        mom_rank = df["mom"].rank(pct=True)
        lowvol_rank = (-df["vol"]).rank(pct=True)

        df["score"] = 0.5 * mom_rank + 0.5 * lowvol_rank
        df = df.sort_values("score", ascending=False)

        self.selected_symbols = list(df.head(self.top_n).index)
        self.last_rebalance_month = self.time.month

        self.debug(f"{self.time.date()} selected {len(self.selected_symbols)} symbols")
        return self.selected_symbols

    def on_securities_changed(self, changes):
        # Rebalance only when the new universe has actually been applied
        if not self.selected_symbols:
            return

        targets = [PortfolioTarget(symbol, 1.0 / len(self.selected_symbols))
                   for symbol in self.selected_symbols]

        self.set_holdings(targets, liquidate_existing_holdings=True)
        self.debug(f"{self.time.date()} rebalanced into {len(self.selected_symbols)} names")