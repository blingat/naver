import sys
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from utils.logger import Logger
from modules.login import NaverLogin
from modules.neighbor_add import NeighborAddAutomation
from modules.comment import CommentAutomation
from modules.gemini import GeminiAPI

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json 파일이 없습니다. 파일을 생성해주세요.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("config.json 파일 형식이 잘못되었습니다.")
        sys.exit(1)

def validate_config(config):
    """설정 파일 검증"""
    required_keys = ['max_action_per_run']
    for key in required_keys:
        if key not in config:
            print(f"[오류] config.json에 {key} 설정이 없습니다.")
            return False
    return True

def check_required_files(file_list):
    """필수 파일 존재 여부 확인"""
    missing_files = []
    for file_path in file_list:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    return missing_files

def initialize_chrome_driver(config, logger=None):
    """Chrome 드라이버 초기화 (ChromeSetup 사용)"""
    try:
        from utils.chrome_setup import ChromeSetup
        chrome_setup = ChromeSetup(config, logger)
        return chrome_setup.create_chrome_driver()
    except Exception as e:
        raise Exception(f"Chrome 드라이버 초기화 실패: {e}")

def handle_neighbor_add():
    """서이추 자동화 핸들러"""
    logger = Logger()
    config = load_config()
    
    if not validate_config(config):
        return
    
    print("\n==== 서이추(서로이웃 추가) 자동화 ====")
    
    # 1. 로그인 정보 입력받기
    print("\n[1단계] 네이버 로그인")
    print("※ 크롬 프로필에 이미 로그인되어 있다면 Enter만 누르세요.")
    user_id = input("네이버 아이디 (Enter: 자동 로그인): ").strip()
    user_pw = ""
    
    if user_id:  # 아이디를 입력한 경우에만 비밀번호 요청
        user_pw = input("네이버 비밀번호: ").strip()
        if not user_pw:
            print("[오류] 비밀번호를 입력해주세요.")
            return
    
    # 2. 서이추 개수 입력받기 (PRD 순서에 맞게)
    print("\n[2단계] 서이추 설정")
    while True:
        try:
            count_input = input("몇 명에게 서로이웃 추가를 할까요? (최대 50): ").strip()
            if count_input == "0":
                print("메인 메뉴로 돌아갑니다.")
                return
            
            count = int(count_input)
            if count < 1 or count > 50:
                print("1~50 사이의 숫자를 입력하세요.")
                continue
            break
        except ValueError:
            print("숫자만 입력하세요.")
    
    # 3. 타겟 키워드 입력받기
    keyword = input("타겟 블로그 키워드를 입력하세요: ").strip()
    if not keyword:
        print("[오류] 키워드를 입력해주세요.")
        return
    
    # 4. 실행
    login = None
    try:
        print("\n[3단계] 자동화 실행")
        print("브라우저를 시작합니다...")
        
        login = NaverLogin(config, logger)
        login.start_browser()
        
        # 로그인 처리
        if user_id and user_pw:
            print("로그인을 시도합니다...")
            if not login.login_with_retry(user_id, user_pw, max_attempts=3):
                print("[오류] 로그인에 실패했습니다.")
                return
        else:
            print("저장된 세션으로 진행합니다...")
        
        # 서이추 자동화 실행
        neighbor = NeighborAddAutomation(login.driver, logger, config)
        neighbor.run(keyword, count)
        
        print("\n✅ 서이추 자동화가 완료되었습니다.")
        print("※ 브라우저는 세션 유지를 위해 열어둡니다.")
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        
    except KeyboardInterrupt:
        print("\n\n사용자가 작업을 중단했습니다.")
    except Exception as e:
        logger.log(f"[서이추] 자동화 중 오류 발생: {e}")
        print(f"\n[오류] 자동화 중 문제가 발생했습니다: {e}")
    finally:
        if login and login.driver:
            try:
                login.quit()
            except:
                pass

def handle_like_automation():
    """공감 자동화 핸들러"""
    print("\n==== 공감 자동화 ====")
    print("[준비 중] 이 기능은 아직 구현되지 않았습니다.")
    input("Enter를 누르면 메인 메뉴로 돌아갑니다...")

