import React, { useState } from "react";
import axios from "axios";

function Signup() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://mcsbt-integration-glebtep.oa.r.appspot.com/signup",
        {
          name,
          password,
        }
      );
      console.log(response.data.message);
      window.location.href = "/login";
      // Redirect to login page or elsewhere after successful signup
    } catch (error) {
      const errorMessage = error.response
        ? error.response.data.message
        : "An unexpected error occurred";
      alert("Signup failed: " + errorMessage);
    }
  };

  return (
    <div className="form-container">
      <div className="form-box">
        <h1 style={{ textAlign: "center" }}>WealthWise</h1>
        <form onSubmit={handleSignup}>
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
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
}

export default Signup;
