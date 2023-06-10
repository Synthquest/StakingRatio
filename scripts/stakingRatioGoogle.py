import os
from dotenv import load_dotenv
import requests
import pandas as pd
import json

# Load environment variables
load_dotenv()

# API key for Google Sheets API
api_key = os.getenv('Google-Key')

url = 'https://api.synthetix.io/staking-ratio'
params = {'key': api_key}

response = requests.get(url, params=params)
print(response)

if response.status_code == 200:
    data = response.json()

    # Normalize 'stakedSnx' object into separate columns since it comes in as a nested object
    stakedSnx_df = pd.json_normalize(data['stakedSnx'])
    del data['stakedSnx']  # Remove the original 'stakedSnx' object

    # Create DataFrame from the remaining data
    df = pd.DataFrame(data, index=[0])

    # Merge the DataFrames
    df = pd.concat([df, stakedSnx_df], axis=1)

    # Convert Unix timestamp to UTC
    df['timestamp_utc'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC')
    
    # Convert Timestamp object to string
    df['timestamp_utc'] = df['timestamp_utc'].astype(str)

    # Define the spreadsheet and sheet names
    spreadsheet_name = 'Staking Ratio'
    sheet_name = 'Data'

    # Prepare the data for writing to the Google Sheet
    values = [df.columns.tolist()] + df.values.tolist()

    # Create the request body
    body = {
        'values': values
    }

    # Convert the request body to JSON
    json_body = json.dumps(body)

    # Create the URL for the API request
    spreadsheet_id = '10VUJhwrbpHLoRMfvd8Fss4U9wsuO7l9pBZqlie4GjHI'  # Extracted from the provided URL
    range_ = f'{sheet_name}!A1'

    # Create the URL for the API request
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_}'

    # Set the API key in the request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Send the PUT request to update the Google Sheet
    response = requests.put(url, headers=headers, data=json_body)

    if response.status_code == 200:
        print('DataFrame successfully appended to Google Sheet')
    else:
        print('Request failed with status code:', response.status_code)
else:
    print('Request failed with status code:', response.status_code)
