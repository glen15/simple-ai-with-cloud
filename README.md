# IT 자기소개서 생성기

대학생을 위한 IT 분야 자기소개서 생성 앱입니다.

## 버전

| 버전 | 파일 | 설명 |
|------|------|------|
| v1 | `app_v1.py` | 템플릿 기반 (AI 없음) |
| v2 | `.app_v2.py` | Bedrock Claude Haiku AI 생성 |
| v3 | `.app_v3.py` | AI 생성 + 모의 면접 (Streamlit) |
| v3 NiceGUI | `.app_v3_nicegui.py` | AI 생성 + 모의 면접 (NiceGUI, UI 개선) |

## 지원 진로

백엔드, 프론트엔드, AI/ML 엔지니어, 데이터 엔지니어, 데이터 분석가, 클라우드 엔지니어, DevSecOps, 솔루션즈 아키텍트, 정보보안 전문가, 풀스택 개발자

## 설치 및 실행

### Kiro 설치

```bash
curl -fsSL https://cli.kiro.dev/install | bash
```

### 패키지 설치

```bash
pip install -r requirements.txt
```

### 실행

```bash
# v1: 템플릿 버전
streamlit run app_v1.py

# v2: AI 버전
streamlit run .app_v2.py

# v3: AI + 모의면접 (Streamlit)
streamlit run .app_v3.py

# v3: AI + 모의면접 (NiceGUI)
python3 .app_v3_nicegui.py
```

## 사전 요구사항

- Python 3.8+
- v2, v3: AWS 자격증명 필요 (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
