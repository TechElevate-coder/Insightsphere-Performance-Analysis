import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import xml.etree.ElementTree as ET
from datetime import datetime

# Set page config for better dark theme support
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv('sales.csv', parse_dates=['Date'])

df = load_data()

# Clean column names (remove trailing spaces)
df.columns = df.columns.str.strip()

# Basic data cleaning and feature engineering
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Quarter'] = df['Date'].dt.quarter
df['Month_Name'] = df['Date'].dt.month_name()

# Dashboard title
st.title("📊 Sales Performance Analysis Dashboard")

# Custom CSS for dark theme compatibility
st.markdown("""
<style>
    /* Main metrics styling */
    .metric-container {
        background-color: rgba(38, 39, 48, 0.8);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .metric-label {
        color: #f0f2f6 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    .metric-value {
        color: white !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    /* Chart styling */
    .stPlotlyChart {
        background-color: rgba(38, 39, 48, 0.8);
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: rgba(38, 39, 48, 0.8) !important;
        color: white !important;
    }
    
    /* General styling */
    .stApp {
        background-color: #0e1117;
    }
    .stHeader {
        color: white !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(38, 39, 48, 0.8);
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262740 !important;
    }
    
    /* Sidebar styling */
    .st-emotion-cache-6qob1r {
        background-color: #0e1117 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=sorted(df['Year'].unique()),
    default=sorted(df['Year'].unique())
)

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

selected_market_sizes = st.sidebar.multiselect(
    "Select Market Sizes",
    options=df['Market Size'].unique(),
    default=df['Market Size'].unique()
)

selected_product_types = st.sidebar.multiselect(
    "Select Product Types",
    options=df['Product Type'].unique(),
    default=df['Product Type'].unique()
)

# Filter data based on selections
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Region'].isin(selected_regions)) &
    (df['Market Size'].isin(selected_market_sizes)) &
    (df['Product Type'].isin(selected_product_types))
]

# Key metrics - using custom containers for better visibility
st.header("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Total Sales</div>
        <div class="metric-value">${total_sales:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_profit = filtered_df['Profit'].sum()
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Total Profit</div>
        <div class="metric-value">${total_profit:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_margin = filtered_df['Margin'].mean()
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Average Margin</div>
        <div class="metric-value">{avg_margin:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    sales_count = len(filtered_df)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">Transactions</div>
        <div class="metric-value">{sales_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

# Sales trends over time
st.header("🕒 Sales Trends Over Time")

tab1, tab2 = st.tabs(["Monthly Trend", "Quarterly Comparison"])

with tab1:
    monthly_sales = filtered_df.groupby(['Year', 'Month', 'Month_Name'])['Sales'].sum().reset_index()
    monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(DAY=1))
    
    fig1 = px.line(
        monthly_sales,
        x='Date',
        y='Sales',
        title='Monthly Sales Trend',
        labels={'Sales': 'Total Sales ($)'},
        markers=True,
        template="plotly_dark"
    )
    fig1.update_layout(
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    quarterly_sales = filtered_df.groupby(['Year', 'Quarter'])['Sales'].sum().reset_index()
    
    fig2 = px.bar(
        quarterly_sales,
        x='Quarter',
        y='Sales',
        color='Year',
        barmode='group',
        title='Quarterly Sales Comparison',
        labels={'Sales': 'Total Sales ($)'},
        text_auto='.2s',
        template="plotly_dark"
    )
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Profit Analysis
st.header("💰 Profit Analysis")

col1, col2 = st.columns(2)

with col1:
    profit_by_product = filtered_df.groupby('Product Type')['Profit'].sum().reset_index()
    profit_by_product = profit_by_product.sort_values('Profit', ascending=False)
    
    fig3 = px.bar(
        profit_by_product,
        x='Product Type',
        y='Profit',
        title='Total Profit by Product Type',
        labels={'Profit': 'Total Profit ($)'},
        color='Product Type',
        template="plotly_dark"
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    fig4 = px.box(
        filtered_df,
        x='Product Type',
        y='Margin',
        title='Profit Margin Distribution by Product Type',
        labels={'Margin': 'Profit Margin (%)'},
        color='Product Type',
        template="plotly_dark"
    )
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig4, use_container_width=True)

# Regional Performance
st.header("🌎 Regional Performance")

col1, col2 = st.columns(2)

with col1:
    sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    
    fig5 = px.pie(
        sales_by_region,
        values='Sales',
        names='Region',
        title='Sales Distribution by Region',
        hole=0.3,
        template="plotly_dark"
    )
    fig5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    profit_by_region_market = filtered_df.groupby(['Region', 'Market Size'])['Profit'].sum().reset_index()
    
    fig6 = px.bar(
        profit_by_region_market,
        x='Region',
        y='Profit',
        color='Market Size',
        title='Profit by Region and Market Size',
        labels={'Profit': 'Total Profit ($)'},
        barmode='group',
        template="plotly_dark"
    )
    fig6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig6, use_container_width=True)

# Top/Bottom Performers
st.header("🏆 Top and Bottom Performers")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 5 Products by Profit")
    top_products = filtered_df.groupby('Product')['Profit'].sum().nlargest(5).reset_index()
    st.dataframe(
        top_products.style.format({'Profit': '${:,.0f}'}),
        hide_index=True,
        use_container_width=True
    )

with col2:
    st.subheader("Bottom 5 Products by Profit")
    bottom_products = filtered_df.groupby('Product')['Profit'].sum().nsmallest(5).reset_index()
    st.dataframe(
        bottom_products.style.format({'Profit': '${:,.0f}'}),
        hide_index=True,
        use_container_width=True
    )

# Data export
st.sidebar.header("💾 Data Export")
if st.sidebar.button("Export Filtered Data to CSV"):
    csv = filtered_df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv,
        file_name='filtered_sales_data.csv',
        mime='text/csv'
    )

# Add explanatory text
st.markdown("""
<style>
.explanatory-text {
    color: #f0f2f6;
    font-size: 14px;
    margin-top: 20px;
    padding: 15px;
    background-color: rgba(38, 39, 48, 0.8);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
<div class="explanatory-text">
    <strong>Dashboard Notes:</strong> Use the filters in the sidebar to customize the data view. 
    All charts and metrics will update automatically based on your selections.
</div>
""", unsafe_allow_html=True)