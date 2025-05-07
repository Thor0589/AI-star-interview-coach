import streamlit as st
from streamlit.components.v1 import html
import io, sys
import os
import json
from datetime import datetime
import re
from pathlib import Path
from unified_star_coach import UnifiedSTARCoach
from star_method_coach import STARMethodCoach
from models import Story
import requests
from competency_questions import COMPETENCY_QUESTIONS

# Set page config FIRST before any other Streamlit calls
st.set_page_config(page_title="STAR Coach Demo", page_icon="✨", layout="wide")

# Store Gemini API key securely - Load from environment variable
# Remove the hardcoded line below if it exists:
# st.session_state['gemini_api_key'] = "YOUR_OLD_HARDCODED_KEY"
if 'gemini_api_key' not in st.session_state:
    st.session_state['gemini_api_key'] = os.environ.get('GEMINI_API_KEY', "")

# Display a warning if the key is missing
if not st.session_state['gemini_api_key']:
    st.warning("⚠️ Gemini API Key not found. Please set the GEMINI_API_KEY environment variable. AI features will be disabled.", icon="⚠️")

# Slugify for safe filenames
def slugify(value):
    value = str(value)
    value = re.sub(r'[^\w\-_. ]', '', value)
    value = value.replace(' ', '_')
    return value[:80]

@st.cache_data(show_spinner="Contacting Gemini...")
def gemini_generate_star_section(section, comp, question, current_story):
    prompt = f"""
You are an expert interview coach. Given the competency '{comp}', the interview question '{question}', and the following STAR story so far:
Situation: {current_story.get('situation','')}
Task: {current_story.get('task','')}
Action: {current_story.get('action','')}
Result: {current_story.get('result','')}

Write a strong, concise response for the '{section.capitalize()}' section. Only return the text for this section.
"""
    api_key = st.session_state['gemini_api_key']
    # Updated URL to v1beta and :generateContent
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    # Updated payload structure for :generateContent
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if not response.ok:
            # Try to parse error for more details
            try:
                error_details = response.json()
                return f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
            except json.JSONDecodeError:
                 return f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
        result = response.json()
        # Extract text from the correct structure
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        return f"[AI Error: {e}]"

# Initialize the STAR Method coach and Unified STAR Coach
coach = STARMethodCoach()
unified_coach = UnifiedSTARCoach()

# --- Initialize Session State ---
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'q_choice' not in st.session_state:
    st.session_state['q_choice'] = ''
if 'q_text' not in st.session_state:
    st.session_state['q_text'] = ''

# Fix: Force dark mode for the whole app for now (override background and text colors globally)
st.markdown('''
<style>
html, body, .stApp, [class*="css"] {
    background: #181c20 !important;
    color: #f5f5f7 !important;
}
.stApp {
    background: #181c20 !important;
}
[data-testid="stSidebar"], .stSidebar {
    background: #23272f !important;
    color: #f5f5f7 !important;
}
[data-testid="stSidebar"] * {
    color: #f5f5f7 !important;
}

/* All textareas and chat input */
textarea, [data-testid="stChatInput"] textarea {
    background: #23272f !important;
    color: #f5f5f7 !important;
    border: 1px solid #444 !important;
}
textarea::placeholder, [data-testid="stChatInput"] textarea::placeholder {
    color: #aaa !important;
}

/* All selectboxes and inputs */
.stTextInput>div>div>input, .stSelectbox>div>div>div>input {
    background: #23272f !important;
    color: #f5f5f7 !important;
    border: 1px solid #444 !important;
}

/* Buttons */
.stButton>button {
    background: #0071e3 !important;
    color: #fff !important;
    border: none;
}
.stButton>button:hover {
    background: #005bb5 !important;
}

/* Expander and progress bar */
details>summary {
    background: #23272f !important;
    color: #f5f5f7 !important;
}
div[style*="background: #eee"] {
    background: #23272f !important;
}

/* Markdown headings */
h1, h2, h3, h4, h5, h6 {
    color: #f5f5f7 !important;
}

</style>
''', unsafe_allow_html=True)

# --- Sidebar: All selection controls ---
st.sidebar.title("STAR Story Builder")
mode = st.sidebar.radio("Choose STAR Mode", ["General STAR", "Apple Interview"], index=0)

if mode == "Apple Interview":
    apple_roles = list(unified_coach.apple_competency_data['roles_competencies'].keys())
    selected_role = st.sidebar.selectbox("Select Apple Role", apple_roles)
    apple_comps = unified_coach.apple_competency_data['roles_competencies'][selected_role]
    comp_list = apple_comps
else:
    competencies = coach.competencies
    comp_list = list(competencies.keys())

comp_choice = st.sidebar.selectbox("Select a competency", comp_list)

# Add Chat Button to Sidebar
st.sidebar.markdown("---")
if st.sidebar.button("💬 Chat with Coach", key="toggle_chat_button"):
    st.session_state.show_chat = not st.session_state.show_chat

# --- Question selection: keep in session state for toggling ---
def get_behavioral_prompts_for_competency(comp_name):
    # Try to get prompts from COMPETENCY_QUESTIONS
    if comp_name in COMPETENCY_QUESTIONS:
        return COMPETENCY_QUESTIONS[comp_name]
    # Fallback: generic behavioral prompts
    return [
        f"Describe a time you demonstrated {comp_name} in a challenging situation.",
        f"Share an experience when your {comp_name} skills made a difference.",
        f"Give an example of how you used {comp_name} to achieve a positive outcome.",
        f"Tell me about a situation where {comp_name} was critical to your success."
    ]

