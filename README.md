# 네이버 블로그 자동화 프로그램 v1.0

네이버 블로그 운영자의 성장을 위한 완전 자동화 CLI 프로그램입니다.

## 주요 기능

1. **공감 자동화** ✅
2. **서이추(서로이웃 추가) 자동화** ✅
3. **댓글 자동화** ✅ (AI 기반)
4. **Chrome 환경 설정 테스트** ✅
5. **Gemini/OpenAI API 테스트** ✅

## 최신 업데이트 v1.0

### 🎯 댓글 자동화 완료
- **AI 기반 댓글 생성**: Gemini API를 활용한 자연스러운 댓글 자동 생성
- **블로그 내용 분석**: 제목과 내용 미리보기를 분석하여 맥락에 맞는 댓글 작성
- **공감 버튼 자동 클릭**: 댓글 작성 전 자동으로 공감 버튼 클릭
- **중복 방지**: 이미 댓글을 작성한 글은 자동으로 건너뛰기
- **자동 기록 정리**: 1주일 초과 기록 자동 삭제

### 🚀 Chrome 환경 완전 자동화
- **ChromeDriver 자동 다운로드**: webdriver-manager를 사용한 ChromeDriver 자동 설치 및 관리
- **Chrome 프로필 자동 생성**: 프로젝트 폴더 내 자동 프로필 생성으로 복잡한 설정 제거
- **설정 파일 간소화**: 복잡한 경로 설정 없이 바로 사용 가능
- **Chrome 환경 테스트**: 메뉴에서 Chrome 설정 상태를 쉽게 확인 가능
- **사용자 편의성 개선**: 기술적 설정 없이 바로 자동화 기능 사용 가능

### 🔧 서이추 자동화 개선
- **팝업창 크기 문제 해결**: Chrome 옵션 최적화로 네이버 기본 크기 유지
- **안전한 창 전환**: 팝업창 처리 시 오류 방지 로직 추가
- **진행중 메시지 처리**: "서로이웃 신청 진행중" 알림창 자동 처리

## 설치 및 설정

### 1. 필요 환경
- Python 3.10 이상
- Chrome 브라우저
- ChromeDriver (Chrome 버전과 일치)

### 2. 설치 방법
```bash
# 저장소 클론
git clone https://github.com/blingat/naver.git
cd naver

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
cp config.example.json config.json
```

### 3. 설정 파일 (config.json)
`config.example.json`을 복사해서 `config.json`으로 만드세요:
```bash
cp config.example.json config.json
```

**자동 설정 항목** (수정 불필요):
- `chrome_profile_path`: 빈 문자열로 두면 프로젝트 폴더에 자동 생성
- `chromedriver_path`: 빈 문자열로 두면 자동으로 다운로드

**필수 설정 항목** (댓글 자동화 사용 시):
- `gemini_api_key`: Google Gemini API 키 입력

**선택적 설정 항목**:
- `openai_api_key`: OpenAI API 키 (향후 사용)

### 4. 메시지 파일
- **eut_message.txt**: 서이추 신청 시 사용할 메시지 (자동 생성됨)
- **eut_comment.txt**: 댓글 작성 기록 (자동 생성 및 관리)

## 사용법

### 기본 사용법
1. `python main.py` 실행
2. **첫 실행 시**: 메뉴에서 "8. Chrome 환경 설정 테스트" 선택하여 환경 확인
3. 메뉴에서 원하는 기능 선택
4. 필요시 네이버 로그인 진행

### 각 기능별 사용법

#### 1. 공감 자동화
- 이웃글 목록에서 자동으로 공감 버튼 클릭
- 처리할 개수와 시작 페이지 설정 가능

#### 2. 서이추 자동화
- 키워드 입력 (예: "맛집", "여행", "육아" 등)
- 처리할 개수 입력 (최대 50)
- 자동으로 검색 → 방문 → 서로이웃 신청

