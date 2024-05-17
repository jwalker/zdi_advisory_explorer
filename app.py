import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
from io import BytesIO

# Function to fetch data from the database
@st.cache_data(ttl=86400)  # Cache the data for 24 hours (86400 seconds)
def load_data():
    conn = sqlite3.connect('zdi_advisories.db')
    query = "SELECT * FROM advisories"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Initialize session state for bookmarks and saved searches
if 'bookmarks' not in st.session_state:
    st.session_state['bookmarks'] = []
if 'saved_searches' not in st.session_state:
    st.session_state['saved_searches'] = {}

# Streamlit app
st.title('ZDI Advisory Explorer')

# Load data
data = load_data()

# About section
st.sidebar.header("ℹ️ - About")
st.sidebar.info(
    """
    **ZDI Advisory Explorer** helps quickly sort and understand the types of vulnerabilities 
    that bug bounties such as ZDI are looking for. It aids in focusing on target applications 
    for auditing N-day and 0-day vulnerabilities.
    
    [GitHub Project](https://github.com/jwalker/zdi_advisory_explorer)

    Connect with me on X: [@call_eax](https://x.com/@call_eax)

    Or Mastodon: [@call_eax](https://infosec.exchange/@calleax)
    """
)
st.sidebar.markdown("---")

# Sidebar
st.sidebar.title('🎛️ - Control Panel')
st.sidebar.markdown("---")

# Filter section
st.sidebar.header("🗄️ - Filters")
years = data['year'].unique()
selected_year = st.sidebar.multiselect('Year', sorted(years), default=years)
search_keyword = st.sidebar.text_input('Search Keyword')

# Save and load searches
search_name = st.sidebar.text_input("Search Name")
if st.sidebar.button("Save Search") and search_name:
    st.session_state['saved_searches'][search_name] = {
        'selected_year': selected_year,
        'search_keyword': search_keyword
    }

saved_search = st.sidebar.selectbox("Load Saved Search", options=[""] + list(st.session_state['saved_searches'].keys()))
if saved_search:
    saved_filter = st.session_state['saved_searches'][saved_search]
    selected_year = saved_filter['selected_year']
    search_keyword = saved_filter['search_keyword']

st.sidebar.markdown("---")

# Download section
st.sidebar.header("💾 - Download Data")

# Filter data based on user selection
filtered_data = data[data['year'].isin(selected_year)]

if search_keyword:
    filtered_data = filtered_data[filtered_data['title'].str.contains(search_keyword, case=False) |
                                  filtered_data['summary'].str.contains(search_keyword, case=False)]

# Download filtered data as CSV
csv = filtered_data.to_csv(index=False)
st.sidebar.download_button(label="Download data as CSV", data=csv, file_name='filtered_advisories.csv', mime='text/csv')

# Download filtered data as Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    filtered_data.to_excel(writer, index=False, sheet_name='Advisories')
excel_data = output.getvalue()
st.sidebar.download_button(label="Download data as Excel", data=excel_data, file_name='filtered_advisories.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Tabs for Data Table, Visualizations, and Bookmarks
tab1, tab2, tab3 = st.tabs(["Data Table", "Visualizations", "Bookmarks"])

with tab1:
    st.write(f"Showing advisories for Year: {selected_year}, Keyword: {search_keyword}")

    for index, row in filtered_data.iterrows():
        with st.expander(row['title']):
            st.markdown(f"**Published Date:** {row['published']}")
            st.markdown(f"**Summary:**\n{row['summary']}")
            st.markdown(f"[Read more]({row['link']})")
            if st.button("Bookmark", key=f"bookmark_{index}"):
                st.session_state['bookmarks'].append(row.to_dict())

with tab2:
    st.header("Dashboard")
    st.subheader("Number of Advisories per Year")
    advisories_per_year = filtered_data.groupby('year').size().reset_index(name='count')
    fig1 = px.bar(advisories_per_year, x='year', y='count', title='Number of Advisories per Year')
    st.plotly_chart(fig1)

    st.subheader("Advisory Distribution by Year")
    fig2 = px.pie(advisories_per_year, names='year', values='count', title='Advisory Distribution by Year')
    st.plotly_chart(fig2)

with tab3:
    st.header("Bookmarked Advisories")
    for index, bookmark in enumerate(st.session_state['bookmarks']):
        with st.expander(bookmark['title']):
            st.markdown(f"**Published Date:** {bookmark['published']}")
            st.markdown(f"**Summary:**\n{bookmark['summary']}")
            st.markdown(f"[Read more]({bookmark['link']})")
            if st.button("Remove Bookmark", key=f"remove_{index}"):
                st.session_state['bookmarks'].pop(index)
                st.experimental_rerun()  # Refresh the page to update the bookmark list
