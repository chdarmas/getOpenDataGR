import requests
import pandas as pd
import json

api_url = "https://data.gov.gr/api/v1/query/hyperion"
api_key = "061e247912117b07f19ef0b093f84d5a8549a765"
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    data = response.json()

    if data:
        df = pd.DataFrame(data)

        # Export to CSV
        csv_filename = "hyperion_data.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Data successfully exported to {csv_filename}")

        # Export to Excel (requires openpyxl or xlsxwriter)
        excel_filename = "hyperion_data.xlsx"
        try:
            df.to_excel(excel_filename, index=False)
            print(f"Data successfully exported to {excel_filename}")
        except ImportError as e:
            print(f"Error exporting to Excel: {e}. Please install 'openpyxl' or 'xlsxwriter' to export to Excel.")

    else:
        print("No data received from the API.")

except requests.exceptions.RequestException as e:
    print(f"Error during API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")