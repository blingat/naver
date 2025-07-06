"""
네이버 블로그 자동화 프로그램 v1.1
"""
import sys
import os

from src.handlers import (
    handle_neighbor_add,
    handle_comment_automation,
    handle_like_automation,
    handle_chrome_setup_test,
    handle_api_test
)


def check_required_files() -> None:
    """필수 파일 존재 여부 확인"""
    try:
        message_file = 'eut_message.txt'
        if os.path.exists(message_file):
            with open(message_file, 'r', encoding='utf-8') as f:
                message = f.read().strip()
                if not message:
                    print("[경고] eut_message.txt 파일이 비어있습니다.")
                    print("서이추 메시지를 작성해주세요.")
        else:
            print("[경고] eut_message.txt 파일이 없습니다.")
            print("서이추 자동화를 사용하려면 이 파일을 생성해주세요.")
    except Exception as e:
        print(f"[경고] 파일 확인 중 오류: {e}")


def main_menu() -> None:
    """메인 메뉴"""
    while True:
        print("\n" + "="*40)
        print("==== 네이버 블로그 자동화 v1.1 ====")
        print("1. 공감 자동화")
        print("2. 서이추 자동화")
        print("3. 댓글 자동화")
        print("8. Chrome 환경 설정 테스트")
        print("9. Gemini API 테스트")
        print("0. 종료")
        print("="*40)
        
        try:
            choice = input("번호를 입력하세요: ").strip()
            
            if choice == '0':
                print("\n프로그램을 종료합니다.")
                print("이용해 주셔서 감사합니다!")
                sys.exit(0)
            elif choice == '1':
                handle_like_automation()
            elif choice == '2':
                handle_neighbor_add()
            elif choice == '3':
                handle_comment_automation()
            elif choice == '8':
                handle_chrome_setup_test()
            elif choice == '9':
                handle_api_test()
            else:
                print("잘못된 입력입니다. 0~3, 8~9 중에서 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            sys.exit(0)
        except Exception as e:
            print(f"\n[오류] 예상치 못한 오류가 발생했습니다: {e}")


def main() -> None:
    """메인 함수"""
    print("네이버 블로그 자동화 프로그램 v1.1")
    print("🚀 코드 품질 개선 완료!")
    print("✨ BaseAutomation 상속, 타입 힌트, docstring 추가")
    print("🔧 ConfigManager 도입, 핸들러 분리")
    
    # 필수 파일 확인
    check_required_files()
    
    # 메인 메뉴 실행
    main_menu()


if __name__ == "__main__":
    main() 