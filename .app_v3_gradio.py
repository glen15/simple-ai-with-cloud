"""
IT 자기소개서 생성기 (v3 Gradio: AI 생성 + 모의 면접)
실행: python .app_v3_gradio.py
필요: pip install gradio boto3
AWS 자격증명 필요 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
"""
import json
import boto3
import gradio as gr

# ===== 학과/진로 데이터 =====
DEPARTMENTS = ["컴퓨터공학부", "컴퓨터인공지능학부", "IT지능정보공학과", "IT정보공학과"]
CAREERS = [
    "백엔드 개발자", "프론트엔드 개발자", "AI/ML 엔지니어", "데이터 엔지니어",
    "데이터 분석가", "클라우드 엔지니어", "DevSecOps 엔지니어",
    "솔루션즈 아키텍트", "정보보안 전문가", "풀스택 개발자",
]
TONES = ["정중하고 격식있는", "친근하고 자연스러운", "열정적이고 적극적인", "차분하고 진솔한"]

# ===== 상태 저장 =====
state = {
    "generated_intro": "",
    "user_info": {},
}


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


def generate_intro(name, university, department, year, career, experience, certificates, motivation, tone):
    """자기소개서 생성"""
    if not name or not university or not department:
        return "이름, 대학교, 학과는 필수 입력입니다."

    prompt = f"""아래 정보를 바탕으로 {tone} 자기소개서를 작성해주세요.

[지원자 정보]
- 이름: {name}
- 대학교: {university}
- 학과: {department}
- 학년: {year}
- 희망 진로: {career}
- 관련 경험: {experience if experience else "아직 관련 경험이 없음 (학습 의지 강조)"}
- 자격증: {certificates if certificates else "없음"}
- 지원 동기: {motivation if motivation else "자유롭게 작성"}

[작성 지침]
1. 자기소개 (본인 소개 및 관심 분야)
2. 지원 동기 (이 분야를 선택한 이유)
3. 강점 및 역량 (기술적/비기술적 강점)
4. 관련 경험 (프로젝트, 학습, 활동 등)
5. 향후 계획 (목표 및 성장 방향)

각 항목을 마크다운 소제목(###)으로 구분하고, 자연스러운 문체로 500-800자 정도로 작성해주세요."""

    system = "당신은 IT 분야 자기소개서 전문 작성 도우미입니다. 지원자의 정보를 바탕으로 설득력 있는 자기소개서를 작성합니다."

    try:
        result = call_bedrock([{"role": "user", "content": prompt}], system)
        state["generated_intro"] = result
        state["user_info"] = {
            "name": name, "university": university,
            "department": department, "year": year,
            "career": career, "experience": experience,
            "certificates": certificates,
        }
        return result
    except Exception as e:
        return f"AI 생성 실패: {e}\n\nAWS 자격증명이 설정되어 있는지 확인해주세요."


