# Python 3.11 이미지를 기반으로 함
FROM python:3.11-slim-buster

# 작업 디렉토리 설정
WORKDIR /usr/src/app

# 환경 변수 설정 (출력 버퍼링 비활성화)
ENV PYTHONUNBUFFERED=1

# 필요한 패키지 설치 (옵션)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt가 있는 경우 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트의 모든 파일 복사
COPY . .

# Scrapy 명령어 실행 (예: 프로젝트 이름이 myproject인 경우)
# CMD [ "scrapy", "crawl", "price" ]
