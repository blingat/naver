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
            # ChromeDriver 경로 가져오기
            driver_path = self.get_chromedriver_path()
            
            # Chrome 옵션 생성
            options = self.create_chrome_options()
            
            # 드라이버 생성
            driver = uc.Chrome(options=options, driver_executable_path=driver_path)
            
            # 창 크기 직접 조정
            width = self.config.get('window_width', 1200)
            height = self.config.get('window_height', 900)
            driver.set_window_size(width, height)
            
            # 자동화 탐지 방지를 위한 스크립트 실행
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko']})")
            
            if self.logger:
                self.logger.log("[Chrome] 브라우저 시작 완료")
            
            return driver
            
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
            'chrome'  # PATH에 있는 경우
        ]
        
        for chrome_path in chrome_paths:
            try:
                import subprocess
                if chrome_path == 'chrome':
                    # PATH에서 chrome 명령어 시도
                    result = subprocess.run(['chrome', '--version'], capture_output=True, text=True, timeout=5)
                else:
                    # 파일 존재 여부 먼저 확인
                    if not os.path.exists(chrome_path):
                        continue
                    result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    if self.logger:
                        self.logger.log(f"[Chrome] Chrome 설치 확인: {version} (경로: {chrome_path})")
                    return True
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"[Chrome] Chrome 경로 시도 실패 ({chrome_path}): {e}")
                continue
        
        # 모든 경로에서 실패한 경우
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