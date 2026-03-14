"""
IT 자기소개서 생성기 (v3 NiceGUI: AI 생성 + 모의 면접)
실행: python3 .app_v3_nicegui.py
필요: pip install nicegui boto3
AWS 자격증명 필요 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
"""
import json
import asyncio
import boto3
from nicegui import ui

# ===== 학과/진로 데이터 =====
DEPARTMENTS = ["컴퓨터공학부", "컴퓨터인공지능학부", "IT지능정보공학과", "IT정보공학과"]
CAREERS = [
    "백엔드 개발자", "프론트엔드 개발자", "AI/ML 엔지니어", "데이터 엔지니어",
    "데이터 분석가", "클라우드 엔지니어", "DevSecOps 엔지니어",
    "솔루션즈 아키텍트", "정보보안 전문가", "풀스택 개발자",
]
TONES = ["정중하고 격식있는", "친근하고 자연스러운", "열정적이고 적극적인", "차분하고 진솔한"]


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


def build_interview_system(intro, info):
    """면접 시스템 프롬프트 생성"""
    return f"""당신은 IT 기업의 경험 많은 기술 면접관입니다.
지원자의 자기소개서를 꼼꼼히 읽고, 자기소개서에 적힌 내용을 기반으로 모의 면접을 진행합니다.

[자기소개서]
{intro}

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
   **[답변 평가]** 냉정하고 솔직하게 평가합니다. 좋은 점이 있으면 인정하되, 부족한 점은 구체적으로 지적하세요. 두루뭉술하거나 핵심이 없는 답변에는 "구체성이 부족합니다", "실제 경험이 드러나지 않습니다" 등 직접적으로 말해주세요. 칭찬 위주로 하지 마세요.
   **[조언]** 이 답변을 실제 면접에서 어떻게 개선해야 하는지 구체적 방법을 1-2문장으로 제시합니다.
   **[다음 질문]** 답변 내용에 따라 꼬리질문 또는 새로운 질문을 합니다.
5. 질문 유형을 골고루 섞으세요:
   - 경험 질문: 자기소개서에 적힌 프로젝트/활동에 대한 구체적 상황
   - 기술 질문: 희망 진로와 관련된 기술적 지식
   - 자격증 질문: 자격증을 보유한 경우, 해당 자격증의 핵심 개념이나 실무 활용에 대해 질문하세요.
   - 상황 질문: "만약 ~한 상황이라면 어떻게 하시겠습니까?"
   - 동기 질문: 왜 이 분야를 선택했는지, 어떤 목표가 있는지
6. 면접관답게 정중하지만 날카롭게 질문합니다.
7. 반드시 한국어로 진행합니다."""


# ===== 상태 =====
app_state = {
    "generated_intro": "",
    "user_info": {},
    "interview_messages": [],
    "interview_started": False,
}


