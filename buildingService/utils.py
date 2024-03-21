import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

def update_address_abbreviations():
    url = 'https://pe.usps.com/text/pub28/28apc_002.htm'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects encountered. The website may be preventing automated access.")
        return

    html_content = response.text
    soup = BeautifulSoup(html_content, 'lxml')

    # Find the specific table by class name or ID and parse it with pandas
    # We use StringIO here to avoid the FutureWarning
    table_html = str(soup.find('table', {'id': 'ep533076'}))
    df = pd.read_html(StringIO(table_html), header=0)[0]

    # Check the number of columns to avoid the ValueError
    if len(df.columns) == 3:
        # Convert all text to lowercase
        df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

        # Create a dictionary where the key is the standard abbreviation and the value is a list of common names
        abbr_dict = (
            df.groupby('Postal Service Standard Suffix Abbreviation')['Commonly Used Street Suffix or Abbreviation']
            .apply(list)
            .to_dict()
        )
        
        return abbr_dict
