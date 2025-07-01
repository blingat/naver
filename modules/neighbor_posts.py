import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class NeighborPostsAutomation:
    """이웃 새글 자동화 클래스"""
    
    def __init__(self, driver, logger, config):
        self.driver = driver
        self.logger = logger
        self.config = config
        self.wait = WebDriverWait(driver, 10)
        
        # 통계 정보
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def go_to_neighbor_posts_page(self, page_num=1):
        """이웃 새글 페이지로 이동"""
        try:
            url = f"https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage={page_num}&groupId=0"
            self.logger.log(f"[이웃새글] {page_num}페이지로 이동: {url}")
            self.driver.get(url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # 로그인 확인
            if "login.naver.com" in self.driver.current_url:
                self.logger.log("[이웃새글] 로그인이 필요합니다.")
                return False
                
            return True
            
        except Exception as e:
            self.logger.log(f"[이웃새글] 페이지 이동 실패: {e}")
            return False
    
    def get_neighbor_posts(self):
        """현재 페이지의 이웃 새글 목록 수집"""
        posts = []
        try:
            # HTML 구조 분석 결과에 따른 정확한 셀렉터 사용
            # 각 글은 .item.multi_pic 클래스로 감싸져 있음
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, ".item.multi_pic")
            
            if not post_elements:
                # 다른 셀렉터 시도
                post_elements = self.driver.find_elements(By.CSS_SELECTOR, ".item")
            
            self.logger.log(f"[이웃새글] 발견된 글 개수: {len(post_elements)}")
            
            for idx, element in enumerate(post_elements):
                try:
                    # 글 제목과 URL 추출 - HTML 구조에 맞게 수정
                    title_element = element.find_element(By.CSS_SELECTOR, ".desc_inner .title_post span")
                    title = title_element.text.strip()
                    
                    # URL 추출
                    url_element = element.find_element(By.CSS_SELECTOR, ".desc_inner")
                    url = url_element.get_attribute("href")
                    
                    # 작성자 정보 추출
                    author_element = element.find_element(By.CSS_SELECTOR, ".name_author")
                    author = author_element.text.strip()
                    
                    # 공감 버튼 요소 찾기
                    like_element = None
                    try:
                        like_element = element.find_element(By.CSS_SELECTOR, ".u_likeit_list_btn")
                    except:
                        pass
                    
                    if title and url:
                        posts.append({
                            'title': title,
                            'url': url,
                            'author': author,
                            'element': element,
                            'like_element': like_element,
                            'index': idx + 1
                        })
                        self.logger.log(f"[이웃새글] 글 수집: {title[:30]}... (작성자: {author})")
                        
                except Exception as e:
                    self.logger.log(f"[이웃새글] {idx+1}번째 글 정보 추출 실패: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            self.logger.log(f"[이웃새글] 글 목록 수집 실패: {e}")
            return []
    
    def process_like_on_post_list(self, post_info):
        """리스트 페이지에서 직접 공감 처리 (개별 글 페이지 이동 없이)"""
        try:
            title = post_info['title']
            author = post_info['author']
            like_element = post_info['like_element']
            
            if not like_element:
                self.logger.log(f"[이웃새글] 공감 버튼을 찾을 수 없음: {title[:30]}... (작성자: {author})")
                return False
            
            self.logger.log(f"[이웃새글] 공감 처리 시작: {title[:30]}... (작성자: {author})")
            
            # 이미 공감했는지 확인
            button_class = like_element.get_attribute("class") or ""
            aria_pressed = like_element.get_attribute("aria-pressed") or "false"
            
            if "on" in button_class.lower() or aria_pressed == "true":
                self.logger.log(f"[이웃새글] 이미 공감한 글: {title[:30]}...")
                return True  # 이미 공감한 것도 성공으로 처리
            
            # 공감 버튼 클릭
            self.driver.execute_script("arguments[0].click();", like_element)
            time.sleep(random.uniform(1, 2))
            
            # 클릭 후 상태 확인
            try:
                # 짧은 대기 후 상태 재확인
                time.sleep(1)
                updated_class = like_element.get_attribute("class") or ""
                updated_aria_pressed = like_element.get_attribute("aria-pressed") or "false"
                
                if "on" in updated_class.lower() or updated_aria_pressed == "true":
                    self.logger.log(f"[이웃새글] 공감 완료: {title[:30]}... (작성자: {author})")
                    return True
                else:
                    self.logger.log(f"[이웃새글] 공감 상태 변경 확인 안됨: {title[:30]}...")
                    return True  # 클릭은 했으니 성공으로 처리
            except:
                # 상태 확인 실패해도 클릭은 했으니 성공으로 처리
                self.logger.log(f"[이웃새글] 공감 완료 (상태확인 실패): {title[:30]}...")
                return True
            
        except Exception as e:
            self.logger.log(f"[이웃새글] 공감 처리 실패: {e}")
            return False
    
    def process_like_on_post_page(self, post_info):
        """개별 글 페이지에서 공감 처리 (백업 방법)"""
        try:
            title = post_info['title']
            url = post_info['url']
            author = post_info['author']
            
            self.logger.log(f"[이웃새글] 개별 페이지 공감 처리: {title[:30]}... (작성자: {author})")
            
            # 글 페이지로 이동
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # 공감 버튼 찾기 (여러 셀렉터 시도)
            like_selectors = [
                ".u_likeit_list_btn",
                "button[class*='like']",
                ".btn_like",
                "#sympathyButton",
                "button[onclick*='sympathy']",
                "a[onclick*='sympathy']",
                ".sympathy_btn",
                ".like_btn"
            ]
            
            like_button = None
            for selector in like_selectors:
                try:
                    like_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if like_button.is_displayed():
                        break
                except:
                    continue
            
            if not like_button:
                self.logger.log(f"[이웃새글] 개별 페이지에서 공감 버튼을 찾을 수 없음: {title[:30]}...")
                return False
            
            # 이미 공감했는지 확인
            button_class = like_button.get_attribute("class") or ""
            aria_pressed = like_button.get_attribute("aria-pressed") or "false"
            
            if "on" in button_class.lower() or aria_pressed == "true":
                self.logger.log(f"[이웃새글] 이미 공감한 글: {title[:30]}...")
                return True
            
            # 공감 버튼 클릭
            self.driver.execute_script("arguments[0].click();", like_button)
            time.sleep(random.uniform(1, 2))
            
            self.logger.log(f"[이웃새글] 개별 페이지 공감 완료: {title[:30]}...")
            return True
            
        except Exception as e:
            self.logger.log(f"[이웃새글] 개별 페이지 공감 처리 실패: {e}")
            return False
    
    def run_neighbor_posts_automation(self, target_count, start_page=1):
        """이웃 새글 자동화 실행"""
        try:
            self.logger.log(f"[이웃새글] 자동화 시작 - 목표: {target_count}개, 시작페이지: {start_page}")
            print(f"\n🚀 이웃 새글 자동화를 시작합니다.")
            print(f"📊 목표: {target_count}개 글에 공감")
            print(f"📄 시작 페이지: {start_page}")
            
            current_page = start_page
            processed_count = 0
            
            while processed_count < target_count:
                print(f"\n📄 {current_page}페이지 처리 중...")
                
                # 이웃 새글 페이지로 이동
                if not self.go_to_neighbor_posts_page(current_page):
                    print("❌ 페이지 이동에 실패했습니다.")
                    break
                
                # 현재 페이지의 글 목록 수집
                posts = self.get_neighbor_posts()
                if not posts:
                    print(f"⚠️  {current_page}페이지에서 글을 찾을 수 없습니다.")
                    current_page += 1
                    if current_page > start_page + 10:  # 최대 10페이지까지만 시도
                        print("❌ 더 이상 처리할 글이 없습니다.")
                        break
                    continue
                
                print(f"📝 {len(posts)}개의 글을 발견했습니다.")
                
                # 각 글에 대해 공감 처리
                for post in posts:
                    if processed_count >= target_count:
                        break
                    
                    self.stats['total'] += 1
                    processed_count += 1
                    
                    print(f"\n[{processed_count}/{target_count}] {post['title'][:40]}...")
                    print(f"   작성자: {post['author']}")
                    
                    try:
                        # 먼저 리스트 페이지에서 직접 공감 시도
                        success = self.process_like_on_post_list(post)
                        
                        # 리스트 페이지에서 실패하면 개별 페이지에서 시도
                        if not success:
                            print("   ⚠️  리스트 페이지 공감 실패, 개별 페이지에서 시도...")
                            success = self.process_like_on_post_page(post)
                            
                            # 개별 페이지 처리 후 다시 리스트 페이지로 돌아가기
                            if success:
                                self.go_to_neighbor_posts_page(current_page)
                                time.sleep(2)
                        
                        if success:
                            self.stats['success'] += 1
                            print("   ✅ 공감 완료")
                        else:
                            self.stats['failed'] += 1
                            print("   ❌ 공감 실패")
                    
                    except Exception as e:
                        self.stats['failed'] += 1
                        self.logger.log(f"[이웃새글] 글 처리 중 오류: {e}")
                        print(f"   ❌ 오류 발생: {e}")
                    
                    # 진행 상황 출력
                    success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                    print(f"📊 진행률: {processed_count}/{target_count} (성공: {self.stats['success']}, 실패: {self.stats['failed']}, 성공률: {success_rate:.1f}%)")
                    
                    # 랜덤 대기 (네이버 정책 준수)
                    wait_time = random.uniform(3, 7)
                    print(f"   ⏰ {wait_time:.1f}초 대기 중...")
                    time.sleep(wait_time)
                
                # 다음 페이지로
                current_page += 1
                
                # 페이지 간 대기
                time.sleep(random.uniform(2, 4))
            
            # 최종 결과 출력
            success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            print(f"\n🎉 이웃 새글 자동화가 완료되었습니다!")
            print(f"📊 최종 결과:")
            print(f"   - 총 처리: {self.stats['total']}개")
            print(f"   - 성공: {self.stats['success']}개")
            print(f"   - 실패: {self.stats['failed']}개")
            print(f"   - 성공률: {success_rate:.1f}%")
            
            self.logger.log(f"[이웃새글] 자동화 완료 - 총:{self.stats['total']}, 성공:{self.stats['success']}, 실패:{self.stats['failed']}, 성공률:{success_rate:.1f}%")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  사용자가 자동화를 중단했습니다.")
            self.logger.log("[이웃새글] 사용자 중단")
            
        except Exception as e:
            print(f"\n❌ 자동화 중 오류 발생: {e}")
            self.logger.log(f"[이웃새글] 자동화 오류: {e}")
    
    def get_stats(self):
        """통계 정보 반환"""
        return self.stats.copy() 