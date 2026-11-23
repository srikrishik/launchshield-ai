from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "LaunchShield AI",
        "description": "LaunchShield AI security assessment platform",
        "status": "running",
    }


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