# ===== 페이지 =====
@ui.page("/")
def main_page():
    ui.colors(primary="#1976D2")

    with ui.header().classes("items-center justify-between bg-primary"):
        ui.label("💬 IT 자기소개서 생성기").classes("text-h5 text-white font-bold")
        ui.label("v3 — AI 생성 + 모의 면접").classes("text-white text-caption")

    with ui.tabs().classes("w-full") as tabs:
        tab_intro = ui.tab("📝 자기소개서 생성")
        tab_interview = ui.tab("🎤 모의 면접")

    with ui.tab_panels(tabs, value=tab_intro).classes("w-full max-w-4xl mx-auto"):
        # ===== 탭1: 자기소개서 생성 =====
        with ui.tab_panel(tab_intro):
            with ui.card().classes("w-full q-pa-md"):
                ui.label("지원자 정보").classes("text-h6 q-mb-md")

                with ui.row().classes("w-full gap-4"):
                    name = ui.input("이름", value="홍길동").classes("flex-1")
                    university = ui.input("대학교", value="전북대학교").classes("flex-1")

                with ui.row().classes("w-full gap-4"):
                    department = ui.select(DEPARTMENTS, label="학과", value=DEPARTMENTS[0]).classes("flex-1")
                    year = ui.select(["1학년", "2학년", "3학년", "4학년", "졸업예정"], label="학년", value="3학년").classes("flex-1")

                with ui.row().classes("w-full gap-4"):
                    career = ui.select(CAREERS, label="희망 진로", value="DevSecOps 엔지니어").classes("flex-1")
                    tone = ui.select(TONES, label="문체 스타일", value=TONES[0]).classes("flex-1")

                experience = ui.textarea(
                    "관련 경험 (선택사항)",
                    value="AWS EC2, ALB, RDS를 활용한 3티어 아키텍처 기반으로 AI 애플리케이션을 설계하고 배포한 경험이 있습니다. Bedrock을 연동하여 생성형 AI 기능을 구현했습니다.",
                ).classes("w-full")
                certificates = ui.input(
                    "자격증 (선택사항)",
                    placeholder="예: AWS SAA, AWS AIF, 정보처리기사 등",
                ).classes("w-full")
                motivation = ui.textarea(
                    "지원 동기 (선택사항)",
                    placeholder="이 분야를 선택한 이유나 계기",
                ).classes("w-full")

            loading_container = ui.row().classes("w-full justify-center q-mt-md hidden")
            with loading_container:
                ui.spinner("dots", size="lg", color="primary")
                ui.label("AI가 자기소개서를 작성하고 있습니다...").classes("text-grey-7 q-ml-sm")

            intro_output = ui.markdown("").classes("w-full q-mt-md")

            async def on_generate():
                if not name.value or not university.value or not department.value:
                    ui.notify("이름, 대학교, 학과는 필수 입력입니다.", type="warning")
                    return

                generate_btn.disable()
                loading_container.classes(remove="hidden")

                prompt = f"""아래 정보를 바탕으로 {tone.value} 자기소개서를 작성해주세요.

[지원자 정보]
- 이름: {name.value}
- 대학교: {university.value}
- 학과: {department.value}
- 학년: {year.value}
- 희망 진로: {career.value}
- 관련 경험: {experience.value if experience.value else "아직 관련 경험이 없음 (학습 의지 강조)"}
- 자격증: {certificates.value if certificates.value else "없음"}
- 지원 동기: {motivation.value if motivation.value else "자유롭게 작성"}

[작성 지침]
1. 자기소개 (본인 소개 및 관심 분야)
2. 지원 동기 (이 분야를 선택한 이유)
3. 강점 및 역량 (기술적/비기술적 강점)
4. 관련 경험 (프로젝트, 학습, 활동 등)
5. 향후 계획 (목표 및 성장 방향)

각 항목을 마크다운 소제목(###)으로 구분하고, 자연스러운 문체로 500-800자 정도로 작성해주세요."""

                system = "당신은 IT 분야 자기소개서 전문 작성 도우미입니다. 지원자의 정보를 바탕으로 설득력 있는 자기소개서를 작성합니다."

                try:
                    result = await asyncio.to_thread(call_bedrock, [{"role": "user", "content": prompt}], system)
                    app_state["generated_intro"] = result
                    app_state["user_info"] = {
                        "name": name.value, "university": university.value,
                        "department": department.value, "year": year.value,
                        "career": career.value, "experience": experience.value,
                        "certificates": certificates.value,
                    }
                    app_state["interview_messages"] = []
                    app_state["interview_started"] = False
                    intro_output.set_content(f"## 📄 생성된 자기소개서\n\n{result}")
                    ui.notify("자기소개서가 생성되었습니다!", type="positive")
                except Exception as e:
                    ui.notify(f"AI 생성 실패: {e}", type="negative")
                finally:
                    loading_container.classes(add="hidden")
                    generate_btn.enable()

            generate_btn = ui.button("🤖 AI로 자기소개서 생성", on_click=on_generate).classes(
                "w-full q-mt-md"
            ).props("color=primary size=lg")

        # ===== 탭2: 모의 면접 =====
        with ui.tab_panel(tab_interview):
            chat_container = ui.column().classes("w-full gap-2")
            interview_input = ui.input(placeholder="답변을 입력하세요...").classes("w-full hidden")

            def render_messages():
                chat_container.clear()
                with chat_container:
                    if not app_state["generated_intro"]:
                        ui.label("먼저 '📝 자기소개서 생성' 탭에서 자기소개서를 생성해주세요.").classes(
                            "text-grey-7 text-center w-full q-pa-lg"
                        )
                        return

                    for msg in app_state["interview_messages"]:
                        is_bot = msg["role"] == "assistant"
                        with ui.card().classes(
                            f"{'bg-blue-1' if is_bot else 'bg-grey-2'} q-pa-sm w-full"
                        ):
                            label = "👔 면접관" if is_bot else "🙋 나"
                            ui.label(label).classes("text-bold text-caption q-mb-xs")
                            ui.markdown(msg["content"])

            interview_loading = ui.row().classes("w-full justify-center q-py-md hidden")
            with interview_loading:
                ui.spinner("dots", size="lg", color="primary")
                loading_label = ui.label("면접관이 질문을 준비하고 있습니다...").classes("text-grey-7 q-ml-sm")

            def show_loading(msg="AI가 응답을 생성하고 있습니다..."):
                loading_label.set_text(msg)
                interview_loading.classes(remove="hidden")
                start_btn.disable()
                end_btn.disable()
                send_btn.disable()

            def hide_loading():
                interview_loading.classes(add="hidden")
                start_btn.enable()
                end_btn.enable()
                send_btn.enable()

            async def start_interview():
                if not app_state["generated_intro"]:
                    ui.notify("먼저 자기소개서를 생성해주세요.", type="warning")
                    return

                show_loading("면접관이 질문을 준비하고 있습니다...")
                app_state["interview_started"] = True
                app_state["interview_messages"] = []
                system_prompt = build_interview_system(
                    app_state["generated_intro"], app_state["user_info"],
                )

                try:
                    first_q = await asyncio.to_thread(
                        call_bedrock,
                        [{"role": "user", "content": "면접을 시작해주세요. 간단한 인사와 함께 첫 번째 질문만 해주세요. [답변 평가], [조언]은 절대 하지 마세요. 질문만 하세요."}],
                        system_prompt,
                    )
                    app_state["interview_messages"].append({"role": "assistant", "content": first_q})
                    interview_input.classes(remove="hidden")
                    render_messages()
                    ui.notify("면접이 시작되었습니다!", type="positive")
                except Exception as e:
                    ui.notify(f"면접 시작 실패: {e}", type="negative")
                    app_state["interview_started"] = False
                finally:
                    hide_loading()

            async def send_answer():
                answer = interview_input.value.strip()
                if not answer:
                    return

                interview_input.value = ""
                app_state["interview_messages"].append({"role": "user", "content": answer})
                render_messages()
                show_loading("면접관이 답변을 평가하고 있습니다...")

                system_prompt = build_interview_system(
                    app_state["generated_intro"], app_state["user_info"],
                )

                # 첫 assistant 메시지 제외 (API는 user부터 시작해야 함)
                api_messages = []
                for i, m in enumerate(app_state["interview_messages"]):
                    if i == 0 and m["role"] == "assistant":
                        continue
                    api_messages.append({"role": m["role"], "content": m["content"]})

                try:
                    response = await asyncio.to_thread(call_bedrock, api_messages, system_prompt)
                    app_state["interview_messages"].append({"role": "assistant", "content": response})
                    render_messages()
                except Exception as e:
                    ui.notify(f"질문 생성 실패: {e}", type="negative")
                finally:
                    hide_loading()

            async def end_interview():
                if not app_state["interview_messages"]:
                    return

                show_loading("종합 피드백을 생성하고 있습니다...")

                info = app_state["user_info"]
                feedback_system = f"""당신은 IT 기업의 경험 많은 면접관입니다.
방금 진행한 모의 면접에 대해 종합 피드백을 제공해주세요.

[지원자 정보]
- 희망 진로: {info.get('career', '')}

[자기소개서]
{app_state['generated_intro']}

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
                for i, m in enumerate(app_state["interview_messages"]):
                    if i == 0 and m["role"] == "assistant":
                        continue
                    api_messages.append({"role": m["role"], "content": m["content"]})
                api_messages.append({"role": "user", "content": "면접이 끝났습니다. 종합 피드백을 주세요."})

                try:
                    feedback = await asyncio.to_thread(call_bedrock, api_messages, feedback_system)
                    app_state["interview_messages"].append({
                        "role": "assistant",
                        "content": f"---\n## 🎯 면접 종합 피드백\n\n{feedback}",
                    })
                    app_state["interview_started"] = False
                    interview_input.classes(add="hidden")
                    render_messages()
                    ui.notify("면접 피드백이 생성되었습니다!", type="positive")
                except Exception as e:
                    ui.notify(f"피드백 생성 실패: {e}", type="negative")
                finally:
                    hide_loading()

            with ui.row().classes("w-full gap-4 q-mb-md"):
                start_btn = ui.button("🎤 면접 시작", on_click=start_interview).props("color=primary")
                end_btn = ui.button("⏹️ 면접 종료 및 피드백", on_click=end_interview).props("color=grey")

            render_messages()

            interview_input.on("keydown.enter", send_answer)
            send_btn = ui.button("전송", on_click=send_answer).classes("w-full").props("color=primary")

    with ui.footer().classes("bg-grey-2 text-center"):
        ui.label("Powered by AWS Bedrock Claude 3 Haiku").classes("text-grey-7 text-caption")


ui.run(title="IT 자기소개서 생성기", port=8080)
