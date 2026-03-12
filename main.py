"""
Quantitative Developer Assignment
---------------------------------

Features
1. User selects:
   - Time unit (days/months/years)
   - Time value
   - Data interval (1m,5m,1h,1d,1wk,1mo, etc.)
2. Downloads Yahoo Finance data
3. Cleans & aligns time series
4. Feature engineering
5. Analytics + correlation
6. Moving average strategy
7. Saves:
   - Raw data -> data/
   - PDF report -> reports/
"""

# ------------------------------------------------
# IMPORT LIBRARIES
# ------------------------------------------------

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime, timedelta

TRADING_DAYS = 252


# ------------------------------------------------
# DIRECTORY SETUP
# ------------------------------------------------

def setup_directories():

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


# ------------------------------------------------
# USER INPUT
# ------------------------------------------------

def get_time_range():

    unit = input("Enter time unit (days / months / years): ").lower()
    value = int(input("Enter value: "))

    end = datetime.today()

    if unit == "days":
        start = end - timedelta(days=value)

    elif unit == "months":
        start = end - timedelta(days=value * 30)

    elif unit == "years":
        start = end - timedelta(days=value * 365)

    else:
        raise ValueError("Invalid unit")

    return start, end


def get_interval():

    print(
        "\nValid intervals:\n"
        "1m 2m 5m 15m 30m 60m 90m\n"
        "1h\n"
        "1d 5d\n"
        "1wk\n"
        "1mo\n"
        "3mo\n"
    )

    interval = input("Enter data interval: ")

    return interval


def get_tickers():

    tickers = input(
        "Enter stock tickers separated by space (max 25): "
    ).upper().split()

    if len(tickers) == 0:
        raise ValueError("No tickers entered")

    if len(tickers) > 25:
        raise ValueError("Maximum allowed tickers = 25")

    return tickers


# ------------------------------------------------
# DATA DOWNLOAD
# ------------------------------------------------

def download_data(tickers, start, end, interval):

    print("\nDownloading market data...")

    data = yf.download(
        tickers,
        start=start,
        end=end,
        interval=interval,
        progress=False
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = f"data/raw_data_{timestamp}.csv"

    data.to_csv(path)

    print(f"Raw data saved to {path}")

    return data


# ------------------------------------------------
# DATA CLEANING
# ------------------------------------------------

def clean_data(data, tickers):

    cleaned = {}

    for ticker in tickers:

        df = data.xs(ticker, level=1, axis=1).copy()

        df.index = pd.to_datetime(df.index)

        df = df[~df.index.duplicated()]

        df = df.dropna()

        cleaned[ticker] = df

    common_dates = cleaned[tickers[0]].index

    for ticker in tickers[1:]:
        common_dates = common_dates.intersection(cleaned[ticker].index)

    for ticker in tickers:
        cleaned[ticker] = cleaned[ticker].loc[common_dates]

    return cleaned


# ------------------------------------------------
# FEATURE ENGINEERING
# ------------------------------------------------

def add_features(cleaned):

    for ticker, df in cleaned.items():

        df["daily_return"] = df["Close"].pct_change()

        df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        df["volatility_30"] = df["daily_return"].rolling(30).std()

        cleaned[ticker] = df.dropna()

    return cleaned


# ------------------------------------------------
# BASIC ANALYTICS
# ------------------------------------------------

def compute_statistics(cleaned):

    returns_df = pd.DataFrame()

    stats = []

    for ticker, df in cleaned.items():

        r = df["daily_return"]

        mean = r.mean()
        std = r.std()

        annual_vol = std * np.sqrt(TRADING_DAYS)

        stats.append([ticker, mean, std, annual_vol])

        returns_df[ticker] = r

    stats_df = pd.DataFrame(
        stats,
        columns=["Ticker", "Mean Daily Return", "Std Dev", "Annual Volatility"]
    )

    print("\n=== BASIC ANALYTICS ===")
    print(stats_df)

    return returns_df, stats_df


# ------------------------------------------------
# CORRELATION HEATMAP
# ------------------------------------------------

def correlation_analysis(returns_df, pdf):

    corr = returns_df.corr()

    fig = plt.figure(figsize=(6,5))

    sns.heatmap(corr, annot=True, cmap="coolwarm")

    plt.title("Correlation Matrix")

    pdf.savefig(fig)

    plt.close()

    return corr


# ------------------------------------------------
# PRICE PLOT
# ------------------------------------------------

def plot_prices(cleaned, pdf):

    fig = plt.figure(figsize=(12,6))

    for ticker, df in cleaned.items():

        plt.plot(df.index, df["Close"], label=ticker)

    plt.title("Stock Price History")

    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend()

    pdf.savefig(fig)

    plt.close()


# ------------------------------------------------
# MOVING AVERAGES
# ------------------------------------------------

def plot_moving_averages(cleaned, pdf):

    for ticker, df in cleaned.items():

        fig = plt.figure(figsize=(12,6))

        plt.plot(df.index, df["Close"], label="Price")
        plt.plot(df.index, df["MA20"], label="MA20")
        plt.plot(df.index, df["MA50"], label="MA50")

        plt.title(f"{ticker} Moving Averages")

        plt.xlabel("Date")
        plt.ylabel("Price")

        plt.legend()

        pdf.savefig(fig)

        plt.close()


# ------------------------------------------------
# STRATEGY
# ------------------------------------------------

def moving_average_strategy(cleaned, ticker, pdf):

    df = cleaned[ticker].copy()

    df["position"] = np.where(df["MA20"] > df["MA50"], 1, 0)

    df["strategy_return"] = df["position"].shift(1) * df["daily_return"]

    df["cum_strategy"] = (1 + df["strategy_return"]).cumprod()

    df["cum_buy_hold"] = (1 + df["daily_return"]).cumprod()

    r = df["strategy_return"].dropna()

    total_return = df["cum_strategy"].iloc[-1] - 1
    buy_hold_return = df["cum_buy_hold"].iloc[-1] - 1

    vol = r.std() * np.sqrt(TRADING_DAYS)

    sharpe = (r.mean() / r.std()) * np.sqrt(TRADING_DAYS)

    print("\n=== STRATEGY RESULTS ===")
    print("Strategy Return:", total_return)
    print("Buy & Hold:", buy_hold_return)
    print("Volatility:", vol)
    print("Sharpe:", sharpe)

    fig = plt.figure(figsize=(12,6))

    plt.plot(df.index, df["cum_strategy"], label="Strategy")

    plt.plot(df.index, df["cum_buy_hold"], label="Buy & Hold")

    plt.title(f"Strategy vs Buy & Hold ({ticker})")

    plt.xlabel("Date")
    plt.ylabel("Growth of $1")

    plt.legend()

    pdf.savefig(fig)

    plt.close()


# ------------------------------------------------
# MAIN
# ------------------------------------------------

def main():

    setup_directories()

    start, end = get_time_range()

    interval = get_interval()

    tickers = get_tickers()

    data = download_data(tickers, start, end, interval)

    cleaned = clean_data(data, tickers)

    cleaned = add_features(cleaned)

    returns_df, stats_df = compute_statistics(cleaned)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = f"reports/quant_report_{timestamp}.pdf"

    with PdfPages(report_path) as pdf:

        correlation_analysis(returns_df, pdf)

        plot_prices(cleaned, pdf)

        plot_moving_averages(cleaned, pdf)

        moving_average_strategy(cleaned, tickers[0], pdf)

    print(f"\nReport saved -> {report_path}")


if __name__ == "__main__":
    main()