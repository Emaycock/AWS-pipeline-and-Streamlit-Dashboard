import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

# 🔄 Auto-refresh
st_autorefresh(interval=30000, key="refresh")

# Page config
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# 🎨 Custom styling
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
div[data-testid="stMetric"] {
    background-color: #111;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<h1 style='text-align: center;'>📊 Real-Time Stock Analytics Dashboard</h1>
<p style='text-align: center; color: gray;'>Live AWS Data Pipeline | Streamlit App</p>
<hr>
""", unsafe_allow_html=True)

# Load local CSV instead of S3
    df = pd.read_csv("stocks_20260401_061342.csv")


# AWS S3
"""
s3 = boto3.client('s3')

bucket_name = "elian-stock-data-lake-2026"
prefix = "processed/finnhub_data/"

response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
files = response.get('Contents', [])

if not files:
    st.error("No data found in S3")
else:
    latest_file = max(files, key=lambda x: x['LastModified'])

    obj = s3.get_object(Bucket=bucket_name, Key=latest_file['Key'])
    data = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(data))

    # 🧠 Feature Engineering
    df['change'] = df['current_price'] - df['previous_close']
    df['percent_change'] = (df['change'] / df['previous_close']) * 100
    df['volatility'] = df['high'] - df['low']
    """

    # Sidebar
    st.sidebar.header("📊 Controls")
    selected_stock = st.sidebar.selectbox("Select Stock", df['symbol'].unique())

    # 🔥 KPI Row
    st.subheader("📊 Market Snapshot")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Stocks", len(df))
    col2.metric("Avg Price", round(df['current_price'].mean(), 2))
    col3.metric("Top Price", round(df['current_price'].max(), 2))
    col4.metric("Lowest Price", round(df['current_price'].min(), 2))

    #st.caption(f"Last updated: {latest_file['LastModified']}")
    st.caption("Data shown is a snapshot from the live pipeline for demo purposes.")

    # 🔥 GRID METRICS (FIXED SPACING)
    st.subheader("📈 Stock Performance")

    rows = [df[i:i+5] for i in range(0, len(df), 5)]

    for row_df in rows:
        cols = st.columns(5)
        for i, (_, row) in enumerate(row_df.iterrows()):
            cols[i].metric(
                label=row['symbol'],
                value=round(row['current_price'], 2),
                delta=f"{row['percent_change']:.2f}%"
            )

    # 🔥 Top Movers
    st.subheader("🔥 Market Movers")

    top_gainer = df.loc[df['percent_change'].idxmax()]
    top_loser = df.loc[df['percent_change'].idxmin()]

    col1, col2 = st.columns(2)

    col1.metric(
        "Top Gainer",
        top_gainer['symbol'],
        f"{top_gainer['percent_change']:.2f}%"
    )

    col2.metric(
        "Top Loser",
        top_loser['symbol'],
        f"{top_loser['percent_change']:.2f}%"
    )

    # 🔥 INTERACTIVE CHARTS (Plotly)
    st.subheader("📊 Interactive Charts")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df,
            x='symbol',
            y='current_price',
            color='current_price',
            title="Stock Prices",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            df,
            x='symbol',
            y='percent_change',
            color='percent_change',
            title="Performance (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # 🔥 FILTERED STOCK DETAIL
    st.subheader(f"📉 {selected_stock} Detail")

    filtered_df = df[df['symbol'] == selected_stock]

    fig3 = px.line(
        filtered_df,
        y=['high', 'low'],
        title=f"{selected_stock} High vs Low"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # 🔥 VOLATILITY
    st.subheader("📊 Volatility")

    fig4 = px.bar(
        df,
        x='symbol',
        y='volatility',
        color='volatility'
    )

    st.plotly_chart(fig4, use_container_width=True)

    # 🔥 RAW DATA (clean toggle)
    with st.expander("📄 View Raw Data"):
        st.dataframe(df)

# Footer
st.markdown("""
---
Built by Elian Maycock 🚀 | AWS Data Engineering Project
""")

