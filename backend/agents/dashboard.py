#!/usr/bin/env python3
"""
Sierra A.V.E.N.G.E.R.S Dashboard (Streamlit)

Beautiful visual roster dashboard + chat interface with Director.

Run with:
    streamlit run backend/agents/dashboard.py

Shows all agents, their status, memory, and lets you chat directly with the Director
(or delegate complex tasks).
"""

import streamlit as st
from backend.agents.sierra_integration import get_avengers_system

st.set_page_config(page_title="Sierra A.V.E.N.G.E.R.S", page_icon="🤖", layout="wide")

st.title("Sierra A.V.E.N.G.E.R.S")
st.caption("Autonomous Virtual Entities for Networked Global Execution & Response Strategy | Powered by Sierra")

# Sidebar
st.sidebar.header("System Status")
st.sidebar.success("All 15 agents online")
st.sidebar.info("Memory: Per-agent + shared | Voice: Enabled | Safety: Sentinel active")

# Initialize system (cached)
@st.cache_resource
def load_avengers():
    # Replace with your actual LLM initialization from Sierra
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)
    except Exception:
        st.error("LLM not initialized. Using demo mode.")
        llm = None
    return get_avengers_system(llm) if llm else None

avengers = load_avengers()

if avengers:
    # Roster view
    st.subheader("Agent Roster")
    status = avengers.get_roster_status()

    cols = st.columns(3)
    for i, agent_info in enumerate(status):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{agent_info['role']}**")
                st.caption(agent_info['goal'][:80] + "...")
                st.caption(f"Memory: {'✅' if agent_info['memory_enabled'] else '❌'} | Voice: {'✅' if agent_info['voice_enabled'] else '❌'}")

    st.divider()

    # Chat with Director
    st.subheader("Chat with Director Sierra")
    user_input = st.text_area("Message to Director", placeholder="Delegate a complex task or ask anything...", height=100)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send to Director", type="primary"):
            if user_input:
                with st.spinner("Director is coordinating the team..."):
                    response = avengers.chat_with_director(user_input, use_voice=False)
                    st.success("Director responded:")
                    st.write(response)
    with col2:
        if st.button("Run via LangGraph (Advanced)"):
            if user_input:
                with st.spinner("Orchestrating with LangGraph..."):
                    result = avengers.handle_complex_task(user_input)
                    st.info("LangGraph result:")
                    st.json(result)

    st.divider()

    # Quick actions
    st.subheader("Quick Actions")
    if st.button("Get Full Roster Status"):
        st.json(status)

    if st.button("Speak as Director (Voice Demo)"):
        avengers.speak_as_agent("Sierra A.V.E.N.G.E.R.S roster is fully operational and ready to assist you.")
else:
    st.warning("LLM not available. Dashboard running in limited demo mode.")

st.caption("Built for Sierra | Inspired by J.A.R.V.I.S | Voice-first • Privacy-first • Self-improving")
