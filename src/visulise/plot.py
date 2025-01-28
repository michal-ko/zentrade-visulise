from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objs as go
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
st.write(f"Last updated at: {raw_df['timestamp'].max()}")
st.logo("misc/logo.jpg", size="large")
st.sidebar.header("Visualization Options")

chart_option = st.sidebar.selectbox("Chart type:", ("Candlestick", "Individual metric"))

display_from = datetime.now() - timedelta(days=7)
selected_start_dt = st.sidebar.date_input("Display data from:", display_from, max_value="today")
# if chart_option=="Graph type 1":
#     selected_columns = st.sidebar.multiselect("Select metrics:", COLUMNS, default=["close"])
downsample = st.sidebar.toggle("Downsample data to 1H interval")
if downsample:
    downsampled_df = downsample_data(raw_df)
    filtered_df = downsampled_df[downsampled_df['timestamp'] > pd.Timestamp(selected_start_dt, tz=TIMEZONE)]
else:
    filtered_df = raw_df[raw_df['timestamp'] > pd.Timestamp(selected_start_dt, tz=TIMEZONE)]


if chart_option=="Individual metric":

    selected_columns = st.sidebar.multiselect("Select metrics:", COLUMNS, default=["close"])
    st.line_chart(
        filtered_df,
        x="timestamp",
        x_label="date",
        y=selected_columns,
        y_label="price"
    )
elif chart_option=="Candlestick":
    # st.subheader("One", divider="gray")
    dates = filtered_df['timestamp'].tolist()
    open_prices = filtered_df['open'].astype(int).tolist()
    high_prices = filtered_df['high'].astype(int).tolist()
    low_prices = filtered_df['low'].astype(int).tolist()
    close_prices = filtered_df['close'].astype(int).tolist()

    # Create candlestick chart using Plotly
    candlestick = go.Candlestick(x=dates,
                                 open=open_prices,
                                 high=high_prices,
                                 low=low_prices,
                                 close=close_prices)

    layout = go.Layout(xaxis=dict(title='Date'), yaxis=dict(title='Price'))

    fig = go.Figure(data=[candlestick], layout=layout)

    # Display the chart using Streamlit
    st.plotly_chart(fig)

    st.subheader("Past trades:", divider="gray")
    # Example DataFrame
    data = {
        'Column1': [1, 2, 3, 4],
        'Column2': ['A', 'B', 'C', 'D']
    }
    dff = pd.DataFrame(data)
    st.dataframe(dff)
