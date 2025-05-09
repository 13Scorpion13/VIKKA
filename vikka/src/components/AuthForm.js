import React, { useState } from "react";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "./AuthForm.css";


const AuthForm = () => {
  const [formData, setFormData] = useState({
    login: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Попытка входа", formData);
    
    try {
      const response = await fetch("http://localhost:8000/users/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const result = await response.json();
      if (response.ok) {
        alert("Успешная авторизация!");
        navigate("/home");
      } else {
        setError(result.message || "Ошибка авторизации");
      }
    } catch (err) {
      alert(err);
      setError("Ошибка соединения с сервером");
    }
  };

  return (
    <div className="auth-container">
      <div className="circles">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>

      <div className="circles-center">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>

      <div className="circles-right">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>

      <h1 className="logo">
        <svg width="209" height="100" viewBox="0 0 209 100" xmlns="http://www.w3.org/2000/svg">
          <text x="0" y="75" fill="#4d4d4d">V</text>
          <text x="50" y="75" fill="#4d4d4d">I</text>
          <text x="66" y="75" fill="#ff833a">K</text>
          <text x="146" y="75" fill="#4d4d4d">A</text>
          <text x="113" y="75" fill="#ff833a">K</text>
        </svg>
      </h1>

      <div className="auth-box">
        <h3 className="text-center">Вход</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Логин</label>
            <input
              type="text"
              name="login"
              className="form-control"
              value={formData.login}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group password-group">
            <label>Пароль</label>
            <div className="password-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                className="form-control"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <button
                type="button"
                className="eye-icon"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </button>
            </div>
          </div>
          {error && <div className="alert alert-danger">{error}</div>}
          <button type="submit" className="btn auth-btn">
            Войти
          </button>
        </form>
        <div className="text-center mt-3">
          <a href="#" className="small-link">
            Нет аккаунта?
          </a>
        </div>
      </div>
    </div>
  );
};

export default AuthForm;
