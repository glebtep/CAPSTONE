import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Login({ setIsLoggedIn }) {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://mcsbt-integration-glebtep.oa.r.appspot.com/login",
        {
          name,
          password,
        }
      );
      console.log(response.data.message);
      // Redirect to homepage or another protected route
      localStorage.setItem("token", response.data.access_token);
      setIsLoggedIn(true);
      // Redirect to homepage or another protected route
      navigate("/");
    } catch (error) {
      // Adjusted to potentially handle cases where the error response is not structured as expected
      const errorMessage =
        error.response && error.response.data
          ? error.response.data.message
          : "An unexpected error occurred";
      alert("Login failed: " + errorMessage);
    }
  };

  return (
    <div className="form-container">
      <div className="form-box">
        <h1 style={{ textAlign: "center" }}>WealthWise</h1>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Username"
            className="form-field"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="form-field"
          />
          <button type="submit" className="form-button">
            Login
          </button>
          <button
            type="button"
            onClick={() => navigate("/signup")}
            className="form-button"
          >
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
