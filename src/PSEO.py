import os
import pandas as pd
from datetime import datetime
import logging

# Setup logging
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"actors_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# File paths
input_file = "Copy_of_Top_500_Actors_and_Actresses.xlsx"  # Replace with your input file
output_file = "Actors_Actresses_Analysis.xlsx"  # Output file

try:
    # Load the input data
    logging.info("Reading input Excel file.")
    df_input = pd.read_excel(input_file, sheet_name="Copy of Top 500 Actors and Actresses")
    logging.info(f"Loaded sheet: 'Copy of Top 500 Actors and Actresses'")

    # Extract the celebrity names from column A
    logging.info("Extracting celebrity names from Column A.")
    celebrity_names = df_input.iloc[:, 0].dropna()  # Assuming the names are in Column A

    # Define the headings for the output sheet
    output_columns = [
        "Celebrity Name", "Category", "Gender", "Tags", "Content",
        "Meta Title", "Meta Description", "Featured Image Link", "Post Link",
        "Date", "Anchor Text", "NAME", "MAIN CATEGORY", "SUB-CATEGORY", "Updated"
    ]

    # Initialize the output DataFrame
    output_df = pd.DataFrame(columns=output_columns)

    # Populate the DataFrame with placeholder data
    logging.info("Populating data for each celebrity.")
    for name in celebrity_names:
        # Placeholder data
        category = "Actor/Actress"
        gender = "Unknown"  # Optionally replace with logic to detect gender
        tags = f"{name}, Celebrity, Movies, TV"
        content = f"This is a placeholder biography for {name}."
        meta_title = f"{name} - Biography and Career"
        meta_description = f"Explore {name}'s life, career, and achievements in the entertainment industry."
        featured_image_link = "https://via.placeholder.com/150"  # Replace with actual image link if available
        post_link = f"https://www.imdb.com/list/ls008474654/{name.replace(' ', '_')}"  # Replace with actual post link if available
        current_date = datetime.now().strftime("%Y-%m-%d")
        main_category = "Entertainment"
        sub_category = "Movies/TV"
        updated_date = current_date

        # Append the row to the output DataFrame
        output_df = output_df.append({
            "Celebrity Name": name,
            "Category": category,
            "Gender": gender,
            "Tags": tags,
            "Content": content,
            "Meta Title": meta_title,
            "Meta Description": meta_description,
            "Featured Image Link": featured_image_link,
            "Post Link": post_link,
            "Date": current_date,
            "Anchor Text": name,
            "NAME": name,
            "MAIN CATEGORY": main_category,
            "SUB-CATEGORY": sub_category,
            "Updated": updated_date
        }, ignore_index=True)

    # Save the output DataFrame to an Excel file
    logging.info("Saving the output data to an Excel file.")
    output_df.to_excel(output_file, index=False)
    logging.info(f"Analysis completed. Data saved to {output_file}")

except Exception as e:
    logging.error(f"An error occurred: {e}")
    print(f"An error occurred. Check the logs for more details: {log_file}")
