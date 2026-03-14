"""
IT 자기소개서 생성기 (v3: AI 생성 + 챗봇 + 모의 면접)
실행: streamlit run .app_v3.py
필요: pip install streamlit boto3
AWS 자격증명 필요 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
"""
import streamlit as st
import json
import boto3

# ===== 학과/진로 데이터 =====
DEPARTMENTS = [
    "컴퓨터공학부 (11명)",
    "컴퓨터인공지능학부 (9명)",
    "IT지능정보공학과 (4명)",
    "IT정보공학과",
]

CAREERS = [
    "백엔드 개발자",
    "프론트엔드 개발자",
    "AI/ML 엔지니어",
    "데이터 엔지니어",
    "데이터 분석가",
    "클라우드 엔지니어",
    "DevSecOps 엔지니어",
    "솔루션즈 아키텍트",
    "정보보안 전문가",
    "풀스택 개발자",
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
st.set_page_config(page_title="IT 자기소개서 + 모의면접", page_icon="💬")
st.title("💬 IT 자기소개서 생성기")
st.caption("v3 — AI 생성 + 챗봇 + 모의 면접")

# 세션 상태 초기화
for key, default in {
    "generated_intro": "",
    "chat_messages": [],
    "user_info": {},
    "interview_messages": [],
    "interview_started": False,
    "interview_question_count": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ===== 탭 구성 =====
tab1, tab2, tab3 = st.tabs(["📝 자기소개서 생성", "💬 AI 챗봇", "🎤 모의 면접"])

# ===== 탭1: 자기소개서 생성 =====
with tab1:
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름", value="홍길동")
        university = st.text_input("대학교", value="전북대학교")
    with col2:
        department = st.selectbox("학과", DEPARTMENTS)
        year = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "졸업예정"], index=2)

    career = st.selectbox("희망 진로", CAREERS)
    tone = st.selectbox(
        "문체 스타일",
        ["정중하고 격식있는", "친근하고 자연스러운", "열정적이고 적극적인", "차분하고 진솔한"],
    )

    experience = st.text_area(
        "관련 경험 (선택사항)",
        value="교내 웹 개발 프로젝트에서 팀장을 맡아 3개월간 서비스를 개발한 경험이 있습니다.",
        height=100,
    )
    motivation = st.text_area(
        "지원 동기 (선택사항)",
        value="",
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
                    st.session_state.chat_messages = [
                        {
                            "role": "assistant",
                            "content": f"자기소개서가 생성되었습니다! 수정하고 싶은 부분이 있으면 말씀해주세요.\n\n예시:\n- \"지원 동기 부분을 더 구체적으로 써줘\"\n- \"경험 부분에 AWS 자격증 내용을 추가해줘\"\n- \"{career}에 필요한 역량이 뭐야?\"\n- \"전체적으로 좀 더 격식있게 바꿔줘\"",
                        }
                    ]
                except Exception as e:
                    st.error(f"AI 생성 실패: {e}")
                    st.info("AWS 자격증명이 설정되어 있는지 확인해주세요.")

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

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_input := st.chat_input("수정 요청이나 질문을 입력하세요...", key="chat_input"):
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

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

                        api_messages = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.chat_messages
                        ]

                        response = call_bedrock(api_messages, system_prompt)
                        st.markdown(response)

                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response,
                        })

                        if "###" in response and len(response) > 200:
                            st.session_state.generated_intro = response
                            st.success("자기소개서가 업데이트되었습니다! '📝 자기소개서 생성' 탭에서 확인하세요.")

                    except Exception as e:
                        st.error(f"응답 생성 실패: {e}")
                        st.info("AWS 자격증명이 설정되어 있는지 확인해주세요.")

