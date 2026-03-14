"""
IT 자기소개서 생성기 (v1: 템플릿 기반, AI 없음)
실행: streamlit run app_v1.py
"""
import streamlit as st

# ===== 진로 데이터 =====
CAREERS = {
    "프론트엔드 개발자": {
        "skills": "HTML/CSS, JavaScript, React, TypeScript",
        "description": "사용자와 가장 가까운 곳에서 인터페이스를 만드는",
        "strength": "사용자 경험을 중시하며 직관적인 화면을 설계하는 데 관심이 많습니다.",
        "goal": "뛰어난 UI/UX를 갖춘 웹 서비스를 만들어 많은 사용자에게 편리함을 제공하는 프론트엔드 개발자",
    },
    "백엔드 개발자": {
        "skills": "Python, Java, Spring, Node.js, DB 설계",
        "description": "서비스의 핵심 로직과 데이터를 다루는",
        "strength": "문제를 논리적으로 분석하고 효율적인 시스템을 설계하는 것을 좋아합니다.",
        "goal": "안정적이고 확장 가능한 서버 시스템을 구축하는 백엔드 개발자",
    },
    "데이터 엔지니어": {
        "skills": "Python, SQL, Spark, Airflow, ETL 파이프라인",
        "description": "대규모 데이터 파이프라인을 설계하고 운영하는",
        "strength": "복잡한 데이터 흐름을 정리하고 최적화하는 것에 흥미를 느낍니다.",
        "goal": "기업의 데이터 인프라를 책임지는 데이터 엔지니어",
    },
    "데이터 분석가": {
        "skills": "Python, R, SQL, Tableau, 통계 분석",
        "description": "데이터에서 인사이트를 발견하여 의사결정을 돕는",
        "strength": "숫자 속에서 의미를 찾고 이를 비즈니스에 연결하는 것을 좋아합니다.",
        "goal": "데이터 기반 의사결정을 이끄는 데이터 분석가",
    },
    "클라우드 엔지니어": {
        "skills": "AWS, Azure, GCP, Terraform, 네트워크",
        "description": "클라우드 인프라를 설계하고 관리하는",
        "strength": "인프라 자동화와 최적화에 관심이 많으며 안정적인 시스템 운영을 추구합니다.",
        "goal": "대규모 클라우드 인프라를 설계하고 운영하는 클라우드 엔지니어",
    },
    "솔루션즈 아키텍트": {
        "skills": "클라우드 아키텍처, 시스템 설계, 기술 컨설팅",
        "description": "고객의 비즈니스 문제를 기술로 해결하는",
        "strength": "기술과 비즈니스를 연결하여 최적의 솔루션을 제안하는 것을 좋아합니다.",
        "goal": "고객에게 최적의 기술 아키텍처를 제안하는 솔루션즈 아키텍트",
    },
    "데브옵스 엔지니어": {
        "skills": "CI/CD, Docker, Kubernetes, Jenkins, 모니터링",
        "description": "개발과 운영의 경계를 허물고 자동화하는",
        "strength": "반복 작업을 자동화하고 개발 생산성을 높이는 데 보람을 느낍니다.",
        "goal": "개발 조직의 생산성과 안정성을 동시에 높이는 데브옵스 엔지니어",
    },
    "보안 엔지니어 (SecOps)": {
        "skills": "보안 모니터링, SIEM, 침투 테스트, 보안 정책",
        "description": "시스템과 데이터를 위협으로부터 보호하는",
        "strength": "보안 위협을 탐지하고 대응하는 과정에서 도전의식을 느낍니다.",
        "goal": "조직의 보안 체계를 설계하고 위협에 대응하는 보안 엔지니어",
    },
    "DevSecOps 엔지니어": {
        "skills": "CI/CD, Docker, Kubernetes, 보안 자동화, IaC, SAST/DAST",
        "description": "개발·보안·운영을 통합하여 안전한 소프트웨어 배포를 자동화하는",
        "strength": "보안을 개발 초기 단계부터 내재화하고, 자동화된 파이프라인으로 안전한 배포를 실현하는 데 관심이 많습니다.",
        "goal": "보안이 내재된 DevOps 문화를 주도하는 DevSecOps 엔지니어",
    },
    "AI 엔지니어": {
        "skills": "Python, PyTorch, TensorFlow, LLM, MLOps",
        "description": "인공지능 모델을 개발하고 서비스에 적용하는",
        "strength": "AI 기술로 실제 문제를 해결하는 것에 큰 열정을 가지고 있습니다.",
        "goal": "AI 기술을 활용하여 혁신적인 서비스를 만드는 AI 엔지니어",
    },
}


def generate_intro(name, university, department, year, career, experience, motivation):
    """템플릿 기반 자기소개서 생성"""
    info = CAREERS[career]

    return f"""## 자기소개서

### 1. 자기소개

안녕하세요, 저는 {university} {department}에 재학 중인 {year} {name}입니다.
{info['description']} {career} 분야에 관심을 가지고 꾸준히 역량을 키워가고 있습니다.

### 2. 지원 동기

{motivation if motivation else f"빠르게 변화하는 IT 업계에서 {career}의 역할이 점점 더 중요해지고 있다고 생각합니다. 특히 {info['skills']} 등의 기술을 활용하여 실질적인 가치를 만들어내는 과정에 매력을 느껴 이 분야를 선택하게 되었습니다."}

### 3. 강점 및 역량

{info['strength']}
{f"그동안의 경험을 통해 이를 더욱 확신하게 되었습니다: {experience}" if experience else f"관련 기술({info['skills']})을 학습하며 역량을 쌓아가고 있습니다."}

### 4. 향후 계획

저의 목표는 **{info['goal']}**가 되는 것입니다.
대학 생활 동안 관련 프로젝트와 스터디에 적극 참여하고, 실무 역량을 갖춘 인재로 성장하겠습니다.
"""


# ===== 앱 시작 =====
st.set_page_config(page_title="IT 자기소개서 생성기", page_icon="📝")
st.title("📝 IT 자기소개서 생성기")
st.caption("v1 — 템플릿 기반 (AI 없음)")

st.markdown("---")

# 입력 폼
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름", value="홍길동")
    university = st.text_input("대학교", value="한국대학교")
with col2:
    department = st.text_input("학과", value="컴퓨터공학과")
    year = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "졸업예정"], index=2)

career_list = list(CAREERS.keys())
career = st.selectbox("희망 진로", career_list, index=career_list.index("DevSecOps 엔지니어"))

# 선택한 진로 정보 표시
with st.expander(f"💡 {career} 관련 정보"):
    info = CAREERS[career]
    st.markdown(f"**주요 기술**: {info['skills']}")
    st.markdown(f"**분야 설명**: {info['description']} 직무입니다.")

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

if st.button("📝 자기소개서 생성", type="primary", use_container_width=True):
    if not name or not university or not department:
        st.warning("이름, 대학교, 학과는 필수 입력입니다.")
    else:
        result = generate_intro(name, university, department, year, career, experience, motivation)
        st.markdown(result)

        st.download_button(
            label="📥 텍스트로 다운로드",
            data=result,
            file_name=f"자기소개서_{name}.md",
            mime="text/markdown",
        )
