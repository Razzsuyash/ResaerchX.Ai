import json
import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")


st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔎",
    layout="wide",
)


def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}",
    }


def api_get(path):
    return requests.get(
        f"{API_URL}{path}",
        headers=auth_headers(),
        timeout=30,
    )


def login(email: str, password: str):
    response = requests.post(
        f"{API_URL}/api/auth/login",
        data={"username": email, "password": password},
        timeout=30,
    )
    if response.ok:
        return response.json()["access_token"]
    return None


if "token" not in st.session_state:
    st.session_state.token = None

if "selected_session" not in st.session_state:
    st.session_state.selected_session = None


if not st.session_state.token:
    st.title("🔎 Deep Research Agent")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")

        if submitted:
            token = login(email, password)
            if token:
                st.session_state.token = token
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with register_tab:
        with st.form("register_form"):
            email = st.text_input("Email", key="register_email")
            password = st.text_input(
                "Password",
                type="password",
                key="register_password",
                help="Use at least 8 characters.",
            )
            submitted = st.form_submit_button("Create account")

        if submitted:
            response = requests.post(
                f"{API_URL}/api/auth/register",
                json={"email": email, "password": password},
                timeout=30,
            )
            if response.ok:
                st.success("Account created. You can now log in.")
            else:
                try:
                    st.error(response.json().get("detail", "Registration failed."))
                except Exception:
                    st.error("Registration failed.")

    st.stop()


with st.sidebar:
    st.header("Research History")

    if st.button("Refresh"):
        st.rerun()

    history_response = api_get("/api/research?limit=20")

    if history_response.ok:
        history = history_response.json()

        for item in history:
            label = item["question"][:55]
            if st.button(
                f'{item["status"].upper()}: {label}',
                key=f'history_{item["id"]}',
                use_container_width=True,
            ):
                st.session_state.selected_session = item["id"]
                st.rerun()

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.selected_session = None
        st.rerun()


st.title("🔎 Deep Research Agent")
st.caption(
    "FastAPI • LangGraph • OpenAI • Tavily • PostgreSQL • Streamlit"
)

with st.expander("🧩 Agent Graph"):
    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;
            START -> DECOMPOSE;
            DECOMPOSE -> "RESEARCH Q1";
            DECOMPOSE -> "RESEARCH Q2";
            DECOMPOSE -> "RESEARCH QN";
            "RESEARCH Q1" -> FACT_CHECK;
            "RESEARCH Q2" -> FACT_CHECK;
            "RESEARCH QN" -> FACT_CHECK;
            FACT_CHECK -> SYNTHESIZE [label="complete"];
            FACT_CHECK -> RESEARCH_AGAIN [label="gaps/conflicts"];
            RESEARCH_AGAIN -> FACT_CHECK;
            SYNTHESIZE -> END;
        }
        """,
        use_container_width=True,
    )


question = st.text_area(
    "Research question",
    placeholder=(
        "Example: Compare electric vehicles and hydrogen vehicles "
        "in India in terms of cost, infrastructure, efficiency, "
        "government support and future adoption."
    ),
    height=130,
)


def render_session(session):
    st.markdown("## 🧠 Final Answer")
    if session.get("answer"):
        st.markdown(session["answer"])
    else:
        st.info(f'Status: {session["status"]}')

    c1, c2, c3 = st.columns(3)
    c1.metric("Sub-questions", len(session.get("sub_questions", [])))
    c2.metric("Sources", len(session.get("sources", [])))
    c3.metric("Research passes", session.get("iterations", 0))

    with st.expander("Generated sub-questions", expanded=True):
        for q in session.get("sub_questions", []):
            st.write(f"• {q}")

    contradictions = session.get("contradictions", [])
    if contradictions:
        with st.expander("⚠️ Contradictions"):
            for item in contradictions:
                st.warning(item)

    gaps = session.get("gaps", [])
    if gaps:
        with st.expander("Knowledge gaps"):
            for item in gaps:
                st.write(f"• {item}")

    with st.expander("📚 Sources"):
        for index, source in enumerate(session.get("sources", []), start=1):
            st.markdown(f"**[Source {index}] {source['title']}**")
            st.caption(source["question"])
            if source.get("score") is not None:
                st.caption(f"Relevance score: {source['score']:.3f}")
            st.write(source["content"])
            st.markdown(source["url"])
            st.divider()


if st.button("🚀 Start Research", type="primary", use_container_width=True):
    if len(question.strip()) < 10:
        st.warning("Please enter a research question with at least 10 characters.")
    else:
        progress = st.empty()
        events = []

        try:
            response = requests.post(
                f"{API_URL}/api/research/stream",
                json={"question": question},
                headers=auth_headers(),
                stream=True,
                timeout=600,
            )

            if not response.ok:
                st.error(response.text)
            else:
                current_event = None

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    if line.startswith("event:"):
                        current_event = line.split(":", 1)[1].strip()

                    elif line.startswith("data:"):
                        payload = json.loads(line.split(":", 1)[1].strip())
                        events.append((current_event, payload))

                        if current_event == "progress":
                            node = payload.get("node", "agent")
                            progress.info(f"🔵 {node} completed")

                        elif current_event == "started":
                            progress.info("🔵 Research started...")

                        elif current_event == "completed":
                            progress.success("✅ Research completed.")

                        elif current_event == "error":
                            progress.error(payload.get("message", "Research failed."))

                completed = next(
                    (data for event, data in reversed(events) if event == "completed"),
                    None,
                )

                if completed:
                    session_response = api_get(
                        f'/api/research/{completed["session_id"]}'
                    )
                    if session_response.ok:
                        render_session(session_response.json())
                    else:
                        st.error("Research completed, but the result could not be loaded.")

        except requests.RequestException as exc:
            st.error(f"Backend connection failed: {exc}")


if st.session_state.selected_session:
    st.divider()
    selected_response = api_get(
        f'/api/research/{st.session_state.selected_session}'
    )

    if selected_response.ok:
        st.markdown("## 🗂️ Selected Research")
        render_session(selected_response.json())
