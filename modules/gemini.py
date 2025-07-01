import requests
import json
import time

class GeminiAPI:
    def __init__(self, api_key, logger=None):
        self.api_key = api_key
        self.logger = logger
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
    def generate_text(self, prompt, max_tokens=1000, temperature=0.7):
        """Gemini API로 텍스트 생성"""
        try:
            if not self.api_key or self.api_key == "여기에 Gemini API 키 입력":
                error_msg = "Gemini API 키가 설정되지 않았습니다."
                if self.logger:
                    self.logger.log(f"[Gemini] {error_msg}")
                return None, error_msg
            
            url = self.base_url
            
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": max_tokens,
                    "stopSequences": [],
                    "thinkingConfig": {
                        "thinkingBudget": 0
                    }
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            if self.logger:
                self.logger.log(f"[Gemini] API 요청 시작 - 프롬프트 길이: {len(prompt)}")
            
            print(f"     * API 요청 전송 중... (프롬프트 길이: {len(prompt)}자)")
            response = requests.post(url, headers=headers, json=data, timeout=5)
            print(f"     * API 응답 수신 완료 (상태코드: {response.status_code})")
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                        generated_text = result['candidates'][0]['content']['parts'][0]['text']
                        
                        if self.logger:
                            self.logger.log(f"[Gemini] API 응답 성공 - 응답 길이: {len(generated_text)}")
                        
                        return generated_text, None
                    else:
                        error_msg = "API 응답에서 텍스트를 찾을 수 없습니다."
                        if self.logger:
                            self.logger.log(f"[Gemini] {error_msg}")
                        return None, error_msg
                else:
                    error_msg = "API 응답에 candidates가 없습니다."
                    if self.logger:
                        self.logger.log(f"[Gemini] {error_msg}")
                    return None, error_msg
                    
            else:
                error_msg = f"API 요청 실패: {response.status_code} - {response.text}"
                if self.logger:
                    self.logger.log(f"[Gemini] {error_msg}")
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "API 요청 시간 초과 (5초)"
            print(f"     * {error_msg}")
            if self.logger:
                self.logger.log(f"[Gemini] {error_msg}")
            return None, error_msg
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API 요청 중 네트워크 오류: {e}"
            print(f"     * {error_msg}")
            if self.logger:
                self.logger.log(f"[Gemini] {error_msg}")
            return None, error_msg
            
        except Exception as e:
            error_msg = f"API 요청 중 예상치 못한 오류: {e}"
            print(f"     * {error_msg}")
            if self.logger:
                self.logger.log(f"[Gemini] {error_msg}")
            return None, error_msg
    
    def test_connection(self):
        """API 연결 테스트"""
        print("   - 테스트 프롬프트 전송 중...")
        test_prompt = "안녕하세요! API 테스트입니다. 간단히 인사해주세요."
        result, error = self.generate_text(test_prompt, max_tokens=100)
        
        if error:
            print(f"   - 연결 실패: {error}")
            return False, error
        else:
            print("   - 연결 성공!")
            return True, f"API 연결 성공! 응답: {result[:100]}..."
    
    def generate_comment(self, blog_title, blog_content_preview=""):
        """블로그 글에 대한 댓글 생성"""
        if blog_content_preview:
            prompt = f"""
다음 블로그 글에 대한 자연스러운 댓글을 작성해주세요.

제목: {blog_title}
내용 미리보기: {blog_content_preview}

조건:
1. 20-50자 정도의 짧은 댓글
2. 자연스럽고 친근한 톤
3. 블로그 내용과 관련된 댓글
4. 과도한 칭찬보다는 공감이나 질문 형태
5. 이모지 1-2개 정도 포함

댓글만 작성해주세요:
"""
        else:
            prompt = f"""
다음 블로그 글 제목에 대한 자연스러운 댓글을 작성해주세요.

제목: {blog_title}

조건:
1. 20-50자 정도의 짧은 댓글
2. 자연스럽고 친근한 톤
3. 제목과 관련된 댓글
4. 과도한 칭찬보다는 공감이나 질문 형태
5. 이모지 1-2개 정도 포함

댓글만 작성해주세요:
"""
        
        result, error = self.generate_text(prompt, max_tokens=200, temperature=0.8)
        
        if error:
            return None, error
        
        # 댓글 정리 (불필요한 부분 제거)
        comment = result.strip()
        if comment.startswith('"') and comment.endswith('"'):
            comment = comment[1:-1]
        
        # 너무 긴 댓글은 자르기
        if len(comment) > 100:
            comment = comment[:97] + "..."
        
        return comment, None 