questions = get_behavioral_prompts_for_competency(comp_choice)
q_options = questions + ["Custom question"]
if not st.session_state.get('q_choice') or st.session_state['q_choice'] not in q_options:
    st.session_state['q_choice'] = q_options[0]

st.markdown("### Interview Question")
q_choice = st.selectbox("Select an interview question", q_options, key="build_q_select_sidebar", index=q_options.index(st.session_state['q_choice']) if st.session_state['q_choice'] in q_options else 0)
st.session_state['q_choice'] = q_choice
if q_choice == "Custom question":
    q_text = st.text_input("Enter your custom interview question", value=st.session_state.get('q_text', ''), key="build_q_text_sidebar")
    st.session_state['q_text'] = q_text
else:
    q_text = q_choice
    st.session_state['q_text'] = q_choice

# --- AI Chat Function (Defined BEFORE it's called) ---
# @st.cache_data # Consider caching if prompts are often repeated
def get_ai_chat_response(user_prompt):
    api_key = st.session_state.get('gemini_api_key')
    if not api_key:
        return "[Error: Gemini API Key not configured]"

    # Construct conversation history for the API
    messages = []
    for msg in st.session_state.chat_history:
        role = "user" if msg["role"] == "user" else "model"
        messages.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Add the latest user prompt
    messages.append({"role": "user", "parts": [{"text": user_prompt}]})

    # Define a system prompt (optional but recommended)
    system_prompt = "You are a helpful interview coach specializing in the STAR method. Answer the user\'s questions concisely and provide actionable advice related to crafting STAR stories."
    # Note: The v1beta API uses a different structure for system instructions if needed.
    # For simplicity here, we'll prepend it or rely on the model's general knowledge.

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    # Send the conversation history
    data = {"contents": messages}
    # Add generationConfig if needed (e.g., temperature, max_output_tokens)
    # data["generationConfig"] = { "temperature": 0.7, "maxOutputTokens": 500 }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=45)
        if not response.ok:
            try:
                error_details = response.json()
                return f"[AI Chat Error: {response.status_code} - {error_details.get('error', {}).get('message', response.text)}]"
            except json.JSONDecodeError:
                 return f"[AI Chat Error: {response.status_code} {response.reason}: {response.text}]"
        result = response.json()
        # Check for empty or blocked response
        if not result.get('candidates') or not result['candidates'][0].get('content') or not result['candidates'][0]['content'].get('parts'):
             # Handle potential safety blocks or empty responses
             finish_reason = result.get('candidates',[{}])[0].get('finishReason', 'UNKNOWN')
             safety_ratings = result.get('candidates',[{}])[0].get('safetyRatings', [])
             return f"[AI Response Error: Finish Reason: {finish_reason}. Safety: {safety_ratings}]"

        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except requests.exceptions.Timeout:
        return "[AI Chat Error: The request timed out. Please try again.]"
    except Exception as e:
        return f"[AI Chat Error: {e}]"

# --- Main area: Tabs for Build and Review ---
tabs = st.tabs(["Build", "Review & Score"])

