from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from datetime import datetime, timedelta
from modules.gemini import GeminiAPI

class CommentAutomation:
    def __init__(self, driver, config, logger):
        self.driver = driver
        self.config = config
        self.logger = logger
        self.wait = WebDriverWait(driver, 10)
        self.comment_file = "eut_comment.txt"
        
        # Gemini API 초기화
        gemini_api_key = config.get('gemini_api_key', '')
        if gemini_api_key and gemini_api_key != "여기에 Gemini API 키 입력":
            self.gemini = GeminiAPI(gemini_api_key, logger)
        else:
            self.gemini = None
            
        # 기존 댓글 기록 정리 (1주일 초과 기록 삭제)
        self.cleanup_old_comments()
    
    def format_duration(self, seconds):
        """시간을 시:분:초 형태로 포맷팅"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}시간 {minutes}분 {secs}초"
        elif minutes > 0:
            return f"{minutes}분 {secs}초"
        else:
            return f"{secs}초"
    
    def cleanup_old_comments(self):
        """1주일 초과 댓글 기록 정리"""
        try:
            if not os.path.exists(self.comment_file):
                return
                
            one_week_ago = datetime.now() - timedelta(days=7)
            valid_lines = []
            
            with open(self.comment_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split(' | ')
                if len(parts) >= 2:
                    try:
                        date_str = parts[1]
                        comment_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        if comment_date > one_week_ago:
                            valid_lines.append(line)
                    except:
                        # 날짜 파싱 실패한 경우 유지
                        valid_lines.append(line)
            
            # 정리된 내용으로 파일 다시 쓰기
            with open(self.comment_file, 'w', encoding='utf-8') as f:
                for line in valid_lines:
                    f.write(line + '\n')
                    
            removed_count = len(lines) - len(valid_lines)
            if removed_count > 0:
                self.logger.log(f"[댓글자동화] 1주일 초과 댓글 기록 {removed_count}개 정리 완료")
                
        except Exception as e:
            self.logger.log(f"[댓글자동화] 댓글 기록 정리 중 오류: {e}")
    
    def is_already_commented(self, blog_url):
        """이미 댓글을 작성한 글인지 확인"""
        try:
            if not os.path.exists(self.comment_file):
                return False
                
            with open(self.comment_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if blog_url in line:
                        return True
            return False
        except Exception as e:
            self.logger.log(f"[댓글자동화] 댓글 기록 확인 중 오류: {e}")
            return False
    
    def save_comment_record(self, blog_url):
        """댓글 작성 기록 저장"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            record = f"{blog_url} | {timestamp}\n"
            
            with open(self.comment_file, 'a', encoding='utf-8') as f:
                f.write(record)
                
        except Exception as e:
            self.logger.log(f"[댓글자동화] 댓글 기록 저장 중 오류: {e}")
    
    def get_neighbor_posts(self, page_num):
        """이웃글 목록 가져오기"""
        try:
            # 네이버 블로그 이웃새글 페이지 (원래 URL)
            url = f"https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage={page_num}&groupId=0"
            print(f"   📄 {page_num}페이지 이웃글 목록 로딩 중...")
            print(f"   🔗 URL: {url}")
            
            self.driver.get(url)
            time.sleep(5)  # 페이지 로딩 시간 증가
            
            # 페이지 로딩 완료 대기
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                time.sleep(2)  # 추가 대기
            except:
                pass
            
            # 현재 페이지 제목 확인
            try:
                page_title = self.driver.title
                print(f"     📄 페이지 제목: {page_title}")
            except:
                pass
            
            # 이웃글 목록 찾기 (간단한 방식)
            posts = []
            try:
                # div.desc 안의 a 태그에서 블로그 포스트 링크 추출
                post_elements = []
                
                # 가장 간단한 방법: desc 클래스 안의 블로그 링크
                desc_links = self.driver.find_elements(By.CSS_SELECTOR, "div.desc a[href*='blog.naver.com']")
                print(f"     🔍 이웃글 링크: {len(desc_links)}개 발견")
                
                if desc_links:
                    # 유효한 블로그 포스트 링크만 필터링
                    for link in desc_links:
                        try:
                            href = link.get_attribute('href')
                            if href and self.is_valid_blog_post_url(href):
                                post_elements.append(link)
                        except:
                            continue
                    
                    print(f"     ✅ 유효한 이웃글: {len(post_elements)}개")
                else:
                    # 백업 방법: 기존 복잡한 셀렉터 사용
                    print(f"     ⚠️  desc 링크를 찾지 못함, 백업 방법 사용...")
                    selectors = [
                        "a[href*='blog.naver.com/'][href*='/2']:not([href*='PostView'])",
                        "a[href*='blog.naver.com/']:not([href*='PostView']):not([href*='prologue']):not([href*='guestbook'])",
                        ".title_post a[href*='blog.naver.com']",
                        ".item a[href*='blog.naver.com']"
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                for elem in elements:
                                    try:
                                        href = elem.get_attribute('href')
                                        if href and self.is_valid_blog_post_url(href):
                                            post_elements.append(elem)
                                    except:
                                        continue
                                if post_elements:
                                    print(f"     ✅ 백업 셀렉터로 {len(post_elements)}개 발견")
                                    break
                        except:
                            continue
                
                if not post_elements:
                    print(f"     ⚠️  이웃글을 찾을 수 없습니다.")
                    return []
                
                # 포스트 정보 추출
                for idx, element in enumerate(post_elements[:15]):  # 최대 15개
                    try:
                        href = element.get_attribute('href')
                        if not href or not self.is_valid_blog_post_url(href):
                            continue
                            
                        # 제목 추출 (간단한 방법)
                        title = element.text.strip()
                        
                        # 제목이 없으면 기본값 사용
                        if not title or len(title) < 3:
                            title = f"제목없음_{idx+1}"
                        
                        posts.append({
                            'url': href,
                            'title': title[:50]  # 제목 길이 제한
                        })
                        print(f"     📝 수집: {title[:30]}... | {href[:50]}...")
                            
                    except Exception as e:
                        print(f"     ⚠️  {idx+1}번째 요소 처리 실패: {e}")
                        continue
                        
                print(f"     ✅ {len(posts)}개 이웃글 발견 (div.desc 셀렉터)")
                return posts
                
            except Exception as e:
                print(f"     ❌ 이웃글 목록 파싱 오류: {e}")
                return []
                
        except Exception as e:
            print(f"     ❌ 이웃글 페이지 로딩 오류: {e}")
            self.logger.log(f"[댓글자동화] 이웃글 페이지 로딩 오류: {e}")
            return []
    
    def is_valid_blog_post_url(self, url):
        """유효한 블로그 포스트 URL인지 확인"""
        try:
            if not url or 'blog.naver.com/' not in url:
                return False
            
            # 제외할 URL 패턴들
            exclude_patterns = [
                'PostView',  # 구 형태는 제외하지 않음
                'prologue',  # 프롤로그
                'guestbook',  # 방명록
                'nidlogin',  # 로그인
                'ThisMonth',  # 이달의 블로그
                'BlogHome',  # 블로그 홈
                'connect',   # 연결
                'Notice',    # 공지
                '/help/',    # 도움말
                '/manage/',  # 관리
                'logout',    # 로그아웃
            ]
            
            for pattern in exclude_patterns:
                if pattern in url:
                    return False
            
            # 유효한 블로그 포스트 URL 패턴 확인
            import re
            
            # 새로운 형태: blog.naver.com/아이디/글번호
            # 글번호는 보통 10자리 이상의 숫자
            pattern1 = r'blog\.naver\.com/[^/]+/\d{10,}'
            if re.search(pattern1, url):
                return True
            
            # 구 형태: PostView.naver가 포함된 경우도 유효
            if 'PostView.naver' in url:
                return True
            
            return False
            
        except Exception as e:
            print(f"     ⚠️  URL 유효성 검사 오류: {e}")
            return False
    
    def extract_blog_content_preview(self):
        """블로그 내용 미리보기 추출 (iframe 내에서)"""
        try:
            # iframe으로 전환
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'mainFrame'))
                )
                self.driver.switch_to.frame('mainFrame')
                time.sleep(2)
            except Exception as e:
                print(f"     ⚠️  iframe 전환 실패 (내용 추출): {e}")
                return ""
            
            # 블로그 본문 내용 추출
            content_selectors = [
                ".se-main-container",  # 스마트에디터 3.0
                ".se-component-content",  # 스마트에디터 구성요소
                "#postViewArea",  # 기본 포스트 영역
                ".post-view",  # 포스트 뷰
                ".blog-content",  # 블로그 내용
                ".__se_object",  # 스마트에디터 객체
                ".post_ct",  # 포스트 내용
                ".entry-content"  # 엔트리 내용
            ]
            
            content_text = ""
            for selector in content_selectors:
                try:
                    content_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if content_elements:
                        for element in content_elements[:3]:  # 처음 3개 요소만
                            text = element.text.strip()
                            if text and len(text) > 20:  # 의미있는 텍스트만
                                content_text += text + " "
                                if len(content_text) > 300:  # 300자 정도면 충분
                                    break
                        if content_text:
                            break
                except:
                    continue
            
            # 내용이 너무 길면 자르기
            if len(content_text) > 500:
                content_text = content_text[:297] + "..."
            
            if content_text:
                print(f"     📖 내용 미리보기 추출: {content_text[:50]}...")
            else:
                print("     ⚠️  내용 미리보기를 추출할 수 없습니다")
            
            return content_text.strip()
            
        except Exception as e:
            print(f"     ⚠️  내용 추출 오류: {e}")
            return ""
        finally:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def click_like_button(self):
        """공감 버튼 클릭 (iframe 내에서)"""
        try:
            # iframe으로 전환
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'mainFrame'))
                )
                self.driver.switch_to.frame('mainFrame')
                time.sleep(2)
                print("     🖼️  iframe으로 전환 완료")
            except Exception as e:
                print(f"     ❌ iframe 전환 실패: {e}")
                return False
            
            # 공감 영역 확인
            try:
                sympathy_area = self.driver.find_element(By.CSS_SELECTOR, ".area_sympathy")
                print("     ✅ 공감 영역 발견")
            except:
                print("     ⏭️  공감 버튼이 없는 글입니다 (PASS)")
                return True
            
            # 공감 버튼 찾기 (성공 케이스 기준)
            try:
                like_btn = sympathy_area.find_element(By.CSS_SELECTOR, ".u_likeit_list_btn._button[data-type='like']")
                print("     ✅ 공감 버튼 발견")
            except:
                print("     ⏭️  공감 버튼을 찾을 수 없습니다 (PASS)")
                return True
            
            # 공감 상태 확인
            class_attr = like_btn.get_attribute("class") or ""
            aria_pressed = like_btn.get_attribute("aria-pressed") or "false"
            
            # off 상태 확인 (공감하지 않은 상태)
            if " off " in f" {class_attr} " or class_attr.endswith(" off"):
                print("     🤍 공감하지 않은 상태 - 공감 버튼 클릭")
                
                # JavaScript로 클릭
                self.driver.execute_script("arguments[0].click();", like_btn)
                time.sleep(2)
                
                # 클릭 후 상태 확인
                new_aria_pressed = like_btn.get_attribute("aria-pressed") or "false"
                if new_aria_pressed == "true":
                    print("     💖 공감 완료!")
                else:
                    print("     🤔 공감 클릭 시도 완료")
                
                return True
            else:
                print("     💖 이미 공감한 글입니다 (PASS)")
                return True
                
        except Exception as e:
            print(f"     ❌ 공감 버튼 처리 오류: {e}")
            return True
        finally:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def write_comment(self, blog_title, blog_content_preview=""):
        """댓글 작성 (iframe 내에서)"""
        try:
            # AI로 댓글 생성
            if not self.gemini:
                print("     ❌ Gemini API가 설정되지 않았습니다")
                return False, "API 미설정"
            
            print("     🤖 AI 댓글 생성 중...")
            comment_text, error = self.gemini.generate_comment(blog_title, blog_content_preview)
            
            if error:
                print(f"     ❌ 댓글 생성 실패: {error}")
                return False, f"댓글 생성 실패: {error}"
            
            print(f"     💬 생성된 댓글: {comment_text}")
            
            # iframe으로 전환
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'mainFrame'))
                )
                self.driver.switch_to.frame('mainFrame')
                time.sleep(2)
                print("     🖼️  댓글 작성을 위해 iframe으로 전환")
            except Exception as e:
                print(f"     ❌ iframe 전환 실패: {e}")
                return False, "iframe 전환 실패"
            
            # 댓글 쓰기 버튼 클릭 (성공 케이스 기준)
            comment_write_selectors = [
                ".btn_comment.pcol2._cmtList",  # 공감 버튼 있는 글
                ".area_comment .btn_comment.pcol2._cmtList"  # 공감 버튼 없는 글
            ]
            
            comment_write_clicked = False
            for selector in comment_write_selectors:
                try:
                    comment_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    comment_btn.click()
                    time.sleep(2)
                    print("     ✅ 댓글 쓰기 버튼 클릭")
                    comment_write_clicked = True
                    break
                except:
                    continue
            
            if not comment_write_clicked:
                print("     ❌ 댓글 쓰기 버튼을 찾을 수 없습니다")
                return False, "댓글 쓰기 버튼 없음"
            
            # 댓글 입력창 찾기 (성공 케이스 기준)
            try:
                comment_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-log='RPC.input']"))
                )
                print("     ✅ 댓글 입력창 발견")
            except:
                print("     ❌ 댓글 입력창을 찾을 수 없습니다")
                return False, "댓글 입력창 없음"
            
            # 댓글 입력 (contenteditable div)
            try:
                self.driver.execute_script("""
                    arguments[0].focus();
                    arguments[0].innerHTML = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, comment_input, comment_text)
                time.sleep(1)
                print("     ✅ 댓글 입력 완료")
            except Exception as e:
                print(f"     ❌ 댓글 입력 실패: {e}")
                return False, f"댓글 입력 실패: {e}"
            
            # 등록 버튼 클릭 (성공 케이스 기준)
            try:
                submit_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-log='RPC.write']"))
                )
                submit_btn.click()
                time.sleep(2)
                print("     ✅ 댓글 등록 완료!")
                return True, None
            except:
                print("     ❌ 댓글 등록 버튼을 찾을 수 없습니다")
                return False, "등록 버튼 없음"
            
        except Exception as e:
            print(f"     ❌ 댓글 작성 오류: {e}")
            return False, f"댓글 작성 오류: {e}"
        finally:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def process_single_post(self, post_info):
        """단일 게시글 처리 (최적화된 버전)"""
        import time
        import random
        
        # 목표 시간 설정 (5-10초 랜덤)
        target_duration = random.uniform(5, 10)
        post_start_time = time.time()
        
        try:
            url = post_info['url']
            title = post_info['title']
            
            print(f"   📝 처리 중: {title}")
            
            # 이미 댓글 작성한 글인지 확인
            if self.is_already_commented(url):
                elapsed = time.time() - post_start_time
                print(f"     ⏭️  이미 댓글을 작성한 글입니다 (PASS) - {elapsed:.1f}초")
                return "pass", "이미 댓글 작성"
            
            # 게시글 열기 (대기시간 단축)
            self.driver.get(url)
            time.sleep(1)  # 3초 → 1초로 단축
            
            # iframe으로 한 번만 전환하여 모든 작업 수행
            try:
                WebDriverWait(self.driver, 5).until(  # 10초 → 5초로 단축
                    EC.presence_of_element_located((By.NAME, 'mainFrame'))
                )
                self.driver.switch_to.frame('mainFrame')
                time.sleep(1)  # 2초 → 1초로 단축
                print("     🖼️  iframe으로 전환 완료")
            except Exception as e:
                elapsed = time.time() - post_start_time
                print(f"     ❌ iframe 전환 실패: {e} - {elapsed:.1f}초")
                return "fail", f"iframe 전환 실패: {e}"
            
            # 1. 블로그 내용 미리보기 추출 (iframe 내에서)
            content_preview = self.extract_blog_content_fast()
            
            # 2. 공감 버튼 클릭 (iframe 내에서)
            self.click_like_button_fast()
            
            # 3. AI 댓글 생성 (iframe 내에서 동시에)
            if not self.gemini:
                self.driver.switch_to.default_content()
                elapsed = time.time() - post_start_time
                print(f"     ❌ Gemini API가 설정되지 않았습니다 - {elapsed:.1f}초")
                return "fail", "API 미설정"
            
            print("     🤖 AI 댓글 생성 중...")
            comment_text, error = self.gemini.generate_comment(title, content_preview)
            
            if error:
                self.driver.switch_to.default_content()
                elapsed = time.time() - post_start_time
                print(f"     ❌ 댓글 생성 실패: {error} - {elapsed:.1f}초")
                return "fail", f"댓글 생성 실패: {error}"
            
            print(f"     💬 생성된 댓글: {comment_text}")
            
            # 4. 댓글 작성 (이미 iframe 내에 있음)
            success, write_error = self.write_comment_fast(comment_text)
            
            # iframe에서 나오기
            self.driver.switch_to.default_content()
            
            if success:
                # 댓글 작성 기록 저장
                self.save_comment_record(url)
                
                # 목표 시간까지 대기
                elapsed = time.time() - post_start_time
                remaining_time = target_duration - elapsed
                if remaining_time > 0:
                    time.sleep(remaining_time)
                    elapsed = time.time() - post_start_time
                
                print(f"     ✅ 댓글 작성 완료! - {elapsed:.1f}초")
                self.logger.log(f"[댓글자동화] 댓글 작성 성공: {title} | {url} | {elapsed:.1f}초")
                return "success", None
            else:
                elapsed = time.time() - post_start_time
                print(f"     ❌ 댓글 작성 실패! - {elapsed:.1f}초")
                self.logger.log(f"[댓글자동화] 댓글 작성 실패: {title} | {write_error} | {elapsed:.1f}초")
                return "fail", write_error
                
        except Exception as e:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
                
            elapsed = time.time() - post_start_time
            error_msg = f"게시글 처리 오류: {e}"
            print(f"     ❌ {error_msg} - {elapsed:.1f}초")
            self.logger.log(f"[댓글자동화] {error_msg} | {elapsed:.1f}초")
            return "fail", error_msg

    def extract_blog_content_fast(self):
        """블로그 내용 미리보기 추출 (최적화된 버전, 이미 iframe 내에서 실행)"""
        try:
            # 빠른 내용 추출을 위한 간단한 셀렉터들
            content_selectors = [
                ".se-main-container",  # 스마트에디터 3.0
                "#postViewArea",  # 기본 포스트 영역
                ".post_ct",  # 포스트 내용
            ]
            
            content_text = ""
            for selector in content_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        text = element.text.strip()
                        if text and len(text) > 20:
                            content_text = text[:200] + "..."  # 200자로 제한
                            break
                except:
                    continue
            
            if content_text:
                print(f"     📖 내용 미리보기 추출: {content_text[:50]}...")
            
            return content_text.strip()
            
        except Exception as e:
            print(f"     ⚠️  내용 추출 오류: {e}")
            return ""

    def click_like_button_fast(self):
        """공감 버튼 클릭 (최적화된 버전, 이미 iframe 내에서 실행)"""
        try:
            # 공감 버튼 빠르게 찾기
            try:
                like_btn = self.driver.find_element(By.CSS_SELECTOR, ".u_likeit_list_btn._button[data-type='like']")
                
                # 공감 상태 확인
                class_attr = like_btn.get_attribute("class") or ""
                
                # off 상태면 클릭
                if " off " in f" {class_attr} " or class_attr.endswith(" off"):
                    print("     🤍 공감하지 않은 상태 - 공감 버튼 클릭")
                    self.driver.execute_script("arguments[0].click();", like_btn)
                    time.sleep(0.5)  # 2초 → 0.5초로 단축
                    print("     💖 공감 완료!")
                else:
                    print("     💖 이미 공감한 글입니다")
                    
            except:
                print("     ⏭️  공감 버튼이 없는 글입니다")
                
        except Exception as e:
            print(f"     ⚠️  공감 버튼 처리 오류: {e}")

    def write_comment_fast(self, comment_text):
        """댓글 작성 (최적화된 버전, 이미 iframe 내에서 실행)"""
        try:
            # 댓글 쓰기 버튼 빠르게 클릭
            try:
                comment_btn = WebDriverWait(self.driver, 3).until(  # 5초 → 3초로 단축
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_comment.pcol2._cmtList"))
                )
                comment_btn.click()
                time.sleep(0.5)  # 2초 → 0.5초로 단축
                print("     ✅ 댓글 쓰기 버튼 클릭")
            except:
                print("     ❌ 댓글 쓰기 버튼을 찾을 수 없습니다")
                return False, "댓글 쓰기 버튼 없음"
            
            # 댓글 입력창 빠르게 찾기
            try:
                comment_input = WebDriverWait(self.driver, 3).until(  # 5초 → 3초로 단축
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-log='RPC.input']"))
                )
                print("     ✅ 댓글 입력창 발견")
            except:
                print("     ❌ 댓글 입력창을 찾을 수 없습니다")
                return False, "댓글 입력창 없음"
            
            # 댓글 입력
            try:
                self.driver.execute_script("""
                    arguments[0].focus();
                    arguments[0].innerHTML = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, comment_input, comment_text)
                time.sleep(0.5)  # 1초 → 0.5초로 단축
                print("     ✅ 댓글 입력 완료")
            except Exception as e:
                print(f"     ❌ 댓글 입력 실패: {e}")
                return False, f"댓글 입력 실패: {e}"
            
            # 등록 버튼 클릭
            try:
                submit_btn = WebDriverWait(self.driver, 3).until(  # 5초 → 3초로 단축
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-log='RPC.write']"))
                )
                submit_btn.click()
                time.sleep(1)  # 2초 → 1초로 단축
                print("     ✅ 댓글 등록 완료!")
                return True, None
            except:
                print("     ❌ 댓글 등록 버튼을 찾을 수 없습니다")
                return False, "등록 버튼 없음"
            
        except Exception as e:
            print(f"     ❌ 댓글 작성 오류: {e}")
            return False, f"댓글 작성 오류: {e}"
    
    def run_comment_automation(self, target_count, start_page):
        """댓글 자동화 실행"""
        import time
        
        # 전체 자동화 시작 시간 기록
        automation_start_time = time.time()
        
        print(f"\n🚀 댓글 자동화 시작!")
        print(f"   📊 목표: {target_count}개 댓글 작성")
        print(f"   📄 시작 페이지: {start_page}")
        print("=" * 50)
        
        success_count = 0
        fail_count = 0
        pass_count = 0
        current_page = start_page
        processed_count = 0
        
        try:
            while processed_count < target_count:
                print(f"\n📄 {current_page}페이지 처리 중...")
                
                # 이웃글 목록 가져오기
                posts = self.get_neighbor_posts(current_page)
                
                if not posts:
                    print(f"   ⚠️  {current_page}페이지에 이웃글이 없습니다. 다음 페이지로...")
                    current_page += 1
                    continue
                
                # 각 게시글 처리
                for post in posts:
                    if processed_count >= target_count:
                        break
                    
                    processed_count += 1
                    print(f"\n🔄 [{processed_count}/{target_count}] 진행 중...")
                    
                    result, error = self.process_single_post(post)
                    
                    if result == "success":
                        success_count += 1
                    elif result == "fail":
                        fail_count += 1
                    elif result == "pass":
                        pass_count += 1
                    
                    # 진행상황 출력
                    print(f"   📊 현재 상황: 성공 {success_count}, 실패 {fail_count}, 패스 {pass_count}")
                    
                    # 잠시 대기 (너무 빠른 요청 방지) - 시간 단축
                    time.sleep(0.5)  # 2초 → 0.5초로 단축
                
                current_page += 1
            
            # 최종 결과
            automation_end_time = time.time()
            total_duration = automation_end_time - automation_start_time
            
            print("\n" + "=" * 50)
            print("🎉 댓글 자동화 완료!")
            print(f"📊 최종 결과:")
            print(f"   ✅ 성공: {success_count}개")
            print(f"   ❌ 실패: {fail_count}개") 
            print(f"   ⏭️  패스: {pass_count}개")
            print(f"   📝 총 처리: {processed_count}개")
            print(f"   ⏰ 총 소요시간: {self.format_duration(total_duration)}")
            
            # 평균 처리 시간 계산
            if processed_count > 0:
                avg_time_per_post = total_duration / processed_count
                print(f"   📈 평균 처리시간: {avg_time_per_post:.1f}초/개")
            
            self.logger.log(f"[댓글자동화] 완료 - 성공: {success_count}, 실패: {fail_count}, 패스: {pass_count}, 소요시간: {total_duration:.1f}초")
            
        except KeyboardInterrupt:
            automation_end_time = time.time()
            total_duration = automation_end_time - automation_start_time
            
            print("\n\n⚠️  사용자가 댓글 자동화를 중단했습니다.")
            print(f"📊 중단 시점 결과:")
            print(f"   ✅ 성공: {success_count}개")
            print(f"   ❌ 실패: {fail_count}개")
            print(f"   ⏭️  패스: {pass_count}개")
            print(f"   ⏰ 소요시간: {self.format_duration(total_duration)}")
            
            if processed_count > 0:
                avg_time_per_post = total_duration / processed_count
                print(f"   📈 평균 처리시간: {avg_time_per_post:.1f}초/개")
            
        except Exception as e:
            automation_end_time = time.time()
            total_duration = automation_end_time - automation_start_time
            
            print(f"\n❌ 댓글 자동화 중 오류 발생: {e}")
            print(f"📊 오류 발생 시점 결과:")
            print(f"   ✅ 성공: {success_count}개")
            print(f"   ❌ 실패: {fail_count}개")
            print(f"   ⏭️  패스: {pass_count}개")
            print(f"   ⏰ 소요시간: {self.format_duration(total_duration)}")
            
            self.logger.log(f"[댓글자동화] 오류 발생: {e}, 소요시간: {total_duration:.1f}초")

    def run(self, count, start_page):
        """댓글 자동화 실행"""
        self.logger.log("[댓글] 댓글 자동화 시작")
        print("[댓글] 이 기능은 현재 개발 중입니다.")
        return 