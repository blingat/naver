# 네이버 블로그 자동화 프로그램

네이버 블로그 운영자의 성장을 위한 자동화 CLI 프로그램입니다.

## 주요 기능

1. **공감 자동화** (준비 중)
2. **서이추(서로이웃 추가) 자동화** ✅
3. **댓글 자동화** (준비 중)
4. **네이버 로그인 테스트** ✅
5. **Gemini/OpenAI API 테스트** (준비 중)

## 최신 업데이트 (세션 관리 강화)

- **세션 쿠키 관리 개선**: 네이버 메인 도메인과 블로그 도메인 간 쿠키 동기화 강화
- **자동화 탐지 회피**: User-Agent 설정 및 자동화 탐지 방지 기능 추가
- **iframe 접근 안정화**: 블로그 페이지의 mainFrame 접근 시 세션 유지 강화
- **로그인 재시도 로직**: 세션 만료 시 자동 재로그인 기능
- **다중 셀렉터 지원**: 네이버 구조 변경에 대비한 여러 셀렉터 지원

## 설치 및 설정

### 1. 필요 환경
- Python 3.10 이상
- Chrome 브라우저
- ChromeDriver (Chrome 버전과 일치)

### 2. 설치 방법
```bash
# 저장소 클론
git clone https://github.com/your-username/naver-blog-automation.git
cd naver-blog-automation

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
cp config.example.json config.json
```

### 3. 설정 파일 (config.json)
`config.example.json`을 복사해서 `config.json`으로 만들고 아래 내용을 수정하세요:
- `chrome_profile_path`: Chrome 프로필 경로
- `chromedriver_path`: ChromeDriver 실행 파일 경로
- API 키들 (필요한 경우만)

### 4. 메시지 파일 (eut_message.txt)
서이추 신청 시 사용할 메시지를 작성해주세요.

## 사용법

1. `python main.py` 실행
2. 메뉴에서 원하는 기능 선택
3. 서이추 자동화 사용 시:
   - 키워드 입력
   - 처리할 개수 입력 (최대 50)
   - 필요시 로그인 진행

## 문제 해결

### 로그인 세션 문제
- 크롬 프로필을 사용하여 세션 관리
- 세션 만료 시 자동 재로그인 시도
- 브라우저는 세션 유지를 위해 자동으로 닫히지 않음

### 이웃추가 버튼을 찾을 수 없는 경우
- 다양한 셀렉터를 자동으로 시도
- 페이지 로딩 대기 시간 증가
- 세션 쿠키 새로고침 후 재시도

## 주의사항
- 네이버 정책을 준수하여 사용해주세요
- 하루 제한이 있을 수 있습니다
- 자동화 탐지 시 수동 인증이 필요할 수 있습니다 