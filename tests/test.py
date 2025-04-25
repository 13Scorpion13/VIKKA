import pytest
from httpx import AsyncClient
from backend.main import app
import os

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_get_recent_templates(client):
    response = await client.get("/api/templates/recent")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_all_templates(client):
    response = await client.get("/api/templates/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_search_templates(client):
    response = await client.get("/api/templates/search?query=представлении")
    assert response.status_code == 200
    assert any("представлении" in item["title"].lower() for item in response.json())

@pytest.mark.asyncio
async def test_get_image(client):
    response = await client.get("/images/preview/image2.png")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")

@pytest.mark.asyncio
async def test_extract_fields(client):
    test_docx = "static/templates/template.docx"
    if os.path.exists(test_docx):
        response = await client.post("/api/extract-fields", json={"docx_path": test_docx})
        assert response.status_code == 200
        assert "fields" in response.json()
    else:
        pytest.skip("Test DOCX file not found")

@pytest.mark.asyncio
async def test_process_document(client):
    test_data = {
        "contract_number": "123",
        "contract_date": "2023-01-01",
        "recipient": "Test Recipient",
        "signer": "Test Signer",
        "pdf_folder_path": "/tmp",
        "docx_path": "static/templates/template.docx"
    }
    
    if os.path.exists(test_data["docx_path"]):
        response = await client.post("/api/process-document/", json=test_data)
        assert response.status_code in [200, 400]  # 400 если не хватает данных
    else:
        pytest.skip("Test DOCX file not found")

@pytest.mark.asyncio
async def test_replace_fields(client):
    test_docx = "static/templates/template.docx"
    if os.path.exists(test_docx):
        test_data = {
            "docx_path": test_docx,
            "fields_data": {"field_name": "test_value"}
        }
        response = await client.post("/api/replace-fields", json=test_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    else:
        pytest.skip("Test DOCX file not found")