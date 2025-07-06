"""
네이버 블로그 자동화 - 자동화 핸들러들
"""
from typing import Dict, Any

from src.config import ConfigManager
from src.utils import NaverLogin, Logger
from src.automation import NeighborAddAutomation, CommentAutomation


def handle_neighbor_add() -> None:
    """서이추 자동화 핸들러"""
    logger = Logger()
    config_manager = ConfigManager()
    config = config_manager.get_all()
    
    if not config_manager.validate():
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
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
    
    # 2. 서이추 개수 입력받기
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


def handle_comment_automation() -> None:
    """댓글 자동화 핸들러"""
    logger = Logger()
    config_manager = ConfigManager()
    config = config_manager.get_all()
    
    if not config_manager.validate():
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        return
    
    print("\n==== 댓글 자동화 ====")
    
    # Gemini API 키 확인
    gemini_api_key = config.get('gemini_api_key', '')
    if not gemini_api_key or gemini_api_key == "여기에 Gemini API 키 입력":
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        print("config.json 파일에서 gemini_api_key를 설정해주세요.")
        input("\nEnter를 누르면 메인 메뉴로 돌아갑니다...")
        return
    
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


def handle_like_automation() -> None:
    """공감 자동화 핸들러"""
    print("\n==== 공감 자동화 ====")
    print("[준비 중] 이 기능은 아직 구현되지 않았습니다.")
    input("Enter를 누르면 메인 메뉴로 돌아갑니다...") 