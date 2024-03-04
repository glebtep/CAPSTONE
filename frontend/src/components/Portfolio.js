import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link, useParams } from "react-router-dom";

const Portfolio = () => {
  const { user_id } = useParams();
  const [symbols, setSymbols] = useState([]);
  const [totalPortfolioValue, setTotalPortfolioValue] = useState(null);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/portfolio/${user_id}`
        );
        setSymbols(response.data.symbols);
        setTotalPortfolioValue(response.data.total_portfolio_value);
      } catch (error) {
        console.error("Error fetching portfolio data:", error);
      }
    };

    fetchPortfolioData();
  }, [user_id]);

  return (
    <div>
      <h1>{user_id} Portfolio</h1>
      <div>
        {symbols.map((symbol, index) => (
          <Link key={index} to={`/symbol/${symbol}`}>
            <button>{symbol}</button>
          </Link>
        ))}
      </div>
      <br />
      {totalPortfolioValue && (
        <p>Total Portfolio Value: {totalPortfolioValue}</p>
      )}
      <br />
      <Link to="/">Go to Homepage</Link>
    </div>
  );
};

export default Portfolio;
