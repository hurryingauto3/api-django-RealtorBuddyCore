import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError
from APIRealtorBuddyCore.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def get_latest_file_from_s3(bucket):
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        response = s3_client.list_objects_v2(Bucket=bucket)
        files = response.get('Contents', [])
        if not files:
            return None
        latest_file = max(files, key=lambda x: x['LastModified'])
        return latest_file['Key']
    except NoCredentialsError:
        print("Credentials not available")
        return None

def download_file_from_s3(bucket, key, download_path):
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        s3_client.download_file(bucket, key, download_path)
        return True
    except Exception as e:
        print(f"Error downloading the file: {e}")
        return False

def update_address_abbreviations():
    url = "https://pe.usps.com/text/pub28/28apc_002.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.TooManyRedirects:
        print(
            "Too many redirects encountered. The website may be preventing automated access."
        )
        return

    html_content = response.text
    soup = BeautifulSoup(html_content, "lxml")

    # Find the specific table by class name or ID and parse it with pandas
    # We use StringIO here to avoid the FutureWarning
    table_html = str(soup.find("table", {"id": "ep533076"}))
    df = pd.read_html(StringIO(table_html), header=0)[0]

    # Check the number of columns to avoid the ValueError
    if len(df.columns) == 3:
        # Convert all text to lowercase
        df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

        # Create a dictionary where the key is the standard abbreviation and the value is a list of common names
        abbr_dict = (
            df.groupby("Postal Service Standard Suffix Abbreviation")[
                "Commonly Used Street Suffix or Abbreviation"
            ]
            .apply(list)
            .to_dict()
        )

        return abbr_dict
