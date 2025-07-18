import requests
import time
import statistics
from datetime import datetime, timedelta

COIN = 'bitcoin'
CURRENCY = 'usd'
THRESHOLD_PERCENT = 1.5  # % зміни для "тривожного" стану
INTERVAL_MINUTES = 10
CHECK_PERIOD_HOURS = 1

def fetch_prices(coin: str, currency: str, interval_minutes: int, hours: int):
    end_time = int(time.time())
    start_time = end_time - hours * 3600
    url = f'https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range'
    params = {
        'vs_currency': currency,
        'from': start_time,
        'to': end_time
    }

    response = requests.get(url, params=params)
    data = response.json()

    prices = data.get('prices', [])
    sampled_prices = []

    last_time = 0
    for timestamp, price in prices:
        if timestamp - last_time >= interval_minutes * 60 * 1000:
            sampled_prices.append(price)
            last_time = timestamp

    return sampled_prices

def analyze_volatility(prices, threshold_percent):
    if len(prices) < 2:
        return "Недостатньо даних для аналізу."

    percent_changes = [
        abs((prices[i] - prices[i - 1]) / prices[i - 1]) * 100
        for i in range(1, len(prices))
    ]
    max_change = max(percent_changes)
    avg_change = statistics.mean(percent_changes)

    if max_change > threshold_percent:
        return f"🚨 Ринок активний! Макс. зміна: {max_change:.2f}%"
    else:
        return f"😴 Все спокійно. Макс. зміна: {max_change:.2f}%"

def main():
    print(f"⏳ Аналізуємо спокійність ринку {COIN.upper()} за останні {CHECK_PERIOD_HOURS} год...")
    try:
        prices = fetch_prices(COIN, CURRENCY, INTERVAL_MINUTES, CHECK_PERIOD_HOURS)
        result = analyze_volatility(prices, THRESHOLD_PERCENT)
        print(result)
    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == "__main__":
    main()

