import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const MyPortfolio = () => {
  const [portfolio, setPortfolio] = useState([]);
  const [totalPortfolioValue, setTotalPortfolioValue] = useState(0);

  const getLatestClosePrice = useCallback(async (symbol) => {
    try {
      const response = await axios.get(
        `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=09I1ESM2FDLI0Y6D`
      );
      const latestClosePrice = response.data["Global Quote"]["05. price"];
      return parseFloat(latestClosePrice);
    } catch (error) {
      console.error(`Error fetching latest close price for ${symbol}:`, error);
      return 0; // Return 0 as a fallback value if an error occurs
    }
  }, []); // getLatestClosePrice has no dependencies

  const calculateTotalPortfolioValue = useCallback(
    async (portfolio) => {
      let totalValue = 0;
      for (const item of portfolio) {
        const latestClosePrice = await getLatestClosePrice(item.symbol);
        totalValue += latestClosePrice * item.quantity;
      }
      setTotalPortfolioValue(totalValue);
    },
    [getLatestClosePrice]
  ); // calculateTotalPortfolioValue depends on getLatestClosePrice

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        const response = await axios.get(
          `http://mcsbt-integration-glebtep.oa.r.appspot.com/portfolio`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        const portfolioData = response.data.portfolio || [];
        setPortfolio(portfolioData);
        calculateTotalPortfolioValue(portfolioData);
      } catch (error) {
        console.error("Error fetching portfolio data:", error);
      }
    };

    fetchPortfolioData();
  }, [calculateTotalPortfolioValue]); // useEffect depends on calculateTotalPortfolioValue

  const deleteStock = async (symbol) => {
    try {
      await axios.post(
        `http://mcsbt-integration-glebtep.oa.r.appspot.com/delete-from-portfolio`,
        {
          symbol,
        }
      );
      const updatedPortfolio = portfolio.filter(
        (item) => item.symbol !== symbol
      );
      setPortfolio(updatedPortfolio);
      calculateTotalPortfolioValue(updatedPortfolio); // Recalculate total value after deletion
    } catch (error) {
      console.error("Error deleting stock:", error);
    }
  };

  const addMoreStock = async (symbol, quantity) => {
    try {
      await axios.post(
        `http://mcsbt-integration-glebtep.oa.r.appspot.com/add-to-portfolio`,
        {
          symbol,
          quantity,
        }
      );
      const updatedPortfolio = portfolio.map((item) => {
        if (item.symbol === symbol) {
          return { ...item, quantity: item.quantity + quantity };
        }
        return item;
      });
      setPortfolio(updatedPortfolio);
      calculateTotalPortfolioValue(updatedPortfolio); // Recalculate total value after adding
    } catch (error) {
      console.error("Error adding more stock:", error);
    }
  };

  return (
    <div className="main-content">
      <h1 style={{ textAlign: "center" }}>Welcome to WealthWise</h1>
      <p style={{ textAlign: "center" }}>
        Your trusted platform for managing your investment portfolio.
      </p>
      <h2 style={{ textAlign: "center" }}>My Portfolio</h2>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {portfolio.map((item, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <Link to={`/symbol/${item.symbol}`}>
              <button style={{ marginRight: "5px" }}>{item.symbol}</button>
            </Link>
            <span style={{ marginRight: "15px" }}>
              Quantity: {item.quantity}
            </span>
            <button onClick={() => addMoreStock(item.symbol, 1)}>
              Add More
            </button>
            <button onClick={() => deleteStock(item.symbol)}>Delete</button>
          </div>
        ))}
      </div>
      <br />
      <p style={{ textAlign: "center" }}>
        Total Portfolio Value: ${totalPortfolioValue.toFixed(2)}
      </p>
      <br />
      <Link to="/">
        <button style={{ cursor: "pointer" }}>Go to Homepage</button>
      </Link>
    </div>
  );
};

export default MyPortfolio;
