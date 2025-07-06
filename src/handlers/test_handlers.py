"""
네이버 블로그 자동화 - 테스트 핸들러들
"""
from src.config import ConfigManager
from src.utils import ChromeSetup, GeminiAPI, Logger


def handle_chrome_setup_test() -> None:
    """Chrome 환경 설정 테스트 핸들러"""
    logger = Logger()
    config_manager = ConfigManager()
    config = config_manager.get_all()
    
    print("\n==== Chrome 환경 설정 테스트 ====")
    
    try:
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


def handle_api_test() -> None:
    """Gemini API 테스트 핸들러"""
    logger = Logger()
    config_manager = ConfigManager()
    config = config_manager.get_all()
    
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