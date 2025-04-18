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
    const [pdfUrl, setPdfUrl] = useState(null);
    const [documentTitle, setDocumentTitle] = useState("Название документа");
    const [isEditable, setIsEditable] = useState(false);

    const [docxPath, setDocxPath] = useState(null);
    const docxContainerRef = useRef(null);

    /* useEffect(() => {
        if (location.state) {
            setDocxPath(location.state.docxPath || "/public/template.docx");
            setDocumentTitle(location.state.templateTitle || "Название документа");
        }
    }, [location.state]); */

    /* useEffect(() => {
        const testPath = "/1.docx";
    
        fetch(testPath)
            .then(res => res.arrayBuffer())
            .then(blob => {
                renderAsync(blob, docxContainerRef.current, null, {
                    className: "docx",
                    inWrapper: true,
                }).then(() => {
                    replacePlaceholders();
                });
            })
            .catch(err => {
                console.error("Ошибка загрузки тестового документа:", err);
            });
    }, []); */
    useEffect(() => {
        const loadDocxFromServer = async () => {
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
    
                await renderAsync(blob, docxContainerRef.current, null, {
                    className: "docx",
                    inWrapper: true,
                });
    
                replacePlaceholders(); // вставка полей
            } catch (error) {
                console.error("Ошибка загрузки документа:", error);
            }
        };
    
        loadDocxFromServer();
    }, []);

    const replacePlaceholders = () => {
        const container = docxContainerRef.current;

        if (!container) return;

        const replacements = {
            "{contract_number}": `<select class="placeholder" data-key="contract_number">
                <option value="123">123</option>
                <option value="456">456</option>
                <option value="789">789</option>
            </select>`,
        };

        Object.entries(replacements).forEach(([key, html]) => {
                container.innerHTML = container.innerHTML.replaceAll(key, html);
        });
    };

    /* useEffect(() => {
        if (location.state) {
            setPdfUrl(location.state.pdfPath);
            setDocumentTitle(location.state.templateTitle || "Название документа");
        }
    }, [location.state]); */

    const toggleEditMode = () => {
        setIsEditable(prev => !prev);
    };

    /* const handleSave = () => {
        if (docxContainerRef.current) {
            const content = docxContainerRef.current.innerHTML;
            console.log("Сохранённый контент:", content);
    
            alert("Изменения сохранены!");
        }
    }; */

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
    

    const handleDownload = () => {
        if (pdfUrl) {
            const link = document.createElement('a');
            link.href = pdfUrl;
            link.download = `${documentTitle}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    const handlePrint = () => {
        if (pdfUrl) {
            window.open(pdfUrl, '_blank').print();
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
                        contentEditable={isEditable}
                        suppressContentEditableWarning={true}
                        className="docx-container"
                        style={{
                            outline: "none",
                            zIndex: 1
                        }}
                    ></div>
                </div>

                {/* Правое меню */}
                <div className="editor-actions text-white d-flex flex-column align-items-center p-3 ms-4">
                    <div
                        className={`menu-icon white-icon mb-3 ${isEditable ? "active-icon" : ""}`}
                        onClick={toggleEditMode}
                        title="Редактировать"
                        style={{ cursor: "pointer" }}
                    >
                        <img src={editIcon} />
                    </div>
                    <div
                        className="menu-icon text-white mb-3"
                        onClick={handleSave}
                        style={{ cursor: "pointer" }}
                        title="Сохранить изменения"
                    >
                        <img src={saveIcon} />
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