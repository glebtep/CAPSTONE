import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

const Homepage = () => {
  const [allStocks, setAllStocks] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredStocks, setFilteredStocks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const parseCSV = (data) => {
      return data
        .split("\n")
        .slice(1)
        .map((line) => {
          const [symbol, name] = line.split(",");
          return { symbol, name, quantity: 0 };
        })
        .filter((stock) => stock.symbol && stock.name);
    };

    const fetchStocks = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/all-stocks");
        const parsedData = parseCSV(response.data);
        setAllStocks(parsedData);
        setFilteredStocks(parsedData);
      } catch (error) {
        console.error("Error fetching stocks:", error);
      }
    };

    fetchStocks();
  }, []);

  const handleSearch = () => {
    const query = searchQuery.toLowerCase();
    const filtered = allStocks.filter(
      (stock) =>
        stock.symbol.toLowerCase().includes(query) ||
        stock.name.toLowerCase().includes(query)
    );
    setFilteredStocks(filtered);
  };

  const addToPortfolio = async (symbol, name, quantity) => {
    // Ensure quantity is a positive number before sending the request
    if (quantity > 0) {
      try {
        await axios.post(
          "http://127.0.0.1:5000/add",
          {
            symbol,
            name,
            quantity,
          },
          {
            headers: {
              // Include the JWT token in the Authorization header
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        navigate("/portfolio"); // Redirect to portfolio page to view added stock
      } catch (error) {
        console.error("Error adding stock to portfolio:", error);
      }
    } else {
      alert("Please enter a valid quantity.");
    }
  };

  const handleLogout = async () => {
    localStorage.removeItem("token");
    navigate("/login"); // Redirect to the login page
  };

  const username = localStorage.getItem("username");

  return (
    <div>
      <div className="greeting">
        Hello 👋, <span className="username">@{username}</span>
      </div>
      <h1 style={{ textAlign: "center" }}>Welcome to WealthWise</h1>
      <p style={{ textAlign: "center" }}>
        Your trusted platform for managing your investment portfolio.
      </p>

      <div>
        <input
          type="text"
          className="stock-search-input"
          placeholder="Search by symbol or name"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      <br></br>
      <Link to="/portfolio">
        <button>My Portfolio</button>
      </Link>
      <button onClick={handleLogout} style={{ float: "right", margin: "10px" }}>
        Logout
      </button>

      <h2>777 Stocks Available:</h2>
      <div>
        {filteredStocks.map((stock, index) => (
          <div
            key={index}
            className="stock-item"
            style={{ marginBottom: "10px" }}
          >
            <Link to={`/symbol/${stock.symbol}`}>
              <button style={{ marginRight: "5px" }}>{stock.symbol}</button>
            </Link>
            <div className="stock-quantity-container">
              <input
                type="number"
                className="stock-quantity-input"
                min="1"
                value={stock.quantity}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || 0;
                  setFilteredStocks((prevStocks) => {
                    return prevStocks.map((prevStock, idx) => {
                      if (idx === index) {
                        return { ...prevStock, quantity: value };
                      }
                      return prevStock;
                    });
                  });
                }}
              />
              <button
                onClick={() =>
                  addToPortfolio(stock.symbol, stock.name, stock.quantity)
                }
              >
                Add to Portfolio
              </button>
            </div>
          </div>
        ))}
      </div>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>About Us</h3>
            <p>
              We are dedicated to providing the best investment portfolio
              management experience. Our platform allows users to track and
              optimize their investments with ease and precision.
            </p>
          </div>
          <div className="footer-section">
            <h3>Contact Info</h3>
            <p>Email: contact@wealthwise.com</p>
            <p>Phone: +123 456 7890</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 WealthWise, Inc. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;
