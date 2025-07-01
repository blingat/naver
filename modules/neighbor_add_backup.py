import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from utils.selector import SELECTORS
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

class NeighborAddAutomation:
    def __init__(self, driver, logger, config):
        self.driver = driver
        self.logger = logger
        self.config = config
        self.blog_links = []
        self.is_logged_in = False

    def check_login_required(self):
        """현재 페이지가 로그인 페이지인지 확인"""
        current_url = self.driver.current_url
        return "nid.naver.com/nidlogin.login" in current_url

    def ensure_login(self):
        """로그인 상태 확인 및 로그인 처리"""
        if self.is_logged_in:
            return True
            
        # 홈페이지에서 로그인 상태 확인
        self.driver.get("https://www.naver.com/")
        time.sleep(2)
        
        # 로그인 상태 확인
        try:
            # 방법 1: 프로필 영역 확인
            profile_area = self.driver.find_element(By.CSS_SELECTOR, "div.sc_login.NM_FAVORITE_LOGIN")
            if profile_area:
                try:
                    my_info = profile_area.find_element(By.CSS_SELECTOR, "a[href*='nid.naver.com/user2/help']")
                    if my_info:
                        self.logger.log("[서이추] 로그인 상태 확인됨")
                        self.is_logged_in = True
                        return True
                except:
                    pass
        except NoSuchElementException:
            pass
        
        # 방법 2: 로그인 버튼 확인 (미로그인 확인)
        try:
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "a.link_login")
            if login_btn and login_btn.is_displayed():
                self.logger.log("[서이추] 미로그인 상태 감지")
                return self.handle_login()
        except NoSuchElementException:
            # 로그인 버튼이 없으면 로그인된 것으로 가정
            self.is_logged_in = True
            return True
        
        self.is_logged_in = True
        return True

    def handle_login(self):
        """로그인 처리"""
        from modules.login import NaverLogin
        
        print("\n[서이추] 로그인이 필요합니다.")
        user_id = input("네이버 아이디를 입력하세요: ")
        user_pw = input("네이버 비밀번호를 입력하세요: ")
        
        # NaverLogin 인스턴스 생성 (driver는 공유)
        login_module = NaverLogin(self.config, self.logger)
        login_module.driver = self.driver  # 기존 드라이버 공유
        
        # 로그인 시도
        result = login_module.login_with_retry(user_id, user_pw, max_attempts=3)
        if result:
            self.logger.log("[서이추] 로그인 성공!")
            print("[서이추] 로그인 성공!")
            self.is_logged_in = True
            return True
        else:
            self.logger.log("[서이추] 로그인 실패!")
            print("[서이추] 로그인 실패!")
            return False

    def search_blogs(self, keyword, count):
        """키워드로 블로그 검색하여 타겟 목록 확보"""
        max_count = min(count, self.config.get('max_action_per_run', 50))
        search_url = f"https://search.naver.com/search.naver?ssc=tab.blog.all&query={keyword}&sm=tab_opt&nso=so%3Ar%2Cp%3A1m"
        
        self.logger.log(f"[서이추] 키워드 '{keyword}' 검색 시작")
        self.driver.get(search_url)
        time.sleep(3)
        
        # 로그인 페이지가 뜨면 처리
        if self.check_login_required():
            if not self.handle_login():
                return False
            # 다시 검색
            self.driver.get(search_url)
            time.sleep(3)
        
        self.blog_links = []
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.title_area a.title_link')
            for el in elements:
                href = el.get_attribute('href')
                if href and 'blog.naver.com' in href:
                    self.blog_links.append(href)
                if len(self.blog_links) >= max_count:
                    break
                    
            self.logger.log(f"[서이추] 추출된 블로그 수: {len(self.blog_links)}")
            return len(self.blog_links) > 0
            
        except Exception as e:
            self.logger.log(f"[서이추] 블로그 링크 추출 실패: {e}")
            return False

    def find_buddy_button(self):
        """이웃추가 버튼 찾기"""
        try:
            # iframe 진입
            main_frame = self.driver.find_element(By.NAME, 'mainFrame')
            self.driver.switch_to.frame(main_frame)
            time.sleep(1)
            
            # 다양한 셀렉터로 버튼 찾기
            button_selectors = [
                'a.btn_buddy._buddy_popup_btn',
                'a.btn_buddy.btn_addbuddy',
                'a[class*="btn_buddy"]'
            ]
            
            for selector in button_selectors:
                try:
                    btns = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in btns:
                        btn_text = btn.text.replace('\n', '').replace(' ', '')
                        if '이웃추가' in btn_text:
                            return btn, '이웃추가'
                        elif '서로이웃' in btn_text:
                            return btn, '서로이웃'
                except:
                    continue
            
            # XPath로 텍스트 기반 검색
            xpath_selectors = [
                "//a[contains(text(), '이웃추가')]",
                "//a[contains(text(), '서로이웃')]"
            ]
            
            for xpath in xpath_selectors:
                try:
                    btns = self.driver.find_elements(By.XPATH, xpath)
                    if btns:
                        btn_text = btns[0].text.replace('\n', '').replace(' ', '')
                        return btns[0], btn_text
                except:
                    continue
            
            return None, ''
            
        except Exception as e:
            self.logger.log(f"[서이추] 버튼 찾기 실패: {e}")
            return None, ''
        finally:
            try:
                self.driver.switch_to.default_content()
            except:
                pass

    def process_buddy_add(self, message):
        """이웃추가 프로세스 진행"""
        try:
            # iframe 진입
            main_frame = self.driver.find_element(By.NAME, 'mainFrame')
            self.driver.switch_to.frame(main_frame)
            
            # 서로이웃 라디오 버튼 찾기 및 클릭
            radio_selectors = [
                'input.radio_button_buddy#each_buddy_add',
                'input[id="each_buddy_add"]',
                'input[name="relation"][value="1"]'
            ]
            
            radio_found = False
            for selector in radio_selectors:
                try:
                    radio = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if radio and radio.is_enabled():
                        radio.click()
                        radio_found = True
                        break
                except:
                    continue
            
            if not radio_found:
                self.logger.log("[서이추] 서로이웃 라디오 버튼 없음 또는 비활성화")
                return "pass"
            
            time.sleep(1)
            
            # 다음 버튼 클릭
            next_btn_selectors = [
                'a.button_next._buddyAddNext',
                'a[href*="buddyAdd"]',
                'a.button_next'
            ]
            
            next_btn_found = False
            for selector in next_btn_selectors:
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_btn:
                        next_btn.click()
                        next_btn_found = True
                        break
                except:
                    continue
            
            if not next_btn_found:
                self.logger.log("[서이추] 다음 버튼 없음")
                return "fail"
            
            time.sleep(2)
            
            # 메시지 입력
            msg_box_selectors = [
                'textarea#message',
                'textarea[name="message"]',
                'textarea.text_box'
            ]
            
            msg_box_found = False
            for selector in msg_box_selectors:
                try:
                    msg_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if msg_box:
                        msg_box.clear()
                        msg_box.send_keys(message)
                        msg_box_found = True
                        break
                except:
                    continue
            
            if not msg_box_found:
                self.logger.log("[서이추] 메시지 입력창 없음")
                return "fail"
            
            time.sleep(1)
            
            # 최종 다음 버튼 클릭
            final_btn_selectors = [
                'a.button_next._addBothBuddy',
                'a[class*="_addBothBuddy"]',
                'a.button_next:last-of-type'
            ]
            
            final_btn_found = False
            for selector in final_btn_selectors:
                try:
                    final_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if final_btn:
                        final_btn.click()
                        final_btn_found = True
                        break
                except:
                    continue
            
            if not final_btn_found:
                self.logger.log("[서이추] 최종 다음 버튼 없음")
                return "fail"
            
            time.sleep(3)
            self.driver.switch_to.default_content()
            
            # 알림창 처리
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                
                if '하루' in alert_text or '제한' in alert_text:
                    return "limit"
                else:
                    return "success"
            except:
                return "success"  # 알림창 없어도 성공으로 간주
                
        except Exception as e:
            self.logger.log(f"[서이추] 이웃추가 프로세스 실패: {e}")
            return "fail"
        finally:
            try:
                self.driver.switch_to.default_content()
            except:
                pass

    def process_blog(self, blog_url, message):
        """개별 블로그 처리 - 단순화된 버전"""
        self.logger.log(f"[서이추] 블로그 처리 시작: {blog_url}")
        
        try:
            # 블로그 방문
            self.driver.get(blog_url)
            time.sleep(3)
            
            # 로그인 페이지 확인
            if self.check_login_required():
                if not self.handle_login():
                    return "로그인실패"
                # 다시 블로그 방문
                self.driver.get(blog_url)
                time.sleep(3)
            
            # 이웃추가 버튼 찾기
            btn, btn_text = self.find_buddy_button()
            
            if not btn:
                self.logger.log(f"[서이추] 이웃추가 버튼 없음")
                return "pass"
            
            if '서로이웃' in btn_text:
                self.logger.log(f"[서이추] 이미 서로이웃")
                return "pass"
            
            if '이웃추가' in btn_text:
                # 버튼 클릭
                try:
                    self.driver.switch_to.frame('mainFrame')
                    
                    # 다양한 방법으로 클릭 시도
                    click_success = False
                    if btn.is_displayed() and btn.is_enabled():
                        try:
                            btn.click()
                            click_success = True
                        except:
                            pass
                    
                    if not click_success:
                        try:
                            self.driver.execute_script("arguments[0].click();", btn)
                            click_success = True
                        except:
                            pass
                    
                    self.driver.switch_to.default_content()
                    
                    if not click_success:
                        self.logger.log("[서이추] 버튼 클릭 실패")
                        return "fail"
                    
                    time.sleep(2)
                    
                    # 로그인 페이지 재확인
                    if self.check_login_required():
                        if not self.handle_login():
                            return "로그인실패"
                        # 다시 블로그 접속 후 버튼 클릭
                        self.driver.get(blog_url)
                        time.sleep(3)
                        btn, btn_text = self.find_buddy_button()
                        if btn and '이웃추가' in btn_text:
                            self.driver.switch_to.frame('mainFrame')
                            try:
                                btn.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", btn)
                            self.driver.switch_to.default_content()
                            time.sleep(2)
                    
                    # 이웃추가 프로세스 진행
                    return self.process_buddy_add(message)
                    
                except Exception as e:
                    self.logger.log(f"[서이추] 버튼 클릭 중 오류: {e}")
                    return "fail"
            
            return "pass"
            
        except Exception as e:
            self.logger.log(f"[서이추] 블로그 처리 중 오류: {e}")
            return "fail"

    def run(self, keyword, count):
        """서이추 자동화 메인 실행"""
        success = 0
        fail = 0
        passed = 0
        max_count = min(count, self.config.get('max_action_per_run', 50))
        
        print(f"[서이추] 서이추 자동화를 시작합니다. (키워드: {keyword}, 개수: {max_count})")
        self.logger.log(f"[서이추] 서이추 자동화 시작 - 키워드: {keyword}, 개수: {max_count}")
        
        # 1단계: 로그인 확인
        print("[서이추] 로그인 상태를 확인합니다...")
        if not self.ensure_login():
            print("[서이추] 로그인 실패. 작업을 중단합니다.")
            return
        
        # 2단계: 블로그 검색 및 목록 확보
        print("[서이추] 타겟 블로그를 검색합니다...")
        if not self.search_blogs(keyword, max_count):
            print("[서이추] 블로그 검색 실패. 작업을 중단합니다.")
            return
        
        print(f"[서이추] {len(self.blog_links)}개의 타겟 블로그를 찾았습니다.")
        
        # 3단계: 메시지 파일 읽기
        try:
            with open('eut_message.txt', 'r', encoding='utf-8') as f:
                message = f.read().strip()
        except FileNotFoundError:
            print("[서이추] eut_message.txt 파일이 없습니다.")
            return
        
        # 4단계: 각 블로그 처리
        print("[서이추] 이웃추가 작업을 시작합니다...")
        
        for idx, blog_url in enumerate(self.blog_links):
            if success + fail + passed >= max_count:
                break
                
            print(f"\n[{idx+1}/{len(self.blog_links)}] 처리 중...")
            self.logger.log(f"[서이추] [{idx+1}/{len(self.blog_links)}] {blog_url}")
            
            result = self.process_blog(blog_url, message)
            
            if result == "success":
                success += 1
                print(f"✅ 성공!")
            elif result == "fail":
                fail += 1
                print(f"❌ 실패")
            elif result == "pass":
                passed += 1
                print(f"⏭️ 패스")
            elif result == "limit":
                print(f"🚫 하루 제한 도달! 작업을 중단합니다.")
                break
            elif result in ["로그인실패"]:
                print(f"🔐 로그인 문제로 작업을 중단합니다.")
                break
                
            print(f"진행상황: {idx+1}/{len(self.blog_links)} | 성공: {success} | 실패: {fail} | 패스: {passed}")
            
            # 잠시 대기 (네이버 부하 방지)
            time.sleep(2)
        
        # 최종 결과
        print(f"\n[서이추] 작업 완료!")
        print(f"[서이추] 최종 결과: 성공 {success}개, 실패 {fail}개, 패스 {passed}개")
        self.logger.log(f"[서이추] 최종 결과: 성공 {success}, 실패 {fail}, 패스 {passed}") 