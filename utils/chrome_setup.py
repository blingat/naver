import os
import sys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

class ChromeSetup:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def get_chrome_profile_path(self):
        """Chrome 프로필 경로 자동 설정"""
        # config에서 사용자 지정 경로 확인
        custom_path = self.config.get('chrome_profile_path', '').strip()
        if custom_path and os.path.exists(custom_path):
            if self.logger:
                self.logger.log(f"[Chrome] 사용자 지정 프로필 사용: {custom_path}")
            return custom_path
        
        # 프로젝트 내 chrome_profile 디렉토리 사용
        default_path = os.path.join(self.project_root, 'chrome_profile')
        
        # 디렉토리가 없으면 생성
        if not os.path.exists(default_path):
            try:
                os.makedirs(default_path, exist_ok=True)
                if self.logger:
                    self.logger.log(f"[Chrome] 프로필 디렉토리 생성: {default_path}")
            except Exception as e:
                if self.logger:
                    self.logger.log(f"[Chrome] 프로필 디렉토리 생성 실패: {e}")
                raise Exception(f"Chrome 프로필 디렉토리 생성 실패: {e}")
        
        if self.logger:
            self.logger.log(f"[Chrome] 기본 프로필 사용: {default_path}")
        return default_path
    
    def get_chromedriver_path(self):
        """ChromeDriver 경로 자동 설정 (webdriver-manager 사용)"""
        # config에서 사용자 지정 경로 확인
        custom_path = self.config.get('chromedriver_path', '').strip()
        if custom_path and os.path.exists(custom_path):
            if self.logger:
                self.logger.log(f"[Chrome] 사용자 지정 ChromeDriver 사용: {custom_path}")
            return custom_path
        
        # webdriver-manager로 자동 다운로드
        try:
            if self.logger:
                self.logger.log("[Chrome] ChromeDriver 자동 다운로드 중...")
            
            driver_path = ChromeDriverManager().install()
            
            if self.logger:
                self.logger.log(f"[Chrome] ChromeDriver 다운로드 완료: {driver_path}")
            return driver_path
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"[Chrome] ChromeDriver 자동 다운로드 실패: {e}")
            raise Exception(f"ChromeDriver 다운로드 실패: {e}")
    
    def create_chrome_options(self):
        """Chrome 옵션 생성"""
        options = uc.ChromeOptions()
        
        # 프로필 경로 설정
        profile_path = self.get_chrome_profile_path()
        options.add_argument(f"--user-data-dir={profile_path}")
        
        # 포트 충돌 방지 및 안정성 옵션
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # 기본 옵션들
        options.add_argument('--lang=ko-KR')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-automation')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        # 쿠키 및 세션 관련 옵션 강화 (팝업창 레이아웃에 영향주는 옵션 제거)
        options.add_argument('--enable-cookies')
        options.add_argument('--disable-web-security')  # 팝업창 레이아웃에 영향
        options.add_argument('--disable-features=VizDisplayCompositor')  # 렌더링 영향
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        
        # User-Agent 설정으로 자동화 탐지 회피
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 창 크기 설정 (팝업창 레이아웃 보호를 위해 scale 옵션도 제거)
        scale = self.config.get('window_scale', 1.0)
        if scale != 1.0:
            options.add_argument(f"--force-device-scale-factor={scale}")
        
        return options
    
    def create_chrome_driver(self):
        """Chrome 드라이버 생성"""
        try:
            if self.logger:
                self.logger.log("[Chrome] 드라이버 생성 시작")
            
            # 1. Chrome 설치 상태 재확인
            if not self.validate_chrome_installation():
                raise Exception("Chrome이 설치되지 않았거나 실행할 수 없습니다")
            
            # 2. ChromeDriver 경로 가져오기
            driver_path = self.get_chromedriver_path()
            if self.logger:
                self.logger.log(f"[Chrome] 사용할 ChromeDriver: {driver_path}")
            
            # 3. ChromeDriver 파일 존재 확인
            if not os.path.exists(driver_path):
                raise Exception(f"ChromeDriver 파일이 존재하지 않습니다: {driver_path}")
            
            # 4. 실행 중인 Chrome 프로세스 확인
            import subprocess
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
                                      capture_output=True, text=True, timeout=10)
                chrome_processes = result.stdout.count('chrome.exe')
                if self.logger:
                    self.logger.log(f"[Chrome] 현재 실행 중인 Chrome 프로세스: {chrome_processes}개")
            except Exception as e:
                if self.logger:
                    self.logger.log(f"[Chrome] 프로세스 확인 실패: {e}")
            
            # 5. 프로필 디렉토리 상태 확인
            profile_path = self.get_chrome_profile_path()
            if os.path.exists(profile_path):
                try:
                    # 프로필 디렉토리 내 파일 수 확인
                    file_count = sum(len(files) for _, _, files in os.walk(profile_path))
                    if self.logger:
                        self.logger.log(f"[Chrome] 프로필 디렉토리 파일 수: {file_count}개")
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"[Chrome] 프로필 디렉토리 확인 실패: {e}")
            
            # 6. 포트 충돌 방지를 위해 여러 번 시도
            max_attempts = 3
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    if self.logger:
                        self.logger.log(f"[Chrome] 브라우저 시작 시도 {attempt + 1}/{max_attempts}")
                    
                    # 7. 매번 완전히 새로운 Chrome 옵션 생성
                    options = uc.ChromeOptions()
                    
                    # 프로필 경로 설정
                    options.add_argument(f"--user-data-dir={profile_path}")
                    
                    # 포트 충돌 방지 및 안정성 옵션
                    options.add_argument('--no-first-run')
                    options.add_argument('--no-default-browser-check')
                    options.add_argument('--disable-default-apps')
                    options.add_argument('--disable-popup-blocking')
                    options.add_argument('--disable-translate')
                    options.add_argument('--disable-background-networking')
                    options.add_argument('--disable-sync')
                    options.add_argument('--disable-ipc-flooding-protection')
                    
                    # 기본 옵션들
                    options.add_argument('--lang=ko-KR')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_argument('--disable-extensions')
                    options.add_argument('--disable-automation')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--no-sandbox')
                    
                    # 쿠키 및 세션 관련 옵션
                    options.add_argument('--enable-cookies')
                    options.add_argument('--disable-web-security')
                    options.add_argument('--disable-features=VizDisplayCompositor')
                    options.add_argument('--disable-background-timer-throttling')
                    options.add_argument('--disable-renderer-backgrounding')
                    options.add_argument('--disable-backgrounding-occluded-windows')
                    
                    # User-Agent 설정
                    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                    
                    # 창 크기 설정
                    scale = self.config.get('window_scale', 1.0)
                    if scale != 1.0:
                        options.add_argument(f"--force-device-scale-factor={scale}")
                    
                    if self.logger:
                        self.logger.log(f"[Chrome] 새로운 옵션 생성: {len(options.arguments)}개")
                    
                    # 8. 환경 변수 확인
                    if self.logger:
                        self.logger.log(f"[Chrome] PATH 환경변수 길이: {len(os.environ.get('PATH', ''))}")
                        self.logger.log(f"[Chrome] TEMP 디렉토리: {os.environ.get('TEMP', 'N/A')}")
                    
                    # 9. 드라이버 생성 (간단한 방식)
                    if self.logger:
                        self.logger.log("[Chrome] undetected_chromedriver 호출 시작")
                    
                    # 간단한 방식으로 드라이버 생성
                    driver = uc.Chrome(
                        options=options, 
                        driver_executable_path=driver_path
                    )
                    
                    if self.logger:
                        self.logger.log("[Chrome] 드라이버 객체 생성 완료")
                    
                    # 10. 브라우저 응답 확인
                    try:
                        current_url = driver.current_url
                        if self.logger:
                            self.logger.log(f"[Chrome] 브라우저 응답 확인: {current_url}")
                    except Exception as e:
                        if self.logger:
                            self.logger.log(f"[Chrome] 브라우저 응답 확인 실패: {e}")
                        raise e
                    
                    # 11. 창 크기 직접 조정
                    width = self.config.get('window_width', 1200)
                    height = self.config.get('window_height', 900)
                    driver.set_window_size(width, height)
                    if self.logger:
                        self.logger.log(f"[Chrome] 창 크기 설정: {width}x{height}")
                    
                    # 12. 자동화 탐지 방지를 위한 스크립트 실행
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko']})")
                    if self.logger:
                        self.logger.log("[Chrome] 자동화 탐지 방지 스크립트 실행 완료")
                    
                    if self.logger:
                        self.logger.log("[Chrome] 브라우저 시작 완료")
                    
                    return driver
                    
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    if self.logger:
                        self.logger.log(f"[Chrome] 브라우저 시작 시도 {attempt + 1} 실패: {error_msg}")
                    
                    # 13. 오류 유형별 상세 분석
                    if "session not created" in error_msg:
                        if self.logger:
                            self.logger.log("[Chrome] 세션 생성 실패 - 포트 충돌 가능성")
                    elif "cannot connect to chrome" in error_msg:
                        if self.logger:
                            self.logger.log("[Chrome] Chrome 연결 실패 - 프로세스 문제 가능성")
                    elif "chrome not reachable" in error_msg:
                        if self.logger:
                            self.logger.log("[Chrome] Chrome 도달 불가 - 네트워크/방화벽 문제 가능성")
                    elif "unknown error" in error_msg:
                        if self.logger:
                            self.logger.log("[Chrome] 알 수 없는 오류 - 권한/리소스 문제 가능성")
                    elif "reuse the ChromeOptions" in error_msg:
                        if self.logger:
                            self.logger.log("[Chrome] ChromeOptions 재사용 오류 - 새로운 옵션으로 재시도")
                    
                    if attempt < max_attempts - 1:
                        # 다음 시도 전에 잠시 대기
                        import time
                        if self.logger:
                            self.logger.log("[Chrome] 5초 대기 후 재시도")
                        time.sleep(5)
                        continue
                    else:
                        # 모든 시도 실패
                        if self.logger:
                            self.logger.log(f"[Chrome] 모든 시도 실패. 최종 오류: {last_error}")
                        raise last_error
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"[Chrome] 브라우저 시작 실패: {e}")
            raise Exception(f"Chrome 브라우저 시작 실패: {e}")
    
    def validate_chrome_installation(self):
        """Chrome 설치 상태 확인"""
        chrome_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME', '')),
        ]
        
        # 1. 파일 존재 여부로 먼저 확인
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                if self.logger:
                    self.logger.log(f"[Chrome] Chrome 파일 확인: {chrome_path}")
                
                # 2. 실행 가능한지 버전 확인 시도
                try:
                    import subprocess
                    result = subprocess.run([chrome_path, '--version'], 
                                          capture_output=True, text=True, timeout=10,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        if self.logger:
                            self.logger.log(f"[Chrome] Chrome 설치 확인: {version} (경로: {chrome_path})")
                        return True
                    else:
                        if self.logger:
                            self.logger.log(f"[Chrome] Chrome 버전 확인 실패 ({chrome_path}): returncode={result.returncode}")
                        
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"[Chrome] Chrome 버전 확인 중 오류 ({chrome_path}): {e}")
                    # 파일이 존재하면 일단 설치된 것으로 간주
                    if self.logger:
                        self.logger.log(f"[Chrome] 파일 존재로 Chrome 설치 확인: {chrome_path}")
                    return True
        
        # 3. PATH에서 chrome 명령어 시도
        try:
            import subprocess
            result = subprocess.run(['chrome', '--version'], 
                                  capture_output=True, text=True, timeout=10,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                version = result.stdout.strip()
                if self.logger:
                    self.logger.log(f"[Chrome] Chrome 설치 확인: {version} (PATH)")
                return True
        except Exception as e:
            if self.logger:
                self.logger.log(f"[Chrome] PATH에서 Chrome 확인 실패: {e}")
        
        # 모든 확인 실패
        if self.logger:
            self.logger.log("[Chrome] Chrome 설치 확인 실패: 모든 경로에서 Chrome을 찾을 수 없음")
        return False
    
    def setup_chrome_environment(self):
        """Chrome 환경 전체 설정"""
        try:
            # Chrome 설치 확인
            if not self.validate_chrome_installation():
                print("❌ Chrome 브라우저가 설치되지 않았습니다.")
                print("💡 https://www.google.com/chrome/ 에서 Chrome을 설치해주세요.")
                return False
            
            # 프로필 경로 확인/생성
            profile_path = self.get_chrome_profile_path()
            print(f"✅ Chrome 프로필: {profile_path}")
            
            # ChromeDriver 확인/다운로드
            driver_path = self.get_chromedriver_path()
            print(f"✅ ChromeDriver: {driver_path}")
            
            print("✅ Chrome 환경 설정 완료!")
            return True
            
        except Exception as e:
            print(f"❌ Chrome 환경 설정 실패: {e}")
            return False 