def handle_comment_automation():
    """댓글 자동화 핸들러"""
    logger = Logger()
    config = load_config()
    
    if not validate_config(config):
        return
    
    print("\n==== 댓글 자동화 ====")
    
    # Gemini API 키 확인
    gemini_api_key = config.get('gemini_api_key', '')
    if not gemini_api_key or gemini_api_key == "여기에 Gemini API 키 입력":
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        print("config.json 파일에서 gemini_api_key를 설정해주세요.")
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        return
    
    # Chrome 환경 확인 제거 (NaverLogin에서 처리)
    
    # 1. 로그인 정보 입력받기
    print("\n[1단계] 네이버 로그인")
    print("※ 크롬 프로필에 이미 로그인되어 있다면 Enter만 누르세요.")
    user_id = input("네이버 아이디 (Enter: 자동 로그인): ").strip()
    user_pw = ""
    
    if user_id:  # 아이디를 입력한 경우에만 비밀번호 요청
        user_pw = input("네이버 비밀번호: ").strip()
        if not user_pw:
            print("[오류] 비밀번호를 입력해주세요.")
            return
    
    # 2. 댓글 작성 개수 입력
    print("\n[2단계] 댓글 자동화 설정")
    while True:
        try:
            count_input = input("몇 명의 이웃글에 댓글을 달까요? (최대 50): ").strip()
            if count_input == "0":
                print("메인 메뉴로 돌아갑니다.")
                return
            
            comment_count = int(count_input)
            if comment_count < 1 or comment_count > 50:
                print("1~50 사이의 숫자를 입력하세요.")
                continue
            break
        except ValueError:
            print("숫자만 입력하세요.")
    
    # 3. 시작 페이지 입력
    while True:
        try:
            page_input = input("몇 페이지부터 댓글을 달까요? (숫자 입력): ").strip()
            start_page = int(page_input)
            
            if start_page >= 1:
                break
            else:
                print("⚠️  1 이상의 숫자를 입력해주세요.")
        except ValueError:
            print("⚠️  올바른 숫자를 입력해주세요.")
    
    print(f"\n📋 설정 확인:")
    print(f"   📝 댓글 작성 목표: {comment_count}개")
    print(f"   📄 시작 페이지: {start_page}")
    print(f"   🤖 AI: Gemini API 사용")
    
    confirm = input("\n위 설정으로 댓글 자동화를 시작하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("댓글 자동화를 취소했습니다.")
        return
    
    # 4. 실행
    login = None
    try:
        print("\n[3단계] 자동화 실행")
        print("브라우저를 시작합니다...")
        
        login = NaverLogin(config, logger)
        login.start_browser()
        
        # 로그인 처리
        if user_id and user_pw:
            print("로그인을 시도합니다...")
            if not login.login_with_retry(user_id, user_pw, max_attempts=3):
                print("[오류] 로그인에 실패했습니다.")
                return
        else:
            print("저장된 세션으로 진행합니다...")
        
        # 댓글 자동화 실행
        comment_automation = CommentAutomation(login.driver, config, logger)
        comment_automation.run_comment_automation(comment_count, start_page)
        
        print("\n✅ 댓글 자동화가 완료되었습니다.")
        print("※ 브라우저는 세션 유지를 위해 열어둡니다.")
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 댓글 자동화를 중단했습니다.")
        logger.log("[댓글자동화] 사용자 중단")
        
    except Exception as e:
        print(f"\n❌ 댓글 자동화 중 오류 발생: {e}")
        logger.log(f"[댓글자동화] 오류 발생: {e}")
        
    finally:
        if login and login.driver:
            try:
                login.quit()
            except:
                pass

def handle_chrome_setup_test():
    """Chrome 환경 설정 테스트 핸들러"""
    logger = Logger()
    config = load_config()
    
    print("\n==== Chrome 환경 설정 테스트 ====")
    
    try:
        from utils.chrome_setup import ChromeSetup
        chrome_setup = ChromeSetup(config, logger)
        
        print("🔍 Chrome 환경을 확인하는 중...")
        
        # Chrome 환경 전체 설정 테스트
        if chrome_setup.setup_chrome_environment():
            print("\n✅ Chrome 환경 설정이 완료되었습니다!")
            
            # 브라우저 실행 테스트
            test_browser = input("\n브라우저 실행 테스트를 하시겠습니까? (y/N): ").strip().lower()
            if test_browser == 'y':
                print("\n🚀 브라우저를 실행하는 중...")
                try:
                    driver = chrome_setup.create_chrome_driver()
                    driver.get("https://www.naver.com")
                    print("✅ 브라우저 실행 성공!")
                    print("💡 브라우저가 열렸습니다. 확인 후 아무 키나 누르세요.")
                    input()
                    driver.quit()
                    print("✅ 브라우저 종료 완료")
                except Exception as e:
                    print(f"❌ 브라우저 실행 실패: {e}")
                    logger.log(f"[Chrome테스트] 브라우저 실행 실패: {e}")
        else:
            print("\n❌ Chrome 환경 설정에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ Chrome 환경 테스트 실패: {e}")
        logger.log(f"[Chrome테스트] 환경 테스트 실패: {e}")
    
    input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")

def handle_api_test():
    """Gemini API 테스트 핸들러"""
    logger = Logger()
    config = load_config()
    
    print("\n==== Gemini API 테스트 ====")
    
    # API 키 확인
    gemini_api_key = config.get('gemini_api_key', '')
    if not gemini_api_key or gemini_api_key == "여기에 Gemini API 키 입력":
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        print("config.json 파일에서 gemini_api_key를 설정해주세요.")
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        return
    
    # Gemini API 초기화
    try:
        gemini = GeminiAPI(gemini_api_key, logger)
        print("✅ Gemini API 초기화 완료")
        
        # API 연결 테스트
        print("\n🔍 API 연결 테스트 중...")
        success, message = gemini.test_connection()
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ API 연결 실패: {message}")
            input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
            return
            
    except Exception as e:
        print(f"❌ Gemini API 초기화 실패: {e}")
        logger.log(f"[API테스트] Gemini API 초기화 실패: {e}")
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        return
    
    # 대화형 테스트
    print("\n" + "="*50)
    print("Gemini API 대화형 테스트")
    print("="*50)
    print("💡 팁:")
    print("  - 자유롭게 질문하거나 요청해보세요")
    print("  - '댓글테스트'를 입력하면 블로그 댓글 생성을 테스트할 수 있습니다")
    print("  - '0'을 입력하면 메인 메뉴로 돌아갑니다")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n프롬프트를 입력하세요: ").strip()
            
            if user_input == '0':
                print("메인 메뉴로 돌아갑니다.")
                break
            
            if not user_input:
                print("⚠️  프롬프트를 입력해주세요.")
                continue
            
            # 댓글 테스트 특별 명령어
            if user_input.lower() == '댓글테스트':
                print("\n🧪 블로그 댓글 생성 테스트")
                blog_title = input("블로그 글 제목을 입력하세요: ").strip()
                if not blog_title:
                    print("⚠️  제목을 입력해주세요.")
                    continue
                
                blog_content = input("블로그 내용 미리보기 (선택사항, Enter로 건너뛰기): ").strip()
                
                print("\n🤖 Gemini가 댓글을 생성하는 중...")
                comment, error = gemini.generate_comment(blog_title, blog_content)
                
                if error:
                    print(f"❌ 댓글 생성 실패: {error}")
                    logger.log(f"[API테스트] 댓글 생성 실패: {error}")
                else:
                    print(f"\n✅ 생성된 댓글:")
                    print(f"💬 {comment}")
                    print(f"📏 길이: {len(comment)}자")
                    
            else:
                # 일반 프롬프트 처리
                print(f"\n🤖 Gemini가 응답하는 중...")
                print(f"📝 입력: {user_input}")
                
                response, error = gemini.generate_text(user_input, max_tokens=500)
                
                if error:
                    print(f"❌ API 요청 실패: {error}")
                    logger.log(f"[API테스트] API 요청 실패: {error}")
                else:
                    print(f"\n✅ Gemini 응답:")
                    print("-" * 30)
                    print(response)
                    print("-" * 30)
                    print(f"📏 응답 길이: {len(response)}자")
                    
        except KeyboardInterrupt:
            print("\n\n사용자가 테스트를 중단했습니다.")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
            logger.log(f"[API테스트] 예상치 못한 오류: {e}")
    
    print("\nGemini API 테스트를 종료합니다.")
    input("Enter를 누르면 메인 메뉴로 돌아갑니다...")

def main_menu():
    """메인 메뉴"""
    while True:
        print("\n" + "="*40)
        print("==== 네이버 블로그 자동화 ====")
        print("1. 공감 자동화")
        print("2. 서이추 자동화")
        print("3. 댓글 자동화")
        print("8. Chrome 환경 설정 테스트")
        print("9. Gemini/OpenAI API 테스트")
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

if __name__ == "__main__":
    print("네이버 블로그 자동화 프로그램 v1.0")
    
    # 필수 파일 확인
    try:
        with open('eut_message.txt', 'r', encoding='utf-8') as f:
            message = f.read().strip()
            if not message:
                print("[경고] eut_message.txt 파일이 비어있습니다.")
                print("서이추 메시지를 작성해주세요.")
    except FileNotFoundError:
        print("[경고] eut_message.txt 파일이 없습니다.")
        print("서이추 자동화를 사용하려면 이 파일을 생성해주세요.")
    
    main_menu() 