from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

TIMEZONE = 'Europe/Warsaw'
COLUMNS = ["open","high","low","close","volume","close_time","quote_volume","trades","taker_buy_base","taker_buy_quote","ignore"]

@st.cache_data(ttl='1h')
def load_data():
    # Read CSV without automatic date parsing
    df = pd.read_csv(
        "output/market_data_BTCUSDT_15m.csv",
        dtype={col: 'float32' for col in COLUMNS},
    )

    # Manual timestamp conversion
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert(TIMEZONE)

    return df[["timestamp", *COLUMNS]]

@st.cache_data
def downsample_data(df, freq='1H'):
    # Downsample data to reduce points while preserving trend
    return df.set_index('timestamp').resample(freq).mean().reset_index()

raw_df = load_data()

st.title("BTCUSDT Market Data - 15min interval")
st.sidebar.header("Visualization Options")

display_from = datetime.now() - timedelta(days=7)
selected_start_dt = st.sidebar.date_input("Display data from:", display_from, max_value="today")
selected_columns = st.sidebar.multiselect("Select metrics:", COLUMNS, default=["close"])
downsample = st.sidebar.toggle("Downsample data to 1H interval")
if downsample:
    downsampled_df = downsample_data(raw_df)
    filtered_df = downsampled_df[downsampled_df['timestamp'] > pd.Timestamp(selected_start_dt, tz=TIMEZONE)]
else:
    filtered_df = raw_df[raw_df['timestamp'] > pd.Timestamp(selected_start_dt, tz=TIMEZONE)]

st.line_chart(
    filtered_df,
    x="timestamp",
    x_label="date",
    y=selected_columns,
    y_label="price"
)
