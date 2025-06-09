# 상벌점 관리 시스템

학생 기숙사 상벌점 관리를 위한 데스크톱 애플리케이션

## 기능

- 상점/벌점/상쇄점 추가 및 관리
- 학생별 요약 보기
- 전체 기록 조회
- 검색 기능
- 데이터 백업 및 초기화
- 비밀번호 보호

## 사용법

1. 릴리즈 페이지에서 운영체제에 맞는 실행 파일 다운로드
2. 실행 파일 실행
3. 기본 비밀번호: `admin123`

## 개발

```bash
pip install -r requirements.txt
python main.py
```

## 빌드

```bash
pyinstaller --onefile --windowed --name="상벌점관리" main.py
```