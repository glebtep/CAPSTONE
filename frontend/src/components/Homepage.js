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
  const [allStocks, setAllStocks] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredStocks, setFilteredStocks] = useState([]);

  useEffect(() => {
    const parseCSV = (data) => {
      return data
        .split("\n")
        .slice(1)
        .map((line) => {
          const [symbol, name] = line.split(",");
          return { symbol, name };
        })
        .filter((stock) => stock.symbol && stock.name);
    };

    const fetchStocks = async () => {
      try {
        const response = await axios.get(
          "http://mcsbt-integration-glebtep.oa.r.appspot.com/all-stocks"
        );
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

  return (
    <div>
      <h1>Welcome to WealthWise</h1>
      <p>Your trusted platform for managing your investment portfolio.</p>

      <div>
        <input
          type="text"
          placeholder="Search by symbol or name"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      <h2>User Portfolios</h2>
      <div className="portfolio-buttons">
        {Object.keys(portfolioSymbols).map((user) => (
          <Link key={user} to={`/portfolio/${user}`}>
            <button>{user}</button>
          </Link>
        ))}
      </div>

      <h2>11,111 Stocks available: </h2>
      <div>
        {filteredStocks.map((stock, index) => (
          <Link key={index} to={`/symbol/${stock.symbol}`}>
            <button>{stock.symbol}</button>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Homepage;