def build_interview_system():
    """면접 시스템 프롬프트 생성"""
    info = state["user_info"]
    return f"""당신은 IT 기업의 경험 많은 기술 면접관입니다.
지원자의 자기소개서를 꼼꼼히 읽고, 자기소개서에 적힌 내용을 기반으로 모의 면접을 진행합니다.

[자기소개서]
{state['generated_intro']}

[지원자 정보]
- 이름: {info.get('name', '')}
- 대학교: {info.get('university', '')}
- 학과: {info.get('department', '')}
- 학년: {info.get('year', '')}
- 희망 진로: {info.get('career', '')}
- 관련 경험: {info.get('experience', '')}
- 자격증: {info.get('certificates', '없음')}

[면접 진행 규칙]
1. 한 번에 질문 1개만 합니다.
2. 반드시 자기소개서에 적힌 구체적인 내용(프로젝트명, 기술, 경험, 목표 등)을 인용하며 질문하세요.
3. 지원자의 답변이 모호하면 꼬리질문으로 더 깊이 파고드세요.
4. 지원자가 답변하면 반드시 아래 형식으로 응답하세요:
   **[답변 평가]** 답변의 좋은 점과 아쉬운 점을 1-2문장으로 짧게 평가합니다.
   **[조언]** 실제 면접에서 이 답변을 더 잘할 수 있는 팁을 1문장으로 제공합니다.
   **[다음 질문]** 답변 내용에 따라 꼬리질문 또는 새로운 질문을 합니다.
5. 질문 유형을 골고루 섞으세요:
   - 경험 질문: 자기소개서에 적힌 프로젝트/활동에 대한 구체적 상황
   - 기술 질문: 희망 진로와 관련된 기술적 지식
   - 자격증 질문: 자격증을 보유한 경우, 해당 자격증의 핵심 개념이나 실무 활용에 대해 질문하세요.
   - 상황 질문: "만약 ~한 상황이라면 어떻게 하시겠습니까?"
   - 동기 질문: 왜 이 분야를 선택했는지, 어떤 목표가 있는지
6. 면접관답게 정중하지만 날카롭게 질문합니다.
7. 반드시 한국어로 진행합니다."""


def interview_chat(user_message, history):
    """모의 면접 챗봇"""
    if not state["generated_intro"]:
        return "먼저 '자기소개서 생성' 탭에서 자기소개서를 생성해주세요."

    system_prompt = build_interview_system()

    # 히스토리를 API 메시지 형식으로 변환
    api_messages = []
    for msg in history:
        api_messages.append({"role": "user", "content": msg["content"]}) if msg["role"] == "user" else api_messages.append({"role": "assistant", "content": msg["content"]})
    api_messages.append({"role": "user", "content": user_message})

    try:
        return call_bedrock(api_messages, system_prompt)
    except Exception as e:
        return f"응답 생성 실패: {e}"


def start_interview():
    """면접 시작 - 첫 질문 생성"""
    if not state["generated_intro"]:
        return [{"role": "assistant", "content": "먼저 '자기소개서 생성' 탭에서 자기소개서를 생성해주세요."}]

    system_prompt = build_interview_system()
    try:
        first_question = call_bedrock(
            [{"role": "user", "content": "면접을 시작해주세요. 자기소개서를 꼼꼼히 읽고 첫 번째 질문을 해주세요."}],
            system_prompt,
        )
        return [{"role": "assistant", "content": f"👔 **면접관**\n\n{first_question}"}]
    except Exception as e:
        return [{"role": "assistant", "content": f"면접 시작 실패: {e}"}]


def end_interview(history):
    """면접 종료 - 피드백 생성"""
    if not history:
        return history

    info = state["user_info"]
    feedback_system = f"""당신은 IT 기업의 경험 많은 면접관입니다.
방금 진행한 모의 면접에 대해 종합 피드백을 제공해주세요.

[지원자 정보]
- 희망 진로: {info.get('career', '')}

[자기소개서]
{state['generated_intro']}

[피드백 형식]
### 📊 종합 평가
전반적인 면접 수행에 대한 평가 (5점 만점)

### ✅ 잘한 점
- 구체적으로 잘했던 답변이나 태도

### ⚠️ 개선할 점
- 부족했던 부분과 개선 방향

### 💡 실전 팁
- 자기소개서 내용과 연결하여 실제 면접에서 도움이 될 구체적 조언"""

    api_messages = []
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            api_messages.append({"role": msg["role"], "content": msg["content"]})

    # 첫 assistant 제외
    if api_messages and api_messages[0]["role"] == "assistant":
        api_messages = api_messages[1:]

    api_messages.append({"role": "user", "content": "면접이 끝났습니다. 종합 피드백을 주세요."})

    try:
        feedback = call_bedrock(api_messages, feedback_system)
        history.append({"role": "assistant", "content": f"---\n## 🎯 면접 종합 피드백\n\n{feedback}"})
    except Exception as e:
        history.append({"role": "assistant", "content": f"피드백 생성 실패: {e}"})

    return history


