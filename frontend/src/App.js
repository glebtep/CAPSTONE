import React, { useState, useEffect } from "react";
import {
  HashRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Homepage from "./components/Homepage";
import MyPortfolio from "./components/MyPortfolio";
import Symbol from "./components/Symbol";
import Login from "./components/Login";
import Signup from "./components/Signup";
import "./styles/AppStyles.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={isLoggedIn ? <Homepage /> : <Navigate to="/login" />}
          exact
        />
        <Route
          path="/login"
          element={<Login setIsLoggedIn={setIsLoggedIn} />}
        />
        <Route
          path="/portfolio"
          element={isLoggedIn ? <MyPortfolio /> : <Navigate to="/login" />}
        />
        <Route
          path="/symbol/:symbol"
          element={isLoggedIn ? <Symbol /> : <Navigate to="/login" />}
        />
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </Router>
  );
}

export default App;
