import requests
import json
import os
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

stock_endpoint = "https://www.alphavantage.co/query"
stock_key = os.getenv("STOCK_KEY")
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_key,
}

news_endpoint = "https://newsapi.org/v2/everything"
news_key = os.getenv("NEWS_KEY")
news_params = {
    "apiKey": news_key,
    "q": f"{COMPANY_NAME} stock",
    "language": "en",
    "sortBy": "relevancy"
}

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")


def write_data():
    stock_response = requests.get(stock_endpoint, stock_params)
    stock_response.raise_for_status()

    with open('stock_data.json', 'w') as stock_json:
        json.dump(stock_response.json(), stock_json, indent=4)

    news_response = requests.get(news_endpoint, news_params)
    news_response.raise_for_status()

    with open('news_data.json', 'w') as news_json:
        json.dump(news_response.json(), news_json, indent=4)


def get_data():
    with open('stock_data.json', 'r') as stock_json:
        stock_data = json.load(stock_json)

    with open('news_data.json', 'r') as news_json:
        news_data = json.load(news_json)

    return stock_data, news_data


def report_stock_change(day_before_yesterday_close: float, yesterday_open: float):
    percent_change = ((yesterday_open - day_before_yesterday_close) / day_before_yesterday_close) * 100
    # Above we have newer price first that way we ensure that we are measuring the percent change of the new price relative to the old one.
    # Newer price minus the older price, so you can see how much the price has gone up (or down) from the older value.
    # The older price is used as the base or reference point, meaning the percent change tells you how much the new price has changed as a proportion of the older price.

    # Use absolute value to check if the change is 5% or more
    print(f"Percent change is: {abs(percent_change):.2f}")
    if abs(percent_change) >= 5:
        print("Get news!")
        return True
    else:
        print("No significant change in price. Not getting news.")
        return False


# write_data()
# commented out so as to not keep making API requests

stock_data = get_data()[0]
print(stock_data)
news_data = get_data()[1]
print(news_data)


stock_data = list(stock_data["Time Series (Daily)"].values())
print(stock_data)



for i in range(2):
    for key, value in (stock_data[i].items()):
        if (i == 0 and key == "1. open") or (i==1 and key == "4. close"):
            print(f"{key, value}")



yesterday_opening_price = (stock_data[0]["1. open"])  # yesterday's opening price
yesterday_opening_price = round(float(yesterday_opening_price), 2)
print(f"Yesterday's opening price: {yesterday_opening_price}")

day_before_yesterday_closing_price = (stock_data[1]["4. close"])  # day before yesterday closing price
day_before_yesterday_closing_price = round(float(day_before_yesterday_closing_price), 2)
print(f"Day before yesterday closing price: {day_before_yesterday_closing_price}")

percent_change = ((yesterday_opening_price - day_before_yesterday_closing_price) / day_before_yesterday_closing_price) * 100
percent_change = abs(percent_change)

if report_stock_change(day_before_yesterday_close=day_before_yesterday_closing_price, yesterday_open=yesterday_opening_price):
    print(f"Here are some possible news articles explaining the price change of {COMPANY_NAME}")
    for i in range(3):
        print(news_data["articles"][i]["title"])
        print(news_data["articles"][i]["url"])

    if yesterday_opening_price > day_before_yesterday_closing_price:
        body = f"🤑 {COMPANY_NAME} is up today by {percent_change}%!" \
               f"Headline: {news_data['articles'][0]['title']}"

    else:
        body = f"🔻 {COMPANY_NAME} is down today by {percent_change}%!" \
               f"Headline: {news_data['articles'][0]['title']}"

""" 
    Optionally can send text message to someone to alert them of stock price changes!

    client = Client(account_sid, auth_token)
    message = client.messages.create(from_="+18555421359", body=body, to=os.getenv("PHONE_NUM"))
    print(f"SID: {message.sid} STATUS: {message.status}")
"""

