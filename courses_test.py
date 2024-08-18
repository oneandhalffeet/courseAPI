import pytest
import json
from fastapi.testclient import TestClient
from pymongo import MongoClient
from app import app  # Make sure to import your FastAPI app here

client = TestClient(app)


mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["kimo"]
courses_collection = db["courses_test"]

@pytest.fixture(scope="module")
def setup_data():
    # Load data from data.json
    with open('data_test.json', 'r') as file:
        data = json.load(file)
    for item in data:
        courses_collection.insert_one(item)
    yield
    courses_collection.delete_many({})

def test_chapter_fetch(setup_data):
    response = client.get("/courses")
    assert response.status_code == 200

def get_course_info(setup_data):
    response = client.get("/courses/ML101")
    assert response.status_code == 200


def test_get_chapter_info(setup_data):
    response = client.get("/courses/ML101/chapters/ML1011")
    assert response.status_code == 200
    

def test_rate_chapter(setup_data):
    data = {
        "rating": 3
    }
    response = client.post("/courses/ML101/chapters/ML1011/rate", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Rating submitted",
        "new_rating": 3
    }

def test_rate_courses(setup_data):
    data = {
        "rating": 10
    }
    response = client.post("/courses/ML101/chapters/ML1011/rate", json=data)
    assert response.status_code == 200
    response = client.post("/courses/ML101/chapters/ML1012/rate", json=data)
    assert response.status_code == 200
    response = client.post("/courses/ML101/chapters/ML1013/rate", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Rating submitted",
        "new_rating": 10
    }


