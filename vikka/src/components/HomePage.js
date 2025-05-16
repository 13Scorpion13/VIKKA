import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import arrowIcon from '../icons/arrow.svg';
import infoIcon from '../icons/info.svg';
import templatesIcon from '../icons/templates.svg';
import profileIcon from '../icons/profile.svg';
import "./HomePage.css";
import "./Header.css";

const API_BASE_URL = 'http://localhost:5000/api';

const HomePage = () => {
  const [currentPage, setCurrentPage] = useState(0);
  const [allTemplatesPage, setAllTemplatesPage] = useState(0);
  const [lastTemplates, setLastTemplates] = useState([]);
  const [recentTemplates, setRecentTemplates] = useState([]);
  const [allTemplates, setAllTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const navigate = useNavigate();

  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    contractNumber: "",
    contractDate: "",
    fileLink: "",
    recipient: "",
    signer: ""
  });


  const templatesPerPage = 6;
  const allTemplatesPerPage = 12;

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setIsLoading(true);
        //const response = await fetch('http://localhost:8000/api/templates/all');
        const [allResponse, recentResponse] = await Promise.all([
          fetch('http://localhost:8000/api/templates/all'),
          fetch('http://localhost:8000/api/templates/recent')
        ])
        //const data = await response.json();
        const [allData, recentData] = await Promise.all([
          allResponse.json(),
          recentResponse.json()
        ]);
        const savedRecent = JSON.parse(localStorage.getItem('recentTemplates')) || [];
        const validRecent = savedRecent.filter(recentTemplate => 
          allData.some(t => t.id === recentTemplate.id)
        );

        setAllTemplates(allData);
        
        //const savedRecent = JSON.parse(localStorage.getItem('recentTemplates')) || [];
        setRecentTemplates(validRecent);
        localStorage.setItem('recentTemplates', JSON.stringify(validRecent));
      } catch (error) {
        console.error('Error fetching templates:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  const handleTemplateClick = (template) => {
    setSelectedTemplate(template);
    setShowModal(true);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCancel = () => {
    setShowModal(false);
    setFormData({
      contractNumber: "",
      contractDate: "",
      fileLink: "",
      recipient: "",
      signer: ""
    });
  };

  const handleConfirm = async () => {
    try {
      if (!formData.recipient || !formData.signer) {
        throw new Error('Заполните обязательные поля: Адресат и Подписант');
      }

      if (selectedTemplate.form_type === 'full' && 
        (!formData.contractNumber || !formData.contractDate || !formData.fileLink)) {
        throw new Error('Заполните все поля для выбранного шаблона');
      }
      setIsLoading(true);
      setShowModal(false);
      //setSelectedTemplate(template);
      
      const updatedRecent = [
        selectedTemplate,
        ...recentTemplates.filter(t => t.id !== selectedTemplate.id)
      ].slice(0, 6);
      
      setRecentTemplates(updatedRecent);
      localStorage.setItem('recentTemplates', JSON.stringify(updatedRecent));

      const payload = selectedTemplate.form_type === 'full' 
        ? { 
            docx_path: selectedTemplate.document_path,
            recipient: formData.recipient,
            signer: formData.signer,
            contract_number: formData.contractNumber,
            contract_date: formData.contractDate,
            pdf_folder_path: formData.fileLink
          }
        : {
            docx_path: selectedTemplate.document_path,
            recipient: formData.recipient,
            signer: formData.signer
          };

      const response = await fetch('http://localhost:8000/api/process-document/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Ошибка обработки документа');
      
      const result = await response.json();
      navigate('/editor', { state: { 
        fullDocxPath: result.full_docx_path,
        templateTitle: selectedTemplate.title
      }});
    } catch (error) {
      console.error('Error:', error);
      alert(error.message);
    } finally {
      setIsLoading(false);
    }
  };

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

  if (isLoading) {
    return <div className="d-flex justify-content-center align-items-center vh-100">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
    </div>;
  }

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
              <span>Гараева Ксения</span>
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
              {recentTemplates.map((tpl) => (
                  <div 
                    key={`recent-${tpl.id}`} 
                    className="template-wrapper"
                    onClick={(e) => {
                      e.preventDefault();
                      handleTemplateClick(tpl);
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="template-card shadow">
                      <img 
                        src={`http://localhost:8000/preview/${tpl.preview_image}`}
                        alt={`Превью шаблона: ${tpl.title}`}
                        className="img-fluid template-preview"
                        loading="lazy"
                        onError={(e) => e.target.src = '/placeholder.png'}
                      />
                    </div>
                  <div className="template-info text-center">
                    <strong>{tpl.title}</strong><br />
                    <small>{tpl.last_modified}</small>
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
          <div className="d-flex justify-content-start flex-nowrap">
            {displayedAllTemplates.map((tpl, index) => (
                <div 
                  key={`all-${tpl.id || index}`}
                  className="template-wrapper"
                  onClick={(e) => {
                    e.preventDefault();
                    handleTemplateClick(tpl);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="template-card shadow">
                    <img 
                      src={`http://localhost:8000/preview/${tpl.preview_image}`}
                      alt={tpl.title}
                      className="img-fluid template-preview"
                      onError={(e) => e.target.src = '/placeholder.png'}
                    />
                  </div>
                <div className="template-info-dark mt-2 w-75 text-center">
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
      
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Заполните данные</h3>
            <div className="modal-form">
              {selectedTemplate?.form_type === 'full' ? (
                <>
                  <div className="form-group">
                    <label>Номер и дата договора</label>
                    <input
                      type="text"
                      name="contractNumber"
                      value={formData.contractNumber}
                      onChange={handleFormChange}
                      placeholder="Номер договора"
                    />
                    <input
                      type="date"
                      name="contractDate"
                      value={formData.contractDate}
                      onChange={handleFormChange}
                      className="mt-2"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Ссылка на файлы с приложениями</label>
                    <input
                      type="text"
                      name="fileLink"
                      value={formData.fileLink}
                      onChange={handleFormChange}
                      placeholder="Укажите путь к файлу"
                    />
                  </div>
                </>
              ) : null}

              {/* Общие поля для всех форм */}
              <div className="form-group">
                <label>Адресат</label>
                <input
                  type="text"
                  name="recipient"
                  value={formData.recipient}
                  onChange={handleFormChange}
                  placeholder="ФИО или название организации"
                />
              </div>
              
              <div className="form-group">
                <label>Подписант</label>
                <input
                  type="text"
                  name="signer"
                  value={formData.signer}
                  onChange={handleFormChange}
                  placeholder="ФИО подписанта"
                />
              </div>
            </div>
            
            <div className="modal-buttons">
              <button onClick={handleCancel} className="btn btn-secondary">
                Отмена
              </button>
              <button onClick={handleConfirm} className="btn btn-primary">
                Подтвердить
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default HomePage;