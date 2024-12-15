# Kane Williams 2024-Dec-15 --- An Amazon Product Analysis
# As part of a 2 hour "Data Test" for a "Data Analyst" position at "Frankies".
# For more please view my Github: https://github.com/kanewilliams

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import numpy as np
from nltk.corpus import stopwords
import nltk
import matplotlib.pyplot as plt

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

df = pd.read_excel("Amazon data Exercise - Kane Williams.xlsx")

def clean_price(price_str):
    return float(str(price_str).replace('₹', '').replace(',', ''))

def clean_percentage(pct):
    if isinstance(pct, str):
        return float(pct.strip('%'))  # Just remove the % sign
    return float(pct) * 100

def generate_wordcloud(text_data, title):
    stop_words = set(stopwords.words('english'))
    
    wordcloud = WordCloud(
        width=800, 
        height=400,
        background_color='white',
        stopwords=stop_words,
        max_words=100
    ).generate(' '.join(text_data))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title)
    return fig

# -------------------------------------------------------------------------------
# Data cleaning
df_cleaned = df.copy()
df_cleaned['discounted_price'] = df_cleaned['discounted_price'].apply(clean_price)
df_cleaned['actual_price'] = df_cleaned['actual_price'].apply(clean_price)
df_cleaned['discount_percentage'] = df_cleaned['discount_percentage'].apply(clean_percentage)  # Add this line here
print(df_cleaned['discount_percentage'].head())
df_cleaned = df_cleaned[df_cleaned['rating'] != '|']
df_cleaned['rating'] = df_cleaned['rating'].astype(float)
df_cleaned['rating_count'] = df_cleaned['rating_count'].astype(str)
df_cleaned['rating_count'] = df_cleaned['rating_count'].str.replace(',', '')
df_cleaned['rating_count'] = pd.to_numeric(df_cleaned['rating_count'], errors='coerce').fillna(0).astype(int)
df_cleaned['broad_category'] = df_cleaned['category'].str.split('|').str[0]

# -------------------------------------------------------------------------------

# Set page config
st.set_page_config(
    page_title="Amazon India Product Analysis",
    page_icon="🛍️",
    layout="wide"
)

# Sidebar filters
st.sidebar.header("Filters")

# Price range filter
price_range = st.sidebar.slider(
    "Price Range (₹)",
    min_value=int(df_cleaned['actual_price'].min()),
    max_value=int(df_cleaned['actual_price'].max()),
    value=(int(df_cleaned['actual_price'].min()), int(df_cleaned['actual_price'].max()))
)

# Rating range filter
rating_range = st.sidebar.slider(
    "Rating Range",
    min_value=float(df_cleaned['rating'].min()),
    max_value=float(df_cleaned['rating'].max()),
    value=(float(df_cleaned['rating'].min()), float(df_cleaned['rating'].max()))
)

# Category filter
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df_cleaned['broad_category'].unique(),
    default=df_cleaned['broad_category'].unique()
)

# Search functionality
st.sidebar.header("Search Products")
search_term = st.sidebar.text_input("Search by product name")

# Apply filters to create filtered dataset
filtered_df = df_cleaned[
    (df_cleaned['actual_price'].between(price_range[0], price_range[1])) &
    (df_cleaned['rating'].between(rating_range[0], rating_range[1])) &
    (df_cleaned['broad_category'].isin(categories))
]

if search_term:
    filtered_df = filtered_df[filtered_df['product_name'].str.contains(search_term, case=False)]

# Add About section in sidebar
st.sidebar.markdown("---")  # Add a separator line
st.sidebar.header("About")
st.sidebar.write("""
Created as part of a 2-hour 'Data Test' for Frankie, while interviewing for the position of "Data Analyst".
""")

