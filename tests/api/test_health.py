# tests/api/test_health.py
import requests

def test_homepage_status():
    url = "https://syeob.lovable.app/"
    response = requests.get(url)
    
    # 200 OK(정상 접속) 확인
    assert response.status_code == 200
    print(f"📡 서버 상태 확인 완료: {response.status_code}")