from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_valid_question():
    response = client.post("/ask", json={"question": "מי המרצה של פייתון?", "history": []})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "category" in response.json()

def test_ask_empty_question():
    # בדיקת קצה: קלט ריק
    response = client.post("/ask", json={"question": "", "history": []})
    assert response.status_code == 200
    # ה-AI אמור להחזיר קטגוריית שגיאה או תשובת Fallback
    assert response.json()["answer"] != ""

def test_ask_english_question():
    # בדיקת קצה: שפה שונה
    response = client.post("/ask", json={"question": "When is the Python exam?", "history": []})
    assert response.status_code == 200
    
def test_ask_out_of_scope():
    # בדיקת קצה: שאלה לא קשורה
    response = client.post("/ask", json={"question": "איך מכינים פיצה?", "history": []})
    assert response.status_code == 200
    assert response.json()["category"] == "Out of Scope"

def test_response_time_metric():
    # בדיקת מדד ביצועים: זמן תגובה (נדרש ברובריקה)
    response = client.post("/ask", json={"question": "איפה חדר 102?", "history": []})
    assert response.status_code == 200
    assert "response_time" in response.json()