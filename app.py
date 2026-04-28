import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Zomato Smart Dashboard", layout="wide")

# ---------------- CUSTOM UI ----------------
st.markdown("""
<style>
.stApp {
    background: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836") no-repeat center center fixed;
    background-size: cover;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    backdrop-filter: blur(6px);
    background: rgba(0, 0, 0, 0.8);
    z-index: -1;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffb6c1, #ff99aa);
}
h1, h2, h3, p, span, label {
    color: white !important;
}
            
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 12px;
    color: white;
}
            
/* 🔥 BIGGER HEADER */
h1 {
    font-size: 50px !important;
    font-weight: 700 !important;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("Cleaned_Zomato_Dataset.csv")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🔍 Filters")

# City
city_list = sorted(df['City'].dropna().unique())
city = st.sidebar.selectbox("📍 Select City", [""] + city_list)

# Food Search
all_foods = (
    df['Cuisines'].dropna().str.split(', ').sum() +
    df['primary_cuisines'].dropna().str.split(', ').sum()
)
food_series = pd.Series(all_foods)
top_foods = food_series.value_counts().head(10).index.tolist()
all_unique_foods = sorted(set(food_series))
food_list = [""] + top_foods + [f for f in all_unique_foods if f not in top_foods]
food = st.sidebar.selectbox("🍕 Select Food", food_list)

# Cost
cost = st.sidebar.multiselect(
    "💰 Cost Category",
    df['cost_category'].unique(),
    default=df['cost_category'].unique()
)

# Rating
rating_range = st.sidebar.slider(
    "⭐ Rating Range",
    float(df['Rating'].min()),
    float(df['Rating'].max()),
    (2.5, 4.5)
)

# ---------------- FILTER ----------------
filtered_df = df.copy()

if city:
    filtered_df = filtered_df[
        filtered_df['City'].str.contains(city, case=False, na=False)
    ]

filtered_df = filtered_df[
    (filtered_df['cost_category'].isin(cost)) &
    (filtered_df['Rating'].between(rating_range[0], rating_range[1]))
]

if food:
    filtered_df = filtered_df[
        filtered_df['Cuisines'].str.contains(food, case=False, na=False) |
        filtered_df['primary_cuisines'].str.contains(food, case=False, na=False)
    ]

if filtered_df.empty:
    st.warning("No data found")
    st.stop()

# ---------------- HEADER ----------------
st.title("🍽️ Smart Restaurant Recommendation System")
st.markdown("---")

# ---------------- KPI ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("🍴 Restaurants", len(filtered_df))
col2.metric("⭐ Avg Rating", round(filtered_df['Rating'].mean(), 2))
col3.metric("🗳️ Avg Votes", int(filtered_df['Votes'].mean()))
col4.metric("💰 Avg Cost", int(filtered_df['Average_Cost_for_two'].mean()))

st.markdown("---")

# ---------------- RECOMMENDATION ----------------
st.subheader("🔥 Top Recommendations")

filtered_df['norm_rating'] = filtered_df['Rating'] / 5
filtered_df['norm_votes'] = filtered_df['Votes'] / filtered_df['Votes'].max()
filtered_df['norm_value'] = filtered_df['Value-for-money'] / filtered_df['Value-for-money'].max()

filtered_df['recommend_score'] = (
    0.5 * filtered_df['norm_rating'] +
    0.3 * filtered_df['norm_votes'] +
    0.2 * filtered_df['norm_value']
)

st.dataframe(
    filtered_df.sort_values(by='recommend_score', ascending=False)
    [['RestaurantName', 'Cuisines', 'Rating', 'Votes', 'cost_per_person']]
    .head(10),
    use_container_width=True
)

st.markdown("---")

# ---------------- SCATTER ----------------
st.subheader("⭐ Popularity vs Quality")
fig1 = px.scatter(
    filtered_df,
    x='Rating',
    y='Votes',
    color='cost_category',
    template="plotly_dark",
    hover_data=['RestaurantName']
)
st.plotly_chart(fig1, use_container_width=True)

# ---------------- BUSINESS ----------------
st.subheader("🚚 Business Insights")

col1, col2 = st.columns(2)

with col1:
    delivery_votes = filtered_df.groupby('Has_Online_delivery')['Votes'].mean().reset_index()
    fig2 = px.bar(delivery_votes, x='Has_Online_delivery', y='Votes', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    fig3 = px.box(filtered_df, x='cost_category', y='Rating', template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---------------- CUISINE ----------------
st.subheader("🍜 Top Cuisines")

top_cuisines = (
    filtered_df.groupby('primary_cuisines')['Votes']
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(top_cuisines, x='primary_cuisines', y='Votes', template="plotly_dark")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ---------------- COMPETITION ----------------
st.subheader("🌆 Market Competition")
fig5 = px.scatter(filtered_df, x='city_competition_norm', y='Rating', template="plotly_dark")
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ---------------- TOP RESTAURANTS ----------------
st.subheader("🏆 Top Restaurants")

st.dataframe(
    filtered_df.sort_values(by='popularity_score', ascending=False)
    [['RestaurantName', 'Rating', 'Votes', 'popularity_score']]
    .head(10),
    use_container_width=True
)

# ---------------- VALUE ----------------
st.subheader("💎 Best Value for Money")

st.dataframe(
    filtered_df.sort_values(by='Value-for-money', ascending=False)
    [['RestaurantName', 'Rating', 'cost_per_person', 'Value-for-money']]
    .head(10),
    use_container_width=True
)
