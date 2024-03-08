import React from "react";
import { HashRouter as Router, Route, Routes } from "react-router-dom";
import Homepage from "./components/Homepage";
import Portfolio from "./components/Portfolio";
import Symbol from "./components/Symbol";

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<Homepage />} exact />
          <Route path="/portfolio/:user_id" element={<Portfolio />} />
          <Route path="/symbol/:symbol" element={<Symbol />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
