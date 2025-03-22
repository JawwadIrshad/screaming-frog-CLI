import os
import requests
import gspread
from dotenv import load_dotenv
from datetime import datetime
import logging
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

# Google API Key for PageSpeed Insights
API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")

# Set up logging
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"pagespeed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_pagespeed_metrics(address, strategy):
    """
    Fetch PageSpeed metrics for a given URL and strategy.
    """
    try:
        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {"url": address, "key": API_KEY, "strategy": strategy}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        metrics = {"PSI Status": "Success", "PSI Error": ""}

        # Performance score
        performance_score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", "N/A")
        metrics["Performance Score"] = round(float(performance_score) * 100) if performance_score != "N/A" else "N/A"

        # Lighthouse metrics
        lighthouse_audits = data.get("lighthouseResult", {}).get("audits", {})
        metrics.update({
            "First Contentful Paint Time (ms)": lighthouse_audits.get("first-contentful-paint", {}).get("numericValue", "N/A"),
            "Speed Index Time (ms)": lighthouse_audits.get("speed-index", {}).get("numericValue", "N/A"),
            "Largest Contentful Paint Time (ms)": lighthouse_audits.get("largest-contentful-paint", {}).get("numericValue", "N/A"),
            "Time to Interactive (ms)": lighthouse_audits.get("interactive", {}).get("numericValue", "N/A"),
            "Total Blocking Time (ms)": lighthouse_audits.get("total-blocking-time", {}).get("numericValue", "N/A"),
            "Cumulative Layout Shift": lighthouse_audits.get("cumulative-layout-shift", {}).get("numericValue", "N/A"),
        })

        return metrics

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching metrics for {address} ({strategy}): {e}")
        return {
            "PSI Status": "Error",
            "PSI Error": str(e),
        }

def append_data(sheet, headings, address, metrics, strategy):
    """
    Append metrics dynamically to the sheet, starting from the first empty row.
    """
    try:
        # Find the first empty row
        last_row = len(sheet.get_all_values()) + 1  # Get the next empty row

        # Initialize the row with empty values
        row_data = [""] * len(headings)

        # Populate mandatory fields
        for index, heading in enumerate(headings):
            if heading.lower() == "week date":
                row_data[index] = datetime.now().strftime("%Y-%m-%d")
            elif heading.lower() == "address":
                row_data[index] = address
            elif heading.lower() == "type":
                row_data[index] = strategy.capitalize()
            elif heading in metrics:  # Match metrics dynamically
                value = metrics[heading]
                row_data[index] = round(value, 2) if isinstance(value, float) else value

        # Append row to the sheet
        sheet.insert_row(row_data, last_row)
        logging.info(f"Appended data for Address {address} ({strategy}).")

    except Exception as e:
        logging.error(f"Error appending data to sheet for {address} ({strategy}): {e}")

def process_sheet(spreadsheet_id, worksheet_name):
    """
    Read the sheet and fetch data for each URL.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account_credentials.json", scope)
        client = gspread.authorize(creds)

        # Access the sheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet(worksheet_name)

        # Read headers
        headings = sheet.row_values(1)
        if "Address" not in headings:
            logging.error("No 'Address' column found.")
            return

        # Get Address column
        address_index = headings.index("Address") + 1  # Convert to 1-based index
        addresses = sheet.col_values(address_index)[1:]  # Skip header

        # Process each address
        for address in addresses:
            address = address.strip()
            if not address:
                logging.warning("Skipping empty address.")
                continue

            logging.info(f"Processing Address: {address}")
            for strategy in ["mobile", "desktop"]:
                metrics = fetch_pagespeed_metrics(address, strategy)
                append_data(sheet, headings, address, metrics, strategy)

    except Exception as e:
        logging.error(f"Error processing spreadsheet: {e}")

# Main execution
if __name__ == "__main__":
    SPREADSHEET_ID = "1NgSQbxgI4HWqOreNny2e_XxjlyLLXOTwzZ4vYrrSxuE"
    WORKSHEET_NAME = "Copy of CWV Data Dump"

    logging.info("Script started.")
    try:
        process_sheet(SPREADSHEET_ID, WORKSHEET_NAME)
    except Exception as e:
        logging.error(f"Unexpected error in main execution: {e}")
    logging.info("Script finished.")
