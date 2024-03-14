import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Login() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/login", {
        name,
        password,
      });
      console.log(response.data.message);
      // Redirect to homepage or another protected route
      localStorage.setItem("token", response.data.access_token);
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
    <div>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Username"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        <button type="submit">Login</button>
        <button type="button" onClick={() => navigate("/signup")}>
          Sign Up
        </button>
      </form>
    </div>
  );
}

export default Login;
