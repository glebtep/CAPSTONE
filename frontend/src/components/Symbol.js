import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function StockGraph({ data }) {
  const highValues = data.map((entry) => entry.high);
  const lowValues = data.map((entry) => entry.low);
  const minValue = Math.min(...lowValues);
  const maxValue = Math.max(...highValues);

  // Adjusting the y-axis domain to include some padding
  const padding = 10; // Adjust this value as needed
  const yAxisDomain = [minValue - padding, maxValue + padding];

  return (
    <ResponsiveContainer width="100%" aspect={3}>
      <LineChart
        width={500}
        height={300}
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis domain={yAxisDomain} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="open" stroke="#A8A9AD" name="Open" />
        <Line type="monotone" dataKey="high" stroke="#FFD700" name="High" />
        <Line type="monotone" dataKey="low" stroke="#800020" name="Low" />
        <Line type="monotone" dataKey="close" stroke="#0F52BA" name="Close" />
      </LineChart>
    </ResponsiveContainer>
  );
}

function Symbol() {
  const { symbol } = useParams();
  const [symbolData, setSymbolData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/symbol/${symbol}`
        );
        const sortedData = response.data.data.reverse();
        setSymbolData({ ...response.data, data: sortedData });
      } catch (error) {
        console.error("Failed to fetch symbol data", error);
      }
    };

    fetchData();
  }, [symbol]);

  if (!symbolData) return <div>Loading...</div>;

  return (
    <div>
      <h1>Stock Details for: {symbolData.symbol}</h1>
      <p>Last Refreshed: {symbolData.last_refreshed}</p>
      <p>Latest Close Price: {symbolData.latest_close_price}</p>
      <p>Volume: {symbolData.volume}</p>
      <h2>Stock Price History</h2>
      <StockGraph data={symbolData.data} />
      <Link to="/">
        <button style={{ cursor: "pointer" }}>Go to Homepage</button>
      </Link>

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
}

export default Symbol;