# ===== Gradio UI =====
custom_css = """
.gradio-container { max-width: 900px !important; margin: auto; }
.tab-nav button { font-size: 16px !important; padding: 12px 24px !important; }
#intro-output { min-height: 300px; }
"""

with gr.Blocks(
    title="IT 자기소개서 생성기 + 모의면접",
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"),
    css=custom_css,
) as app:
    gr.Markdown("# 💬 IT 자기소개서 생성기\n**v3 Gradio** — AI 생성 + 모의 면접")

    with gr.Tabs():
        # ===== 탭1: 자기소개서 생성 =====
        with gr.Tab("📝 자기소개서 생성"):
            with gr.Row():
                with gr.Column():
                    name = gr.Textbox(label="이름", value="홍길동")
                    university = gr.Textbox(label="대학교", value="전북대학교")
                with gr.Column():
                    department = gr.Dropdown(label="학과", choices=DEPARTMENTS, value=DEPARTMENTS[0])
                    year = gr.Dropdown(label="학년", choices=["1학년", "2학년", "3학년", "4학년", "졸업예정"], value="3학년")

            with gr.Row():
                career = gr.Dropdown(label="희망 진로", choices=CAREERS, value="DevSecOps 엔지니어")
                tone = gr.Dropdown(label="문체 스타일", choices=TONES, value=TONES[0])

            experience = gr.Textbox(
                label="관련 경험 (선택사항)",
                value="AWS EC2, ALB, RDS를 활용한 3티어 아키텍처 기반으로 AI 애플리케이션을 설계하고 배포한 경험이 있습니다. Bedrock을 연동하여 생성형 AI 기능을 구현했습니다.",
                lines=3,
            )
            certificates = gr.Textbox(
                label="자격증 (선택사항)",
                placeholder="예: AWS SAA, AWS AIF, 정보처리기사 등",
            )
            motivation = gr.Textbox(
                label="지원 동기 (선택사항)",
                placeholder="이 분야를 선택한 이유나 계기",
                lines=3,
            )

            generate_btn = gr.Button("🤖 AI로 자기소개서 생성", variant="primary", size="lg")
            intro_output = gr.Markdown(label="생성된 자기소개서", elem_id="intro-output")

            generate_btn.click(
                fn=generate_intro,
                inputs=[name, university, department, year, career, experience, certificates, motivation, tone],
                outputs=intro_output,
            )

        # ===== 탭2: 모의 면접 =====
        with gr.Tab("🎤 모의 면접"):
            gr.Markdown("자기소개서를 기반으로 모의 면접을 진행합니다. 면접관이 질문하면 답변해주세요.")

            with gr.Row():
                start_btn = gr.Button("🎤 면접 시작", variant="primary")
                end_btn = gr.Button("⏹️ 면접 종료 및 피드백", variant="secondary")

            chatbot = gr.Chatbot(
                label="모의 면접",
                height=500,
                type="messages",
                avatar_images=(None, "https://em-content.zobj.net/source/twitter/376/necktie_1f454.png"),
            )
            msg = gr.Textbox(
                label="답변 입력",
                placeholder="면접 질문에 대한 답변을 입력하세요...",
                lines=2,
            )
            send_btn = gr.Button("전송", variant="primary")

            def respond(user_message, history):
                if not user_message.strip():
                    return "", history
                history = history or []
                history.append({"role": "user", "content": user_message})
                bot_response = interview_chat(user_message, history[:-1])
                history.append({"role": "assistant", "content": f"👔 **면접관**\n\n{bot_response}"})
                return "", history

            start_btn.click(fn=start_interview, outputs=chatbot)
            send_btn.click(fn=respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
            msg.submit(fn=respond, inputs=[msg, chatbot], outputs=[msg, chatbot])
            end_btn.click(fn=end_interview, inputs=chatbot, outputs=chatbot)

if __name__ == "__main__":
    app.launch()
