from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import generate_password_hash, checkpytpassword_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationship to Portfolio
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8') if isinstance(generate_password_hash(password), bytes) else generate_password_hash(password)

    def check_password(self, password):
        # Check the entered password against the stored hash
        return check_password_hash(self.password_hash, password)

class Stock(db.Model):
    __tablename__ = 'stock'
    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationship to PortfolioStock
    portfolio_stocks = db.relationship('PortfolioStock', backref='stock', lazy=True)

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    portfolio_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to PortfolioStock
    portfolio_stocks = db.relationship('PortfolioStock', backref='portfolio', lazy=True)

class PortfolioStock(db.Model):
    __tablename__ = 'portfolio_stocks'
    portfolio_stock_id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    acquisition_price = db.Column(db.Float, nullable=False)
    acquisition_date = db.Column(db.Date, nullable=False)