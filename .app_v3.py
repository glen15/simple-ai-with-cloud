"""
IT 자기소개서 생성기 (v3: AI 생성 + 챗봇)
실행: streamlit run app_v3.py
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


def call_bedrock(messages, system_prompt=""):
    """Bedrock Claude 3 Haiku 호출"""
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": messages,
    }
    if system_prompt:
        body["system"] = system_prompt

    response = client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def generate_intro(name, university, department, year, career, experience, motivation, tone):
    """자기소개서 생성"""
    prompt = f"""아래 정보를 바탕으로 {tone} 자기소개서를 작성해주세요.

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

    system = "당신은 IT 분야 자기소개서 전문 작성 도우미입니다. 지원자의 정보를 바탕으로 설득력 있는 자기소개서를 작성합니다."
    return call_bedrock([{"role": "user", "content": prompt}], system)


# ===== 앱 시작 =====
st.set_page_config(page_title="IT 자기소개서 생성기 AI+챗봇", page_icon="💬")
st.title("💬 IT 자기소개서 생성기")
st.caption("v3 — AI 생성 + 챗봇으로 수정/질문")

# 세션 상태 초기화
if "generated_intro" not in st.session_state:
    st.session_state.generated_intro = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# ===== 탭 구성 =====
tab1, tab2 = st.tabs(["📝 자기소개서 생성", "💬 AI 챗봇"])

# ===== 탭1: 자기소개서 생성 =====
with tab1:
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름", placeholder="홍길동")
        university = st.text_input("대학교", placeholder="한국대학교")
    with col2:
        department = st.text_input("학과", placeholder="컴퓨터공학과")
        year = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "졸업예정"])

    career = st.selectbox("희망 진로", CAREERS)
    tone = st.selectbox(
        "문체 스타일",
        ["정중하고 격식있는", "친근하고 자연스러운", "열정적이고 적극적인", "차분하고 진솔한"],
    )

    experience = st.text_area(
        "관련 경험 (선택사항)",
        placeholder="프로젝트, 인턴, 스터디, 자격증, 공모전 등",
        height=100,
    )
    motivation = st.text_area(
        "지원 동기 (선택사항)",
        placeholder="이 분야를 선택한 이유나 계기",
        height=100,
    )

    st.markdown("---")

    if st.button("🤖 AI로 자기소개서 생성", type="primary", use_container_width=True):
        if not name or not university or not department:
            st.warning("이름, 대학교, 학과는 필수 입력입니다.")
        else:
            with st.spinner("AI가 자기소개서를 작성하고 있습니다..."):
                try:
                    result = generate_intro(
                        name, university, department, year,
                        career, experience, motivation, tone,
                    )
                    st.session_state.generated_intro = result
                    st.session_state.user_info = {
                        "name": name, "university": university,
                        "department": department, "year": year,
                        "career": career, "experience": experience,
                    }
                    # 챗봇 컨텍스트 초기화
                    st.session_state.chat_messages = [
                        {
                            "role": "assistant",
                            "content": f"자기소개서가 생성되었습니다! 수정하고 싶은 부분이 있으면 말씀해주세요.\n\n예시:\n- \"지원 동기 부분을 더 구체적으로 써줘\"\n- \"경험 부분에 AWS 자격증 내용을 추가해줘\"\n- \"{career}에 필요한 역량이 뭐야?\"\n- \"전체적으로 좀 더 격식있게 바꿔줘\"",
                        }
                    ]
                except Exception as e:
                    st.error(f"AI 생성 실패: {e}")
                    st.info("AWS 자격증명이 설정되어 있는지 확인해주세요.")

    # 생성된 자기소개서 표시
    if st.session_state.generated_intro:
        st.markdown("## 📄 생성된 자기소개서")
        st.markdown(st.session_state.generated_intro)

        st.download_button(
            label="📥 텍스트로 다운로드",
            data=st.session_state.generated_intro,
            file_name=f"자기소개서_{name}.md",
            mime="text/markdown",
        )

# ===== 탭2: 챗봇 =====
with tab2:
    if not st.session_state.generated_intro:
        st.info("먼저 '📝 자기소개서 생성' 탭에서 자기소개서를 생성해주세요.")
    else:
        st.markdown("자기소개서에 대해 수정 요청이나 질문을 해보세요.")
        st.markdown("---")

        # 채팅 히스토리 표시
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 사용자 입력
        if user_input := st.chat_input("수정 요청이나 질문을 입력하세요..."):
            # 사용자 메시지 추가
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # AI 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("생각 중..."):
                    try:
                        system_prompt = f"""당신은 IT 분야 자기소개서 전문 작성 도우미입니다.

[현재 자기소개서]
{st.session_state.generated_intro}

[지원자 정보]
- 이름: {st.session_state.user_info.get('name', '')}
- 대학교: {st.session_state.user_info.get('university', '')}
- 학과: {st.session_state.user_info.get('department', '')}
- 학년: {st.session_state.user_info.get('year', '')}
- 희망 진로: {st.session_state.user_info.get('career', '')}

사용자가 자기소개서 수정을 요청하면 수정된 전체 자기소개서를 마크다운으로 작성해주세요.
자기소개서와 관련된 질문에는 친절하게 답변해주세요.
IT 진로 상담도 해줄 수 있습니다."""

                        # 대화 히스토리 구성 (시스템 프롬프트 제외)
                        api_messages = []
                        for msg in st.session_state.chat_messages:
                            api_messages.append({
                                "role": msg["role"],
                                "content": msg["content"],
                            })

                        response = call_bedrock(api_messages, system_prompt)
                        st.markdown(response)

                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response,
                        })

                        # 수정된 자기소개서가 포함된 경우 업데이트
                        if "###" in response and len(response) > 200:
                            st.session_state.generated_intro = response
                            st.success("자기소개서가 업데이트되었습니다! '📝 자기소개서 생성' 탭에서 확인하세요.")

                    except Exception as e:
                        error_msg = f"응답 생성 실패: {e}"
                        st.error(error_msg)
                        st.info("AWS 자격증명이 설정되어 있는지 확인해주세요.")
