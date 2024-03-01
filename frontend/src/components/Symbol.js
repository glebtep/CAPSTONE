import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

function Symbol() {
  const { symbol } = useParams();
  const [symbolData, setSymbolData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/symbol/${symbol}`
        );
        setSymbolData(response.data);
      } catch (error) {
        console.error("Failed to fetch symbol data", error);
      }
    };

    fetchData();
  }, [symbol]);

  if (!symbolData) return <div>Loading...</div>;

  return (
    <div>
      <h1>{symbolData.symbol}</h1>
      <p>Last Refreshed: {symbolData.last_refreshed}</p>
      <p>Latest Close Price: {symbolData.latest_close_price}</p>
      <Link to="/">Go to Homepage</Link>
    </div>
  );
}

export default Symbol;
