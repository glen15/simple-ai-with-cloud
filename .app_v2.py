"""
IT 자기소개서 생성기 (v2: Bedrock Claude Haiku AI 생성)
실행: streamlit run app_v2.py
필요: pip install streamlit boto3
AWS 자격증명 필요 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
"""
import streamlit as st
import json
import boto3

# ===== 진로 데이터 =====
CAREERS = [
    "프론트엔드 개발자",
    "백엔드 개발자",
    "데이터 엔지니어",
    "데이터 분석가",
    "클라우드 엔지니어",
    "솔루션즈 아키텍트",
    "데브옵스 엔지니어",
    "보안 엔지니어 (SecOps)",
    "AI 엔지니어",
    "풀스택 개발자",
    "모바일 개발자",
    "게임 개발자",
    "QA 엔지니어",
    "IT 컨설턴트",
]


def generate_with_ai(name, university, department, year, career, experience, motivation, tone):
    """Bedrock Claude 3 Haiku로 자기소개서 생성"""
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    prompt = f"""당신은 IT 분야 자기소개서 전문 작성 도우미입니다.
아래 정보를 바탕으로 {tone} 자기소개서를 작성해주세요.

[지원자 정보]
- 이름: {name}
- 대학교: {university}
- 학과: {department}
- 학년: {year}
- 희망 진로: {career}
- 관련 경험: {experience if experience else "아직 관련 경험이 없음 (학습 의지 강조)"}
- 지원 동기: {motivation if motivation else "자유롭게 작성"}

[작성 지침]
1. 자기소개 (본인 소개 및 관심 분야)
2. 지원 동기 (이 분야를 선택한 이유)
3. 강점 및 역량 (기술적/비기술적 강점)
4. 관련 경험 (프로젝트, 학습, 활동 등)
5. 향후 계획 (목표 및 성장 방향)

각 항목을 마크다운 소제목(###)으로 구분하고, 자연스러운 문체로 500-800자 정도로 작성해주세요."""

    response = client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        }),
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# ===== 앱 시작 =====
st.set_page_config(page_title="IT 자기소개서 생성기 AI", page_icon="🤖")
st.title("🤖 IT 자기소개서 생성기")
st.caption("v2 — Bedrock Claude AI가 작성해드립니다")

st.markdown("---")

# 입력 폼
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름", value="홍길동")
    university = st.text_input("대학교", value="한국대학교")
with col2:
    department = st.text_input("학과", value="컴퓨터공학과")
    year = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "졸업예정"], index=2)

career = st.selectbox("희망 진로", CAREERS)
tone = st.selectbox("문체 스타일", ["정중하고 격식있는", "친근하고 자연스러운", "열정적이고 적극적인", "차분하고 진솔한"])

experience = st.text_area(
    "관련 경험 (선택사항)",
    value="교내 웹 개발 프로젝트에서 팀장을 맡아 3개월간 서비스를 개발한 경험이 있습니다.",
    height=120,
)
motivation = st.text_area(
    "지원 동기 (선택사항)",
    value="",
    height=120,
)

st.markdown("---")

if st.button("🤖 AI로 자기소개서 생성", type="primary", use_container_width=True):
    if not name or not university or not department:
        st.warning("이름, 대학교, 학과는 필수 입력입니다.")
    else:
        with st.spinner("AI가 자기소개서를 작성하고 있습니다..."):
            try:
                result = generate_with_ai(
                    name, university, department, year,
                    career, experience, motivation, tone,
                )
                st.markdown("## 📄 생성된 자기소개서")
                st.markdown(result)

                st.download_button(
                    label="📥 텍스트로 다운로드",
                    data=result,
                    file_name=f"자기소개서_{name}.md",
                    mime="text/markdown",
                )
            except Exception as e:
                st.error(f"AI 생성 실패: {e}")
                st.info("AWS 자격증명이 설정되어 있는지 확인해주세요.")
