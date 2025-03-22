import os
import subprocess

# Configuration
SCREAMING_FROG_CLI = "C:\\Program Files (x86)\\Screaming Frog SEO Spider\\ScreamingFrogSEOSpiderCli"
OUTPUT_DIR = "./output"
URLS = [
    "https://www.estateandtrustlawyer.com/",
    "https://www.ocpond.org/",
    "https://soswaxlv.com/"
]

def run_screaming_frog_with_metrics(url, output_dir):
    """
    Runs Screaming Frog CLI for a given URL and exports Core Web Vitals data.
    """
    print(f"Running Screaming Frog CLI for URL: {url}")
    try:
        command = [
            SCREAMING_FROG_CLI,
            "--crawl", url,
            "--headless",
            "--output-folder", output_dir,
            "--export-tabs", "PageSpeed:All",  # Update tab and filter as per configuration
            "--export-format", "csv",
            "--overwrite",
            "--save-crawl"
        ]
        subprocess.run(command, check=True)
        print(f"Screaming Frog CLI completed for {url}. Output saved to {output_dir}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Screaming Frog CLI for {url}: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for url in URLS:
        run_screaming_frog_with_metrics(url, OUTPUT_DIR)

if __name__ == "__main__":
    main()
