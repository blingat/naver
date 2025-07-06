"""
설정 관리 패키지

프로그램 설정 파일들을 관리하는 패키지입니다.
"""

import os
import json
import sys
from .config_manager import ConfigManager, load_config, validate_config

def load_config():
    """설정 파일 로드"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
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

__all__ = ['ConfigManager', 'load_config', 'validate_config'] 