with tabs[0]:  # Build tab
    st.markdown("## Build Your STAR Story")
    # Floating assistant avatar - REMOVE THE COACH MODAL PART
    html("""
    <!-- Main avatar bubble -->
    <div id="ai-avatar" style="
      position: fixed;
      bottom: 28px;
      right: 28px;
      background: #fff;
      border: 2px solid #0071e3;
      border-radius: 18px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.1);
      padding: 16px 20px;
      width: 320px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      z-index: 1000;
      transition: all 0.25s ease-in-out;
      cursor: pointer;
    ">
      <div style="display:flex;align-items:center;gap:12px;">
        <img id="ai-avatar-img" src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="48" height="48" style="border-radius:50%;">
        <div id="ai-avatar-text" style="font-size:1rem;color:#222;line-height:1.3;">
          <b>Hi, I'm your STAR Coach!</b><br>
          <span style='font-size:0.95em;'>Use the sidebar to chat!</span> <!-- Updated text -->
        </div>
      </div>
    </div>

    <!-- Minimized icon (hidden by default) -->
    <div id="ai-avatar-mini" style="
      display:none;
      position: fixed;
      bottom: 32px;
      right: 32px;
      background: #0071e3;
      border-radius: 50%;
      width: 50px;
      height: 50px;
      box-shadow: 0 6px 18px rgba(0,0,0,0.12);
      z-index: 1001;
      cursor:pointer;
      transition: all 0.25s ease-in-out;
    ">
      <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="32" height="32" style="margin:9px;">
    </div>

    <script>
    function minimizeAvatar() {
      document.getElementById('ai-avatar').style.display = 'none';
      document.getElementById('ai-avatar-mini').style.display = 'block';
    }

    function restoreAvatar() {
      document.getElementById('ai-avatar').style.display = 'block';
      document.getElementById('ai-avatar-mini').style.display = 'none';
    }

    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('ai-avatar').onclick = minimizeAvatar;
      document.getElementById('ai-avatar-mini').onclick = restoreAvatar;
    });

    // Fallback in case DOMContentLoaded has already fired (Streamlit quirk)
    setTimeout(function(){
      var main = document.getElementById('ai-avatar');
      if(main && !main.onclick) main.onclick = minimizeAvatar;
    },800);
    </script>

    <style>
    @media (max-width: 700px){
      #ai-avatar { width: 260px; padding:12px 14px;}
      #ai-avatar-mini { right: 20px; bottom: 20px; }
    }
    #ai-avatar { animation: fadeSlide 0.3s ease-out; }
    @keyframes fadeSlide { from { opacity:0; transform:translateY(8px);} to { opacity:1; transform:translateY(0);} }
    </style>
    """, height=100) # Adjust height as needed, maybe less now

    # --- Chat Interface Container (Placed AFTER get_ai_chat_response definition) ---
    if st.session_state.show_chat:
        with st.container():
            st.markdown("### 💬 Coach Chat")
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("Ask your coach anything..."):
                # Add user message to history and display
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Get AI response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    with st.spinner("Thinking..."):
                        full_response = get_ai_chat_response(prompt)
                    message_placeholder.markdown(full_response)
                # Add AI response to history
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                # No explicit rerun needed, chat_input handles it
            
            if st.button("Close Chat", key="close_chat_button"):
                 st.session_state.show_chat = False
                 st.rerun() # Rerun to hide the chat interface

    st.markdown("### Interview Question")
    if questions:
        q_options = questions + (["Custom question"] if questions else [])
        q_choice = st.selectbox("Select an interview question", q_options, key="build_q_select", index=q_options.index(st.session_state['q_choice']) if st.session_state['q_choice'] in q_options else 0)
        st.session_state['q_choice'] = q_choice
        if q_choice == "Custom question":
            q_text = st.text_input("Enter your custom interview question", value=st.session_state['q_text'], key="build_q_text")
            st.session_state['q_text'] = q_text
        else:
            q_text = q_choice
            st.session_state['q_text'] = q_choice
    else:
        q_text = st.text_input("Enter your custom interview question", value=st.session_state['q_text'], key="build_q_text")
        st.session_state['q_text'] = q_text

    # Progress bar logic with color
    def star_progress(s, t, a, r):
        total = 4
        filled = sum([bool(s.strip()), bool(t.strip()), bool(a.strip()), bool(r.strip())])
        percent = filled / total
        color = "#4caf50" if percent == 1 else ("#ffc107" if percent >= 0.5 else "#e57373")
        st.markdown(f"""
        <div style='height: 24px; background: #eee; border-radius: 8px; margin-bottom: 16px;'>
            <div style='width: {percent*100:.0f}%; height: 100%; background: {color}; border-radius: 8px; text-align: center; color: white; line-height: 24px; font-weight: bold;'>
                {int(percent*100)}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Helper for hoverable help icon
    def help_icon(tip):
        return f"<span style='cursor:help;' title='{tip}'>❓</span>"

    # Section-Specific Tips (for tooltips)
    def tips_md(section, comp):
        tips = unified_coach.get_star_section_tips(section, comp)
        if tips:
            return '\n'.join([f"- {tip}" for tip in tips])
        return ''

    # Expander logic for STAR steps with icons, tooltips, and spacing
    s = t = a = r = ""
    with st.expander("🟢 S – Situation", expanded=True):
        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"Describe the context and background {help_icon(tips_md('situation', comp_choice))}", unsafe_allow_html=True)
        # Opt-in toggles for AI assists
        ai_assist_enabled = st.toggle("Enable AI Assists for Situation", value=True, key="toggle_ai_situation")
        if ai_assist_enabled:
            if st.button("AI Assist: Suggest Situation", key="ai_situation"):
                ai_s = gemini_generate_star_section('situation', comp_choice, q_text, {})
                st.session_state['situation'] = ai_s
        s = st.text_area(
            "",
            key='situation',
            placeholder="E.g. Our team was facing a tight deadline on a critical project..."
        )
        # Grammar & Style Checker for Situation
        grammar_feedback = ""
        if st.button("Check Grammar & Style", key="grammar_situation"):
            proofread_prompt = f"Proofread and suggest grammar/style improvements for this STAR Situation section. If there are errors or awkward phrasing, rewrite the text and explain the changes.\\n\\nText:\\n{s}"
            api_key = st.session_state['gemini_api_key']
            # Updated URL
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            # Updated payload
            data = {"contents": [{"parts": [{"text": proofread_prompt}]}]}
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                if response.ok:
                    result = response.json()
                    # Updated extraction
                    grammar_feedback = result['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    # Try to parse error for more details
                    try:
                        error_details = response.json()
                        grammar_feedback = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                    except json.JSONDecodeError:
                        grammar_feedback = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
            except Exception as e:
                grammar_feedback = f"[AI Error: {e}]"
        if grammar_feedback:
            st.markdown("<div style='background:#23272f;padding:12px 12px 8px 12px;border-radius:8px;margin-top:10px;'>", unsafe_allow_html=True)
            st.markdown(f"**Grammar & Style Suggestions:**\n\n{grammar_feedback}")
            st.markdown("</div>", unsafe_allow_html=True)
        # Tone Analysis for Situation
        tone_feedback = ""
        if st.button("Check Tone", key="tone_situation"):
            tone_prompt = f"Analyze the emotional and professional tone of this STAR Situation section. Is it confident, empathetic, assertive, etc.? Give a short summary and suggest improvements if needed.\\n\\nText:\\n{s}"
            api_key = st.session_state['gemini_api_key']
            # Updated URL
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            # Updated payload
            data = {"contents": [{"parts": [{"text": tone_prompt}]}]}
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                if response.ok:
                    result = response.json()
                    # Updated extraction
                    tone_feedback = result['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                     # Try to parse error for more details
                    try:
                        error_details = response.json()
                        tone_feedback = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                    except json.JSONDecodeError:
                        tone_feedback = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
            except Exception as e:
                tone_feedback = f"[AI Error: {e}]"
        if tone_feedback:
            st.markdown("<div style='background:#2a2e38;padding:10px 10px 6px 10px;border-radius:8px;margin-top:8px;'>", unsafe_allow_html=True)
            st.markdown(f"**Tone Analysis:**\n\n{tone_feedback}")
            st.markdown("</div>", unsafe_allow_html=True)
        # Dynamic Prompt Templates for Situation
        if st.button("Show Situation Templates", key="template_situation"):
            st.info("Example template: 'Describe a challenging situation you faced, including the context, key players, and stakes.'\n\nAnother: 'Set the scene by explaining the background, your role, and why the situation was important.'")
        # True semantic search for similar examples
        if st.button("Show Similar Situation Examples", key="examples_situation"):
            st.info("Finding the most semantically similar example from your saved stories...")
            # Gather all saved stories
            stories_path = Path("Stories")
            files = list(stories_path.glob("*.json"))
            best_score = -1
            best_example = None
            for f in files:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, list):
                    for story in data:
                        # Use Gemini to get a similarity score
                        sim_prompt = f"Compare the following two STAR Situation sections and return a similarity score from 0 (not similar) to 1 (identical).\\n\\nSection 1:\\n{s}\\n\\nSection 2:\\n{story.get('situation','')}\\n\\nScore only:"
                        api_key = st.session_state['gemini_api_key']
                        # Updated URL
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                        headers = {"Content-Type": "application/json"}
                        # Updated payload
                        data_gem = {"contents": [{"parts": [{"text": sim_prompt}]}]}
                        try:
                            response = requests.post(url, headers=headers, json=data_gem, timeout=30)
                            if response.ok:
                                result = response.json()
                                # Updated extraction
                                score_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
                                try:
                                    score = float(score_str)
                                except Exception:
                                    score = 0
                                if score > best_score:
                                    best_score = score
                                    best_example = story.get('situation','')
                        except Exception:
                            pass # Silently fail on similarity check error
            if best_example:
                st.markdown(f"**Most Similar Example:**\n{best_example}")
                if st.button("⭐ Save to Inspiration Library", key=f"save_example_situation"):
                    st.success("Saved! (Inspiration Library feature coming soon)")
            else:
                st.info("No similar examples found.")
    if s.strip():
        with st.expander("🟡 T – Task", expanded=True):
            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
            st.markdown(f"What was your responsibility or challenge? {help_icon(tips_md('task', comp_choice))}", unsafe_allow_html=True)
            # Opt-in toggles for AI assists
            ai_assist_enabled = st.toggle("Enable AI Assists for Task", value=True, key="toggle_ai_task")
            if ai_assist_enabled:
                if st.button("AI Assist: Suggest Task", key="ai_task"):
                    ai_t = gemini_generate_star_section('task', comp_choice, q_text, {'situation': s})
                    st.session_state['task'] = ai_t
            t = st.text_area(
                "",
                key='task',
                placeholder="E.g. I was responsible for coordinating the team and ensuring we met the deadline..."
            )
            # Grammar & Style Checker for Task
            grammar_feedback_t = ""
            if st.button("Check Grammar & Style", key="grammar_task"):
                proofread_prompt = f"Proofread and suggest grammar/style improvements for this STAR Task section. If there are errors or awkward phrasing, rewrite the text and explain the changes.\\n\\nText:\\n{t}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": proofread_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        grammar_feedback_t = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            grammar_feedback_t = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            grammar_feedback_t = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    grammar_feedback_t = f"[AI Error: {e}]"
            if grammar_feedback_t:
                st.markdown("<div style='background:#23272f;padding:12px 12px 8px 12px;border-radius:8px;margin-top:10px;'>", unsafe_allow_html=True)
                st.markdown(f"**Grammar & Style Suggestions:**\n\n{grammar_feedback_t}")
                st.markdown("</div>", unsafe_allow_html=True)
            # Tone Analysis for Task
            tone_feedback_t = ""
            if st.button("Check Tone", key="tone_task"):
                tone_prompt = f"Analyze the emotional and professional tone of this STAR Task section. Is it confident, empathetic, assertive, etc.? Give a short summary and suggest improvements if needed.\\n\\nText:\\n{t}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": tone_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        tone_feedback_t = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            tone_feedback_t = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            tone_feedback_t = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    tone_feedback_t = f"[AI Error: {e}]"
            if tone_feedback_t:
                st.markdown("<div style='background:#2a2e38;padding:10px 10px 6px 10px;border-radius:8px;margin-top:8px;'>", unsafe_allow_html=True)
                st.markdown(f"**Tone Analysis:**\n\n{tone_feedback_t}")
                st.markdown("</div>", unsafe_allow_html=True)
            # Dynamic Prompt Templates for Task
            if st.button("Show Task Templates", key="template_task"):
                st.info("Example template: 'State your main responsibility or the challenge you were given.'\n\nAnother: 'Describe what you needed to accomplish and why it mattered.'")
            # True semantic search for similar examples
            if st.button("Show Similar Task Examples", key="examples_task"):
                st.info("Finding the most semantically similar example from your saved stories...")
                # Gather all saved stories
                stories_path = Path("Stories")
                files = list(stories_path.glob("*.json"))
                best_score = -1
                best_example = None
                for f in files:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        for story in data:
                            # Use Gemini to get a similarity score
                            sim_prompt = f"Compare the following two STAR Task sections and return a similarity score from 0 (not similar) to 1 (identical).\\n\\nSection 1:\\n{t}\\n\\nSection 2:\\n{story.get('task','')}\\n\\nScore only:"
                            api_key = st.session_state['gemini_api_key']
                            # Updated URL
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                            headers = {"Content-Type": "application/json"}
                            # Updated payload
                            data_gem = {"contents": [{"parts": [{"text": sim_prompt}]}]}
                            try:
                                response = requests.post(url, headers=headers, json=data_gem, timeout=30)
                                if response.ok:
                                    result = response.json()
                                    # Updated extraction
                                    score_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
                                    try:
                                        score = float(score_str)
                                    except Exception:
                                        score = 0
                                    if score > best_score:
                                        best_score = score
                                        best_example = story.get('task','')
                            except Exception:
                                pass # Silently fail on similarity check error
                if best_example:
                    st.markdown(f"**Most Similar Example:**\n{best_example}")
                    if st.button("⭐ Save to Inspiration Library", key=f"save_example_task"):
                        st.success("Saved! (Inspiration Library feature coming soon)")
                else:
                    st.info("No similar examples found.")
    if t.strip():
        with st.expander("🔵 A – Action", expanded=True):
            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
            st.markdown(f"What actions did you take? {help_icon(tips_md('action', comp_choice))}", unsafe_allow_html=True)
            # Opt-in toggles for AI assists
            ai_assist_enabled = st.toggle("Enable AI Assists for Action", value=True, key="toggle_ai_action")
            if ai_assist_enabled:
                if st.button("AI Assist: Suggest Action", key="ai_action"):
                    ai_a = gemini_generate_star_section('action', comp_choice, q_text, {'situation': s, 'task': t})
                    st.session_state['action'] = ai_a
            a = st.text_area(
                "",
                key='action',
                placeholder="E.g. I organized daily stand-ups, delegated tasks, and communicated progress to stakeholders..."
            )
            # Grammar & Style Checker for Action
            grammar_feedback_a = ""
            if st.button("Check Grammar & Style", key="grammar_action"):
                proofread_prompt = f"Proofread and suggest grammar/style improvements for this STAR Action section. If there are errors or awkward phrasing, rewrite the text and explain the changes.\\n\\nText:\\n{a}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": proofread_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        grammar_feedback_a = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            grammar_feedback_a = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            grammar_feedback_a = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    grammar_feedback_a = f"[AI Error: {e}]"
            if grammar_feedback_a:
                st.markdown("<div style='background:#23272f;padding:12px 12px 8px 12px;border-radius:8px;margin-top:10px;'>", unsafe_allow_html=True)
                st.markdown(f"**Grammar & Style Suggestions:**\n\n{grammar_feedback_a}")
                st.markdown("</div>", unsafe_allow_html=True)
            # Tone Analysis for Action
            tone_feedback_a = ""
            if st.button("Check Tone", key="tone_action"):
                tone_prompt = f"Analyze the emotional and professional tone of this STAR Action section. Is it confident, empathetic, assertive, etc.? Give a short summary and suggest improvements if needed.\\n\\nText:\\n{a}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": tone_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        tone_feedback_a = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            tone_feedback_a = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            tone_feedback_a = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    tone_feedback_a = f"[AI Error: {e}]"
            if tone_feedback_a:
                st.markdown("<div style='background:#2a2e38;padding:10px 10px 6px 10px;border-radius:8px;margin-top:8px;'>", unsafe_allow_html=True)
                st.markdown(f"**Tone Analysis:**\n\n{tone_feedback_a}")
                st.markdown("</div>", unsafe_allow_html=True)
            # Dynamic Prompt Templates for Action
            if st.button("Show Action Templates", key="template_action"):
                st.info("Example template: 'Describe the specific steps you took to address the challenge.'\n\nAnother: 'Explain your thought process and how you involved others.'")
            # True semantic search for similar examples
            if st.button("Show Similar Action Examples", key="examples_action"):
                st.info("Finding the most semantically similar example from your saved stories...")
                # Gather all saved stories
                stories_path = Path("Stories")
                files = list(stories_path.glob("*.json"))
                best_score = -1
                best_example = None
                for f in files:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        for story in data:
                            # Use Gemini to get a similarity score
                            sim_prompt = f"Compare the following two STAR Action sections and return a similarity score from 0 (not similar) to 1 (identical).\\n\\nSection 1:\\n{a}\\n\\nSection 2:\\n{story.get('action','')}\\n\\nScore only:"
                            api_key = st.session_state['gemini_api_key']
                            # Updated URL
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                            headers = {"Content-Type": "application/json"}
                            # Updated payload
                            data_gem = {"contents": [{"parts": [{"text": sim_prompt}]}]}
                            try:
                                response = requests.post(url, headers=headers, json=data_gem, timeout=30)
                                if response.ok:
                                    result = response.json()
                                    # Updated extraction
                                    score_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
                                    try:
                                        score = float(score_str)
                                    except Exception:
                                        score = 0
                                    if score > best_score:
                                        best_score = score
                                        best_example = story.get('action','')
                            except Exception:
                                pass # Silently fail on similarity check error
                if best_example:
                    st.markdown(f"**Most Similar Example:**\n{best_example}")
                    if st.button("⭐ Save to Inspiration Library", key=f"save_example_action"):
                        st.success("Saved! (Inspiration Library feature coming soon)")
                else:
                    st.info("No similar examples found.")
    if a.strip():
        with st.expander("🟣 R – Result", expanded=True):
            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
            st.markdown(f"What was the outcome? {help_icon(tips_md('result', comp_choice))}", unsafe_allow_html=True)
            # Opt-in toggles for AI assists
            ai_assist_enabled = st.toggle("Enable AI Assists for Result", value=True, key="toggle_ai_result")
            if ai_assist_enabled:
                if st.button("AI Assist: Suggest Result", key="ai_result"):
                    ai_r = gemini_generate_star_section('result', comp_choice, q_text, {'situation': s, 'task': t, 'action': a})
                    st.session_state['result'] = ai_r
            r = st.text_area(
                "",
                key='result',
                placeholder="E.g. We delivered the project on time, resulting in a 20% increase in customer satisfaction..."
            )
            # Grammar & Style Checker for Result
            grammar_feedback_r = ""
            if st.button("Check Grammar & Style", key="grammar_result"):
                proofread_prompt = f"Proofread and suggest grammar/style improvements for this STAR Result section. If there are errors or awkward phrasing, rewrite the text and explain the changes.\\n\\nText:\\n{r}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": proofread_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        grammar_feedback_r = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            grammar_feedback_r = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            grammar_feedback_r = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    grammar_feedback_r = f"[AI Error: {e}]"
            if grammar_feedback_r:
                st.markdown("<div style='background:#23272f;padding:12px 12px 8px 12px;border-radius:8px;margin-top:10px;'>", unsafe_allow_html=True)
                st.markdown(f"**Grammar & Style Suggestions:**\n\n{grammar_feedback_r}")
                st.markdown("</div>", unsafe_allow_html=True)
            # Tone Analysis for Result
            tone_feedback_r = ""
            if st.button("Check Tone", key="tone_result"):
                tone_prompt = f"Analyze the emotional and professional tone of this STAR Result section. Is it confident, empathetic, assertive, etc.? Give a short summary and suggest improvements if needed.\\n\\nText:\\n{r}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": tone_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        tone_feedback_r = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            tone_feedback_r = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            tone_feedback_r = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    tone_feedback_r = f"[AI Error: {e}]"
            if tone_feedback_r:
                st.markdown("<div style='background:#2a2e38;padding:10px 10px 6px 10px;border-radius:8px;margin-top:8px;'>", unsafe_allow_html=True)
                st.markdown(f"**Tone Analysis:**\n\n{tone_feedback_r}")
                st.markdown("</div>", unsafe_allow_html=True)
            # Dynamic Prompt Templates for Result
            if st.button("Show Result Templates", key="template_result"):
                st.info("Example template: 'Describe the outcome, impact, and what you learned.'\n\nAnother: 'Quantify the results and explain how they benefited your team or organization.'")
            # True semantic search for similar examples
            if st.button("Show Similar Result Examples", key="examples_result"):
                st.info("Finding the most semantically similar example from your saved stories...")
                # Gather all saved stories
                stories_path = Path("Stories")
                files = list(stories_path.glob("*.json"))
                best_score = -1
                best_example = None
                for f in files:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        for story in data:
                            # Use Gemini to get a similarity score
                            sim_prompt = f"Compare the following two STAR Result sections and return a similarity score from 0 (not similar) to 1 (identical).\\n\\nSection 1:\\n{r}\\n\\nSection 2:\\n{story.get('result','')}\\n\\nScore only:"
                            api_key = st.session_state['gemini_api_key']
                            # Updated URL
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                            headers = {"Content-Type": "application/json"}
                            # Updated payload
                            data_gem = {"contents": [{"parts": [{"text": sim_prompt}]}]}
                            try:
                                response = requests.post(url, headers=headers, json=data_gem, timeout=30)
                                if response.ok:
                                    result = response.json()
                                    # Updated extraction
                                    score_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
                                    try:
                                        score = float(score_str)
                                    except Exception:
                                        score = 0
                                    if score > best_score:
                                        best_score = score
                                        best_example = story.get('result','')
                            except Exception:
                                pass # Silently fail on similarity check error
                if best_example:
                    st.markdown(f"**Most Similar Example:**\n{best_example}")
                    if st.button("⭐ Save to Inspiration Library", key=f"save_example_result"):
                        st.success("Saved! (Inspiration Library feature coming soon)")
                else:
                    st.info("No similar examples found.")

    star_progress(s, t, a, r)

with tabs[1]:  # Review & Score tab
    st.markdown("## Review & Score Your STAR Story")
    # Only show review if all fields are filled
    if all([s.strip(), t.strip(), a.strip(), r.strip()]):
        left, right = st.columns([2, 1], gap="large")
        with left:
            st.markdown("""
            <style>
            .star-preview-section { line-height: 1.7; margin-bottom: 18px; }
            .star-section-header { padding-bottom: 8px; }
            @media (max-width: 900px) {
                .element-container > div { flex-direction: column !important; }
            }
            </style>
            """, unsafe_allow_html=True)
            st.markdown("### STAR Story Preview")
            st.markdown(f"<div class='star-preview-section'><b>Competency:</b> <span style='color:#1976d2'>{comp_choice}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-preview-section'><b>Question:</b> <span style='color:#388e3c'>{st.session_state['q_text']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-preview-section'><span class='star-section-header'><b>Situation:</b></span><br>{s}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-preview-section'><span class='star-section-header'><b>Task:</b></span><br>{t}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-preview-section'><span class='star-section-header'><b>Action:</b></span><br>{a}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='star-preview-section'><span class='star-section-header'><b>Result:</b></span><br>{r}</div>", unsafe_allow_html=True)
        with right:
            st.markdown("### Score & Feedback")
            story = Story(competency=comp_choice, question=st.session_state['q_text'], situation=s, task=t, action=a, result=r)
            coach.story = story
            unified_coach.story = {
                'competency': comp_choice,
                'question': st.session_state['q_text'],
                'situation': s,
                'task': t,
                'action': a,
                'result': r
            }
            unified_coach.score_story()
            score = unified_coach.story.get('score','')
            emoji = "💪" if score == "Talented" else ("👍" if score == "Skilled" else ("⚠️" if score == "Unskilled" else "❗"))
            st.subheader(f"Score: {score} {emoji}")
            export_story = {
                'competency': comp_choice,
                'question': st.session_state['q_text'],
                'situation': s,
                'task': t,
                'action': a,
                'result': r
            }
            # Use role (if Apple Interview) or 'General' for filename
            role_str = selected_role if mode == "Apple Interview" else "General"
            fname_base = f"STAR_{slugify(role_str)}_{slugify(comp_choice)}"
            export_format = st.selectbox("Download format", ["JSON", "Text"])
            if st.button("Download STAR Story", key="download_top"):
                if export_format == "JSON":
                    json_str = json.dumps(export_story, indent=2, ensure_ascii=False)
                    st.download_button("Download STAR Story (JSON)", data=json_str, file_name=f"{fname_base}.json", mime="application/json", key="download_json_top")
                else:
                    text_str = f"Competency: {comp_choice}\nQuestion: {st.session_state['q_text']}\n\nSITUATION:\n{s}\n\nTASK:\n{t}\n\nACTION:\n{a}\n\nRESULT:\n{r}\n"
                    st.download_button("Download STAR Story (Text)", data=text_str, file_name=f"{fname_base}.txt", mime="text/plain", key="download_txt_top")
            st.markdown("---")
            st.markdown("#### AI Coach Feedback")
            st.markdown("<div style='background:#23272f;padding:16px 16px 8px 16px;border-radius:10px;margin-bottom:12px;'>", unsafe_allow_html=True)
            feedback_stream = io.StringIO()
            stdout_orig = sys.stdout
            sys.stdout = feedback_stream
            unified_coach.provide_feedback(score)
            sys.stdout = stdout_orig
            def strip_ansi_codes(text):
                import re
                ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
                return ansi_escape.sub('', text)
            feedback_clean = strip_ansi_codes(feedback_stream.getvalue())
            st.text(feedback_clean)
            st.markdown("</div>", unsafe_allow_html=True)
            # Show tips toggle
            show_tips = st.toggle("Show STAR Section Tips", value=False)
            if show_tips:
                for section in ['situation', 'task', 'action', 'result']:
                    tips = unified_coach.get_star_section_tips(section, comp_choice)
                    if tips:
                        st.markdown(f"**{section.capitalize()} Tips:**")
                        for tip in tips:
                            st.info(tip)
            # Repeat download at bottom
            if st.button("Download STAR Story", key="download_bottom"):
                if export_format == "JSON":
                    json_str = json.dumps(export_story, indent=2, ensure_ascii=False)
                    st.download_button("Download STAR Story (JSON)", data=json_str, file_name=f"{fname_base}.json", mime="application/json", key="download_json_bottom")
                else:
                    text_str = f"Competency: {comp_choice}\nQuestion: st.session_state['q_text']\n\nSITUATION:\n{s}\n\nTASK:\n{t}\n\nACTION:\n{a}\n\nRESULT:\n{r}\n"
                    st.download_button("Download STAR Story (Text)", data=text_str, file_name=f"{fname_base}.txt", mime="text/plain", key="download_txt_bottom")
            with st.expander("Advanced » Load/Save Stories"):
                save_path = Path("Stories")
                save_path.mkdir(exist_ok=True)
                if st.button("Save this story"):
                    story_dict = export_story.copy()
                    story_dict['timestamp'] = datetime.utcnow().isoformat()
                    fname = save_path / f"{slugify(q_text)}_{slugify(comp_choice)}.json"
                    if fname.exists():
                        with open(fname, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        if not isinstance(data, list):
                            data = [data]
                    else:
                        data = []
                    data.append(story_dict)
                    with open(fname, "w", encoding="utf-8") as fh:
                        json.dump(data, fh, indent=2, ensure_ascii=False)
                    # Add clickable link to open Stories folder
                    stories_path = os.path.abspath(str(save_path))
                    st.success(f"Story saved to <a href='file://{stories_path}' target='_blank'>{stories_path}</a>", icon="✅", unsafe_allow_html=True)
                files = list(save_path.glob("*.json"))
                if files:
                    file_names = [f.name for f in files]
                    selected_file = st.selectbox("Select a saved story file", file_names)
                    if st.button("Load selected story"):
                        with open(save_path / selected_file, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        if isinstance(data, list) and data:
                            loaded = data[-1]
                            st.info(f"Loaded story: {selected_file}")
                            st.write(loaded)
                else:
                    st.info("No saved stories found.")
    else:
        # Show checklist of missing STAR sections and a button to return to Build tab
        missing = []
        if not s.strip():
            missing.append("Situation")
        if not t.strip():
            missing.append("Task")
        if not a.strip():
            missing.append("Action")
        if not r.strip():
            missing.append("Result")
        st.warning("Cannot save or review an incomplete story. Please complete the following sections:")
        for part in missing:
            st.markdown(f"- [ ] **{part}**")
        if st.button("Go back to Build tab to complete your story"):
            st.experimental_set_query_params(tab="Build")
            st.info("Please fill in the missing sections in the Build tab.")

# Automated Feedback Reviewer in Review tab
with tabs[1]:
    # ...existing code...
    if all([s.strip(), t.strip(), a.strip(), r.strip()]):
        # ...existing code...
        with right:
            # ...existing code...
            if st.button("Get Automated Writing Review", key="ai_review"):
                review_prompt = f"Review this full STAR story for clarity, conciseness, and impact. Highlight areas for improvement and provide actionable suggestions.\\n\\nSituation:\\n{s}\\n\\nTask:\\n{t}\\n\\nAction:\\n{a}\\n\\nResult:\\n{r}"
                api_key = st.session_state['gemini_api_key']
                # Updated URL
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                # Updated payload
                data = {"contents": [{"parts": [{"text": review_prompt}]}]}
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    if response.ok:
                        result = response.json()
                        # Updated extraction
                        review_feedback = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    else:
                        # Try to parse error for more details
                        try:
                            error_details = response.json()
                            review_feedback = f"[AI Error: {response.status_code} {response.reason} - {error_details.get('error', {}).get('message', response.text)}]"
                        except json.JSONDecodeError:
                            review_feedback = f"[AI Error: {response.status_code} {response.reason}: {response.text}]"
                except Exception as e:
                    review_feedback = f"[AI Error: {e}]"
                st.markdown("<div style='background:#2a2e38;padding:12px 12px 8px 12px;border-radius:8px;margin-top:10px;'>", unsafe_allow_html=True)
                st.markdown(f"**Automated Writing Review:**\n\n{review_feedback}")
                st.markdown("</div>", unsafe_allow_html=True)

# Improved CSS for chat input: adapts to dark/light mode and fixes white color issues for all textareas
st.markdown('''
<style>
/* Chat input for both themes */
[data-testid="stChatInput"] textarea {
    min-height: 40px !important;
    max-height: 80px !important;
    border-radius: 10px !important;
    font-size: 1.08rem !important;
    padding: 10px 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: background 0.2s, color 0.2s;
}
/* Light mode for chat input and all textareas */
body:not(.dark) [data-testid="stChatInput"] textarea,
body:not(.dark) textarea {
    background: #fff !important;
    color: #222 !important;
    border: 1px solid #ccc !important;
}
body:not(.dark) [data-testid="stChatInput"] textarea::placeholder,
body:not(.dark) textarea::placeholder {
    color: #888 !important;
}
/* Dark mode for chat input and all textareas */
body.dark [data-testid="stChatInput"] textarea,
body.dark textarea {
    background: #23272f !important;
    color: #f5f5f7 !important;
    border: 1px solid #444 !important;
}
body.dark [data-testid="stChatInput"] textarea::placeholder,
body.dark textarea::placeholder {
    color: #aaa !important;
}
[data-testid="stChatInput"] {
    margin-bottom: 0.5rem !important;
}
</style>
''', unsafe_allow_html=True)

# Add subtle animation to theme toggle
st.markdown("""
<style>
[data-testid="stRadio"] label { transition: background 0.3s, color 0.3s; border-radius: 8px; }
[data-testid="stRadio"] label:hover { background: #e3f0ff; color: #0071e3; }
</style>
""", unsafe_allow_html=True)

# After export/save, show a toast
import streamlit.components.v1 as components

def show_toast(msg):
    components.html(f"""
    <script>
    function showToast() {{
      var x = document.getElementById('star-toast');
      x.className = 'show';
      setTimeout(function(){{ x.className = x.className.replace('show', ''); }}, 3000);
    }}
    window.onload = showToast;
    </script>
    <style>
    #star-toast {{
      visibility: visible;
      min-width: 250px;
      margin-left: -125px;
      background-color: #0071e3;
      color: #fff;
      text-align: center;
      border-radius: 8px;
      padding: 16px;
      position: fixed;
      z-index: 9999;
      left: 50%;
      bottom: 60px;
      font-size: 1.1em;
      opacity: 0.95;
    }}
    #star-toast.show {{ visibility: visible; opacity: 1; }}
    </style>
    <div id='star-toast'>{msg}</div>
    """, height=80)

# --- Run the app ---
# (The rest of your Streamlit app code goes here, including the sidebar, main content, etc.)