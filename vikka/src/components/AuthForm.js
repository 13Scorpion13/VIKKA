import React, { useState } from "react";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import "./AuthForm.css";
import "bootstrap/dist/css/bootstrap.min.css";

const AuthForm = () => {
  const [formData, setFormData] = useState({
    login: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Попытка входа", formData);
    
    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const result = await response.json();
      if (response.ok) {
        alert("Успешная авторизация!");
      } else {
        setError(result.message || "Ошибка авторизации");
      }
    } catch (err) {
      setError("Ошибка соединения с сервером");
    }
  };

  return (
    <div className="auth-container">
      {/* Левая группа кругов */}
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

      {/* Правая группа кругов */}
      <div className="circles-right">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      {/* Логотип отдельно за окном */}
      <h1 className="logo">
      <svg width="252" height="100" viewBox="0 0 252 100" xmlns="http://www.w3.org/2000/svg">
        <text x="0" y="75" font-family="Archivo Black, sans-serif" font-size="80" font-weight="bold" fill="#4d4d4d">V</text>
        <text x="54" y="75" font-family="Archivo Black, sans-serif" font-size="80" font-weight="bold" fill="#4d4d4d">I</text>
        <text x="72" y="75" font-family="Archivo Black, sans-serif" font-size="80" font-weight="bold" fill="#ff833a">K</text>
        <text x="130" y="75" font-family="Archivo Black, sans-serif" font-size="80" font-weight="bold" fill="#ff833a">K</text>
        <text x="190" y="75" font-family="Archivo Black, sans-serif" font-size="80" font-weight="bold" fill="#4d4d4d">A</text>
      </svg>
      
        {/* <span className="logo-gray">VI</span>
        <span className="logo-orange">KK</span>
        <span className="logo-gray">A</span> */}
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
