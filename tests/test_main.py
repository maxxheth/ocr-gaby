import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ocr_endpoint_no_file():
    """Test OCR endpoint without file"""
    response = client.post("/ocr")
    assert response.status_code == 422  # Validation error

def test_ocr_endpoint_wrong_file_type():
    """Test OCR endpoint with wrong file type"""
    response = client.post(
        "/ocr",
        files={"file": ("test.txt", b"test content", "text/plain")}
    )
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]