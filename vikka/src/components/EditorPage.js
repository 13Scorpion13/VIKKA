import React, {useEffect, useRef, useState} from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { renderAsync } from "docx-preview";
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
    const location = useLocation();
    const navigate = useNavigate();
    const [documentTitle, setDocumentTitle] = useState("Название документа");
    const [isEditable, setIsEditable] = useState(false);
    const [fields, setFields] = useState([]); // Поля вида {field_name}
    const [fieldValues, setFieldValues] = useState({}); // Значения полей

    const docxContainerRef = useRef(null);

    useEffect(() => {
        const loadDocxAndExtractFields = async () => {
            try {
                let fullPath = location.state?.fullDocxPath;

                if (!fullPath) {
                    console.error("Не передан путь к документу");
                    return;
                }

                fullPath = fullPath.replace(/\\/g, "/");

                if (!fullPath.startsWith("http")) {
                    fullPath = `http://localhost:8000/${fullPath}`;
                }

                // 1. Загружаем DOCX для превью
                const res = await fetch(fullPath);
                const blob = await res.arrayBuffer();
                await renderAsync(blob, docxContainerRef.current, null, {
                    className: "docx",
                    inWrapper: true,
                });

                // 2. Извлекаем поля через бэкенд
                const backendPath = fullPath.replace("http://localhost:8000/", "");
                const fieldsResponse = await fetch("http://localhost:8000/api/extract-fields", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ docx_path: backendPath }),
                });
                const { fields } = await fieldsResponse.json();
                setFields(fields);

                // Инициализируем значения полей
                const initialValues = {};
                fields.forEach(field => {
                    initialValues[field] = "";
                });
                setFieldValues(initialValues);

            } catch (error) {
                console.error("Ошибка:", error);
            }
        };

        loadDocxAndExtractFields();
    }, []);

    useEffect(() => {
        if (!isEditable || !docxContainerRef.current) return;

        const container = docxContainerRef.current;
        let html = container.innerHTML;

        fields.forEach(field => {
            const value = fieldValues[field] || "";
            html = html.replace(
                new RegExp(`\\{${field}\\}`, "g"),
                `<input 
                    type="text" 
                    class="docx-field" 
                    data-field="${field}" 
                    value="${value}"
                    style="border: 1px solid #ccc; padding: 2px; width: 90px;"
                />`
            );
        });

        container.innerHTML = html;

        // Добавляем обработчики изменений
        container.querySelectorAll(".docx-field").forEach(input => {
            input.addEventListener("change", (e) => {
                const field = e.target.dataset.field;
                setFieldValues(prev => ({
                    ...prev,
                    [field]: e.target.value,
                }));
            });
        });
    }, [isEditable, fields, fieldValues]);

    // Генерация документа с заменёнными полями
    const handleGenerateDocument = async () => {
        try {
            const backendPath = location.state?.fullDocxPath.replace(/\\/g, "/").replace("http://localhost:8000/", "");
            
            const response = await fetch("http://localhost:8000/api/replace-fields", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    docx_path: backendPath,
                    fields_data: fieldValues,
                }),
            });

            const { processed_docx_path } = await response.json();
            alert(`Документ сохранён: ${processed_docx_path}`);
            
            // Можно добавить скачивание:
            window.open(`http://localhost:8000/${processed_docx_path}`);

        } catch (error) {
            console.error("Ошибка генерации документа:", error);
        }
    };

    const toggleEditMode = () => {
        setIsEditable(prev => !prev);
    };

    const handleSave = async () => {
        if (docxContainerRef.current) {
            const htmlContent = docxContainerRef.current.innerHTML;
    
            try {
                const response = await fetch("http://localhost:8000/api/save-docx", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        html: htmlContent,
                        original_path: location.state?.fullDocxPath || null,
                    }),
                });
    
                if (!response.ok) {
                    throw new Error("Ошибка при сохранении документа");
                }
    
                alert("Изменения сохранены!");
            } catch (err) {
                console.error("Ошибка сохранения:", err);
                alert("Не удалось сохранить изменения");
            }
        }
    };
    

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
                    <p>Получатель:</p>
                    <p><strong>Иванов И.И.</strong></p>
                    <p>Подписант:</p>
                    <p><strong>В.Е. Кушнаренко</strong></p>
                </div>

                {/* Контейнер для Word-документа */}
                <div class="docx-container">
                    <div
                        ref={docxContainerRef}
                        className="docx-container"
                        style={{
                            outline: "none",
                            zIndex: 1
                        }}
                    ></div>
                </div>

                {/* Правое меню */}
                <div className="editor-actions text-white d-flex flex-column align-items-center p-3 ms-4">
                    {/* Кнопка редактирования/просмотра */}
                    <button
                        className={`menu-icon white-icon mb-3 ${isEditable ? '' : ''}`}
                        onClick={() => setIsEditable(!isEditable)}
                        title={isEditable ? "Предпросмотр" : "Редактировать"}
                    >
                        <img src={editIcon} alt="Редактировать" />
                    </button>

                    {/* Кнопка сохранения (видна только в режиме редактирования) */}
                    {isEditable && (
                        <button
                            className="menu-icon text-white mb-3"
                            onClick={handleGenerateDocument}
                            title="Сохранить изменения"
                        >
                            <img src={saveIcon} alt="Сохранить" />
                        </button>
                    )}

                    {/* Кнопка скачивания */}
                    <button
                        className="menu-icon text-white mb-3"
                        onClick={() => window.open(`http://localhost:8000/${location.state?.fullDocxPath}`)}
                        title="Скачать DOCX"
                    >
                        <img src={downloadIcon} alt="Скачать" />
                    </button>

                    {/* Кнопка отправки */}
                    <button
                        className="menu-icon text-white mb-3"
                        onClick={() => alert("Функция отправки в разработке")}
                        title="Отправить"
                    >
                        <img src={sendIcon} alt="Отправить" />
                    </button>

                    {/* Кнопка печати */}
                    <button
                        className="menu-icon text-white mb-3"
                        onClick={() => window.print()}
                        title="Печать"
                    >
                        <img src={printIcon} alt="Печать" />
                    </button>
                </div>
            </div>
        </section>
      </div>
    );
  };
  
  export default EditorPage;