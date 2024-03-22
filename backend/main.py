from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import requests
from models import db, Portfolio, PortfolioStock, Stock, User
from sqlalchemy.pool import NullPool
import oracledb
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError # i was using it to fix errors in db
from datetime import datetime
import logging

app = Flask(__name__)
bcrypt = Bcrypt(app)
#My secret key (I know it should be hidden, but kept it not to overcomplicate the code):
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

#Add simple message 
@app.route('/')
def homepage():
    return "Welcome to WealthWise - Your trusted platform for managing your investment portfolio"

@app.route('/all-stocks')
def get_all_stocks():
    """Fetches all stocks listing status using a third-party API and streams it back to the client."""
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
@jwt_required()
def get_portfolio():
    """Fetches the current user's portfolio, displaying each stock's symbol, quantity, and acquisition price."""
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=current_user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    portfolio_stocks = PortfolioStock.query.filter_by(portfolio_id=user.portfolios.portfolio_id).all()
    portfolio_data = [{
        "symbol": stock.stock.symbol,
        "quantity": stock.quantity,
        "acquisition_price": stock.acquisition_price
    } for stock in portfolio_stocks]

    return jsonify({"portfolio": portfolio_data})


def get_or_create_stock(symbol, name=None):
    """Utility function to get or create a stock entry."""
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        stock = Stock(symbol=symbol, name=name)
        db.session.add(stock)
        db.session.commit()
    return stock

@app.route('/add', methods=['POST'])
@jwt_required()
def add_stock_to_portfolio():
    """Adds a specified stock to the current user's portfolio."""
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=current_user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    symbol = data.get('symbol')
    name = data.get('name', 'Unknown Stock')  # Provide a default name if not provided
    quantity = data.get('quantity', 0)
    # Default acquisition price and date are set to 0.0 and current date respectively if not provided
    acquisition_price = data.get('acquisition_price', 0.0)
    acquisition_date = data.get('acquisition_date', datetime.utcnow().date())

    if not symbol or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Invalid symbol or quantity"}), 400

    # Use the utility function to get or create the stock
    stock = get_or_create_stock(symbol, name)
    portfolio_stock = PortfolioStock.query.filter_by(portfolio_id=user.portfolios.portfolio_id, stock_id=stock.stock_id).first()

    if portfolio_stock:
        # If the stock already exists in the portfolio, increase the quantity
        portfolio_stock.quantity += quantity
    else:
        # If the stock is not in the portfolio, create a new entry
        portfolio_stock = PortfolioStock(portfolio_id=user.portfolios.portfolio_id, stock_id=stock.stock_id, quantity=quantity, acquisition_price=acquisition_price, acquisition_date=acquisition_date)
        db.session.add(portfolio_stock)

    try:
        db.session.commit()
        return jsonify({"message": "Stock added to portfolio successfully"}), 200
    except Exception as e:
        logging.error(f"Error adding stock to portfolio: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding stock to portfolio"}), 500

    
@app.route('/remove', methods=['POST'])
@jwt_required()
def delete_from_portfolio():
    current_user_id = get_jwt_identity()
    data = request.json
    symbol = data.get('symbol')

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        return jsonify({"error": "Stock not found"}), 404

    # Adjusted from portfolio.id to portfolio.portfolio_id
    portfolio = Portfolio.query.filter_by(user_id=current_user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    # Adjusted from portfolio.id to portfolio.portfolio_id and stock.id to stock.stock_id
    portfolio_stock = PortfolioStock.query.filter_by(portfolio_id=portfolio.portfolio_id, stock_id=stock.stock_id).first()
    if portfolio_stock:
        db.session.delete(portfolio_stock)
        db.session.commit()
        return jsonify({"message": "Stock removed from the portfolio successfully"}), 200
    else:
        return jsonify({"error": "Stock not found in portfolio"}), 404
    

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
    data = request.json
    user = User.query.filter_by(name=data['name']).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400
    
    # Create new User instance
    new_user = User(name=data['name'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    # Automatically create a portfolio for the new user
    new_portfolio = Portfolio(user_id=new_user.user_id)
    db.session.add(new_portfolio)
    db.session.commit()

    return jsonify({'message': 'User and portfolio created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(name=data['name']).first()
    if user and user.check_password(data['password']):
        # Use user.user_id as the JWT identity
        access_token = create_access_token(identity=user.user_id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'Access granted to protected route'})

    
if __name__ == '__main__':
    app.run(debug=True)

