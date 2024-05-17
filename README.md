# ZDI Advisory Explorer

ZDI Advisory Explorer is a Streamlit application designed to help you quickly sort and understand the types of vulnerabilities that bug bounties such as ZDI are looking for. The app allows you to filter, search, and visualize advisories, making it easier to hone in on target applications for auditing N-day and 0-day vulnerabilities.

## Features

- **Filter by Year**: Select multiple years to filter advisories.
- **Keyword Search**: Search advisories by keywords in titles and summaries.
- **Saved Searches**: Save your search filters and quickly apply them later.
- **Bookmark Advisories**: Bookmark specific advisories for quick access.
- **Download Data**: Download filtered advisories as CSV or Excel files.
- **Visualizations**: View interactive charts of the number of advisories per year and their distribution.
- **Expandable Details**: Expand advisories to view detailed information.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/jwalker/zdi_advisory_explorer.git
    cd zdi_advisory_explorer
    ```

2. Create and activate a virtual environment (optional but recommended):
    ```sh
    uv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```sh
    uv pip install -r requirements.txt
    ```

## Usage

### Update the RSS Feeds

1. Run the `update_rss_feeds.py` script to fetch and store the latest advisories:
    ```sh
    python update_rss_feeds.py
    ```

2. Set up a cron job to run the `update_rss_feeds.py` script daily to keep the data up to date. Open the crontab editor:
    ```sh
    crontab -e
    ```

3. Add the following line to schedule the script to run daily at midnight:
    ```sh
    0 0 * * * /usr/bin/python3 /path/to/update_rss_feeds.py
    ```

    Replace `/usr/bin/python3` with the path to your Python interpreter and `/path/to/update_rss_feeds.py` with the path to the script.

### Run the Streamlit App

1. Start the Streamlit app:
    ```sh
    streamlit run app.py
    ```

## About

I created ZDI Advisory Explorer to help quickly sort and understand the types of vulnerabilities that bug bounty programs, such as ZDI, are looking for. The [ZDI advisory section](https://www.zerodayinitiative.com/advisories/published/) on their website allows searching for advisories one year at a time, but provides RSS access for previous years. This tool aggregates these advisories and aids in focusing on target applications for auditing N-day and 0-day vulnerabilities.