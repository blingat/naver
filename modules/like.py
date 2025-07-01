# 공감 자동화 모듈
from utils.selector import SELECTORS

class LikeAutomation:
    def __init__(self, driver, logger, config):
        self.driver = driver
        self.logger = logger
        self.config = config
    
    def run(self, start_page, end_page):
        """공감 자동화 실행"""
        self.logger.log("[공감] 공감 자동화 시작")
        print("[공감] 이 기능은 현재 개발 중입니다.")
        return 