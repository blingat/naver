"""
네이버 블로그 자동화 - 기본 자동화 클래스
모든 자동화 기능의 공통 기능을 제공하는 베이스 클래스
"""
import time
import random
from typing import Optional, Any, Dict, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    WebDriverException
)

from src.utils.logger import Logger


class BaseAutomation:
    """
    자동화 기능의 기본 클래스
    
    공통 기능:
    - 드라이버 연결 상태 확인
    - 랜덤 대기 시간 생성
    - 안전한 요소 찾기
    - 에러 처리 및 로깅
    - 창 관리 (팝업, 메인 창)
    """
    
    def __init__(self, driver: webdriver.Chrome, logger: Optional[Logger] = None):
        """
        기본 자동화 클래스 초기화
        
        Args:
            driver: Chrome 웹드라이버
            logger: 로거 인스턴스 (선택사항)
        """
        self.driver = driver
        self.logger = logger or Logger()
        self.main_window = None
        self._save_main_window()
    
    def _save_main_window(self) -> None:
        """메인 창 핸들 저장"""
        try:
            self.main_window = self.driver.current_window_handle
        except Exception as e:
            self.log_error("메인 창 핸들 저장 실패", e)
    
    def log_info(self, message: str, category: str = "자동화") -> None:
        """정보 로그 기록"""
        if self.logger:
            self.logger.log(f"[{category}] {message}")
    
    def log_error(self, message: str, error: Exception, category: str = "자동화") -> None:
        """에러 로그 기록"""
        if self.logger:
            self.logger.log(f"[{category}] {message}: {error}")
    
    def random_wait(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
        """
        랜덤 대기 시간 생성 및 실행
        
        Args:
            min_seconds: 최소 대기 시간
            max_seconds: 최대 대기 시간
            
        Returns:
            실제 대기한 시간
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)
        return wait_time
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """
        안전한 요소 찾기 (타임아웃 포함)
        
        Args:
            by: 찾기 방법 (By.ID, By.CLASS_NAME 등)
            value: 찾을 값
            timeout: 타임아웃 시간 (초)
            
        Returns:
            찾은 요소 또는 None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
        except Exception as e:
            self.log_error(f"요소 찾기 실패 ({by}, {value})", e)
            return None
    
    def safe_find_elements(self, by: By, value: str, timeout: int = 10) -> List[Any]:
        """
        안전한 요소들 찾기 (타임아웃 포함)
        
        Args:
            by: 찾기 방법
            value: 찾을 값
            timeout: 타임아웃 시간 (초)
            
        Returns:
            찾은 요소들의 리스트
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return self.driver.find_elements(by, value)
        except TimeoutException:
            return []
        except Exception as e:
            self.log_error(f"요소들 찾기 실패 ({by}, {value})", e)
            return []
    
    def safe_click(self, element: Any, description: str = "요소") -> bool:
        """
        안전한 클릭 (에러 처리 포함)
        
        Args:
            element: 클릭할 요소
            description: 요소 설명 (로그용)
            
        Returns:
            성공 여부
        """
        try:
            if element and element.is_displayed() and element.is_enabled():
                element.click()
                return True
            else:
                self.log_error(f"{description} 클릭 불가", Exception("요소가 비활성화되어 있음"))
                return False
        except Exception as e:
            self.log_error(f"{description} 클릭 실패", e)
            return False
    
    def safe_send_keys(self, element: Any, text: str, description: str = "요소") -> bool:
        """
        안전한 텍스트 입력 (에러 처리 포함)
        
        Args:
            element: 입력할 요소
            text: 입력할 텍스트
            description: 요소 설명 (로그용)
            
        Returns:
            성공 여부
        """
        try:
            if element and element.is_displayed() and element.is_enabled():
                element.clear()
                element.send_keys(text)
                return True
            else:
                self.log_error(f"{description} 입력 불가", Exception("요소가 비활성화되어 있음"))
                return False
        except Exception as e:
            self.log_error(f"{description} 입력 실패", e)
            return False
    
    def check_driver_connection(self) -> bool:
        """
        드라이버 연결 상태 확인
        
        Returns:
            연결 상태 (True: 연결됨, False: 연결 끊어짐)
        """
        try:
            self.driver.current_url
            return True
        except WebDriverException:
            return False
        except Exception as e:
            # ConnectionResetError 등 네트워크 오류 포함
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['connection', 'reset', '10054', '10061']):
                return False
            self.log_error("드라이버 연결 확인 실패", e)
            return False
    
    def safe_switch_to_window(self, window_handle: str) -> bool:
        """
        안전한 창 전환
        
        Args:
            window_handle: 전환할 창 핸들
            
        Returns:
            성공 여부
        """
        try:
            self.driver.switch_to.window(window_handle)
            return True
        except Exception as e:
            self.log_error("창 전환 실패", e)
            return False
    
    def safe_close_popup_and_return_to_main(self) -> bool:
        """
        안전한 팝업 닫기 및 메인 창 복귀
        
        Returns:
            성공 여부
        """
        try:
            current_window = self.driver.current_window_handle
            
            # 팝업창이 열려있으면 닫기
            if current_window != self.main_window and len(self.driver.window_handles) > 1:
                self.driver.close()
            
            # 메인 창으로 복귀
            return self.safe_switch_to_window(self.main_window)
            
        except Exception as e:
            self.log_error("팝업 닫기 및 메인 창 복귀 실패", e)
            # 최후의 수단으로 메인 창 복귀 시도
            try:
                return self.safe_switch_to_window(self.main_window)
            except:
                return False
    
    def handle_alert(self, accept: bool = True) -> Tuple[bool, str]:
        """
        알림창 처리
        
        Args:
            accept: True면 확인, False면 취소
            
        Returns:
            (성공 여부, 알림창 텍스트)
        """
        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            
            if accept:
                alert.accept()
            else:
                alert.dismiss()
            
            return True, alert_text
        except TimeoutException:
            return False, ""
        except Exception as e:
            self.log_error("알림창 처리 실패", e)
            return False, ""
    
    def restart_driver_if_needed(self) -> bool:
        """
        필요시 드라이버 재시작
        
        Returns:
            재시작 성공 여부
        """
        if not self.check_driver_connection():
            self.log_info("드라이버 연결 끊어짐 - 재시작 필요")
            return self.restart_driver()
        return True
    
    def restart_driver(self) -> bool:
        """
        드라이버 재시작 (하위 클래스에서 구현)
        
        Returns:
            재시작 성공 여부
        """
        raise NotImplementedError("하위 클래스에서 restart_driver 메서드를 구현해야 합니다")
    
    def process_with_retry(self, func, max_retries: int = 3, *args, **kwargs) -> Tuple[bool, Any]:
        """
        재시도 로직이 포함된 함수 실행
        
        Args:
            func: 실행할 함수
            max_retries: 최대 재시도 횟수
            *args, **kwargs: 함수에 전달할 인자들
            
        Returns:
            (성공 여부, 결과값)
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                self.log_error(f"함수 실행 실패 (시도 {attempt}/{max_retries})", e)
                
                if attempt < max_retries:
                    self.random_wait(1, 2)  # 재시도 전 대기
                    
                    # 드라이버 연결 확인 및 재시작
                    if not self.restart_driver_if_needed():
                        self.log_error("드라이버 재시작 실패", Exception("드라이버 재시작 불가"))
                        break
        
        return False, last_error 