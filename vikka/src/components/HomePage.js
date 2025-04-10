import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import arrowIcon from '../icons/arrow.svg';
import infoIcon from '../icons/info.svg';
import templatesIcon from '../icons/templates.svg';
import profileIcon from '../icons/profile.svg';
import "./HomePage.css";
import "./Header.css";

const lastTemplates = [
  ...Array(6).fill({ title: "Документ 1", time: "5 минут назад" }),
  ...Array(6).fill({ title: "Документ 2", time: "1 минуту назад" }),
  ...Array(3).fill({ title: "Документ 3", time: "Только что" })
];

const allTemplates = Array(30).fill({ title: "Документ 1" });

const HomePage = () => {
  const [currentPage, setCurrentPage] = useState(0);
  const [allTemplatesPage, setAllTemplatesPage] = useState(0);

  const templatesPerPage = 6;
  const allTemplatesPerPage = 12;

  const totalPages = Math.ceil(lastTemplates.length / templatesPerPage);
  const totalAllPages = Math.ceil(allTemplates.length / allTemplatesPerPage);

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage((prev) => prev - 1);
    }
  };

  const handleNextAllTemplatesPage = () => {
    if (allTemplatesPage < totalAllPages - 1) {
      setAllTemplatesPage((prev) => prev + 1);
    }
  };

  const handlePrevAllTemplatesPage = () => {
    if (allTemplatesPage > 0) {
      setAllTemplatesPage((prev) => prev - 1);
    }
  };

  const displayedTemplates = lastTemplates.slice(
    currentPage * templatesPerPage,
    (currentPage + 1) * templatesPerPage
  );

  const displayedAllTemplates = allTemplates.slice(
    allTemplatesPage * allTemplatesPerPage,
    (allTemplatesPage + 1) * allTemplatesPerPage
  );

  return (
    <div className="homepage-container">
      {/* Хедер */}
      <header className="header position-relative">
        <div className="header-content d-flex justify-content-end align-items-center p-5">
          <nav className="d-flex gap-4">
            <div className="nav-item d-flex align-items-center">
              <img src={infoIcon} className="me-2"/>
              <a href="#">О сервисе</a>
            </div>
            <div className="nav-item d-flex align-items-center">
              <img src={templatesIcon} className="me-2"/>
              <a href="/home">Шаблоны</a>
            </div>
            <div className="nav-item d-flex align-items-center">
              <img src={profileIcon} className="me-2"/>
              <span>Имя Имя</span>
            </div>
          </nav>
        </div>
        <div className="header-curve-wrapper">
          <svg viewBox="0 0 1440 200" preserveAspectRatio="none" className="header-curve">
            <path d="M0,100 C600,0 1200,200 1440,100 L1440,200 L0,200 Z" fill="white" />
            <path d="M0,90 C600,-10 1200,190 1440,90" fill="none" stroke="white" strokeWidth="4" />
          </svg>
        </div>
      </header>

      {/* Последние шаблоны */}
      <section className="recent-templates px-5 py-4">
        <h2 className="section-title">Последние шаблоны</h2>
        <div className="recent-templates-bg">
          <div className="circle-group">
            <div className="circle circle1"></div>
            <div className="circle circle2"></div>
            <div className="circle circle3"></div>
            <div className="circle circle4"></div>
            <div className="circle circle5"></div>
          </div>
          <div className="d-flex templates-scroll w-100 align-items-center">
            <div className="template-nav me-3">
              <button
                className="arrow-button"
                onClick={handlePrevPage}
                style={{ visibility: currentPage === 0 ? 'hidden' : 'visible' }}
              >
                <img src={arrowIcon} alt="Назад" style={{ transform: 'rotate(180deg)' }} />
              </button>
            </div>
            <div className="d-flex justify-content-start flex-nowrap gap-4">
              {displayedTemplates.map((tpl, index) => (
                <div key={index} className="template-wrapper">
                  <div className="template-card shadow"></div>
                  <div className="template-info">
                    <strong>{tpl.title}</strong><br />
                    <small>{tpl.time}</small>
                  </div>
                </div>
              ))}
            </div>
            {currentPage < totalPages - 1 && (
              <div className="template-nav">
                <button className="arrow-button" onClick={handleNextPage}>
                  <img src={arrowIcon}/>
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Все шаблоны */}
      <section className="all-templates px-5 py-4">
        
        <div className="orange-circle-group-left">
          <div className="circle left-circle1"></div>
          <div className="circle left-circle2"></div>
          <div className="circle left-circle3"></div>
          <div className="circle left-circle4"></div>
          <div className="circle left-circle5"></div>
        </div>
        <div className="orange-circle-group-right">
          <div className="circle right-circle1"></div>
          <div className="circle right-circle2"></div>
          <div className="circle right-circle3"></div>
          <div className="circle right-circle4"></div>
          <div className="circle right-circle5"></div>
        </div>

        <div className="d-flex justify-content-between align-items-center mb-3 all-templates-header">
          <div className="d-flex align-items-center left-controls">
            <h2 className="section-header me-4 mb-0">Все шаблоны</h2>
            <input 
              type="text" 
              className="form-control search-input" 
              placeholder="Поиск" 
            />
          </div>
          <div className="d-flex align-items-center">
            <button className="btn btn-icon me-2">
              <i className="bi bi-sort-down-alt"></i> Сортировка
            </button>
            <button className="btn btn-icon">
              <i className="bi bi-funnel"></i> Фильтр
            </button>
          </div>
        </div>
        <div className="d-flex all-templates-content">
          <div className="template-nav me-3">
            <button
              className="arrow-button"
              onClick={handlePrevAllTemplatesPage}
              style={{ visibility: allTemplatesPage === 0 ? 'hidden' : 'visible' }}
            >
              <img src={arrowIcon} style={{ transform: 'rotate(180deg)' }} />
            </button>
          </div>
          <div className="d-flex gap-4 flex-wrap">
            {displayedAllTemplates.map((tpl, index) => (
              <div key={index} className="template-wrapper">
                <div className="template-card shadow"></div>
                <div className="template-info-dark mt-2 text-center">
                  <strong>{tpl.title}</strong>
                </div>
              </div>
            ))}
          </div>
          <div className="template-nav">
            <button
              className="arrow-button"
              onClick={handleNextAllTemplatesPage}
              style={{ visibility: allTemplatesPage === totalAllPages - 1 ? 'hidden' : 'visible' }}
            >
              <img src={arrowIcon}/>
            </button>
          </div>
        </div>

      </section>
    </div>
  );
};

export default HomePage;