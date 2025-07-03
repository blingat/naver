import os
import sys
import time
import subprocess
import psutil
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
        # config에서 사용자 지정 경로 확인 (하위 호환성)
        custom_path = self.config.get('chromedriver_path', '').strip()
        if custom_path and os.path.exists(custom_path):
            if self.logger:
                self.logger.log(f"[Chrome] 사용자 지정 ChromeDriver 사용: {custom_path}")
            return custom_path
        
        # webdriver-manager로 자동 다운로드 (기본 방식)
        try:
            if self.logger:
                self.logger.log("[Chrome] ChromeDriver 자동 관리 시작...")
            
            driver_path = ChromeDriverManager().install()
            
            if self.logger:
                self.logger.log(f"[Chrome] ChromeDriver 준비 완료: {driver_path}")
            return driver_path
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"[Chrome] ChromeDriver 자동 관리 실패: {e}")
            raise Exception(f"ChromeDriver 자동 관리 실패: {e}")
    
    def kill_chrome_processes(self):
        """Chrome 관련 프로세스 정리"""
        try:
            chrome_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if chrome_processes:
                if self.logger:
                    self.logger.log(f"[Chrome] {len(chrome_processes)}개 Chrome 프로세스 발견, 정리 중...")
                
                for proc in chrome_processes:
                    try:
                        proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                time.sleep(2)  # 프로세스 종료 대기
                
                if self.logger:
                    self.logger.log("[Chrome] Chrome 프로세스 정리 완료")
            else:
                if self.logger:
                    self.logger.log("[Chrome] 정리할 Chrome 프로세스 없음")
                    
        except Exception as e:
            if self.logger:
                self.logger.log(f"[Chrome] 프로세스 정리 중 오류: {e}")
    
    def create_chrome_options(self):
        """Chrome 옵션 생성 (매번 새로 생성)"""
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
        
        # 안정성 강화 옵션
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        
        # 포트 충돌 방지
        options.add_argument('--remote-debugging-port=0')  # 자동 포트 할당
        
        # User-Agent 설정으로 자동화 탐지 회피
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 창 크기 설정
        scale = self.config.get('window_scale', 1.0)
        if scale != 1.0:
            options.add_argument(f"--force-device-scale-factor={scale}")
        
        return options
    
    def create_chrome_driver_with_retry(self, max_attempts=3):
        """재시도 로직이 포함된 Chrome 드라이버 생성 (최적화)"""
        import threading
        
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                if self.logger:
                    self.logger.log(f"[Chrome] 브라우저 시작 시도 {attempt}/{max_attempts}")
                
                # 첫 번째 시도 실패 시 Chrome 프로세스 정리
                if attempt > 1:
                    if self.logger:
                        self.logger.log("[Chrome] Chrome 프로세스 정리 후 재시도")
                    self.kill_chrome_processes()
                    time.sleep(2)
                
                # ChromeDriver 경로 가져오기
                driver_path = self.get_chromedriver_path()
                
                # 최적화된 Chrome 옵션 생성 (create_chrome_options 메서드 사용)
                options = self.create_chrome_options()
                
                # 추가 최적화 옵션
                options.add_argument('--disable-logging')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-web-security')
                options.add_argument('--no-first-run')
                options.add_argument('--no-default-browser-check')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--disable-translate')
                options.add_argument('--disable-default-apps')
                options.add_argument('--disable-sync')
                options.add_argument('--disable-features=TranslateUI')
                options.add_argument('--disable-features=ChromeWhatsNewUI')
                
                # 페이지 로드 전략 설정 (더 빠른 시작)
                options.page_load_strategy = 'eager'  # DOM 로드 완료 시 진행
                
                if self.logger:
                    self.logger.log(f"[Chrome] 최적화된 옵션으로 드라이버 생성 시도...")
                
                # 타임아웃 설정 (30초로 단축)
                driver = None
                driver_created = False
                error_occurred = None
                
                def create_driver():
                    nonlocal driver, driver_created, error_occurred
                    try:
                        # undetected_chromedriver 대신 일반 Chrome 사용 (더 빠름)
                        driver = uc.Chrome(
                            options=options,
                            driver_executable_path=driver_path,
                            version_main=None,
                            use_subprocess=False  # 서브프로세스 사용 안함 (더 빠름)
                        )
                        driver_created = True
                    except Exception as e:
                        error_occurred = e
                
                # 별도 스레드에서 드라이버 생성
                thread = threading.Thread(target=create_driver)
                thread.daemon = True
                thread.start()
                thread.join(timeout=30)  # 30초 타임아웃으로 단축
                
                if thread.is_alive():
                    if self.logger:
                        self.logger.log("[Chrome] 드라이버 생성 타임아웃 (30초)")
                    raise TimeoutError("Chrome 드라이버 생성 타임아웃")
                
                if error_occurred:
                    raise error_occurred
                
                if not driver_created or driver is None:
                    raise Exception("드라이버 생성 실패")
                
                # config.json의 창 크기 설정 적용
                try:
                    width = self.config.get('window_width', 1200)
                    height = self.config.get('window_height', 900)
                    driver.set_window_size(width, height)
                    
                    # 창 위치 설정 (선택사항)
                    if 'window_position_x' in self.config and 'window_position_y' in self.config:
                        x = self.config.get('window_position_x', 0)
                        y = self.config.get('window_position_y', 0)
                        driver.set_window_position(x, y)
                    
                    if self.logger:
                        self.logger.log(f"[Chrome] 창 크기 설정: {width}x{height}")
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"[Chrome] 창 크기 설정 실패 (무시): {e}")
                
                # 자동화 탐지 방지 스크립트 (빠르게 실행)
                try:
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        'source': '''
                            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                            Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko']});
                        '''
                    })
                except:
                    pass  # 실패해도 계속 진행
                
                if self.logger:
                    self.logger.log(f"[Chrome] 브라우저 시작 성공 (시도 {attempt}/{max_attempts})")
                
                return driver
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                if self.logger:
                    self.logger.log(f"[Chrome] 브라우저 시작 시도 {attempt} 실패: {error_msg}")
                
                # 실패한 드라이버 정리
                try:
                    if 'driver' in locals() and driver:
                        driver.quit()
                except:
                    pass
                
                # 마지막 시도가 아니면 재시도
                if attempt < max_attempts:
                    wait_time = 2 + attempt
                    if self.logger:
                        self.logger.log(f"[Chrome] {wait_time}초 대기 후 재시도")
                    time.sleep(wait_time)
                else:
                    if self.logger:
                        self.logger.log(f"[Chrome] 모든 시도 실패. 최종 오류: {error_msg}")
        
        # 모든 시도 실패
        raise Exception(f"Chrome 브라우저 시작 실패 (총 {max_attempts}회 시도): {last_error}")
    
    def create_chrome_driver(self):
        """Chrome 드라이버 생성 (재시도 로직 포함)"""
        return self.create_chrome_driver_with_retry()
    
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
                if chrome_path == 'chrome':
                    # PATH에서 chrome 명령어 시도
                    result = subprocess.run(['chrome', '--version'], capture_output=True, text=True, timeout=10)
                else:
                    # 파일 존재 여부 먼저 확인
                    if not os.path.exists(chrome_path):
                        continue
                    result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    if self.logger:
                        self.logger.log(f"[Chrome] Chrome 설치 확인: {version} (경로: {chrome_path})")
                    return True
                    
            except subprocess.TimeoutExpired:
                if self.logger:
                    self.logger.log(f"[Chrome] Chrome 버전 확인 타임아웃 ({chrome_path})")
                # 파일이 존재하면 설치된 것으로 간주
                if chrome_path != 'chrome' and os.path.exists(chrome_path):
                    if self.logger:
                        self.logger.log(f"[Chrome] 파일 존재로 Chrome 설치 확인: {chrome_path}")
                    return True
            except Exception as e:
                if self.logger:
                    self.logger.log(f"[Chrome] Chrome 경로 시도 실패 ({chrome_path}): {e}")
                continue
        
        # 모든 경로에서 실패한 경우
        if self.logger:
            self.logger.log("[Chrome] Chrome 설치 확인 실패: 모든 경로에서 Chrome을 찾을 수 없음")
        return False
    
    def get_chrome_version_info(self):
        """Chrome과 ChromeDriver 버전 정보 반환"""
        try:
            # Chrome 버전 확인
            chrome_version = "알 수 없음"
            chrome_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    try:
                        result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            chrome_version = result.stdout.strip()
                            break
                    except:
                        continue
            
            # ChromeDriver 버전 확인
            driver_version = "알 수 없음"
            try:
                driver_path = self.get_chromedriver_path()
                result = subprocess.run([driver_path, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    driver_version = result.stdout.strip().split('\n')[0]
            except:
                pass
            
            return chrome_version, driver_version
            
        except Exception as e:
            return "오류", "오류"
    
    def setup_chrome_environment(self):
        """Chrome 환경 전체 설정"""
        try:
            # Chrome 설치 확인
            if not self.validate_chrome_installation():
                print("❌ Chrome 브라우저가 설치되지 않았습니다.")
                print("💡 https://www.google.com/chrome/ 에서 Chrome을 설치해주세요.")
                return False
            
            # 버전 정보 확인
            chrome_version, driver_version = self.get_chrome_version_info()
            print(f"✅ Chrome 버전: {chrome_version}")
            print(f"✅ ChromeDriver 버전: {driver_version}")
            
            # 프로필 경로 확인/생성
            profile_path = self.get_chrome_profile_path()
            print(f"✅ Chrome 프로필: {profile_path}")
            
            # ChromeDriver 확인/다운로드
            driver_path = self.get_chromedriver_path()
            print(f"✅ ChromeDriver: 자동 관리됨")
            
            print("✅ Chrome 환경 설정 완료!")
            return True
            
        except Exception as e:
            print(f"❌ Chrome 환경 설정 실패: {e}")
            return False 