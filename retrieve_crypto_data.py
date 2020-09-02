from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

cmc = requests.get('https://coinmarketcap.com/')
soup = BeautifulSoup(cmc.content, 'html.parser')

data = soup.find('script', id="__NEXT_DATA__", type="application/json")

coins = {}
slugs = {}
coin_data = json.loads(data.contents[0])
listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']

historical_list = []

for i in listings:
    coins[str(i['id'])] = i['slug']
    slugs[i['slug']] = str(i['id'])

# https://coinmarketcap.com/currencies/[slug]/historical-data/?start=[YYYYMMDD]&end=[YYYYMMDD]

for i in coins:
    page = requests.get(f'https://coinmarketcap.com/currencies/{coins[i]}/historical-data/?start=20200101&end=20200630')
    soup = BeautifulSoup(page.content, 'html.parser')
    data = soup.find('script', id="__NEXT_DATA__", type="application/json")
    if data is not None:
        historical_data = json.loads(data.contents[0])
        if str(i) in historical_data['props']['initialState']['cryptocurrency']['ohlcvHistorical']:
            quotes = historical_data['props']['initialState']['cryptocurrency']['ohlcvHistorical'][i]['quotes']
            name = historical_data['props']['initialState']['cryptocurrency']['ohlcvHistorical'][i]['name']
            symbol = historical_data['props']['initialState']['cryptocurrency']['ohlcvHistorical'][i]['symbol']
            historical_list.append((quotes, name, symbol))

market_cap = []
volume = []
high = []
low = []
open = []
timestamp = []
name = []
symbol = []
# slug = []

for data in historical_list:
    quotes, curr_name, curr_symbol = data
    # curr_slug = slugs[curr_name.lower()]
    for j in quotes:
        market_cap.append(j['quote']['USD']['market_cap'])
        volume.append(j['quote']['USD']['volume'])
        high.append(j['quote']['USD']['high'])
        low.append(j['quote']['USD']['low'])
        open.append(j['quote']['USD']['open'])
        timestamp.append(j['quote']['USD']['timestamp'])
        name.append(curr_name)
        symbol.append(curr_symbol)
        # slug.append(curr_slug)

df = pd.DataFrame(columns=['marketcap', 'volume', 'high', 'low', 'open', 'timestamp', 'name', 'symbol'])
df['marketcap'] = market_cap
df['volume'] = volume
df['high'] = high
df['low'] = low
df['open'] = open
df['timestamp'] = timestamp
df['name'] = name
df['symbol'] = symbol
# df['slug'] = slug

df.to_csv('cryptos.csv', index=False)
