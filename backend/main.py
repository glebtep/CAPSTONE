from flask import Flask, jsonify, Response, request, session
from flask_cors import CORS
import requests
from models import db, Portfolio, PortfolioStock, Stock, User
from sqlalchemy.pool import NullPool
import oracledb
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = b'0S=\xa0\xa8trRj\x8e\xe5\xf2\x87\xefLC\xbb\x08\xed\xf1\xccF\xe8\xa5'
jwt = JWTManager(app) 

CORS(app)

#Copied from LAB
un = 'MYOWNSH'
pw = 'AaZZ0r_cle#1'
dsn = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=g2148b2691cdb11_capstone_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

pool = oracledb.create_pool(user=un, password=pw,
                            dsn=dsn)

app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+oracledb://{un}:{pw}@{dsn}'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'creator': pool.acquire,
    'poolclass': NullPool
}
app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)

with app.app_context():
    db.create_all()

API_KEY = "09I1ESM2FDLI0Y6D"
STOCK_DATA_URL = "https://www.alphavantage.co/query"
MAX_STOCKS = 777

#Dynamic portfolio
portfolio = []

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
    
@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify({"portfolio": portfolio})

@app.route('/add-to-portfolio', methods=['POST'])
def add_to_portfolio():
    data = request.json
    symbol = data.get('symbol')
    quantity = int(data.get('quantity', 0))

    if not symbol or quantity <= 0:
        return jsonify({"error": "Invalid symbol or quantity"}), 400

    stock = next((item for item in portfolio if item['symbol'] == symbol), None)

    if stock:
        # Update quantity for the existing stock
        stock['quantity'] += quantity
    else:
        # Add a new stock to the portfolio
        portfolio.append({'symbol': symbol, 'quantity': quantity})

    return jsonify({"message": "Stock updated in the portfolio successfully"}), 200

@app.route('/delete-from-portfolio', methods=['POST'])
def delete_from_portfolio():
    data = request.json
    symbol = data.get('symbol')

    stock_index = next((index for (index, d) in enumerate(portfolio) if d['symbol'] == symbol), None)

    if stock_index is not None:
        # Remove the stock from the portfolio
        del portfolio[stock_index]
        return jsonify({"message": "Stock removed from the portfolio successfully"}), 200
    else:
        return jsonify({"error": "Stock not found in the portfolio"}), 404
    

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

#AUTHENTIFICATION 

@app.route('/signup', methods=['POST'])
def signup():
    print("Login route hit")
    data = request.json
    user = User.query.filter_by(name=data['name']).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(name=data['name'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(name=data['name']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=data['name'])
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'Access granted to protected route'})

if __name__ == '__main__':
    app.run(debug=True)
