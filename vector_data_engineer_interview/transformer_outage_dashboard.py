# question_3.py is part of an interview for the role of "Data Engineer" at Vector, New Zealand.
# It is a streamlit app to build a simple dashboard.
# Kane Williams  17-Dec-2024.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="Outage Dashboard", layout="wide")

def load_data():
    # Outage data
    df_q3 = {
        'outage_id': [12345, 12346, 12347, 12347, 12347, 13349],
        'suburb': ['Ponsonby', 'Albany', 'Remuera', 'Remuera', 'Remuera', 'Ponsonby'],
        'transformer_name': ['KCN ME01', 'KNN CEP1', 'REMU MK01', 'REMU MK09', 'REMU MU78', 'KCN ME01'],
        'customers_on_transformer': [1200, 500, 30, 2000, 100, 13],
        'start_time': ['25/06/2024 8:00', '25/07/2024 8:30', '27/08/2024 8:30', '27/08/2024 8:30', 
                       '27/08/2024 8:30', '31/08/2024 20:00'],
        'end_time': ['25/06/2024 9:00', '25/07/2024 10:30', '27/08/2024 10:30', '27/08/2024 9:00',
                     '27/08/2024 8:50', None],
        'status': ['Closed', 'Closed', 'Closed', 'Closed', 'Closed', 'Open'],
        'duration_minutes': [60, 120, 120, 30, 20, 300]
    }
    
    # Suburb limits data
    df_q4 = {
        'suburb': ['Ponsonby', 'Albany', 'Remuera'],
        'duration_limit': [500, 100, 150]
    }
    
    # Convert to DataFrames
    df_outages = pd.DataFrame(df_q3)
    df_limits = pd.DataFrame(df_q4)
    
    # Convert datetime strings to datetime objects
    df_outages['start_time'] = pd.to_datetime(df_outages['start_time'], format='%d/%m/%Y %H:%M')
    df_outages['end_time'] = pd.to_datetime(df_outages['end_time'], format='%d/%m/%Y %H:%M')
    
    # Handle None in end_time by using current time
    df_outages['end_time'] = df_outages['end_time'].fillna(pd.Timestamp.now())
    
    # Join the dataframes
    df_combined = pd.merge(df_outages, df_limits, on='suburb', how='left')
    
    return df_combined

def create_gantt_chart(df):
    """Create a horizontal timeline showing outages by transformer, colored by suburb"""
    fig = go.Figure()
    
    colors = {
        'Ponsonby': '#1f77b4',
        'Albany': '#2ca02c',
        'Remuera': '#ff7f0e'
    }
    
    # Function to adjust end time for very short outages to ensure visibility
    def adjust_duration(start, end):
        duration = (end - start).total_seconds() / 3600  # duration in hours
        if duration < 24:  # if less than 24 hours
            return start + pd.Timedelta(hours=24)
        return end
    
    for idx, row in df.iterrows():
        # Adjust end time for visibility of short outages
        visible_end = adjust_duration(row['start_time'], row['end_time'])
        
        fig.add_trace(go.Bar(
            base=row['start_time'],  # Start time of the bar
            x=[(visible_end - row['start_time']).total_seconds() * 1000],  # Duration in milliseconds
            y=[row['transformer_name']],
            orientation='h',  # Make the bars horizontal
            marker_color=colors[row['suburb']],
            name=row['suburb'],
            text=f"{row['suburb']}",
            hovertemplate=(
                f"Transformer: {row['transformer_name']}<br>" +
                f"Suburb: {row['suburb']}<br>" +
                f"Start: {row['start_time'].strftime('%Y-%m-%d %H:%M')}<br>" +
                f"End: {row['end_time'].strftime('%Y-%m-%d %H:%M')}<br>" +
                f"Duration: {row['duration_minutes']} mins<br>" +
                f"Customers: {row['customers_on_transformer']:,}<br>" +
                f"Status: {row['status']}<br>" +
                "<extra></extra>"
            ),
            showlegend=True
        ))
    
    min_time = df['start_time'].min() - pd.Timedelta(days=1)
    max_time = df['end_time'].max() + pd.Timedelta(days=1)
    
    fig.update_layout(
        title="Outage Timeline by Transformer",
        height=300,
        xaxis=dict(
            type='date',
            tickformat='%Y-%m-%d %H:%M',
            title="Time",
            range=[min_time, max_time]
        ),
        yaxis=dict(
            title="Transformer",
            categoryorder='array',
            categoryarray=sorted(df['transformer_name'].unique())
        ),
        showlegend=True,
        legend_title="Suburbs",
        hovermode='closest',
        barmode='overlay'
    )
    
    return fig

def main():
    st.title("Electricity Outage Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Suburb filter
    suburbs = ['All'] + sorted(df['suburb'].unique().tolist())
    selected_suburb = st.sidebar.selectbox("Select Suburb", suburbs)
    
    # Date range filter
    min_date = df['start_time'].min().date()
    max_date = df['start_time'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_suburb != 'All':
        filtered_df = filtered_df[filtered_df['suburb'] == selected_suburb]
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['start_time'].dt.date >= date_range[0]) &
            (filtered_df['start_time'].dt.date <= date_range[1])
        ]
    
    # Calculate metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("All Outages", len(filtered_df['outage_id'].unique()))
    with col2:
        st.metric("Open Outages", len(filtered_df[filtered_df['status'] == 'Open']))
    with col3:
        total_customers = filtered_df['customers_on_transformer'].sum()
        st.metric("Total Customers Affected (Possible Duplicates)", f"{total_customers:,}")
    
    # Display Gantt chart
    st.plotly_chart(create_gantt_chart(filtered_df), use_container_width=True)
    
    # Create two columns for additional charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Total Outage Duration vs Limits by Suburb")
        suburb_durations = filtered_df.groupby('suburb').agg({
            'duration_minutes': 'sum',
            'duration_limit': 'first'
        }).reset_index()
        
        fig = go.Figure(data=[
            go.Bar(name='Total Outage Time', x=suburb_durations['suburb'], 
                  y=suburb_durations['duration_minutes']),
            go.Bar(name='Duration Limit', x=suburb_durations['suburb'], 
                  y=suburb_durations['duration_limit'])
        ])
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Customers Affected by Suburb")
        customers_by_suburb = filtered_df.groupby('suburb')['customers_on_transformer'].sum()
        fig_pie = px.pie(values=customers_by_suburb.values, names=customers_by_suburb.index)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed data view
    st.subheader("Detailed Outage Data")
    display_df = filtered_df.drop('duration_limit', axis=1)
    st.dataframe(display_df.style.format({
        'customers_on_transformer': '{:,}'.format,
        'duration_minutes': '{:,.0f}'.format,
        'start_time': lambda x: x.strftime('%Y-%m-%d %H:%M'),
        'end_time': lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notna(x) else 'Ongoing'
    }))

if __name__ == "__main__":
    main()