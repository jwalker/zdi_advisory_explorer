import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from io import BytesIO
import json

# Function to safely parse JSON strings
def safe_json_loads(s):
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON: {e}, Data: {s}")
        return []

# Function to fetch data from the database
@st.cache_data(ttl=86400)  # Cache the data for 24 hours (86400 seconds)
def load_data(years):
    conn = sqlite3.connect('zdi_advisories_v2.db')
    if years:
        query = f"SELECT * FROM advisories WHERE published_date LIKE '{years[0]}%'"
        for year in years[1:]:
            query += f" OR published_date LIKE '{year}%'"
    else:
        query = "SELECT * FROM advisories WHERE 1=0"  # Return no results if no years are selected
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to clean and format data for display
def clean_data(df):
    # Ensure relevant columns are parsed as JSON
    df['products'] = df['products'].apply(safe_json_loads)
    df['responses'] = df['responses'].apply(safe_json_loads)
    df['discoverers'] = df['discoverers'].apply(safe_json_loads)
    df['cves'] = df['cves'].apply(safe_json_loads)

    # Process the parsed JSON data
    df['products'] = df['products'].apply(lambda x: ', '.join([product['name'] for product in x]))
    df['response_texts'] = df['responses'].apply(lambda x: ' '.join([response['text'] for response in x if 'text' in response and response['text']]))
    df['response_vendors'] = df['responses'].apply(lambda x: ', '.join([response['vendor']['name'] for response in x if 'vendor' in response and 'name' in response['vendor']]))
    df['response_uris'] = df['responses'].apply(lambda x: ', '.join([response['uri'] for response in x if 'uri' in response and response['uri']]))
    df['discoverers'] = df['discoverers'].apply(lambda x: ', '.join(x))
    df['cvss_vector'] = df['cvss_vector'].apply(lambda x: x.replace('/', ' ') if x else '')
    df['cves'] = df['cves'].apply(lambda x: ', '.join([f"[{cve}](https://www.cve.org/CVERecord?id={cve})" for cve in x]))
    return df

# Initialize session state for bookmarks and saved searches
if 'bookmarks' not in st.session_state:
    st.session_state['bookmarks'] = []
if 'saved_searches' not in st.session_state:
    st.session_state['saved_searches'] = {}

# Streamlit app
st.title('ZDI Advisory Explorer v2')

# About section
st.sidebar.header("ℹ️ - About")
st.sidebar.info(
    """
    **ZDI Advisory Explorer v2** helps quickly sort and understand the types of vulnerabilities 
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
all_years = [str(year) for year in range(2005, 2025)]
recent_years = ['2024']  # default to recent year for performance reasons
selected_year = st.sidebar.multiselect('Year', sorted(all_years), default=recent_years)
search_keyword = st.sidebar.text_input('Search Keyword')

# Load data
data = load_data(selected_year)

# Clean data
data = clean_data(data)

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
    data = load_data(selected_year)
    data = clean_data(data)

st.sidebar.markdown("---")

# Download section
st.sidebar.header("💾 - Download Data")

# Filter data based on user selection
filtered_data = data.copy()
if search_keyword:
    filtered_data = filtered_data[filtered_data['title'].str.contains(search_keyword, case=False) |
                                  filtered_data['public_advisory'].str.contains(search_keyword, case=False)]

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
    if not selected_year:
        st.write("Please select at least one year to view advisories.")
    else:
        st.write(f"Showing advisories for Year: {selected_year}, Keyword: {search_keyword}")

        for index, row in filtered_data.iterrows():
            with st.expander(row['title']):
                st.markdown(f"**Published Date:** {row['published_date']}")
                st.markdown(f"**Summary:**\n{row['public_advisory']}")
                st.markdown(f"**Products:** {row['products']}")
                st.markdown(f"**Vendor:** {row['response_vendors']}")
                st.markdown(f"**URI(s):** {row['response_uris']}")
                st.markdown(f"**Discoverers:** {row['discoverers']}")
                st.markdown(f"**CVSS Score:** {row['cvss_score']}")
                st.markdown(f"**CVEs:** {row['cves']}")
                st.markdown(f"**Response Details:**\n{row['response_texts']}")
                if st.button("Bookmark", key=f"bookmark_{index}"):
                    st.session_state['bookmarks'].append(row.to_dict())

with tab2:
    st.header("Dashboard")
    st.subheader("Number of Advisories per Year")
    advisories_per_year = filtered_data.groupby(filtered_data['published_date'].str[:4]).size().reset_index(name='count')
    fig1 = px.bar(advisories_per_year, x='published_date', y='count', title='Number of Advisories per Year')
    st.plotly_chart(fig1)

    st.subheader("Advisory Distribution by Year")
    fig2 = px.pie(advisories_per_year, names='published_date', values='count', title='Advisory Distribution by Year')
    st.plotly_chart(fig2)

with tab3:
    st.header("Bookmarked Advisories")
    for index, bookmark in enumerate(st.session_state['bookmarks']):
        with st.expander(bookmark['title']):
            st.markdown(f"**Published Date:** {bookmark['published_date']}")
            st.markdown(f"**Summary:**\n{bookmark['public_advisory']}")
            st.markdown(f"**Products:** {bookmark['products']}")
            st.markdown(f"**Vendors:** {bookmark['response_vendors']}")
            st.markdown(f"**URIs:** {bookmark['response_uris']}")
            st.markdown(f"**Discoverers:** {bookmark['discoverers']}")
            st.markdown(f"**CVSS Score:** {bookmark['cvss_score']}")
            st.markdown(f"**CVEs:** {bookmark['cves']}")
            st.markdown(f"**Response Details:**\n{bookmark['response_texts']}")
            if st.button("Remove Bookmark", key=f"remove_{index}"):
                st.session_state['bookmarks'].pop(index)
                st.experimental_rerun()  # Refresh the page to update the bookmark list
