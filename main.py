import subprocess
import os
import pandas as pd
import logging
from datetime import datetime

# Configure paths and settings
current_directory = "D:\\Screaming-Frog-Through-CLI"  # Your working directory
urls_file = os.path.join(current_directory, "urls.csv")  # CSV file containing URLs to crawl
output_folder = os.path.join(current_directory, "output")  # Folder for Screaming Frog output files
logs_folder = os.path.join(current_directory, "logs")  # Folder for log files
log_file = os.path.join(logs_folder, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
excel_file = os.path.join(current_directory, "screamingfrog_output.xlsx")  # Final Excel file

# Correct Screaming Frog CLI executable path
screaming_frog_cli = "C:\\Program Files\\Screaming Frog SEO Spider\\screamingfrogseospidercli.exe"

# Ensure output and logs folders exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(logs_folder, exist_ok=True)

# Configure logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

# Function to run Screaming Frog CLI for a given URL
def run_screaming_frog(url):
    try:
        logger.info(f"Starting crawl for: {url}")
        command = [
            screaming_frog_cli,
            "--crawl", url,
            "--headless",  # Run in headless mode (no GUI)
            "--output-folder", output_folder,
            "--export-tabs", "InternalAll",  # Export all internal URLs as a CSV
            "--save-crawl"  # Save the crawl file for later review
        ]
        subprocess.run(command, check=True)  # Removed `run=True` parameter
        logger.info(f"Crawl completed for: {url}")
    except FileNotFoundError:
        logger.error(f"Error: Screaming Frog CLI not found at {screaming_frog_cli}. Check the path.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error crawling {url}: {e}")
    except PermissionError:
        logger.error("Error: Permission denied while accessing files or folders. Try running as Administrator.")
    except Exception as e:
        logger.exception(f"Unexpected error crawling {url}: {e}")

# Function to automate crawling multiple URLs
def crawl_all_urls():
    logger.info("Starting batch crawl...")
    try:
        if not os.path.exists(urls_file):
            raise FileNotFoundError(f"The file '{urls_file}' does not exist.")
        
        urls_df = pd.read_csv(urls_file)
        if "URL" not in urls_df.columns:
            raise ValueError("The CSV file must have a 'URL' column.")
        
        urls = urls_df["URL"].dropna().tolist()
        if not urls:
            logger.warning("No URLs found in the CSV file. Aborting crawl.")
            return

        for url in urls:
            run_screaming_frog(url)
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except PermissionError:
        logger.error(f"Permission denied while accessing '{urls_file}'. Ensure it is readable.")
    except Exception as e:
        logger.exception(f"Error reading the CSV file: {e}")
    logger.info("Batch crawl completed!")

# Combine exported data into an Excel workbook
def export_to_excel():
    logger.info("Exporting data to Excel...")
    writer = pd.ExcelWriter(excel_file, engine='openpyxl')
    has_data = False  # Flag to check if data exists

    for file in os.listdir(output_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(output_folder, file)
            try:
                sheet_name = os.path.splitext(file)[0][:31]  # Limit to 31 chars for Excel
                df = pd.read_csv(file_path)
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    logger.info(f"Added {file} to Excel sheet: {sheet_name}")
                    has_data = True
            except Exception as e:
                logger.exception(f"Error processing {file}: {e}")

    if has_data:
        writer.save()
        logger.info(f"Data exported to {excel_file}")
    else:
        logger.warning("No data to export. Skipping Excel creation.")

# Main workflow
if __name__ == "__main__":
    # Step 1: Crawl all URLs
    crawl_all_urls()

    # Step 2: Export results to Excel
    export_to_excel()
