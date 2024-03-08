from flask import Flask, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "09I1ESM2FDLI0Y6D"
STOCK_DATA_URL = "https://www.alphavantage.co/query"
MAX_STOCKS = 11111

DATABASE = {
        "user1": {"symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "PYPL"], "quantities": {"AAPL": 10, "MSFT": 4, "GOOGL": 5, "TSLA": 3, "NVDA": 8, "PYPL": 7} },
        "user2": {"symbols": ["AMZN", "MCD", "NFLX", "AMD", "INTC", "CRM"], "quantities": {"AMZN": 15, "MCD": 10, "NFLX": 8, "AMD": 12, "INTC": 6, "CRM": 9}},
        "user3": {"symbols": ["DIS", "BABA", "UBER", "SQ", "ADBE", "PEP"], "quantities": {"DIS": 20, "BABA": 14, "UBER": 11, "SQ": 8, "ADBE": 15, "PEP": 13}},
        "user4": {"symbols": ["JNJ", "V", "MA", "BAC", "WMT", "NVAX"], "quantities": {"JNJ": 25, "V": 18, "MA": 16, "BAC": 21, "WMT": 23, "NVAX": 11}},
        "user5": {"symbols": ["PG", "KO", "T", "INTU", "IBM", "NOW"], "quantities": {"PG": 22, "KO": 17, "T": 14, "INTU": 19, "IBM": 20, "NOW": 16}}
    }

@app.route('/')
def homepage():
    return "Welcome to WealthWise - Your trusted platform for managing your investment portfolio"

@app.route('/all-stocks')
def get_all_stocks():
    url = f"{STOCK_DATA_URL}?function=LISTING_STATUS&apikey={API_KEY}"
    try:
        def generate():
            with requests.get(url, stream=True) as r:
                r.raise_for_status()  
                lines = r.iter_lines()
                for _ in range(MAX_STOCKS):
                    try:
                        yield next(lines) + b'\n'
                    except StopIteration:
                        break
        return Response(generate(), content_type='text/csv')
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return jsonify(error=str(errh)), errh.response.status_code
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return jsonify(error=str(errc)), 503
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return jsonify(error=str(errt)), 504
    except requests.exceptions.RequestException as err:
        print("Unknown error", err)
        return jsonify(error=str(err)), 500
    
@app.route('/portfolio/<user_id>')
def get_portfolio(user_id):
    if user_id in DATABASE:
        portfolio_data = DATABASE[user_id]["quantities"]
        total_portfolio_value = calculate_total_portfolio_value(portfolio_data)
        return jsonify({
            "user_id": user_id,
            "portfolio_data": portfolio_data,
            "total_portfolio_value": total_portfolio_value
        })
    else:
        return jsonify({"error_message": "User not found"}), 404

@app.route('/symbol/<symbol>')
def get_symbol_data(symbol):

    weekly_api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={API_KEY}"
    global_quote_api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    
    response = requests.get(weekly_api_url)
    if response.status_code == 200:
        symbol_data = response.json()
        if "Weekly Time Series" in symbol_data:
            weekly_data = symbol_data["Weekly Time Series"]
            last_refreshed = symbol_data["Meta Data"]["3. Last Refreshed"]
            latest_close_price = weekly_data[last_refreshed]["4. close"]
            volume = weekly_data[last_refreshed]["5. volume"]
            formatted_data = []
            for date, values in weekly_data.items():
                formatted_data.append({
                    "date": date,
                    "open": values["1. open"],
                    "high": values["2. high"],
                    "low": values["3. low"],
                    "close": values["4. close"]
                })
            return jsonify({
                "symbol": symbol,
                "data": formatted_data,
                "last_refreshed": last_refreshed,
                "latest_close_price": latest_close_price,
                "volume": volume
            })
        elif "Error Message" in symbol_data:
            return jsonify({"error_message": symbol_data["Error Message"]}), 400
    
    response = requests.get(global_quote_api_url)
    if response.status_code == 200:
        symbol_data = response.json()
        if "Global Quote" in symbol_data:
            last_refreshed = symbol_data["Global Quote"]["07. latest trading day"]
            latest_close_price = symbol_data["Global Quote"]["05. price"]
            volume = symbol_data["Global Quote"]["06. volume"]
            formatted_data = [{
                "date": last_refreshed,
                "open": symbol_data["Global Quote"]["02. open"],
                "high": symbol_data["Global Quote"]["03. high"],
                "low": symbol_data["Global Quote"]["04. low"],
                "close": latest_close_price
            }]
            return jsonify({
                "symbol": symbol,
                "data": formatted_data,
                "last_refreshed": last_refreshed,
                "latest_close_price": latest_close_price,
                "volume": volume
            })
        elif "Error Message" in symbol_data:
            return jsonify({"error_message": symbol_data["Error Message"]}), 400
    
    return jsonify({"error_message": "Failed to fetch data from Alpha Vantage API"}), 500

# Function to calculate portfolio value
def calculate_total_portfolio_value(portfolio_data):
    total_value = 0
    for symbol, quantity in portfolio_data.items():
        latest_close_price = get_latest_close_price(symbol)
        if latest_close_price is not None:
            total_value += latest_close_price * quantity
    return total_value

# Function to fetch the latest close price of a symbol
def get_latest_close_price(symbol):
    global_quote_api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(global_quote_api_url)
    if response.status_code == 200:
        symbol_data = response.json()
        if "Global Quote" in symbol_data:
            latest_close_price = float(symbol_data["Global Quote"]["05. price"])
            return latest_close_price
    return None

if __name__ == '__main__':
    app.run(debug=True)
