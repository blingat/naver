# 네이버 블로그 자동화 프로그램 v1.0

네이버 블로그 운영자의 성장을 위한 완전 자동화 CLI 프로그램입니다.

## 주요 기능

1. **공감 자동화** ✅
2. **서이추(서로이웃 추가) 자동화** ✅
3. **댓글 자동화** ✅ (AI 기반)
4. **Chrome 환경 설정 테스트** ✅
5. **Gemini/OpenAI API 테스트** ✅

## 최신 업데이트 v1.0 (2025-01-02)

### 🎯 댓글 자동화 시간 표시 기능 추가
- **전체 자동화 소요시간**: 시작부터 완료까지 전체 시간 표시 (시:분:초 형태)
- **개별 게시글 처리시간**: 각 게시글당 소요된 시간 실시간 표시
- **평균 처리시간 계산**: 전체 완료 후 게시글당 평균 시간 계산
- **중단/오류 시에도 시간 정보 제공**: 사용자 중단이나 오류 발생 시에도 현재까지의 시간 정보 표시

### 🚀 서이추 자동화 성능 최적화
- **타이머 기반 시간 제어**: 이웃추가 1명당 5-10초로 제어하는 정밀한 타이머 시스템
- **대기시간 최적화**: 모든 대기시간을 1-2초 랜덤으로 변경하여 자연스러운 동작
- **스크롤 처리 개선**: 기본 30명 추출, 50명 요청 시 자동 스크롤로 더 많은 타겟 확보
- **1일 제한 감지**: "1일 서로이웃 신청 제한" 메시지 감지 시 즉시 중단 및 사용자 친화적 안내

### 🎨 댓글 스타일 개선
- **스타일 가이드 파일**: `eut_comment_style.txt` 파일로 댓글 스타일 관리
- **래주부 페르소나**: 친근한 래주부 컨셉의 존댓말, 이모티콘 1개 포함
- **동적 스타일 적용**: 파일 내용이 있을 때만 사용, 없으면 기본 스타일 적용
- **Gemini API 프롬프트 최적화**: 스타일 가이드를 반영한 자연스러운 댓글 생성

### 🔧 Chrome 브라우저 안정성 개선
- **포트 충돌 방지**: 자동 포트 할당 및 다중 시도 로직
- **ChromeOptions 재사용 문제 해결**: 매 시도마다 새로운 옵션 객체 생성
- **상세 디버깅 시스템**: 13단계 디버깅 로그로 문제 지점 정확한 파악
- **오류 유형별 해결 방법 제시**: 각 오류별 구체적인 해결책 자동 안내

### 📊 중복 방지 시스템 개선
- **URL 기반 중복 체크**: 이미 댓글 작성한 글 정확한 건너뛰기
- **자동 기록 정리**: 1주일 초과 기록 자동 삭제로 성능 최적화
- **패스 상황 최소화**: 효율적인 중복 체크로 실제 작업 비율 향상

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
- **eut_comment_style.txt**: 댓글 스타일 가이드 (자동 생성됨)

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
- **새로운 기능**: 1명당 5-10초 타이머 제어, 1일 제한 자동 감지

#### 3. 댓글 자동화 (AI 기반)
- Gemini API 키 설정 필요
- 이웃글 내용을 분석하여 자연스러운 댓글 자동 생성
- 공감 버튼 자동 클릭 + 댓글 작성
- 중복 방지 및 기록 관리
- **새로운 기능**: 시간 표시, 스타일 가이드 적용

#### 4. Chrome 환경 테스트
- Chrome 설치 상태 확인
- ChromeDriver 자동 다운로드 및 버전 확인
- 브라우저 실행 테스트
- **새로운 기능**: 상세 디버깅 정보, 오류별 해결 방법 제시

#### 5. API 테스트
- Gemini API 연결 상태 확인
- API 키 유효성 검증

## 파일 구조
```
naver/
├── main.py                    # 메인 실행 파일
├── config.json               # 설정 파일 (사용자 생성)
├── config.example.json       # 설정 파일 예제
├── requirements.txt          # Python 의존성
├── README.md                # 이 파일
├── modules/                 # 핵심 모듈
│   ├── login.py            # 네이버 로그인
│   ├── neighbor_add.py     # 서이추 자동화
│   ├── comment.py          # 댓글 자동화
│   ├── like.py            # 공감 자동화
│   └── gemini.py          # AI API 연동
├── utils/                  # 유틸리티
│   ├── chrome_setup.py    # Chrome 환경 설정
│   ├── logger.py          # 로깅
│   ├── selector.py        # 셀렉터 관리
│   └── session.py         # 세션 관리
├── chrome_profile/         # Chrome 프로필 (자동 생성)
├── cookies/               # 쿠키 저장소 (자동 생성)
├── eut_message.txt        # 서이추 메시지 (자동 생성)
├── eut_comment.txt        # 댓글 기록 (자동 생성)
└── eut_comment_style.txt  # 댓글 스타일 가이드 (자동 생성)
```

## 문제 해결

### Chrome 관련 문제
- **Chrome이 설치되지 않은 경우**: https://www.google.com/chrome/ 에서 Chrome 설치
- **ChromeDriver 오류**: 프로그램이 자동으로 최신 버전을 다운로드하므로 별도 조치 불필요
- **프로필 오류**: 프로젝트 폴더의 `chrome_profile` 디렉토리가 자동 생성됨

### ⚠️ 현재 알려진 문제 (해결 필요)

#### Chrome 브라우저 실행 문제
**증상**: Chrome 환경 테스트에서 브라우저 실행이 실패하는 경우
**오류 메시지**: 
- `session not created: cannot connect to chrome`
- `you cannot reuse the ChromeOptions object`
- `chrome not reachable`

**해결 우선순위**:
1. **Chrome 프로세스 완전 종료**
   ```bash
   taskkill /f /im chrome.exe
   ```

2. **undetected_chromedriver 버전 호환성 확인**
   - 현재 사용 중인 undetected_chromedriver 버전과 Chrome 버전 호환성
   - 최신 Chrome 업데이트로 인한 호환성 문제 가능성

3. **ChromeOptions 객체 생성 방식 개선**
   - 현재 매 시도마다 새로운 객체 생성하도록 수정했으나 여전히 재사용 오류 발생
   - undetected_chromedriver 내부 구조 분석 필요

4. **대안 접근 방법**
   - selenium + webdriver-manager 조합으로 변경 검토
   - Chrome 대신 Edge 브라우저 지원 추가 검토

**임시 해결책**:
- 집 환경에서 테스트 후 환경별 차이점 분석
- 다른 PC에서 정상 작동 여부 확인
- Chrome 버전 다운그레이드 테스트

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

### v1.0 (2025-01-02)
- 댓글 자동화 시간 표시 기능 추가
- 서이추 자동화 성능 최적화 (타이머 기반 제어)
- 댓글 스타일 개선 (래주부 페르소나)
- Chrome 브라우저 안정성 개선 시도
- 상세 디버깅 시스템 구축

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