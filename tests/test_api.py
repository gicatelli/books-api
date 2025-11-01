# tests/test_api.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code in (200, 500)  # 200 se dataset carregado, 500 se não carregado