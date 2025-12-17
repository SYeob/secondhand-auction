# tests/ui/test_ui_basic.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_browser_title():
    # 1. 크롬 브라우저 세팅 (자동으로 드라이버 설치됨)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 나중에 이 주석을 풀면 브라우저 창 없이 실행됩니다 (서버용)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 2. 사이트 접속
        url = "https://syeob.lovable.app/"
        driver.get(url)
        
        # 3. 로딩 대기 (임시로 2초, 나중엔 똑똑한 대기(Wait)로 바꿀 예정)
        time.sleep(2)
        
        # 4. 검증: 브라우저 탭 제목(Title)에 'Pa-Bi'나 원하는 글자가 있는지 확인
        print(f"현재 페이지 제목: {driver.title}")
        assert "Pa-Bi" in driver.title  # 사이트 제목에 맞는 글자로 수정 필요할 수 있음
        
    finally:
        # 5. 테스트 끝나면 브라우저 끄기 (중요)
        driver.quit()