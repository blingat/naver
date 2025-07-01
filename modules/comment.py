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
            
            # 이웃글 목록 찾기
            posts = []
            try:
                # 네이버 블로그의 새로운 URL 형태에 맞는 셀렉터들
                selectors = [
                    # 새로운 네이버 블로그 URL 형태: blog.naver.com/아이디/글번호
                    "a[href*='blog.naver.com/'][href*='/2']:not([href*='PostView'])",  # 2024년 이후 글번호 패턴
                    "a[href*='blog.naver.com/'][href*='/22']:not([href*='PostView'])",  # 2022년 이후 글번호 패턴  
                    "a[href*='blog.naver.com/']:not([href*='PostView']):not([href*='prologue']):not([href*='guestbook'])",  # 일반 블로그 링크
                    ".title_post a[href*='blog.naver.com']",  # 제목 포스트 링크
                    ".item a[href*='blog.naver.com']",  # 아이템 링크
                    # 기존 PostView 형태도 유지 (혹시 모르니)
                    "a[href*='PostView.naver']",  # 기본 포스트 링크
                    "a[href*='blog.naver.com'][href*='PostView']",  # 블로그 포스트 링크
                ]
                
                post_elements = []
                found_selector = None
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        print(f"     🔍 셀렉터 '{selector}': {len(elements)}개 요소 발견")
                        
                        if elements:
                            # 블로그 포스트 링크만 필터링 (새로운 형태)
                            filtered_elements = []
                            for elem in elements:
                                try:
                                    href = elem.get_attribute('href')
                                    if href and self.is_valid_blog_post_url(href):
                                        filtered_elements.append(elem)
                                except:
                                    continue
                            
                            print(f"     🎯 셀렉터 '{selector}': {len(filtered_elements)}개 유효한 블로그 포스트 링크 발견")
                            
                            if filtered_elements:
                                post_elements = filtered_elements
                                found_selector = selector
                                print(f"     ✅ 사용된 셀렉터: {selector} ({len(post_elements)}개 발견)")
                                break
                    except Exception as e:
                        print(f"     ⚠️  셀렉터 {selector} 실패: {e}")
                        continue
                
                if not post_elements:
                    # 디버깅을 위해 페이지의 모든 블로그 링크 확인
                    print(f"     🔍 페이지 디버깅 중...")
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    print(f"     📊 전체 링크 수: {len(all_links)}")
                    
                    # 블로그 관련 링크 찾기
                    blog_links = []
                    
                    for link in all_links[:50]:  # 처음 50개 확인
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            
                            if href and 'blog.naver.com/' in href:
                                # URL 패턴 분석
                                if self.is_valid_blog_post_url(href):
                                    blog_links.append(f"✅ VALID: {href[:80]}..., text: {text[:30]}...")
                                else:
                                    blog_links.append(f"❌ INVALID: {href[:80]}..., text: {text[:30]}...")
                        except:
                            continue
                    
                    if blog_links:
                        print(f"     🔗 발견된 블로그 링크들 ({len(blog_links)}개):")
                        for link_info in blog_links[:10]:
                            print(f"       - {link_info}")
                    else:
                        print(f"     ❌ 블로그 관련 링크를 찾을 수 없음")
                    
                    print(f"     ⚠️  이웃글을 찾을 수 없습니다.")
                    return []
                
                # 포스트 정보 추출
                for idx, element in enumerate(post_elements[:15]):  # 최대 15개
                    try:
                        href = element.get_attribute('href')
                        if not href or not self.is_valid_blog_post_url(href):
                            continue
                            
                        # 제목 추출 (다양한 방법 시도)
                        title = None
                        
                        # 1. title 속성
                        title = element.get_attribute('title')
                        
                        # 2. 텍스트 내용
                        if not title:
                            title = element.text.strip()
                        
                        # 3. 부모 요소에서 제목 찾기
                        if not title:
                            try:
                                parent = element.find_element(By.XPATH, "./..")
                                title = parent.text.strip()
                            except:
                                pass
                        
                        # 4. 형제 요소에서 제목 찾기
                        if not title:
                            try:
                                siblings = element.find_elements(By.XPATH, "./following-sibling::*")
                                for sibling in siblings[:3]:
                                    sibling_text = sibling.text.strip()
                                    if sibling_text and len(sibling_text) > 5:
                                        title = sibling_text
                                        break
                            except:
                                pass
                        
                        if not title:
                            title = f"제목없음_{idx+1}"
                        
                        posts.append({
                            'url': href,
                            'title': title[:50]  # 제목 길이 제한
                        })
                        print(f"     📝 수집: {title[:30]}... | {href[:50]}...")
                            
                    except Exception as e:
                        print(f"     ⚠️  {idx+1}번째 요소 처리 실패: {e}")
                        continue
                        
                print(f"     ✅ {len(posts)}개 이웃글 발견 (셀렉터: {found_selector})")
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
    
    def click_like_button(self):
        """공감 버튼 클릭"""
        try:
            # 공감 버튼 셀렉터들
            like_selectors = [
                ".btn_sympathy",
                ".u_likeit_layer .u_likeit_list_btn",
                "[data-clk='smp.good']",
                ".area_sympathy .btn_sympathy"
            ]
            
            for selector in like_selectors:
                try:
                    like_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    # 이미 공감했는지 확인
                    if "on" in like_btn.get_attribute("class") or "active" in like_btn.get_attribute("class"):
                        print("     💖 이미 공감한 글입니다")
                        return True
                    
                    like_btn.click()
                    time.sleep(1)
                    print("     💖 공감 완료!")
                    return True
                    
                except:
                    continue
            
            print("     ⚠️  공감 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            print(f"     ❌ 공감 버튼 클릭 오류: {e}")
            return False
    
    def write_comment(self, blog_title):
        """댓글 작성"""
        try:
            # AI로 댓글 생성
            if not self.gemini:
                print("     ❌ Gemini API가 설정되지 않았습니다")
                return False, "API 미설정"
            
            print("     🤖 AI 댓글 생성 중...")
            comment_text, error = self.gemini.generate_comment(blog_title)
            
            if error:
                print(f"     ❌ 댓글 생성 실패: {error}")
                return False, f"댓글 생성 실패: {error}"
            
            print(f"     💬 생성된 댓글: {comment_text}")
            
            # 댓글 입력창 찾기
            comment_selectors = [
                "textarea[placeholder*='댓글']",
                ".comment_inbox textarea",
                ".area_comment textarea",
                "#comment_inbox"
            ]
            
            comment_input = None
            for selector in comment_selectors:
                try:
                    comment_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if comment_input.is_enabled():
                        break
                except:
                    continue
            
            if not comment_input:
                print("     ❌ 댓글 입력창을 찾을 수 없습니다")
                return False, "댓글 입력창 없음"
            
            # 댓글 입력창이 비활성화되어 있는지 확인
            if not comment_input.is_enabled():
                print("     ❌ 댓글 입력창이 비활성화되어 있습니다")
                return False, "댓글 입력창 비활성화"
            
            # 댓글 입력
            comment_input.clear()
            comment_input.send_keys(comment_text)
            time.sleep(1)
            
            # 댓글 등록 버튼 찾기 및 클릭
            submit_selectors = [
                ".btn_register",
                ".comment_register",
                "button[type='submit']",
                ".btn_comment_register"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_btn.is_enabled():
                        submit_btn.click()
                        time.sleep(2)
                        print("     ✅ 댓글 작성 완료!")
                        return True, None
                except:
                    continue
            
            print("     ❌ 댓글 등록 버튼을 찾을 수 없습니다")
            return False, "등록 버튼 없음"
            
        except Exception as e:
            print(f"     ❌ 댓글 작성 오류: {e}")
            return False, f"댓글 작성 오류: {e}"
    
    def process_single_post(self, post_info):
        """단일 게시글 처리"""
        try:
            url = post_info['url']
            title = post_info['title']
            
            print(f"   📝 처리 중: {title}")
            
            # 이미 댓글 작성한 글인지 확인
            if self.is_already_commented(url):
                print("     ⏭️  이미 댓글을 작성한 글입니다 (PASS)")
                return "pass", "이미 댓글 작성"
            
            # 게시글 열기
            self.driver.get(url)
            time.sleep(3)
            
            # 공감 버튼 클릭
            self.click_like_button()
            
            # 댓글 작성
            success, error = self.write_comment(title)
            
            if success:
                # 댓글 작성 기록 저장
                self.save_comment_record(url)
                self.logger.log(f"[댓글자동화] 댓글 작성 성공: {title} | {url}")
                return "success", None
            else:
                self.logger.log(f"[댓글자동화] 댓글 작성 실패: {title} | {error}")
                return "fail", error
                
        except Exception as e:
            error_msg = f"게시글 처리 오류: {e}"
            print(f"     ❌ {error_msg}")
            self.logger.log(f"[댓글자동화] {error_msg}")
            return "fail", error_msg
    
    def run_comment_automation(self, target_count, start_page):
        """댓글 자동화 실행"""
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
                    
                    # 잠시 대기 (너무 빠른 요청 방지)
                    time.sleep(2)
                
                current_page += 1
            
            # 최종 결과
            print("\n" + "=" * 50)
            print("🎉 댓글 자동화 완료!")
            print(f"📊 최종 결과:")
            print(f"   ✅ 성공: {success_count}개")
            print(f"   ❌ 실패: {fail_count}개") 
            print(f"   ⏭️  패스: {pass_count}개")
            print(f"   📝 총 처리: {processed_count}개")
            
            self.logger.log(f"[댓글자동화] 완료 - 성공: {success_count}, 실패: {fail_count}, 패스: {pass_count}")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  사용자가 댓글 자동화를 중단했습니다.")
            print(f"📊 중단 시점 결과:")
            print(f"   ✅ 성공: {success_count}개")
            print(f"   ❌ 실패: {fail_count}개")
            print(f"   ⏭️  패스: {pass_count}개")
            
        except Exception as e:
            print(f"\n❌ 댓글 자동화 중 오류 발생: {e}")
            self.logger.log(f"[댓글자동화] 오류 발생: {e}")

    def run(self, count, start_page):
        """댓글 자동화 실행"""
        self.logger.log("[댓글] 댓글 자동화 시작")
        print("[댓글] 이 기능은 현재 개발 중입니다.")
        return 