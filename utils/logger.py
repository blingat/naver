import os
import datetime

class Logger:
    def __init__(self, log_file='log.txt', max_size_mb=10):
        self.log_file = log_file
        self.max_size_bytes = max_size_mb * 1024 * 1024  # MB to bytes
        self._check_and_rotate()
    
    def _check_and_rotate(self):
        """로그 파일 크기 확인 및 백업"""
        if os.path.exists(self.log_file):
            file_size = os.path.getsize(self.log_file)
            if file_size > self.max_size_bytes:
                # 기존 백업 파일이 있으면 삭제
                backup_file = f"{self.log_file}.1"
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                # 현재 로그 파일을 백업으로 이동
                os.rename(self.log_file, backup_file)
                print(f"[로그] 로그 파일이 {self.max_size_bytes/1024/1024}MB를 초과하여 백업했습니다.")
    
    def log(self, message):
        """로그 메시지 기록 - PRD 형식"""
        self._check_and_rotate()
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"[오류] 로그 기록 실패: {e}")
    
    def log_separator(self):
        """구분선 로그"""
        self.log("=" * 70)
    
    def log_result(self, module, success, fail, passed, total):
        """결과 요약 로그 - PRD 예시 형식"""
        message = f"[{module}] {success+fail+passed}/{total} 완료 (성공: {success}, 실패: {fail}, pass: {passed})"
        self.log(message)
    
    def clean_old_comments(self):
        """1주일 초과된 댓글 기록 정리"""
        comment_file = 'eut_comment.txt'
        if not os.path.exists(comment_file):
            return
        
        try:
            one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            
            # 파일 읽기
            with open(comment_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 1주일 이내 기록만 필터링
            valid_lines = []
            for line in lines:
                try:
                    # 날짜 파싱 (형식: URL | YYYY-MM-DD HH:MM:SS)
                    if '|' in line:
                        date_str = line.split('|')[1].strip()
                        line_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        if line_date > one_week_ago:
                            valid_lines.append(line)
                except:
                    # 파싱 실패한 라인은 유지
                    valid_lines.append(line)
            
            # 정리된 내용으로 파일 재작성
            with open(comment_file, 'w', encoding='utf-8') as f:
                f.writelines(valid_lines)
                
            removed_count = len(lines) - len(valid_lines)
            if removed_count > 0:
                self.log(f"[댓글] 1주일 초과 기록 {removed_count}개 정리 완료")
                
        except Exception as e:
            self.log(f"[댓글] 오래된 기록 정리 실패: {e}") 