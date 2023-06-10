import requests
import pandas as pd
import os.path

url = 'https://api.synthetix.io/staking-ratio'
headers = {
    'accept': 'application/json'
}

response = requests.get(url, headers=headers)

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

    # Check if the CSV file already exists
    if os.path.isfile('staking_ratio.csv'):
        # Append DataFrame to the existing CSV file
        df.to_csv('staking_ratio.csv', mode='a', header=False, index=False)
    else:
        # Create a new CSV file
        df.to_csv('staking_ratio.csv', index=False)
    print("Staking Data Updated")
else:
    print('Request failed with status code:', response.status_code)
