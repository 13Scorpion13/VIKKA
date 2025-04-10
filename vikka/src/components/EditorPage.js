import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import infoIcon from '../icons/info.svg';
import templatesIcon from '../icons/templates.svg';
import profileIcon from '../icons/profile.svg';
import editIcon from '../icons/edit.svg';
import saveIcon from '../icons/save.svg';
import downloadIcon from '../icons/download.svg';
import sendIcon from '../icons/send.svg';
import printIcon from '../icons/print.svg';
import "./EditorPage.css";
import "./Header.css";

const EditorPage = () => {
    return (
      <div className="editor-page-container">
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

        <div className="breadcrumb-nav ms-4 mt-3">
            <a href="/templates" className="breadcrumb-item text-decoration-none text-dark">Шаблоны</a>
            <span className="text-orange mx-2" style={{ fontSize: '2 rem', color: '#FF833A' }}>›</span>
            <a href="/document/1" className="breadcrumb-current text-decoration-none text-dark">Документ 1</a>
        </div>
  
        {/* Контент страницы редактирования */}
        <section className="editor-content-section">
            <h2 className="document-title text-start mb-4">Название документа</h2>

            <div className="orange-circle-editor-group-left">
                <div className="circle editor-left-circle1"></div>
                <div className="circle editor-left-circle2"></div>
                <div className="circle editor-left-circle3"></div>
                <div className="circle editor-left-circle4"></div>
                <div className="circle editor-left-circle5"></div>
            </div>
            <div className="orange-circle-editor-group-right">
                <div className="circle editor-right-circle1"></div>
                <div className="circle editor-right-circle2"></div>
                <div className="circle editor-right-circle3"></div>
                <div className="circle editor-right-circle4"></div>
                <div className="circle editor-right-circle5"></div>
            </div>

            <div className="editor-content d-flex w-100 justify-content-center align-items-start">
                {/* Согласование */}
                <div className="approval-box text-white p-3 me-4">
                    <p>Согласовал:</p>
                    <p><strong>Иванов И.И.</strong></p>
                    <p>Дата: 01.01.2025</p>
                </div>

                {/* Контейнер для Word-документа */}
                <div className="editor-document d-flex justify-content-center align-items-center">
                    <iframe
                        src="C:\Users\andre\Desktop\templates\asdd.docx"
                        title="Документ"
                        className="document-frame a4-frame"
                    ></iframe>
                </div>

                {/* Правое меню */}
                <div className="editor-actions text-white d-flex flex-column align-items-center p-3 ms-4">
                    <div className="menu-icon white-icon mb-3">
                        <img src={editIcon}/>
                    </div>
                    <div className="menu-icon text-white mb-3">
                        <img src={saveIcon}/>
                    </div>
                    <div className="menu-icon text-white mb-3">
                        <img src={downloadIcon}/>
                    </div>
                    <div className="menu-icon text-white mb-3">
                        <img src={sendIcon}/>
                    </div>
                    <div className="menu-icon text-white mb-3">
                        <img src={printIcon}/>
                    </div>
                </div>
            </div>
        </section>
      </div>
    );
  };
  
  export default EditorPage;