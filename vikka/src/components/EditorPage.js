import React, {useEffect, useRef, useState, useMemo} from "react";
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
    const [fields, setFields] = useState([]);
    const [fieldValues, setFieldValues] = useState({});

    const [tables, setTables] = useState([]);
    const [selectedTable, setSelectedTable] = useState(null);
    const [buttonPosition, setButtonPosition] = useState(null);
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
    
    const [initialFieldValues, setInitialFieldValues] = useState({});
    const [showUnsavedChangesModal, setShowUnsavedChangesModal] = useState(false);

    const [notification, setNotification] = useState({
        show: false,
        message: "",
        type: ""
    });

    const FIELD_TYPES = {
        data_field: {
            type: "text",
            placeholder: "Дата (ДД.ММ.ГГГГ)",
            style: { 
                height: "25px",
                width: "140px",
                fontStyle: "italic",
                textAlign: "center"
            }
        },
        numbering_date: {
            type: "text",
            placeholder: "Дата (ДД.ММ.ГГГГ)",
            style: { 
                height: "25px",
                width: "140px",
                textAlign: "center"
            }
        },
        contract_field: {
            type: "text",
            placeholder: "№ договора",
            style: { 
                height: "25px",
                width: "140px",
                fontStyle: "italic",
                textAlign: "center"
            }
        },
        number_field: {
            type: "text",
            placeholder: "Учетный номер",
            style: { 
                height: "25px",
                width: "110px",
                textAlign: "center"
            }
        },
        documentation_type: {
            type: "select",
            options: ["", "рабочую", "исполнительную", "эксплутационную", "рабочую и исполнительную", "рабочую и эксплутационную", "исполнительную и эксплутацонную", "рабочую, исполнительную и эксплутационную"],
            style: { 
                height: "25px",
                width: "140px",
                textAlign: "center"
            }
        },
        num_copies: {
            type: "text",
            placeholder: "1/1",
            style: {
                height: "25px",
                width: "50px",
                textAlign: "center"
            }
        }
    };

    const docxContainerRef = useRef(null);

    useEffect(() => {
        const changesExist = Object.keys(fieldValues).some(
            key => fieldValues[key] !== initialFieldValues[key]
        );
        setHasUnsavedChanges(changesExist);
    }, [fieldValues, initialFieldValues]);

    const UnsavedChangesModal = ({ isOpen, onConfirm, onCancel }) => {
        if (!isOpen) return null;
      
        return (
          <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h3>Внимание!</h3>
              <p>Вы не сохранили внесенные изменения!</p>
              <p>Выйти без сохранения?</p>
              <div className="modal-buttons">
                <button 
                  className="btn btn-danger" 
                  onClick={onConfirm}
                >
                  Да, выйти
                </button>
                <button 
                  className="btn btn-secondary" 
                  onClick={onCancel}
                >
                  Отмена
                </button>
              </div>
            </div>
          </div>
        );
    };

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

                const res = await fetch(fullPath);
                const blob = await res.arrayBuffer();
                await renderDocument(blob, isEditable);

                const backendPath = fullPath.replace("http://localhost:8000/", "");
                const fieldsResponse = await fetch("http://localhost:8000/api/extract-fields", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ docx_path: backendPath }),
                });
                
                const { fields } = await fieldsResponse.json();
                setFields(fields);

                const initialValues = {};
                fields.forEach(field => {
                    initialValues[field] = "";
                });
                
                setFieldValues(initialValues);
                setInitialFieldValues({...initialValues});
                setHasUnsavedChanges(false);

            } catch (error) {
                console.error("Ошибка:", error);
            }
        };

        loadDocxAndExtractFields();
    }, [isEditable]);




    const renderDocument = async (blob, isEditMode) => {       
        await renderAsync(blob, docxContainerRef.current, null, {
            className: "docx",
            inWrapper: true,
            showHeader: true,
            showFooter: true
        });
    
        const container = docxContainerRef.current;
        
        if (isEditMode) {
            let html = container.innerHTML;
            fields.forEach(field => {
                const config = FIELD_TYPES[field] || { type: "text" };
                const value = fieldValues[field] || "";
                
                if (config.type === "select") {
                    html = html.replace(
                        new RegExp(`\\{${field}\\}`, "g"),
                        `<select 
                            class="docx-field docx-select"
                            data-field="${field}"
                            style="${cssStyleToString(config.style)}"
                        >
                            ${config.options.map(opt => 
                                `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>`
                            ).join('')}
                        </select>`
                    );
                } else {
                    html = html.replace(
                        new RegExp(`\\{${field}\\}`, "g"),
                        `<input 
                            type="${config.type}"
                            class="docx-field"
                            data-field="${field}"
                            value="${value}"
                            placeholder="${config.placeholder || ''}"
                            style="${cssStyleToString(config.style)}"
                        />`
                    );
                }
            });
            container.innerHTML = html;

            container.querySelectorAll(".docx-field").forEach(input => {
                input.style.fontStyle = 'italic';
                input.style.textAlign = 'center';
                input.addEventListener("input", (e) => {
                    const field = e.target.dataset.field;
                    updateFieldValue(field, e.target.value);
                });
            });
    
            container.querySelectorAll(".docx-select").forEach(select => {
                select.style.fontStyle = 'italic';
                select.style.textAlign = 'center';
                select.addEventListener("change", (e) => {
                    const field = e.target.dataset.field;
                    updateFieldValue(field, e.target.value);
                });
            });
    
        } else {
            let html = container.innerHTML;
            html = html.replace(
                /\{(data_field|contract_field|documentation_type|num_copies|number_field|numbering_date)\}/g, 
                (match, field) => `<span class="docx-template-field" data-field="${field}">${getFieldDisplayName(field)}</span>`
            );
            container.innerHTML = html;
        }
    };

    const updateFieldValue = (field, value) => {
        setFieldValues(prev => {
            const newValues = { ...prev, [field]: value };
            const changesExist = Object.keys(newValues).some(
                key => newValues[key] !== initialFieldValues[key]
            );
            setHasUnsavedChanges(changesExist);
            return newValues;
        });
    };

    const cssStyleToString = (styleObj) => {
        return Object.entries(styleObj).map(([key, value]) => 
            `${key}:${value}`
        ).join(';');
    };

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
    
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || "Ошибка сохранения");
            }

            setInitialFieldValues({...fieldValues});
    
            setNotification({
                show: true,
                message: "Изменения успешно сохранены",
                type: "success"
            });
                
            setTimeout(() => {
                setNotification(prev => ({...prev, show: false}));
            }, 3000);

            const updatedDocPath = data.processed_docx_path || backendPath;
            const res = await fetch(`http://localhost:8000/${updatedDocPath}`);
            const blob = await res.arrayBuffer();
            
            docxContainerRef.current.innerHTML = '';
            await renderAsync(blob, docxContainerRef.current, null, {
                className: "docx",
                inWrapper: true,
            });
                
            setIsEditable(false);
                
        } catch (error) {
            console.error("Ошибка сохранения:", error);
            setNotification({
                show: true,
                message: `Ошибка: ${error.message}`,
                type: "error"
            });
            setTimeout(() => {
                setNotification(prev => ({...prev, show: false}));
            }, 3000);
        }
    };

    const toggleEditMode = async () => {
        if (isEditable && hasUnsavedChanges) {
            setShowUnsavedChangesModal(true);
            return;
        }
        setIsEditable(!isEditable);
    
        try {
            let fullPath = location.state?.fullDocxPath;
            fullPath = fullPath.replace(/\\/g, "/");
            if (!fullPath.startsWith("http")) {
                fullPath = `http://localhost:8000/${fullPath}`;
            }
            
            const res = await fetch(fullPath);
            const blob = await res.arrayBuffer();
            await renderDocument(blob, !isEditable);
            
            setIsEditable(!isEditable);
        } catch (error) {
            console.error("Ошибка переключения режима:", error);
        }
    };


    const getFieldDisplayName = (field) => {
        const fieldNames = {
            'data_field': 'Дата письма',
            'contract_field': 'Номер письма',
            num_copies: 'Кол-во экземпляров',
            documentation_type: 'тип документации',
            number_field: 'Учетный номер',
            numbering_date: 'Дата'
        };
        return fieldNames[field] || field;
    };

    const handleModalConfirm = async () => {
        setShowUnsavedChangesModal(false);
        setIsEditable(false);
        setFieldValues({...initialFieldValues});
        
        try {
          const fullPath = location.state?.fullDocxPath.replace(/\\/g, "/");
          const res = await fetch(
            fullPath.startsWith("http") 
              ? fullPath 
              : `http://localhost:8000/${fullPath}`
          );
          const blob = await res.arrayBuffer();
          await renderAsync(blob, docxContainerRef.current);
        } catch (error) {
          console.error("Ошибка загрузки документа:", error);
        }
    };
      
    const handleModalCancel = () => {
        setShowUnsavedChangesModal(false);
    };

    useEffect(() => {
        const handleTableClick = (table, index) => {
            tables.forEach(t => t.style.outline = "");
            table.style.outline = "2px solid #0d6efd";
            
            
            const rect = table.getBoundingClientRect();
            setButtonPosition({
                style: {
                    top: `${rect.bottom + window.scrollY + 5}px`,
                    left: `${rect.left + rect.width / 2}px`,
                    transform: 'translateX(-50%)'
                },
                tableIndex: index
            });
            
            setSelectedTable(index);
        };
    
        if (docxContainerRef.current && isEditable) {
            const tablesInDoc = Array.from(docxContainerRef.current.querySelectorAll('table'));
            tablesInDoc.forEach((table, index) => {
                table.onclick = (e) => {
                    e.stopPropagation();
                    handleTableClick(table, index);
                };
            });
            
            setTables(tablesInDoc);
        }
    
        return () => {
            tables.forEach(table => {
                table.onclick = null;
                table.style.outline = "";
            });
        };
    }, [isEditable, tables]);

    const AddRowButton = ({ tableIndex, onAdd }) => {
        return (
            <div className="add-row-button" onClick={(e) => {
                e.stopPropagation();
                onAdd(tableIndex);
            }}>
                + Добавить строку
            </div>
        );
    };

    const handleAddRow = (tableIndex) => {
        if (tableIndex !== 2) {
            setNotification({
                show: true,
                message: "Строки можно добавлять только в указанную таблицу",
                type: "warning"
            });
            return;
        }
    
        handleAddTableRow(tableIndex);
    };

    const handleAddTableRow = async (tableIndex) => {
        try {
            const backendPath = location.state?.fullDocxPath
                .replace(/\\/g, "/")
                .replace("http://localhost:8000/", "");
            
            const response = await fetch("http://localhost:8000/api/add-table-row", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    docx_path: backendPath,
                    table_index: tableIndex
                }),
            });
    
            if (response.ok) {
                const res = await fetch(`http://localhost:8000/${backendPath}`);
                const blob = await res.arrayBuffer();
                docxContainerRef.current.innerHTML = '';
                await renderAsync(blob, docxContainerRef.current);
            }
        } catch (error) {
            setNotification({
                show: true,
                message: `Ошибка: ${error.message}`,
                type: "error"
            });
        }
    };

    useEffect(() => {
        if (!buttonPosition || !tables[buttonPosition.tableIndex]) return;

        const updatePosition = () => {
            const table = tables[buttonPosition.tableIndex];
            const rect = table.getBoundingClientRect();
            const scrollY = window.scrollY || window.pageYOffset;
            
            setButtonPosition(prev => ({
                ...prev,
                style: {
                    ...prev.style,
                    top: `${rect.bottom + scrollY + 5}px`,
                    left: `${rect.left + rect.width / 2}px`
                }
            }));
        };
        
        updatePosition();

        window.addEventListener('scroll', updatePosition);
        window.addEventListener('resize', updatePosition);
        
        return () => {
            window.removeEventListener('scroll', updatePosition);
            window.removeEventListener('resize', updatePosition);
        };
    }, [buttonPosition, tables]);



    

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
                        className={`menu-icon white-icon mb-3 ${isEditable ? 'active' : ''}`}
                        onClick={toggleEditMode}
                        title={isEditable ? "Предпросмотр" : "Редактировать"}
                    >
                        <img src={editIcon} alt={isEditable ? "Предпросмотр" : "Редактировать"} />
                        {hasUnsavedChanges && (
                            <div className="unsaved-changes-indicator" title="Есть несохраненные изменения">
                                <span className="unsaved-dot"></span>
                            </div>
                        )}
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
        {showUnsavedChangesModal && (
            <UnsavedChangesModal
                isOpen={showUnsavedChangesModal}
                onConfirm={handleModalConfirm}
                onCancel={handleModalCancel}
            />
        )}

        {notification.show && (
            <div className={`notification ${notification.type}`}>
                {notification.message}
            </div>
        )}

        {buttonPosition && (
            <div 
                className="add-row-button"
                style={buttonPosition.style}
                onClick={(e) => {
                    e.stopPropagation();
                    handleAddRow(buttonPosition.tableIndex);
                }}
            >
                + Добавить строку
            </div>
        )}
      </div>
    );
  };
  
  export default EditorPage;