# ===== 탭3: 모의 면접 =====
with tab3:
    if not st.session_state.generated_intro:
        st.info("먼저 '📝 자기소개서 생성' 탭에서 자기소개서를 생성해주세요.")
    else:
        st.markdown("자기소개서를 기반으로 모의 면접을 진행합니다. 면접관이 질문하면 답변해주세요.")
        st.markdown("---")

        # 면접 시작/종료 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎤 면접 시작", type="primary", use_container_width=True, disabled=st.session_state.interview_started):
                st.session_state.interview_started = True
                st.session_state.interview_question_count = 0
                st.session_state.interview_messages = []

                # 첫 질문 생성
                system_prompt = f"""당신은 IT 기업의 경험 많은 면접관입니다.
아래 지원자의 자기소개서를 읽고 모의 면접을 진행합니다.

[자기소개서]
{st.session_state.generated_intro}

[지원자 정보]
- 이름: {st.session_state.user_info.get('name', '')}
- 대학교: {st.session_state.user_info.get('university', '')}
- 학과: {st.session_state.user_info.get('department', '')}
- 학년: {st.session_state.user_info.get('year', '')}
- 희망 진로: {st.session_state.user_info.get('career', '')}

[면접 진행 규칙]
1. 한 번에 질문 1개만 합니다.
2. 자기소개서 내용을 기반으로 구체적인 질문을 합니다.
3. 지원자의 답변에 따라 꼬리질문을 하거나 다음 주제로 넘어갑니다.
4. 기술 질문, 경험 질문, 상황 질문을 골고루 섞습니다.
5. 면접관답게 정중하지만 날카로운 질문을 합니다.
6. 답변이 부족하면 더 구체적으로 답변해달라고 요청합니다.
7. 반드시 한국어로 질문합니다.

먼저 간단한 인사와 함께 첫 번째 질문을 해주세요."""

                with st.spinner("면접관이 질문을 준비하고 있습니다..."):
                    try:
                        first_question = call_bedrock(
                            [{"role": "user", "content": "면접을 시작해주세요."}],
                            system_prompt,
                        )
                        st.session_state.interview_messages = [
                            {"role": "assistant", "content": first_question}
                        ]
                        st.session_state.interview_question_count = 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"면접 시작 실패: {e}")
                        st.session_state.interview_started = False

        with col2:
            if st.button("⏹️ 면접 종료 및 피드백", use_container_width=True, disabled=not st.session_state.interview_started):
                # 종합 피드백 생성
                system_prompt = f"""당신은 IT 기업의 경험 많은 면접관입니다.
방금 진행한 모의 면접에 대해 종합 피드백을 제공해주세요.

[지원자 정보]
- 희망 진로: {st.session_state.user_info.get('career', '')}

[피드백 형식]
### 📊 종합 평가
전반적인 면접 수행에 대한 평가 (5점 만점)

### ✅ 잘한 점
- 구체적으로 잘했던 답변이나 태도

### ⚠️ 개선할 점
- 부족했던 부분과 개선 방향

### 💡 팁
- 실제 면접에서 도움이 될 조언"""

                with st.spinner("피드백을 생성하고 있습니다..."):
                    try:
                        api_messages = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.interview_messages
                        ]
                        api_messages.append({
                            "role": "user",
                            "content": "면접이 끝났습니다. 종합 피드백을 주세요.",
                        })

                        feedback = call_bedrock(api_messages, system_prompt)
                        st.session_state.interview_messages.append({
                            "role": "assistant",
                            "content": f"---\n## 🎯 면접 종합 피드백\n\n{feedback}",
                        })
                        st.session_state.interview_started = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"피드백 생성 실패: {e}")

        # 면접 질문 수 표시
        if st.session_state.interview_messages:
            st.caption(f"진행된 질문 수: {st.session_state.interview_question_count}")

        # 면접 대화 히스토리 표시
        for msg in st.session_state.interview_messages:
            role_label = "면접관" if msg["role"] == "assistant" else "나"
            avatar = "👔" if msg["role"] == "assistant" else "🙋"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # 답변 입력
        if st.session_state.interview_started:
            if answer := st.chat_input("답변을 입력하세요...", key="interview_input"):
                st.session_state.interview_messages.append({"role": "user", "content": answer})

                system_prompt = f"""당신은 IT 기업의 경험 많은 면접관입니다.
모의 면접을 진행 중입니다.

[자기소개서]
{st.session_state.generated_intro}

[지원자 정보]
- 이름: {st.session_state.user_info.get('name', '')}
- 희망 진로: {st.session_state.user_info.get('career', '')}

[면접 진행 규칙]
1. 한 번에 질문 1개만 합니다.
2. 지원자의 답변이 모호하거나 부족하면 꼬리질문을 합니다.
3. 답변이 충분하면 다음 주제로 넘어갑니다.
4. 기술 질문, 경험 질문, 인성 질문, 상황 질문을 골고루 섞습니다.
5. 간단히 답변에 대한 반응(좋은 답변입니다/조금 더 구체적으로 등)을 한 후 다음 질문을 합니다.
6. 반드시 한국어로 진행합니다."""

                with st.spinner("면접관이 다음 질문을 준비하고 있습니다..."):
                    try:
                        api_messages = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.interview_messages
                        ]

                        response = call_bedrock(api_messages, system_prompt)
                        st.session_state.interview_messages.append({
                            "role": "assistant",
                            "content": response,
                        })
                        st.session_state.interview_question_count += 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"질문 생성 실패: {e}")