# Add copyright info at the bottom of sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Author:** Kane Williams  
**Date:** December 15, 2024
""")

# Title
st.title("🛍️ Amazon India Product Analysis")

# Display key metrics based on filtered data
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Average Rating", f"{filtered_df['rating'].mean():.2f}")
with col2:
    st.metric("Median Price", f"₹{filtered_df['actual_price'].median():.0f}")
with col3:
    st.metric("Median Discounted Price", f"₹{filtered_df['discounted_price'].median():.0f}")
with col4:
    st.metric("Average Discount", f"{filtered_df['discount_percentage'].mean():.1f}%")
with col5:
    st.metric("Total Products", f"{len(filtered_df):,}")

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Price Analysis", "Ratings Analysis", "Discount Analysis", "Category Analysis", "Word Analysis"])

with tab1:
    st.header("Price Analysis")
    
    # Price vs Rating scatter plot
    fig_price_rating = px.scatter(
        filtered_df,
        x='actual_price',
        y='rating',
        color='broad_category',
        title='Price vs Rating Distribution',
        hover_data=['product_name']
    )
    st.plotly_chart(fig_price_rating, use_container_width=True)
    
    # Price distribution by category
    fig_price_box = px.box(
        filtered_df,
        x='broad_category',
        y='actual_price',
        title='Price Distribution by Category'
    )
    st.plotly_chart(fig_price_box, use_container_width=True)

with tab2:
    st.header("Ratings Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating distribution
        fig_rating_dist = px.histogram(
            filtered_df,
            x='rating',
            nbins=20,
            title='Overall Rating Distribution'
        )
        st.plotly_chart(fig_rating_dist, use_container_width=True)
    
    with col2:
        # Rating vs Number of Reviews
        fig_rating_count = px.scatter(
            filtered_df,
            x='rating_count',
            y='rating',
            color='broad_category',
            title='Rating vs Number of Reviews'
        )
        st.plotly_chart(fig_rating_count, use_container_width=True)
    
    # New: Ratings by category histograms
    st.subheader("Rating Distribution by Category")
    fig_category_ratings = px.histogram(
        filtered_df,
        x='rating',
        color='broad_category',
        nbins=20,
        facet_col='broad_category',
        facet_col_wrap=2,  # Show 2 categories per row
        title='Rating Distribution by Category'
    )
    # Update layout to make it more readable
    fig_category_ratings.update_layout(
        height=100 * (len(categories) // 2 + len(categories) % 2) * 2,  # Adjust height based on number of categories
        showlegend=False
    )
    # Remove repeated axis titles
    fig_category_ratings.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig_category_ratings, use_container_width=True)

with tab3:
    st.header("Discount Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Discount vs Rating scatter plot
        fig_discount_rating = px.scatter(
            filtered_df,
            x='discount_percentage',
            y='rating',
            color='broad_category',
            title='Discount Percentage vs Rating',
            hover_data=['product_name']
        )
        st.plotly_chart(fig_discount_rating, use_container_width=True)
    
    with col2:
        # Discount vs Rating Count scatter plot
        fig_discount_count = px.scatter(
            filtered_df,
            x='discount_percentage',
            y='rating_count',
            color='broad_category',
            title='Discount Percentage vs Number of Ratings',
            hover_data=['product_name']
        )
        fig_discount_count.update_layout(yaxis_type="log")  # Log scale for rating count
        st.plotly_chart(fig_discount_count, use_container_width=True)
    
    # Box plot of discounts by category
    fig_discount_box = px.box(
        filtered_df,
        x='broad_category',
        y='discount_percentage',
        title='Discount Distribution by Category'
    )
    st.plotly_chart(fig_discount_box, use_container_width=True)

with tab4:
    st.header("Category Analysis")
    
    # Category statistics
    category_stats = filtered_df.groupby('broad_category').agg({
        'rating': 'mean',
        'rating_count': 'mean',
        'discount_percentage': 'mean',
        'actual_price': 'mean'
    }).round(2)
    
    # Display category statistics with better column names
    category_stats.columns = ['Avg Rating', 'Avg Review Count', 'Avg Discount %', 'Avg Price']
    st.dataframe(category_stats)
    
    # Category distribution
    category_counts = filtered_df['broad_category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig_category = px.bar(
        category_counts,
        x='Category',
        y='Count',
        title='Number of Products by Category'
    )
    st.plotly_chart(fig_category, use_container_width=True)

with tab5:
    st.header("Word Analysis (Broken! But the idea is there.)")
    
    # Percentile selector
    percentile = st.slider(
        "Select percentile for analysis",
        min_value=5,
        max_value=25,
        value=10,
        help="Products with ratings in the top and bottom X% will be analyzed"
    )
    
    # Add radio button for text source selection
    text_source = st.radio(
        "Select text source for analysis",
        ["Review Content", "Product Description"],
        help="Choose whether to analyze review content or product descriptions"
    )
    
    # Map radio button selection to column name
    text_column = 'review_content' if text_source == "Review Content" else 'about_product'
    
    # Calculate percentile thresholds for ratings
    lower_threshold = np.percentile(filtered_df['rating'], percentile)
    upper_threshold = np.percentile(filtered_df['rating'], 100 - percentile)
    
    # Get products in the selected percentiles and ensure they have non-null text content
    top_products = filtered_df[
        (filtered_df['rating'] >= upper_threshold) & 
        (filtered_df[text_column].notna())
    ]
    bottom_products = filtered_df[
        (filtered_df['rating'] <= lower_threshold) & 
        (filtered_df[text_column].notna())
    ]
    
    # Display the number of products being analyzed
    st.write(f"Number of products in top {percentile}%: {len(top_products)}")
    st.write(f"Number of products in bottom {percentile}%: {len(bottom_products)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Top {percentile}% Products Word Cloud")
        st.write(f"Products with ratings >= {upper_threshold:.1f}")
        if not top_products.empty:
            combined_text = ' '.join(top_products[text_column])
            if combined_text.strip():  # Check if there's actual text to analyze
                fig_top = generate_wordcloud(
                    [combined_text],
                    f"Word Cloud of {text_source} for Top {percentile}% Products"
                )
                st.pyplot(fig_top)
            else:
                st.write("Not enough text data to generate word cloud")
    
    with col2:
        st.subheader(f"Bottom {percentile}% Products Word Cloud")
        st.write(f"Products with ratings <= {lower_threshold:.1f}")
        if not bottom_products.empty:
            combined_text = ' '.join(bottom_products[text_column])
            if combined_text.strip():  # Check if there's actual text to analyze
                fig_bottom = generate_wordcloud(
                    [combined_text],
                    f"Word Cloud of {text_source} for Bottom {percentile}% Products"
                )
                st.pyplot(fig_bottom)
            else:
                st.write("Not enough text data to generate word cloud")

# Show raw data with filters
st.header("Raw Data")
st.dataframe(filtered_df)