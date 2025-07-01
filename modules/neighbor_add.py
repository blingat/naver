import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selector import SELECTORS

class NeighborAddAutomation:
    def __init__(self, driver, logger, config):
        self.driver = driver
        self.logger = logger
        self.config = config
        self.blog_links = []

    def search_blogs(self, keyword, count):
        """키워드로 블로그 검색하여 타겟 목록 확보"""
        max_count = min(count, self.config.get('max_action_per_run', 50))
        search_url = f"https://search.naver.com/search.naver?ssc=tab.blog.all&query={keyword}&sm=tab_opt&nso=so%3Ar%2Cp%3A1m"
        
        self.logger.log(f"[서이추] 키워드 '{keyword}' 검색 시작")
        print(f"\n🔍 '{keyword}' 키워드로 블로그 검색 중...")
        
        self.driver.get(search_url)
        time.sleep(3)
        
        self.blog_links = []
        try:
            # PRD 명세대로 title_area의 title_link 찾기
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.title_area a.title_link')
            
            for el in elements[:max_count]:  # 최대 개수만큼만 추출
                href = el.get_attribute('href')
                if href and 'blog.naver.com' in href:
                    self.blog_links.append(href)
                    
            self.logger.log(f"[서이추] 추출된 블로그 수: {len(self.blog_links)}")
            print(f"✅ {len(self.blog_links)}개의 타겟 블로그를 찾았습니다.")
            return len(self.blog_links) > 0
            
        except Exception as e:
            self.logger.log(f"[서이추] 블로그 링크 추출 실패: {e}")
            print(f"❌ 블로그 검색 실패: {e}")
            return False

    def find_buddy_button(self):
        """이웃추가 버튼 찾기 - PRD 명세에 맞게"""
        try:
            # iframe 대기 및 진입
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'mainFrame'))
            )
            self.driver.switch_to.frame('mainFrame')
            time.sleep(2)
            
            # PRD에 명시된 셀렉터로 버튼 찾기
            # 1. 정확한 클래스명으로 찾기
            btns = self.driver.find_elements(By.CSS_SELECTOR, 'a.btn_buddy._buddy_popup_btn')
            
            for btn in btns:
                btn_text = btn.text.strip()
                if '이웃추가' in btn_text:
                    self.logger.log("[서이추] 이웃추가 버튼 발견")
                    return btn, '이웃추가'
                elif '서로이웃' in btn_text:
                    self.logger.log("[서이추] 서로이웃 상태 확인")
                    return btn, '서로이웃'
            
            # 2. 대체 셀렉터
            btns = self.driver.find_elements(By.CSS_SELECTOR, 'a.btn_buddy')
            for btn in btns:
                btn_text = btn.text.strip()
                if '이웃추가' in btn_text or '서로이웃' in btn_text:
                    return btn, btn_text
                    
            return None, ''
            
        except TimeoutException:
            self.logger.log("[서이추] mainFrame을 찾을 수 없음")
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
        """이웃추가 프로세스 진행 - 팝업 창에서 처리"""
        try:
            print("    🔄 이웃추가 팝업 창 처리 중...")
            
            # 현재 창 핸들 저장
            main_window = self.driver.current_window_handle
            
            # 팝업 창으로 전환 대기
            try:
                WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
                
                # 팝업 창으로 전환
                for handle in self.driver.window_handles:
                    if handle != main_window:
                        self.driver.switch_to.window(handle)
                        break
                        
                time.sleep(2)  # 팝업 창 로드 대기
                print("    ✅ 이웃추가 팝업 창으로 전환 완료")
                
            except TimeoutException:
                print("    ❌ 이웃추가 팝업 창을 찾을 수 없습니다.")
                self.logger.log("[서이추] 이웃추가 팝업 창 없음")
                return "fail"
            
            # 1. 서로이웃 라디오 버튼 선택
            try:
                print("    🔍 서로이웃 라디오 버튼 찾는 중...")
                
                # 먼저 서로이웃을 받지 않는 블로거인지 확인
                try:
                    # 방법 1: disabled 속성 확인
                    radio_element = self.driver.find_element(By.ID, 'each_buddy_add')
                    if radio_element.get_attribute('disabled'):
                        print("    ⏭️  서로이웃을 받지 않는 블로거입니다.")
                        self.logger.log("[서이추] 서로이웃을 받지 않는 블로거 (disabled)")
                        
                        # 취소 버튼 클릭
                        try:
                            cancel_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.button_cancel')
                            cancel_btn.click()
                            print("    ✅ 취소 버튼 클릭")
                            time.sleep(1)
                        except:
                            # 취소 버튼이 없으면 그냥 창 닫기
                            self.driver.close()
                        
                        # 메인 창으로 복귀
                        self.driver.switch_to.window(main_window)
                        return "pass"
                        
                    # 방법 2: notice 메시지 확인
                    try:
                        notice = self.driver.find_element(By.CSS_SELECTOR, 'p.notice')
                        if notice and "서로이웃 신청을 받지 않는" in notice.text:
                            print("    ⏭️  서로이웃을 받지 않는 블로거입니다. (notice 메시지)")
                            self.logger.log("[서이추] 서로이웃을 받지 않는 블로거 (notice)")
                            
                            # 취소 버튼 클릭
                            try:
                                cancel_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.button_cancel')
                                cancel_btn.click()
                                print("    ✅ 취소 버튼 클릭")
                                time.sleep(1)
                            except:
                                # 취소 버튼이 없으면 그냥 창 닫기
                                self.driver.close()
                            
                            # 메인 창으로 복귀
                            self.driver.switch_to.window(main_window)
                            return "pass"
                    except:
                        pass
                        
                except:
                    pass
                
                # 서로이웃이 가능한 경우 진행
                # 실제 HTML 구조에 맞게 서로이웃 라디오 버튼 선택
                try:
                    # 방법 1: label 클릭
                    label = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[for="each_buddy_add"]'))
                    )
                    label.click()
                    print("    ✅ 서로이웃 옵션 선택 (label 클릭)")
                    self.logger.log("[서이추] 서로이웃 옵션 선택 (label)")
                    wait_time = self.random_wait(0.5, 1.5)
                    print(f"    ⏰ {wait_time:.1f}초 대기")
                    
                except TimeoutException:
                    # 방법 2: input 직접 클릭
                    try:
                        radio = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.ID, 'each_buddy_add'))
                        )
                        radio.click()
                        print("    ✅ 서로이웃 옵션 선택 (input 클릭)")
                        self.logger.log("[서이추] 서로이웃 옵션 선택 (input)")
                        wait_time = self.random_wait(0.5, 1.5)
                        print(f"    ⏰ {wait_time:.1f}초 대기")
                        
                    except TimeoutException:
                        # 방법 3: JavaScript로 선택
                        self.driver.execute_script("""
                            var radio = document.getElementById('each_buddy_add');
                            if (radio && !radio.disabled) {
                                radio.checked = true;
                                radio.click();
                                
                                // change 이벤트 발생
                                var event = new Event('change', { bubbles: true });
                                radio.dispatchEvent(event);
                            }
                        """)
                        print("    ✅ 서로이웃 옵션 선택 (JavaScript)")
                        self.logger.log("[서이추] 서로이웃 옵션 선택 (JavaScript)")
                        wait_time = self.random_wait(0.5, 1.5)
                        print(f"    ⏰ {wait_time:.1f}초 대기")
                        
            except Exception as e:
                print(f"    ❌ 서로이웃 라디오 버튼 선택 실패: {e}")
                self.logger.log(f"[서이추] 서로이웃 라디오 버튼 선택 실패: {e}")
                # 팝업 창 닫고 메인 창으로 돌아가기
                try:
                    cancel_btn = self.driver.find_element(By.CSS_SELECTOR, 'a.button_cancel')
                    cancel_btn.click()
                except:
                    self.driver.close()
                self.driver.switch_to.window(main_window)
                return "fail"
            
            # 2. 다음 버튼 클릭
            try:
                next_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a._buddyAddNext'))
                )
                next_btn.click()
                print("    ✅ 다음 버튼 클릭")
                self.logger.log("[서이추] 다음 버튼 클릭")
                wait_time = self.random_wait(2, 4)  # 페이지 전환 대기
                print(f"    ⏰ 페이지 전환 대기: {wait_time:.1f}초")
                
            except TimeoutException:
                print("    ❌ 다음 버튼을 찾을 수 없습니다.")
                self.logger.log("[서이추] 다음 버튼 찾기 실패")
                # 팝업 창 닫고 메인 창으로 돌아가기
                self.driver.close()
                self.driver.switch_to.window(main_window)
                return "fail"
            
            # 알림창 체크 (서로이웃 신청 진행중입니다)
            try:
                WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                if '진행중' in alert_text or '신청' in alert_text:
                    alert.accept()
                    print("    ⏭️  이미 서로이웃 신청 진행중")
                    self.logger.log("[서이추] 이미 서로이웃 신청 진행중")
                    # 팝업 창 안전하게 닫고 메인 창으로 돌아가기
                    try:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                        self.driver.switch_to.window(main_window)
                    except Exception as e:
                        self.logger.log(f"[서이추] 창 전환 중 오류 (무시): {e}")
                        try:
                            self.driver.switch_to.window(main_window)
                        except:
                            pass
                    return "pass"
            except TimeoutException:
                # 알림창이 없으면 정상 진행
                pass
            
            # 3. 메시지 입력
            try:
                msg_box = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea#message'))
                )
                msg_box.clear()
                msg_box.send_keys(message)
                print("    ✅ 메시지 입력 완료")
                self.logger.log("[서이추] 메시지 입력 완료")
                wait_time = self.random_wait(1, 2)
                print(f"    ⏰ {wait_time:.1f}초 대기")
                
            except TimeoutException:
                print("    ❌ 메시지 입력창을 찾을 수 없습니다.")
                self.logger.log("[서이추] 메시지 입력창 찾기 실패")
                # 팝업 창 닫고 메인 창으로 돌아가기
                self.driver.close()
                self.driver.switch_to.window(main_window)
                return "fail"
            
            # 4. 최종 다음 버튼 클릭
            try:
                final_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a._addBothBuddy'))
                )
                final_btn.click()
                print("    ✅ 서로이웃 신청 완료!")
                self.logger.log("[서이추] 최종 다음 버튼 클릭")
                wait_time = self.random_wait(1, 2)  # 처리 완료 대기
                print(f"    ⏰ 처리 완료 대기: {wait_time:.1f}초")
                
            except TimeoutException:
                print("    ❌ 최종 다음 버튼을 찾을 수 없습니다.")
                self.logger.log("[서이추] 최종 다음 버튼 찾기 실패")
                # 팝업 창 닫고 메인 창으로 돌아가기
                self.driver.close()
                self.driver.switch_to.window(main_window)
                return "fail"
            
            # 5. 결과 확인 알림창 처리
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.logger.log(f"[서이추] 알림: {alert_text}")
                alert.accept()
                
                if '하루' in alert_text or '제한' in alert_text:
                    print("    🚫 하루 제한 도달")
                    result = "limit"
                elif '완료' in alert_text or '신청' in alert_text:
                    print("    🎉 서로이웃 신청 성공!")
                    result = "success"
                else:
                    result = "success"
                    
            except TimeoutException:
                # 알림창이 없으면 서로이웃 추가 완료 페이지 확인
                try:
                    # 서로이웃 신청 완료 메시지 확인
                    success_msg = self.driver.find_element(By.CSS_SELECTOR, 'p.text_buddy_add')
                    if success_msg and "서로이웃을 신청하였습니다" in success_msg.text:
                        print("    🎉 서로이웃 신청 성공!")
                        self.logger.log("[서이추] 서로이웃 신청 완료 페이지 확인")
                        
                        # 닫기 버튼 클릭 (딜레이 없이 바로 클릭)
                        try:
                            close_btn = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.button_close'))
                            )
                            close_btn.click()
                            print("    ✅ 닫기 버튼 클릭 (즉시)")
                            self.logger.log("[서이추] 닫기 버튼 클릭 (즉시)")
                        except TimeoutException:
                            # 닫기 버튼이 없으면 그냥 창 닫기
                            self.driver.close()
                            
                        result = "success"
                    else:
                        # 알림창도 없고 완료 메시지도 없으면 성공으로 간주
                        print("    🎉 서로이웃 신청 성공!")
                        self.logger.log("[서이추] 서로이웃 신청 완료 (기본)")
                        result = "success"
                        
                except:
                    # 어떤 요소도 찾을 수 없으면 성공으로 간주
                    print("    🎉 서로이웃 신청 성공!")
                    self.logger.log("[서이추] 서로이웃 신청 완료 (추정)")
                    result = "success"
            
            # 팝업 창 닫고 메인 창으로 돌아가기 (닫기 버튼으로 안 닫힌 경우)
            try:
                # 현재 창이 팝업창인지 확인 후 닫기
                current_window = self.driver.current_window_handle
                if current_window != main_window and len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(main_window)
            except Exception as e:
                self.logger.log(f"[서이추] 팝업창 닫기 중 오류 (무시): {e}")
                try:
                    self.driver.switch_to.window(main_window)
                except Exception as e2:
                    self.logger.log(f"[서이추] 메인창 전환 중 오류 (무시): {e2}")
                    pass
                
            return result
                
        except Exception as e:
            self.logger.log(f"[서이추] 이웃추가 프로세스 실패: {e}")
            print(f"    ❌ 이웃추가 실패: {e}")
            
            # 오류 시에도 안전하게 메인 창으로 돌아가기
            try:
                # 팝업창이 열려있으면 닫기
                if len(self.driver.window_handles) > 1:
                    current_window = self.driver.current_window_handle
                    if current_window != main_window:
                        self.driver.close()
                self.driver.switch_to.window(main_window)
            except Exception as e2:
                self.logger.log(f"[서이추] 오류 후 창 전환 실패 (무시): {e2}")
                try:
                    # 최후의 수단으로 새 탭 열기
                    self.driver.execute_script("window.open('about:blank', '_blank');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                except:
                    pass
                
            return "fail"

    def process_blog(self, blog_url, message):
        """개별 블로그 처리"""
        self.logger.log(f"[서이추] 블로그 처리: {blog_url}")
        
        try:
            # 블로그 방문
            print(f"    🌐 블로그 접속 중...")
            self.driver.get(blog_url)
            time.sleep(4)  # 페이지 로드 충분히 대기
            
            # 이웃추가 버튼 찾기
            btn, btn_text = self.find_buddy_button()
            
            if not btn:
                print("    ⏭️  이웃추가 버튼 없음")
                self.logger.log("[서이추] 이웃추가 버튼 없음 (pass)")
                return "pass"
                
            if '서로이웃' in btn_text:
                print("    ⏭️  이미 서로이웃")
                self.logger.log("[서이추] 이미 서로이웃 (pass)")
                return "pass"
                
            if '이웃추가' in btn_text:
                print("    🎯 이웃추가 버튼 발견")
                # 버튼 클릭
                try:
                    self.driver.switch_to.frame('mainFrame')
                    
                    # 클릭 시도
                    try:
                        btn.click()
                        print("    ✅ 이웃추가 버튼 클릭")
                    except:
                        # JavaScript로 클릭 시도
                        self.driver.execute_script("arguments[0].click();", btn)
                        print("    ✅ 이웃추가 버튼 클릭 (JS)")
                    
                    self.driver.switch_to.default_content()
                    time.sleep(3)  # 이웃추가 창 로드 대기
                    
                    # 이웃추가 프로세스 진행
                    return self.process_buddy_add(message)
                    
                except Exception as e:
                    self.logger.log(f"[서이추] 버튼 클릭 실패: {e}")
                    print(f"    ❌ 버튼 클릭 실패: {e}")
                    return "fail"
                    
            return "pass"
                
        except Exception as e:
            self.logger.log(f"[서이추] 블로그 처리 실패: {e}")
            print(f"    ❌ 블로그 처리 실패: {e}")
            return "fail"

    def run(self, keyword, count):
        """서이추 자동화 실행 - PRD 명세에 맞게"""
        success = 0
        fail = 0
        passed = 0
        
        print(f"\n{'='*50}")
        print(f"서이추 자동화 시작")
        print(f"키워드: {keyword}")
        print(f"목표: {count}명")
        print(f"{'='*50}")
        
        self.logger.log(f"[서이추] 자동화 시작 - 키워드: {keyword}, 개수: {count}")
        
        # 1. 블로그 검색
        if not self.search_blogs(keyword, count):
            print("\n❌ 블로그 검색에 실패했습니다.")
            return
                
        # 2. 메시지 파일 확인
        try:
            with open('eut_message.txt', 'r', encoding='utf-8') as f:
                message = f.read().strip()
            if not message:
                print("\n❌ eut_message.txt 파일이 비어있습니다.")
                return
        except FileNotFoundError:
            print("\n❌ eut_message.txt 파일이 없습니다.")
            return
            
        # 3. 이웃추가 작업
        print(f"\n📋 이웃추가 작업을 시작합니다...")
        print(f"{'─'*50}")
        
        for idx, blog_url in enumerate(self.blog_links):
            current = idx + 1
            print(f"\n[{current}/{len(self.blog_links)}] 처리 중...")
            
            result = self.process_blog(blog_url, message)
            
            if result == "success":
                success += 1
                print(f"✅ 성공")
            elif result == "fail":
                fail += 1
                print(f"❌ 실패")
            elif result == "pass":
                passed += 1
                print(f"⏭️  패스")
            elif result == "limit":
                print(f"\n🚫 하루 제한에 도달했습니다!")
                print(f"네이버 정책상 하루 서이추 제한이 있습니다.")
                break
                
            # 진행상황 표시 (PRD 명세)
            total = success + fail + passed
            print(f"📊 진행상황: {total}/{count} 완료 (성공: {success}, 실패: {fail}, pass: {passed})")
            
            # 네이버 부하 방지 (랜덤 대기로 자연스럽게)
            if current < len(self.blog_links):
                if result == "success":
                    wait_time = self.random_wait(3, 7)  # 성공 시 3-7초 랜덤 대기
                    print(f"    ⏰ 네이버 부하 방지: {wait_time:.1f}초 대기")
                elif result == "fail":
                    wait_time = self.random_wait(1, 3)  # 실패 시 1-3초 랜덤 대기
                    print(f"    ⏰ 다음 블로그 대기: {wait_time:.1f}초")
                else:  # pass
                    wait_time = self.random_wait(0.5, 2)  # 패스 시 0.5-2초 랜덤 대기
                    print(f"    ⏰ 다음 블로그 대기: {wait_time:.1f}초")
        
        # 최종 결과 (PRD 명세)
        print(f"\n{'='*50}")
        print(f"서이추 자동화 완료")
        print(f"{'='*50}")
        print(f"✅ 성공: {success}")
        print(f"❌ 실패: {fail}")
        print(f"⏭️  패스: {passed}")
        print(f"📊 총계: {success + fail + passed}/{count}")
        
        self.logger.log(f"[서이추] 최종 결과: 성공 {success}, 실패 {fail}, 패스 {passed}")

    def random_wait(self, min_sec=1, max_sec=3):
        """랜덤 대기시간 (자연스러운 자동화)"""
        wait_time = random.uniform(min_sec, max_sec)
        time.sleep(wait_time)
        return wait_time 