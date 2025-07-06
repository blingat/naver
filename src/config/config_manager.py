"""
네이버 블로그 자동화 - 설정 관리
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    설정 관리 클래스
    
    주요 기능:
    - 설정 파일 로드/저장
    - 설정 유효성 검사
    - 기본값 제공
    - 환경 변수 지원
    """
    
    DEFAULT_CONFIG = {
        "gemini_api_key": "여기에 Gemini API 키 입력",
        "window_width": 1200,
        "window_height": 900,
        "window_position_x": 0,
        "window_position_y": 0,
        "window_scale": 1.0,
        "chrome_profile_path": "",
        "chromedriver_path": "",
        "automation_delay": {
            "min_wait": 1.0,
            "max_wait": 3.0,
            "page_load_timeout": 10,
            "element_timeout": 5
        },
        "logging": {
            "level": "INFO",
            "max_file_size": "10MB",
            "backup_count": 5
        }
    }
    
    def __init__(self, config_path: str = "src/config/config.json"):
        """
        ConfigManager 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """설정 파일 로드"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # 기본 설정과 파일 설정 병합
                self._config = self._merge_configs(self.DEFAULT_CONFIG.copy(), file_config)
            else:
                # 설정 파일이 없으면 기본 설정 사용 후 생성
                self._config = self.DEFAULT_CONFIG.copy()
                self._create_default_config()
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  설정 파일 로드 실패: {e}")
            print("기본 설정을 사용합니다.")
            self._config = self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        설정 딕셔너리 병합 (재귀적)
        
        Args:
            base: 기본 설정
            override: 덮어쓸 설정
            
        Returns:
            병합된 설정
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_default_config(self) -> None:
        """기본 설정 파일 생성"""
        try:
            # 디렉토리 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 기본 설정 파일 생성
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 기본 설정 파일 생성: {self.config_path}")
            
        except Exception as e:
            print(f"❌ 설정 파일 생성 실패: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값 조회 (점 표기법 지원)
        
        Args:
            key: 설정 키 (예: "automation_delay.min_wait")
            default: 기본값
            
        Returns:
            설정값 또는 기본값
        """
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        설정값 변경 (점 표기법 지원)
        
        Args:
            key: 설정 키 (예: "automation_delay.min_wait")
            value: 설정값
        """
        try:
            keys = key.split('.')
            config = self._config
            
            # 마지막 키를 제외한 모든 키에 대해 딕셔너리 생성
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 마지막 키에 값 설정
            config[keys[-1]] = value
            
        except Exception as e:
            print(f"❌ 설정값 변경 실패: {e}")
    
    def save(self) -> bool:
        """
        설정을 파일에 저장
        
        Returns:
            저장 성공 여부
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False
    
    def validate(self) -> bool:
        """
        설정 유효성 검사
        
        Returns:
            유효성 검사 통과 여부
        """
        errors = []
        
        # Gemini API 키 확인
        api_key = self.get('gemini_api_key', '')
        if not api_key or api_key == "여기에 Gemini API 키 입력":
            errors.append("Gemini API 키가 설정되지 않았습니다.")
        
        # 창 크기 확인
        width = self.get('window_width', 0)
        height = self.get('window_height', 0)
        if not isinstance(width, int) or width < 800:
            errors.append("창 너비는 800 이상이어야 합니다.")
        if not isinstance(height, int) or height < 600:
            errors.append("창 높이는 600 이상이어야 합니다.")
        
        # 자동화 지연 시간 확인
        min_wait = self.get('automation_delay.min_wait', 0)
        max_wait = self.get('automation_delay.max_wait', 0)
        if not isinstance(min_wait, (int, float)) or min_wait < 0:
            errors.append("최소 대기 시간은 0 이상이어야 합니다.")
        if not isinstance(max_wait, (int, float)) or max_wait < min_wait:
            errors.append("최대 대기 시간은 최소 대기 시간보다 커야 합니다.")
        
        if errors:
            print("❌ 설정 유효성 검사 실패:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """
        모든 설정 반환
        
        Returns:
            전체 설정 딕셔너리
        """
        return self._config.copy()
    
    def reset_to_default(self) -> None:
        """기본 설정으로 초기화"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
        print("✅ 설정이 기본값으로 초기화되었습니다.")
    
    def print_config(self) -> None:
        """설정 내용 출력"""
        print("\n📋 현재 설정:")
        print("=" * 50)
        self._print_dict(self._config, indent=0)
        print("=" * 50)
    
    def _print_dict(self, d: Dict[str, Any], indent: int = 0) -> None:
        """딕셔너리 내용을 들여쓰기와 함께 출력"""
        for key, value in d.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                self._print_dict(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")


def load_config(config_path: str = "src/config/config.json") -> Dict[str, Any]:
    """
    설정 로드 함수 (하위 호환성)
    
    Args:
        config_path: 설정 파일 경로
        
    Returns:
        설정 딕셔너리
    """
    manager = ConfigManager(config_path)
    return manager.get_all()


def validate_config(config: Dict[str, Any]) -> bool:
    """
    설정 유효성 검사 함수 (하위 호환성)
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        유효성 검사 통과 여부
    """
    # 임시 ConfigManager로 유효성 검사
    manager = ConfigManager()
    manager._config = config
    return manager.validate() 