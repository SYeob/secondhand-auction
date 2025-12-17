from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_view_first_product():
    # 1. 브라우저 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    try:
        # 2. 메인 페이지 접속
        driver.get("https://syeob.lovable.app/")
        
        # 3. 로딩 대기 및 상품 찾기
        wait = WebDriverWait(driver, 10)

        print("상품 목록 로딩 대기 중...")
        target_text_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), '현재가')]")))
        driver.execute_script("arguments[0].click();", target_text_element)
        
        time.sleep(3) 
        
        current_url = driver.current_url
        print(f"이동한 페이지 URL: {current_url}")
        
        assert current_url != "https://syeob.lovable.app/" or "입찰" in driver.page_source
        print("상품 상세 페이지 진입 성공")

    except Exception as e:
        print(f"테스트 실패: {e}")
        raise e 

    finally:
        driver.quit()