#### 3. 댓글 자동화 (AI 기반)
- Gemini API 키 설정 필요
- 이웃글 내용을 분석하여 자연스러운 댓글 자동 생성
- 공감 버튼 자동 클릭 + 댓글 작성
- 중복 방지 및 기록 관리

#### 4. Chrome 환경 테스트
- Chrome 설치 상태 확인
- ChromeDriver 자동 다운로드 및 버전 확인
- 브라우저 실행 테스트

#### 5. API 테스트
- Gemini API 연결 상태 확인
- API 키 유효성 검증

## 파일 구조
```
naver/
├── main.py                 # 메인 실행 파일
├── config.json            # 설정 파일 (사용자 생성)
├── config.example.json    # 설정 파일 예제
├── requirements.txt       # Python 의존성
├── README.md             # 이 파일
├── modules/              # 핵심 모듈
│   ├── login.py         # 네이버 로그인
│   ├── neighbor_add.py  # 서이추 자동화
│   ├── comment.py       # 댓글 자동화
│   ├── like.py         # 공감 자동화
│   └── gemini.py       # AI API 연동
├── utils/               # 유틸리티
│   ├── chrome_setup.py # Chrome 환경 설정
│   ├── logger.py       # 로깅
│   ├── selector.py     # 셀렉터 관리
│   └── session.py      # 세션 관리
├── chrome_profile/      # Chrome 프로필 (자동 생성)
├── cookies/            # 쿠키 저장소 (자동 생성)
├── eut_message.txt     # 서이추 메시지 (자동 생성)
└── eut_comment.txt     # 댓글 기록 (자동 생성)
```

## 문제 해결

### Chrome 관련 문제
- **Chrome이 설치되지 않은 경우**: https://www.google.com/chrome/ 에서 Chrome 설치
- **ChromeDriver 오류**: 프로그램이 자동으로 최신 버전을 다운로드하므로 별도 조치 불필요
- **프로필 오류**: 프로젝트 폴더의 `chrome_profile` 디렉토리가 자동 생성됨

### API 관련 문제
- **Gemini API 키 오류**: config.json에서 올바른 API 키 설정 확인
- **API 요청 실패**: 인터넷 연결 및 API 할당량 확인
- **댓글 생성 실패**: API 테스트 메뉴에서 연결 상태 확인

### 로그인 세션 문제
- 크롬 프로필을 사용하여 세션 관리
- 세션 만료 시 자동 재로그인 시도
- 브라우저는 세션 유지를 위해 자동으로 닫히지 않음

### 자동화 관련 문제
- **공감 버튼을 찾을 수 없음**: 일부 블로그는 공감 기능이 비활성화됨 (정상)
- **댓글 입력창을 찾을 수 없음**: 일부 블로그는 댓글 기능이 비활성화됨 (정상)
- **서이추 신청 실패**: 이미 이웃이거나 신청 제한에 걸린 경우 (정상)

## 개발 히스토리

### v1.0 (2024-12-21)
- 댓글 자동화 완료 (AI 기반)
- 공감 자동화 완료
- Chrome 환경 완전 자동화
- 서이추 자동화 안정성 개선
- 사용자 편의성 대폭 개선

### v0.1 (초기 버전)
- 서이추 자동화 기본 기능
- 네이버 로그인 기능
- Chrome 수동 설정

## API 키 발급 방법

### Gemini API 키 발급
1. https://makersuite.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 키를 config.json의 `gemini_api_key`에 입력

## 주의사항
- 네이버 정책을 준수하여 사용해주세요
- 하루 제한이 있을 수 있습니다 (네이버 정책)
- 자동화 탐지 시 수동 인증이 필요할 수 있습니다
- API 사용량에 따른 요금이 발생할 수 있습니다 (Gemini API)
- 개인 사용 목적으로만 사용해주세요

## 라이선스
MIT License

## 기여하기
이슈 리포트나 개선 제안은 GitHub Issues를 통해 해주세요.

## 작성자
- GitHub: [@blingat](https://github.com/blingat)
- 프로젝트: https://github.com/blingat/naver 