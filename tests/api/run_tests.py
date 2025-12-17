import pytest
import sys

def run_tests():
    print("=" * 50)
    print("🚀 Pa-Bi Auction QA Automation Started (Python Runner)")
    print("=" * 50)

    # 1. API 테스트 실행
    print("\n[Step 1] API Test Running...")
    # pytest.main()을 사용해 코드 내부에서 테스트 실행
    # Exit Code 0: 성공, 그 외: 실패
    api_result = pytest.main(["-v", "tests/api"])
    
    if api_result != 0:
        print("\n❌ API Tests Failed! Stopping execution.")
        sys.exit(1) # 테스트 실패 시 프로세스 종료 (Fail Fast)
    else:
        print("✅ API Tests Passed!")

    # 2. UI 테스트 실행
    print("\n[Step 2] UI Test Running...")
    ui_result = pytest.main(["-s", "tests/ui"]) # -s: print문 출력 허용

    if ui_result != 0:
        print("\n❌ UI Tests Failed!")
        sys.exit(1)
    else:
        print("✅ UI Tests Passed!")

    print("\n" + "=" * 50)
    print("✨ All Tests Completed Successfully ✨")
    print("=" * 50)

if __name__ == "__main__":
    run_tests()