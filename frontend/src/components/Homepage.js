import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const Homepage = () => {
  const [portfolioSymbols, setPortfolioSymbols] = useState({
    user1: [],
    user2: [],
    user3: [],
    user4: [],
    user5: [],
  });
  const [featuredStocks, setFeaturedStocks] = useState([]);

  useEffect(() => {
    const fetchPortfolioSymbols = async () => {
      try {
        const promises = Object.keys(portfolioSymbols).map((user) =>
          axios.get(`http://127.0.0.1:5000/portfolio/${user}`)
        );
        const responses = await Promise.all(promises);

        const updatedPortfolioSymbols = {};
        responses.forEach((response, index) => {
          const user = `user${index + 1}`;
          updatedPortfolioSymbols[user] = response.data.symbols;
        });

        setPortfolioSymbols(updatedPortfolioSymbols);
      } catch (error) {
        console.error("Error fetching portfolio symbols:", error);
      }
    };

    fetchPortfolioSymbols();

    // Set featured stocks
    setFeaturedStocks([
      "AAPL",
      "MSFT",
      "GOOGL",
      "TSLA",
      "NVDA",
      "PYPL",
      "AMZN",
      "MCD",
      "NFLX",
      "AMD",
      "INTC",
      "CRM",
      "DIS",
      "BABA",
      "UBER",
      "SQ",
      "ADBE",
      "PEP",
      "JNJ",
      "V",
      "MA",
      "BAC",
      "WMT",
      "NVAX",
      "PG",
      "KO",
      "T",
      "INTU",
      "IBM",
      "NOW",
    ]);
  }, []);

  return (
    <div>
      <h1>Welcome to WealthWise</h1>
      <p>Your trusted platform for managing your investment portfolio.</p>

      <h2>Featured Stocks</h2>
      <div>
        {featuredStocks.map((stock, index) => (
          <Link key={index} to={`/symbol/${stock}`}>
            <button>{stock}</button>
          </Link>
        ))}
      </div>

      <h2>User Portfolios</h2>
      <div className="portfolio-buttons">
        {Object.keys(portfolioSymbols).map((user) => (
          <Link key={user} to={`/portfolio/${user}`}>
            <button>{user}</button>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Homepage;
