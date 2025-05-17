from flask import Flask, render_template
import requests
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from flask import send_file

app = Flask(__name__)

API_URL = "https://data.gov.gr/api/v1/query/minedu_students_school"
API_KEY = "061e247912117b07f19ef0b093f84d5a8549a765"  # Replace with your actual API key from data.gov.gr
HEADERS = {"Authorization": f"Token {API_KEY}"}

def fetch_all_data():
    """Fetches all data from the API."""
    all_data = []
    offset = 0
    limit = 100  # Fetch data in chunks

    while True:
        params = {"offset": offset, "limit": limit}
        response = requests.get(API_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Error fetching data at offset {offset}: {response.status_code} - {response.text}")
            break

        data = response.json()
        if not data:
            break  # No more data

        all_data.extend(data)
        offset += limit

    return all_data

@app.route("/")
def index():
    data = fetch_all_data()

    # Sort by total students (boys + girls) and get top 10 schools for the chart
    for item in data:
        item["num_students"] = item.get("registered_students_boys", 0) + item.get("registered_students_girls", 0)

    sorted_data = sorted(data, key=lambda x: x["num_students"], reverse=True)[:10]
    labels = [item["school_name"] for item in sorted_data]
    values = [item["num_students"] for item in sorted_data]

    return render_template("chart.html", labels=labels, values=values)

@app.route("/export/csv")
def export_csv():
    """Exports all fetched data to a CSV file."""
    all_data = fetch_all_data()
    df = pd.DataFrame(all_data)
    csv_io = BytesIO()
    df.to_csv(csv_io, index=False, encoding='utf-8')
    csv_io.seek(0)
    return send_file(
        csv_io,
        mimetype='text/csv',
        as_attachment=True,
        download_name='school_data.csv'
    )

@app.route("/export/xlsx")
def export_xlsx():
    """Exports all fetched data to an XLSX file."""
    all_data = fetch_all_data()
    df = pd.DataFrame(all_data)
    excel_io = BytesIO()
    wb = Workbook()
    ws = wb.active
    for r_idx, row in enumerate(dataframe_to_rows(df, header=True, index=False)):
        ws.append(row)
    wb.save(excel_io)
    excel_io.seek(0)
    return send_file(
        excel_io,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='school_data.xlsx'
    )

if __name__ == "__main__":
    app.run(debug=True)