import React from "react";
import { HashRouter as Router, Route, Routes } from "react-router-dom";
import Homepage from "./components/Homepage";
import MyPortfolio from "./components/MyPortfolio";
import Symbol from "./components/Symbol";
import "./styles/AppStyles.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} exact />
        <Route path="/portfolio" element={<MyPortfolio />} />
        <Route path="/symbol/:symbol" element={<Symbol />} />
      </Routes>
    </Router>
  );
}

export default App;
