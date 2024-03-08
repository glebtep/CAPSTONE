import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link, useParams } from "react-router-dom";

const Portfolio = () => {
  const { user_id } = useParams();
  const [portfolioData, setPortfolioData] = useState(null);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        const response = await axios.get(
          `http://mcsbt-integration-glebtep.oa.r.appspot.com/portfolio/${user_id}`
        );
        setPortfolioData(response.data);
      } catch (error) {
        console.error("Error fetching portfolio data:", error);
      }
    };

    fetchPortfolioData();
  }, [user_id]);

  if (!portfolioData) return <div>Loading...</div>;

  return (
    <div>
      <h1>{user_id} Portfolio</h1>
      <div>
        {Object.entries(portfolioData.portfolio_data).map(
          ([symbol, quantity], index) => (
            <div key={index}>
              <Link to={`/symbol/${symbol}`}>
                <button>{symbol}</button>
              </Link>
              <p>Quantity: {quantity}</p>
            </div>
          )
        )}
      </div>
      <br />
      <p>Total Portfolio Value: {portfolioData.total_portfolio_value}</p>
      <br />
      <Link to="/">Go to Homepage</Link>
    </div>
  );
};

export default Portfolio;
