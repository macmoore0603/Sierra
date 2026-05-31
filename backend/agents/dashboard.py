# backend/agents/dashboard.py
# Maxed Sierra Dashboard with Arc Reactor + Side Panels + Voice Mode

import streamlit as st
import time

st.set_page_config(page_title="Sierra", page_icon="🤖", layout="wide")

# Custom CSS for Arc Reactor effect
st.markdown("""
<style>
.arc-reactor {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, #00f0ff 10%, #0066ff 40%, #001a33 70%);
    box-shadow: 0 0 40px #00f0ff, 0 0 80px #0066ff;
    animation: pulse 2s infinite ease-in-out;
    margin: auto;
}

@keyframes pulse {
    0% { box-shadow: 0 0 40px #00f0ff, 0 0 80px #0066ff; }
    50% { box-shadow: 0 0 70px #00f0ff, 0 0 140px #0066ff; }
    100% { box-shadow: 0 0 40px #00f0ff, 0 0 80px #0066ff; }
}

.voice-active .arc-reactor {
    animation: pulse 0.8s infinite;
    box-shadow: 0 0 60px #ff00aa, 0 0 120px #ff00aa;
}
</style>
""", unsafe_allow_html=True)

st.title("Sierra – Arc Reactor Dashboard")

# Layout with side panels
col1, col2, col3 = st.columns([1, 2, 1])

# LEFT PANEL - Agents & Status
with col1:
    st.subheader("Agent Status")
    st.success("Director Sierra – Online")
    st.info("Morning Oracle – Ready")
    st.info("Background Operator – Active")
    st.info("Neural Link – Connected")
    st.caption("40+ agents active")

# CENTER - Arc Reactor + Main Controls
with col2:
    st.subheader("Core Interface")
    
    # Arc Reactor Visual
    reactor_html = """
    <div style="text-align: center; padding: 20px;">
        <div class="arc-reactor"></div>
        <h3 style="margin-top: 15px; color: #00f0ff;">ARC REACTOR</h3>
        <p style="color: #aaa;">Sierra Core – Stable</p>
    </div>
    """
    st.components.v1.html(reactor_html, height=280)
    
    # Voice Mode Toggle
    voice_mode = st.toggle("Move to Voice Mode", value=False)
    
    if voice_mode:
        st.success("🔊 Voice Mode Active – Listening...")
        st.markdown('<div class="voice-active">', unsafe_allow_html=True)
        
        if st.button("Speak to Sierra", use_container_width=True):
            st.info("Voice input simulated. Connect to real STT.")
    else:
        st.caption("Toggle above to activate voice interface")
    
    # Quick Actions
    st.divider()
    if st.button("Generate Daily Briefing", use_container_width=True):
        st.success("Daily Briefing generated via Morning Oracle + Neural Link.")

# RIGHT PANEL - Neural Link & Proactive
with col3:
    st.subheader("Neural Link")
    st.metric("Energy Level", "High")
    st.metric("Focus", "Focused")
    st.metric("Proactive Alerts", "2")
    
    if st.button("Run Proactive Check"):
        st.info("Proactive suggestions would appear here.")
    
    st.divider()
    st.caption("Last updated: just now")