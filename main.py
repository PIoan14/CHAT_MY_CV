import streamlit as st
from streamlit_option_menu import option_menu
import pypdf
from server_calls import register_user, login_user, update_user, delete_user
import pandas as pd
from collections import Counter
import re
import altair as alt
from web_search import search_on_internet
import json
import pdfplumber
from server_calls import get_analytics
import shutil
import time

st.set_page_config(page_title="Proiect Pro", layout="wide", page_icon="🤗")

import secrets


query_params = st.query_params

if "session" not in query_params:
    new_token = secrets.token_hex(16)
    st.query_params["session"] = new_token
    token_activ = new_token
else:
    token_activ = query_params["session"]

from pathlib import Path

def create_session_file(path):
    path = Path(path)
    
    path.parent.mkdir(parents=True, exist_ok=True)
query_params = st.query_params


try :
    with open(f"{token_activ}/session_state.json", "r") as f:
        login_state = json.load(f)
    if login_state["status"] == "false":
        st.session_state.logged_in = False
    else:
        st.session_state.logged_in = True
        st.session_state.current_user = login_state["current_user"]
        st.session_state.current_user_name = login_state["current_user_name"]
        st.session_state.pdf_extracted_text = login_state["pdf_extracted_text"]
        st.session_state.txt_extracted_text = login_state["txt_extracted_text"]
        st.session_state.user_data = login_state["user_data"]
        
except:
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

import urllib.parse

if st.session_state.logged_in and st.session_state.current_user:
    username_safe = urllib.parse.quote(st.session_state.get('user_data', {}).get('name', st.session_state.current_user))
    chat_url = f"/chat?user={st.session_state.current_user}&username={username_safe}"
else:
    chat_url = "/"

# --- NAVBAR NEGRU (Top Navigation) ---
st.markdown(f"""
<style>
    .top-navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #000;
        color: white;
        padding: 15px 30px;
        z-index: 999999;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }}
    .top-navbar a {{
        color: white !important;
        text-decoration: none;
        font-weight: 600;
        font-family: inherit;
        margin-left: 20px;
        font-size: 16px;
        transition: color 0.2s ease;
    }}
    .top-navbar a:hover {{
        color: #ffd21e !important;
    }}
    /* Ascunde header-ul standard Streamlit pentru a nu suprapune navbar-ul */
    .stApp > header {{
        display: none !important;
    }}
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(180deg, #ffffff 0%, #f5f3ff 80%, #ede9fe 100%) !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid rgba(0,0,0,0.05);
    }}
    .stApp {{
        margin-top: 50px;
        background: transparent !important;
    }}
    
    /* Ridica continutul mai sus ca sa nu fie gap mare dupa Navbar */
    .block-container {{
        padding-top: 1.5rem !important;
    }}

    /* Ascunde lista implicita de pagini Streamlit din sidebar */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
</style>
<div class="top-navbar">
    <a href="/" target="_self">🏠 Home</a>
    <a href="{chat_url}" target="_self">💬 Chat</a>
</div>
""", unsafe_allow_html=True)


# Ascunde complet sidebar-ul la login
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAȚA DE LOGIN / REGISTER ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    
    with cols[1]:
        st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Chat My CV Login! ✨</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Authenticate yourself to access the platform 🔐</p>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                u = st.text_input("👤 Username")
                p = st.text_input("🔒 Password", type="password")
                submit = st.form_submit_button("Log In 🚀", use_container_width=True)
                if submit:
                    response = login_user(u, p)
                    if response.status_code == 200:
                     
                        st.session_state.current_user = response.json()["logged_in_id"]
                        st.session_state.current_user_name = response.json()["username"]
                        st.session_state.pdf_extracted_text = response.json()["CV_content"]

                        if st.session_state.pdf_extracted_text:
                            st.session_state.pdf_extracted_text = " ".join(line.strip() for line in st.session_state.pdf_extracted_text.splitlines() if line.strip())

                            phrases = st.session_state.pdf_extracted_text.split(". ")
                            phrases_text = st.session_state.pdf_extracted_text.split(". ")

                            final_pdf_show = ""

                            for phrase in phrases:

                                if not phrase.endswith("."):
                                    final_pdf_show += f"{phrase}.\n"
                                else:
                                    final_pdf_show += f"{phrase}\n"

                            st.session_state.pdf_extracted_text = final_pdf_show
                        
                        st.session_state.txt_extracted_text = response.json()["text_summary"]
                        st.session_state.logged_in = True
                        #if 'user_data' not in st.session_state:
                        st.session_state.user_data = {"user": "admin", "pass": "1234", "name": st.session_state.current_user_name}
                        if 'current_user' not in st.session_state:
                            st.session_state.current_user = ""

                        login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                        create_session_file(f"{token_activ}/session_state.json")
                        with open(f"{token_activ}/session_state.json", "w") as f:
                            json.dump(login_state, f, indent=4)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
        
        with tab2:
            
            with st.form("reg_form"):
                new_u = st.text_input("👤 New Username")
                new_p = st.text_input("🔒 New Password", type="password")
                reg_submit = st.form_submit_button("Register ✨", use_container_width=True)
                if reg_submit:
                    
                    if register_user(new_u, new_p) != 400:
                        st.success("✅ Registered! Check console.")
                        response = login_user(new_u, new_p)
                        if response.status_code == 200:

                            st.session_state.current_user = response.json()["logged_in_id"]
                            st.session_state.current_user_name = response.json()["username"]
                            st.session_state.pdf_extracted_text = response.json()["CV_content"]
                            st.session_state.txt_extracted_text = response.json()["text_summary"]
                            st.session_state.logged_in = True
                            st.session_state.user_data = {"user": "admin", "pass": "1234", "name": st.session_state.current_user_name}
                            if 'current_user' not in st.session_state:
                                st.session_state.current_user = ""

                            create_session_file(f"{token_activ}/session_state.json")
                            login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                            with open(f"{token_activ}/session_state.json", "w") as f:
                                json.dump(login_state, f, indent=4)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials!")
                    
else:
   
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown(f"### 👋 Hello, {st.session_state.user_data['name']}! 🌟")
        
        selected = option_menu(
            menu_title="Main Menu 🚀",
            options=["Home", "Analytics", "Global Search", "Settings"],
            icons=["house", "graph-up", "search", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#4f46e5"},
            }
        )
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            login_state = {"status": "false", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
            # with open(f"{token_activ}/session_state.json", "w") as f:
            #     json.dump(login_state, f, indent=4)
            shutil.rmtree(token_activ)
            st.rerun()

    if selected == "Home":

        css_stil_carduri = """
            <style>
                .bs-card {
                    background-color: var(--background-color);
                    border-radius: 8px;
                    border: 1px solid rgba(128, 128, 128, 0.2);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    padding: 1px;
                    padding-top: 300px;
                    margin-bottom: 20px;
                    color: var(--text-color);
                    font-family: Comic Sans MS, serif;
                }
            </style>
            """

        st.markdown(f"""
        <style>
            /* CSS PREMIUM PENTRU EXPANDERE (DROPDOWN-URI) STREAMLIT */
            [data-testid="stExpander"] {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%) !important;
                border-radius: 16px !important;
                border: 1px solid rgba(226, 232, 240, 0.8) !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02), 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
                overflow: hidden !important;
            }}
            [data-testid="stExpander"]:hover {{
                box-shadow: 0 12px 25px -5px rgba(15, 38, 92, 0.12) !important;
                border-color: rgba(79, 70, 229, 0.3) !important;
            }}
            [data-testid="stExpanderDetails"] {{
                padding: 20px !important;
            }}
            /* Header-ul (summary) expanderului */
            [data-testid="stExpander"] summary {{
                padding: 15px 20px !important;
                background-color: transparent !important; /* eliminam hover-ul gri default */
            }}
            [data-testid="stExpander"] summary p {{
                font-weight: 700 !important;
                color: #0f172a !important;
                font-size: 1.15rem !important;
            }}
            [data-testid="stExpander"] svg {{
                fill: #4f46e5 !important;
                stroke: #4f46e5 !important;
            }}

            /* --- Formatare Titlu --- */
            .welcome-title {{
                margin: 0;
                font-size: 1.8rem;
                font-weight: 800;
                color: #0f172a;
                background: linear-gradient(90deg, #0f265c, #4f46e5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: inline-block;
                letter-spacing: -0.5px;
            }}
            .system-pills {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-top: 15px;
                padding-top: 20px;
                border-top: 1px solid rgba(0,0,0,0.05);
            }}
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
                70% {{ box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
            }}
            @media (max-width: 768px) {{
                .welcome-title {{ font-size: 1.8rem; }}
            }}
        </style>
        
        <div style="margin: 10px 0 30px 0; padding: 0 5px;">
            <h3 style="font-family: Comic Sans MS, serif;" class="welcome-title">Welcome, {st.session_state.user_data['name']}!👋🎉</h3>
            <div style="font-family: Comic Sans MS, serif; display: flex; flex-direction: column; gap: 15px; margin: 15px 0;">
                <div style="font-size: 1rem; font-weight: 600; color: #1e293b; line-height: 1.4;">
                    <span style="background: linear-gradient(135deg, #4f46e5, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">✨ Transform your standard CV</span>
                    into a powerful AI interactive experience! 🚀
                </div>
                <div style="background: rgba(255, 255, 255, 0.3); border-left: 4px solid #4f46e5; border-radius: 12px; padding: 18px 25px; display: flex; flex-direction: column; gap: 12px; backdrop-filter: blur(5px);">
                    <div style="display: flex; align-items: flex-start; gap: 15px;">
                        <span style="font-size: 1.4rem; padding-top: 2px; line-height: 1;">📄</span>
                        <div style="font-family: Arial, sans-serif; font-size: 1rem; color: #334155; line-height: 1.5;"><strong>Upload your document:</strong> Highlight your best tech skills, projects, and experiences.</div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px;">
                        <span style="font-size: 1.4rem; padding-top: 2px; line-height: 1;">🚀</span>
                        <div style="font-family: Arial, sans-serif; font-size: 1rem; color: #334155; line-height: 1.5;"><strong>AI Engine Magic:</strong> Our intelligent engine crafts a highly personalized knowledge base instantly.</div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px;">
                        <span style="font-size: 1.4rem; padding-top: 2px; line-height: 1;">🔗</span>
                        <div style="font-family: Arial, sans-serif; font-size: 1rem; color: #334155; line-height: 1.5;"><strong>Share & Impress:</strong> Get your unique link so recruiters can chat directly with your virtual profile and discover why you're the perfect fit! 🎯</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("AI-Powered Interview Preparation", divider='rainbow')
        # CSS pentru cardurile rotative (inaltime redusa la jumatate)
        css_stil_carduri = """
        <style>
            .flip-card {
                background-color: transparent;
                width: 100%;
                height: 150px; /* Inaltime redusa considerabil */
                perspective: 1000px;
                cursor: pointer;
                margin-bottom: 25px;
                display: block;
            }
            .flip-card-inner {
                position: relative;
                width: 100%;
                height: 100%;
                text-align: center;
                transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
                transform-style: preserve-3d;
            }
            .flip-card input[type="checkbox"] {
                display: none;
            }
            .flip-card input[type="checkbox"]:checked ~ .flip-card-inner {
                transform: rotateY(180deg);
            }
            .flip-card-front, .flip-card-back {
                position: absolute;
                width: 100%;
                height: 100%;
                backface-visibility: hidden;
                border-radius: 16px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 10px 15px; /* Padding mai mic si optimizat */
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.08);
            }
            .flip-card-front {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(225, 210, 255, 0.95) 100%) !important;
                backdrop-filter: blur(8px);
                color: #0f265c;
            }
            .flip-card-front h3 {
                margin: 0;
                font-size: 1rem;
                font-weight: 600;
                font-family: Comic Sans MS, serif;
                line-height: 1.2;
            }
            .flip-card-front .icon {
                font-size: 1.8rem;
                margin-bottom: 8px;
            }
            .flip-card-front .flip-btn {
                margin-top: auto;
                border: 1px solid rgba(15, 38, 92, 0.25);
                background: rgba(15, 38, 92, 0.05);
                color: #0f265c;
                padding: 2px 10px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.7rem;
                transition: all 0.3s;
                display: inline-block;
            }
            .flip-card-back {
                background: linear-gradient(135deg, rgba(235, 245, 255, 0.95) 0%, rgba(175, 205, 255, 0.95) 100%);
                color: #222;
                transform: rotateY(180deg);
                backdrop-filter: blur(8px);
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 10px;
            }

            .flip-card-back p {
                font-size: 1rem;
                font-weight: 600;
                line-height: 1.5;
                margin: 0;
                text-align: center;
                width: 100%;
            }
            .flip-card:hover .flip-card-front .flip-btn {
                background: rgba(15, 38, 92, 0.15);
            }
        </style>
        """
        st.markdown(css_stil_carduri, unsafe_allow_html=True)
        
        card_1 = """
<label class="flip-card">
    <input type="checkbox">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="icon">📄</div>
            <h3>How to upload your CV</h3>
            <div class="flip-btn">Check</div>
        </div>
        <div class="flip-card-back">
            <p>Just scroll down and click on <b>"Upload your CV in PDF format. The same works for summary."</b></p>
        </div>
    </div>
</label>
"""
        
        card_2 = """
<label class="flip-card">
    <input type="checkbox">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="icon">⚙️</div>
            <h3>How it works</h3>
            <div class="flip-btn">Check</div>
        </div>
        <div class="flip-card-back">
            <p>Upload ➔ AI learns 🤖<br>➔ Get Link 🔗<br>➔ <b>Live Chat</b> 💬</p>
        </div>
    </div>
</label>
"""

        card_3 = """
<label class="flip-card">
    <input type="checkbox">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="icon">✨</div>
            <h3>How to edit CV content</h3>
            <div class="flip-btn">Check</div>
        </div>
        <div class="flip-card-back">
            <p>Edit your skills, projects, and experience in the <b>"Edit CV"</b> section at the bottom of the page. The same works for summary.</p>
        </div>
    </div>
</label>
"""

        card_4 = """
<label class="flip-card">
    <input type="checkbox">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="icon">❗</div>
            <h3>Prerequisites</h3>
            <div class="flip-btn">Check</div>
        </div>
        <div class="flip-card-back">
            <p>Both CV and Summary have to be uploaded so that the Chat can answer questions!</p>
        </div>
    </div>
</label>
"""
        
        # Randarea pe 4 coloane in aceeasi linie sub titlu
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            if hasattr(st, "html"):
                st.html(card_1)
            else:
                st.markdown(card_1, unsafe_allow_html=True)
        with c2:
            if hasattr(st, "html"):
                st.html(card_2)
            else:
                st.markdown(card_2, unsafe_allow_html=True)
        with c3:
            if hasattr(st, "html"):
                st.html(card_3)
            else:
                st.markdown(card_3, unsafe_allow_html=True)
        with c4:
            if hasattr(st, "html"):
                st.html(card_4)
            else:
                st.markdown(card_4, unsafe_allow_html=True)
            
        # Sectiunea de Chat URL plasata exact sub randul de carduri
        st.divider()
        with st.expander("🔗 Check your CV Chat url", expanded=False):
            st.code("https://chatmycv-production.up.railway.app"+f"{chat_url}")
            
    

        # Histograme bazate pe "phrases" și "phrases_text" (lungime în cuvinte)
        st.markdown("""
        <style>
            /* Aplicăm stilul luminos tip "Search Findings" pe toate containerele native cu border (de exemplu cardurile cu histograme). */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 248, 255, 0.95) 100%) !important;
                backdrop-filter: blur(8px) !important;
                border-radius: 16px !important;
                padding: 20px 25px !important;
                box-shadow: 0 6px 12px rgba(0,0,0,0.1) !important;
                border: 1px solid rgba(255,255,255,0.8) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 10px 20px rgba(0,0,0,0.15) !important;
            }
            /* Culoare albastru închis pentru a asigura lizibilitatea textului din Streamlit chiar și cu sistemul pe Dark Mode */
            div[data-testid="stVerticalBlockBorderWrapper"] p,
            div[data-testid="stVerticalBlockBorderWrapper"] h1,
            div[data-testid="stVerticalBlockBorderWrapper"] h2,
            div[data-testid="stVerticalBlockBorderWrapper"] h3,
            div[data-testid="stVerticalBlockBorderWrapper"] h4,
            div[data-testid="stVerticalBlockBorderWrapper"] span {
                color: #0f265c !important;
            }
        </style>
        """, unsafe_allow_html=True)
        col_hist1, spacer, col_hist2 = st.columns([10, 1, 10]) # Am adăugat spațiu între ele
       
        st.markdown(f"""
        <style>
        .premium-interactive-banner {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(225, 210, 255, 0.95) 100%) !important;
            backdrop-filter: blur(8px);
            border-radius: 16px;
            padding: 20px 30px;
            margin-top: 15px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.8);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }}
        .premium-interactive-banner:hover {{
            transform: translateY(-4px) scale(1.01);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }}
        /* Efect de lumina care se plimba subtil pe fundal */
        .premium-interactive-banner::after {{
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(225, 210, 255, 0.95) 100%) !important;
            transform: skewX(-25deg);
            animation: shine 6s infinite;
        }}
        @keyframes shine {{
            0% {{ left: -100%; }}
            20% {{ left: 200%; }}
            100% {{ left: 200%; }}
        }}
        .banner-text h2 {{
            margin: 0 0 5px 0;
            font-size: 1.4rem;
            font-weight: 700;
            color: #0c1e4a !important;
            display: flex;
            align-items: center;
        }}
        .banner-text p {{
            margin: 0;
            font-size: 0.95rem;
            color: #334155 !important;
        }}
        .banner-action {{
            background: rgba(15, 38, 92, 0.08);
            border-radius: 50px;
            padding: 10px 25px;
            font-weight: 600;
            border: 1px solid rgba(15, 38, 92, 0.35);
            transition: all 0.3s ease;
            color: #0c1e4a;
            text-align: center;
            z-index: 2;
        }}
        .premium-interactive-banner:hover .banner-action {{
            background: rgba(15, 38, 92, 0.18);
            transform: scale(1.05);
        }}
        .pulse-dot {{
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse-animation 2s infinite;
            margin-right: 12px;
        }}
        @keyframes pulse-animation {{
            0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}
        @media (max-width: 768px) {{
            .premium-interactive-banner {{ flex-direction: column; text-align: center; gap: 15px; }}
        }}
        </style>
        
        <a href="{chat_url}" target="_self" style="text-decoration: none;">
            <div class="premium-interactive-banner">
                <div class="banner-text" style="z-index: 2;">
                    <h2><span class="pulse-dot"></span> AI Engine Online & Ready</h2>
                    <p>When your CV is synced, the intelligent assistant is ready for interviews.</p>
                </div>
                <div class="banner-action">
                    Test Live Chat ⚡
                </div>
            </div>
        </a>
        """, unsafe_allow_html=True)
        #st.divider()
        st.subheader("📂 Documents area", divider='rainbow')
    
        st.markdown("""
        <!-- Blob-uri decorative invizibile structural, dar care dau un gradient fain spatiului gol din jumatatea inferioara -->
        <div style="position: relative; width: 100%; height: 0; pointer-events: none; z-index: -1;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; max-width: 100vw; height: 1200px; overflow: hidden; pointer-events: none;">
                <div style="position: absolute; width: 500px; height: 500px; background: radial-gradient(circle, rgba(79, 70, 229, 0.05) 0%, transparent 60%); top: 50px; left: -150px; border-radius: 50%;"></div>
                <div style="position: absolute; width: 600px; height: 600px; background: radial-gradient(circle, rgba(236, 72, 153, 0.04) 0%, transparent 60%); top: 150px; right: -200px; border-radius: 50%;"></div>
            </div>
        </div>
        
        <div style="margin-top: 40px; margin-bottom: 25px;">
            <span style="background: rgba(79, 70, 229, 0.1); color: #4f46e5; padding: 8px 25px; border-radius: 30px; font-size: 1.15rem; font-weight: 800; display: inline-flex; align-items: center; gap: 10px; border: 1px solid rgba(79, 70, 229, 0.2); box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
                <span style="font-size: 1.4rem;">📂</span> Upload your documents to sync with the AI assistant
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.info("💡 Tip: After each upload wait until the bike animation from the top of the page stops.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            #st.divider()
            #st.subheader("📄 PDF Text Extractor 🚀")

            with st.expander("📄 Upload your CV here (PDF) 🚀", expanded=False):
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(226, 232, 240, 0.6) 100%); border-left: 4px solid #4f46e5; border-radius: 8px; padding: 15px 20px; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #1e293b; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; font-family: Arahoni, serif;">
                        <span style="font-size: 1.4rem;">📑</span> Automated PDF Processing
                    </h3>
                    <p style="margin: 5px 0 0 0; color: #475569; font-size: 0.95rem; line-height: 1.5; font-family: Comic Sans MS, serif;">
                        Upload your resume in PDF format. The extraction engine will intelligently process the text and generate the AI knowledge base.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                uploaded_file = st.file_uploader("📂 Upload a PDF", type="pdf", label_visibility="collapsed")
                
                if st.button("✅ Submit PDF & Print to Console"):
                        if uploaded_file:
                            try:
                                print(uploaded_file)
                                reader = pypdf.PdfReader(uploaded_file)
                                full_text = ""
                                for page in reader.pages:
                                    
                                    full_text += page.extract_text()
                                    print(full_text)
                            
                                st.info("ℹ️ Loading...")
                        
                                st.session_state.pdf_extracted_text = full_text

                                st.session_state.pdf_extracted_text = " ".join(line.strip() for line in st.session_state.pdf_extracted_text.splitlines() if line.strip())

                                phrases = st.session_state.pdf_extracted_text.split(". ")

                                final_pdf_show = ""

                                for phrase in phrases:

                                    if not phrase.endswith("."):
                                        final_pdf_show += f"{phrase}.\n"
                                    else:
                                        final_pdf_show += f"{phrase}\n"

                                st.session_state.pdf_extracted_text = final_pdf_show

                                update_user(st.session_state.current_user, "CV_content", st.session_state.pdf_extracted_text)

                                login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                                with open(f"{token_activ}/session_state.json", "w") as f:
                                    json.dump(login_state, f, indent=4)
                                
                                st.success("✅ PDF text submitted to console!")
                                time.sleep(2)
                                st.rerun()


                            except Exception as e:

                                st.error(f"❌ Try with with pdfplumber")

                                try:
                                    with pdfplumber.open(uploaded_file) as pdf:
                                        full_text = ""
                                        for page in pdf.pages:
                                            full_text += page.extract_text()
                                            print(full_text)
                                        
                                        st.info("ℹ️ Loading...")

                                    st.session_state.pdf_extracted_text = full_text

                                    st.session_state.pdf_extracted_text = " ".join(line.strip() for line in st.session_state.pdf_extracted_text.splitlines() if line.strip())

                                    phrases = st.session_state.pdf_extracted_text.split(". ")

                                    final_pdf_show = ""

                                    for phrase in phrases:

                                        if not phrase.endswith("."):
                                            final_pdf_show += f"{phrase}.\n"
                                        else:
                                            final_pdf_show += f"{phrase}\n"

                                    st.session_state.pdf_extracted_text = final_pdf_show

                                    update_user(st.session_state.current_user, "CV_content", st.session_state.pdf_extracted_text)

                                    login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                                    with open(f"{token_activ}/session_state.json", "w") as f:
                                        json.dump(login_state, f, indent=4)
                                    
                                    st.success("✅ PDF text submitted to console!")
                                    time.sleep(2)
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"❌ error: {e}")
                        else:
                            st.warning("⚠️ Please upload a PDF file before pressing the button!")

        with col2:
            #st.divider()

            with st.expander("📝 Upload your summary here (markdown file) 🚀", expanded=False):
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(226, 232, 240, 0.6) 100%); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 15px 20px; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #1e293b; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; font-family: Arahoni, serif;">
                        <span style="font-size: 1.4rem;">⌨️</span> Simple Text Extraction
                    </h3>
                    <p style="margin: 5px 0 0 0; color: #475569; font-size: 0.95rem; line-height: 1.5; font-family: Comic Sans MS, serif;">
                        Support for raw Text (TXT) or Markdown (MD) files. Perfect for providing the AI with unstructured extra details about your experience.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                uploaded_txt_file = st.file_uploader("📂 Upload a markdown/text file", type=["md", "txt"], label_visibility="collapsed")
                    
                if st.button("✅ Submit File & Print"):
                    if uploaded_txt_file:
                        try:
                            txt_full_text = uploaded_txt_file.getvalue().decode("utf-8")
                            st.info("ℹ️ Loading...")
                            update_user(st.session_state.current_user, "text_summary", txt_full_text)
                                  
                            st.session_state.txt_extracted_text = txt_full_text

                            login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                            with open(f"{token_activ}/session_state.json", "w") as f:
                                json.dump(login_state, f, indent=4)
                            
                            st.success("✅ The summary has been submitted to the console!")
                            time.sleep(2)
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error Updating file: {e}")
                        else:
                            st.warning("⚠️ Te rog să încarci un fișier înainte de a apăsa butonul!")
        st.write("<hr style='border: 1px dashed #f59e0b;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top: 50px; margin-bottom: 15px;">
            <span style="background: rgba(245, 158, 11, 0.1); color: #d97706; padding: 8px 25px; border-radius: 30px; font-size: 1.15rem; font-weight: 800; display: inline-flex; align-items: center; gap: 10px; border: 1px solid rgba(245, 158, 11, 0.2); box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
                <span style="font-size: 1.4rem;">✏️</span> Adjust and check the extracted text automatically
            </span>
        </div>
        <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #f59e0b; padding: 14px 20px; border-radius: 8px; color: #b45309; margin-bottom: 30px; font-weight: 500; font-size: 0.95rem; display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <span style="font-size: 1.3rem;">💡</span> <span style="line-height:1.5;"><strong>Note:</strong> At the first upload of new documents, the extraction will be successful. If you don't see the extracted text immediately, you need to give a short <strong>Refresh to the page</strong>!</span>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("✏️ Edit CV content:", expanded=False):
            st.markdown("""
            <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed rgba(0,0,0,0.1);">
                <h4 style="margin: 0; color: #0f172a; font-size: 1.1rem; font-weight: 700; font-family: Arahoni, serif;">Quick Edit Console (PDF)</h4>
                <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.9rem; font-family: Comic Sans MS, serif;">Format the raw text extracted from the PDF. Any adjustment you save here will be instantly synced with the AI.</p>
            </div>
            """, unsafe_allow_html=True)
            pdf_edited_text = st.text_area("Editable Text Field", value=st.session_state.pdf_extracted_text, height=400, key="pdf_editor", label_visibility="collapsed")
            if st.button("💾 Change PDF Content"):

                st.info("ℹ️ Loading...")
                st.session_state.pdf_extracted_text = pdf_edited_text
                update_user(st.session_state.current_user, "CV_content", pdf_edited_text)

                login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                with open(f"{token_activ}/session_state.json", "w") as f:
                    json.dump(login_state, f, indent=4)
                st.success("✅ PDF content was updated!")
                time.sleep(2)
                st.rerun()

        #st.divider()
        with st.expander("✏️ Edit Summary:", expanded=False):
            st.markdown("""
            <div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed rgba(0,0,0,0.1);">
                <h4 style="margin: 0; color: #0f172a; font-size: 1.1rem; font-weight: 700; font-family: Arahoni, serif;">Quick Edit Console (TXT/MD)</h4>
                <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.9rem; font-family: Comic Sans MS, serif;">Directly edit the auxiliary data. Modifications made here directly influence the chatbot's knowledge pool.</p>
            </div>
            """, unsafe_allow_html=True)
            txt_edited_text = st.text_area("Editable Text Field", value=st.session_state.txt_extracted_text, height=400, key="txt_editor", label_visibility="collapsed")
            if st.button("💾 Change TXT Content"):

                st.info("ℹ️ Loading...")
                st.session_state.txt_extracted_text = txt_edited_text
                update_user(st.session_state.current_user, "text_summary", txt_edited_text)

                login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                with open(f"{token_activ}/session_state.json", "w") as f:
                    json.dump(login_state, f, indent=4)
                st.success("✅ TXT/MD content was updated!")
                time.sleep(2)
                st.rerun()

        st.divider()
        
        # --- FOOTER PROFESIONAL ---
        st.markdown("""
        <div style="text-align: center; margin-top: 60px; padding-top: 30px; margin-bottom: 20px; border-top: 1px solid rgba(0,0,0,0.05); color: #94a3b8; font-size: 0.85rem; display: flex; flex-direction: column; gap: 8px;">
            <div style="font-weight: 700; color: #64748b; font-size: 1.1rem; letter-spacing: 0.5px;">PROIECT PRO <span style="color: #4f46e5;">AI</span></div>
            <div>Made with ❤️ by PIOAN 14</div>
            <div style="font-size: 0.75rem; opacity: 0.7;">Transforming Resumes into Conversations • © 2026 All rights reserved</div>
        </div>
        """, unsafe_allow_html=True)
        
    elif selected == "Analytics":
        st.markdown("<h1 style='font-family: Comic Sans MS, serif; color: #0f172a; margin-top: 10px; margin-bottom: 0px;'>📈📊 Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 1.1rem; font-family: Comic Sans MS, serif; margin-bottom: 20px;'>Monitor insights and engagement based on live interactions with your AI resume. 🚀</p>", unsafe_allow_html=True)
        st.divider()
        
        analytics = get_analytics(st.session_state.current_user)
        try:
            to_use = json.loads(analytics)
        

            try:    
                category_data = {k:v for k,v in to_use.items() if k != 'summary'}
            
                
                on_topic = 0
                of_topic = 0
                df_chart_data = []

                for k, v in category_data.items():
                    # Handle the case where the API dict value returns numeric or dict
                    current_val = v.get('count', 0) if isinstance(v, dict) else v
                    if "off topic" in str(k).lower() or "off_topic" in str(k).lower():
                        of_topic = current_val
                    else:
                        on_topic += current_val
                    
                    df_chart_data.append({"Category": str(k).replace("_", " ").title(), "Value": current_val})
                
                total_questions = on_topic + of_topic
                on_topic_rate = round(on_topic / total_questions * 100, 1) if total_questions > 0 else 0
            except:
                st.rerun()
            # --- Premium Box for Summary ---
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-radius: 16px; padding: 25px 30px; border-left: 6px solid #4f46e5; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); margin-bottom: 40px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 1.8rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">🤖</span>
                    <h3 style="margin: 0; color: #1e3a8a; font-size: 1.4rem; font-family: Arahoni, serif; font-weight: 800;">LLM hints based on the questions related to your CV</h3>
                </div>
                <p style="margin: 0; color: #334155; font-size: 1.1rem; line-height: 1.6; font-family: Comic Sans MS, serif;">
                    {to_use.get('summary', 'Nu există suficiente date în sumar momentan.')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- Custom HTML Metric Cards ---
            st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 40px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 220px; background: #ffffff; border: 1px solid rgba(0,0,0,0.05); border-radius: 16px; padding: 25px 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(to right, #6366f1, #3b82f6);"></div>
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">❓</div>
                    <div style="color: #64748b; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; font-family: -apple-system, sans-serif;">Total Questions identified as relevant</div>
                    <div style="color: #0f172a; font-size: 2.6rem; font-weight: 800; font-family: Arahoni, serif; margin-top: 5px;">{total_questions}</div>
                </div>
                <div style="flex: 1; min-width: 220px; background: #ffffff; border: 1px solid rgba(0,0,0,0.05); border-radius: 16px; padding: 25px 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(to right, #f43f5e, #fda4af);"></div>
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">👀</div>
                    <div style="color: #64748b; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; font-family: -apple-system, sans-serif;">Off Topic Questions</div>
                    <div style="color: #0f172a; font-size: 2.6rem; font-weight: 800; font-family: Arahoni, serif; margin-top: 5px;">{of_topic}</div>
                </div>
                <div style="flex: 1; min-width: 220px; background: #ffffff; border: 1px solid rgba(0,0,0,0.05); border-radius: 16px; padding: 25px 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(to right, #10b981, #34d399);"></div>
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">✅</div>
                    <div style="color: #64748b; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; font-family: -apple-system, sans-serif;">On Topic Rate</div>
                    <div style="color: #0f172a; font-size: 2.6rem; font-weight: 800; font-family: Arahoni, serif; margin-top: 5px;">{on_topic_rate}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
                
            col_pie, col_hist = st.columns(2)
            
            with col_pie:
                st.markdown("<h4 style='font-family: Arahoni, serif; color: #1e293b; margin-bottom: 15px;'>📊 Category Distribution</h4>", unsafe_allow_html=True)
                df_pie = pd.DataFrame(df_chart_data)
                
                # Pie chart Altair elegant
                pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=60, cornerRadius=3).encode(
                    theta=alt.Theta(field="Value", type="quantitative"),
                    color=alt.Color(field="Category", type="nominal", scale=alt.Scale(scheme='category20')),
                    tooltip=["Category", "Value"]
                ).properties(
                    height=400
                ).configure_view(strokeWidth=0)
                
                with st.container(border=True):
                    st.altair_chart(pie_chart, use_container_width=True, theme="streamlit")
                    
            with col_hist:
                st.markdown("<h4 style='font-family: Arahoni, serif; color: #1e293b; margin-bottom: 15px;'>📈 On/Off Topic count</h4>", unsafe_allow_html=True)
                df_hist = pd.DataFrame([
                    {"Status": "Related to Expertise", "Total": on_topic},
                    {"Status": "Off Topic", "Total": of_topic}
                ])
                
                bar_chart = alt.Chart(df_hist).mark_bar(size=70, cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
                    x=alt.X('Status', sort=None, title=''),
                    y=alt.Y('Total', title='Number of Questions', axis=alt.Axis(grid=False)),
                    color=alt.Color('Status', scale=alt.Scale(range = ["#22c55e", "#f97316"]), legend=None),
                    tooltip=['Status', 'Total']
                ).properties(
                    height=400
                ).configure_view(strokeWidth=0)
                
                with st.container(border=True):
                    st.altair_chart(bar_chart, use_container_width=True, theme="streamlit")
            
            st.divider()
            col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
        
            with col_r2:
                st.markdown("<div style='min-height: 10px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 REFRESH DATA", type="primary", use_container_width=True):
                    st.rerun()
        except Exception as e:
            #st.markdown(f"<p style='font-family: Comic Sans MS, serif; color: #0f172a; margin-top: 10px; margin-bottom: 0px;'>{analytics}</p>", unsafe_allow_html=True)
            st.info(analytics)
            print(e)

    elif selected == "Global Search":
        st.markdown("<h1 style='font-family: Comic Sans MS, serif; color: #0f172a; margin-top: 10px; margin-bottom: 0px;'>🕵️‍♂️🔍 Global Web Search</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 1.1rem; font-family: Comic Sans MS, serif; margin-bottom: 20px;'>Instantly search your queries across the web and aggregate contextual data. ⚡</p>", unsafe_allow_html=True)
        st.divider()
        
        query = st.text_input("🔎 Search Term...", placeholder="e.g. Latest Generative AI trends 2026")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(226, 232, 240, 0.6) 100%); border-left: 4px solid #14b8a6; border-radius: 8px; padding: 12px 18px; margin-top: 5px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.3rem;">💡</span>
            <span style="color: #334155; font-size: 0.95rem; font-family: Comic Sans MS, serif; font-weight: 500;"><strong>Pro Tip:</strong> You can use exact phrases by wrapping your query in quotes for better precision.</span>
        </div>
        """, unsafe_allow_html=True)

        if query:
            with st.spinner("Searching the web for information... 🌐"):
                try:
                    query_results = search_on_internet(query)
                except Exception as e:
                    query_results = []
                    st.error(f"Error executing search query: {e}")
                
            if query_results:
                #st.success(f"✅ Am găsit {len(query_results)} rezultate relevante pentru căutarea ta:")
                
                # CSS personalizat pentru cardurile de tip "Home", dar statice și luminoase
                st.markdown("""
                <style>
                    .search-finding-card {
                        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 248, 255, 0.95) 100%);
                        backdrop-filter: blur(8px);
                        border-radius: 16px;
                        padding: 20px 25px;
                        margin-top: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
                        border: 1px solid rgba(255,255,255,0.8);
                        transition: transform 0.2s ease, box-shadow 0.2s ease;
                        display: block;
                        width: 100%;
                    }
                    .search-finding-card:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
                    }
                    .search-finding-card h4 {
                        margin-top: 0;
                        margin-bottom: 8px;
                        font-weight: 600;
                        font-family: inherit;
                    }
                    .search-finding-card a {
                        color: #0f265c !important; /* Culoarea dark blue de la Home */
                        text-decoration: none;
                        font-size: 1.15rem;
                    }
                    .search-finding-card a:hover {
                        text-decoration: underline;
                    }
                    .search-finding-card .url-text {
                        color: #10b981;
                        font-size: 0.85rem;
                        margin-bottom: 12px;
                        font-weight: 500;
                    }
                    .search-finding-card .content-text {
                        color: #475569;
                        font-size: 0.95rem;
                        line-height: 1.6;
                        font-weight: 400;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                for finding in query_results:
                    title = finding.get('title', 'Fără Titlu')
                    url = finding.get('url', '#')
                    content = finding.get('content', '')
                    
                    # Curățăm textul
                    clean_content = str(content).replace("\\n", " ").replace("  ", " ").strip()
                    
                    # Randăm un card personalizat 1 la 1 cu stilul din Home
                    card_html = f'''
                    <div class="search-finding-card">
                        <h4><a href="{url}" target="_blank">{title}</a></h4>
                        <div class="url-text">{url}</div>
                        <div class="content-text">{clean_content}</div>
                    </div>
                    '''
                    st.markdown(card_html, unsafe_allow_html=True)
                st.success(f"✅ Found {len(query_results)} relevant results for your search:")
            else:
                st.warning("⚠️ No results found. Try using different keywords.")
            



    elif selected == "Settings":
        st.markdown("<h1 style='font-family: Comic Sans MS, serif; color: #0f172a; margin-top: 10px; margin-bottom: 0px;'>⚙️ Settings & Security</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 1.1rem; font-family: Comic Sans MS, serif; margin-bottom: 20px;'>Manage your account credentials and critical platform configurations. 🛡️</p>", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(226, 232, 240, 0.6) 100%); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 15px 20px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #1e293b; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; font-family: Arahoni, serif;">
                <span style="font-size: 1.4rem;">👤</span> Update Profile Details
            </h3>
            <p style="margin: 5px 0 0 0; color: #475569; font-size: 0.95rem; line-height: 1.5; font-family: Comic Sans MS, serif;">
                Modify your username. These changes will reflect immediately upon saving.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("change_username_form", border=True):
            current_username = st.session_state.user_data['name']
            
            new_username = st.text_input("👤 New Username", value=current_username)
            
            submit_creds = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if submit_creds:
                if new_username != "":
                    update_user(st.session_state.current_user, "username", new_username)
                    
                    st.session_state.user_data['name'] = new_username
                    login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                    #create_session_file(f"{token_activ}/session_state.json")
                    with open(f"{token_activ}/session_state.json", "w") as f:
                        json.dump(login_state, f, indent=4)
                    st.success("✅ Username was successfully updated!")
            
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(226, 232, 240, 0.6) 100%); border-left: 4px solid #8b5cf6; border-radius: 8px; padding: 15px 20px; margin-top: 30px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #1e293b; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; font-family: Arahoni, serif;">
                <span style="font-size: 1.4rem;">🔒</span> Security & Password
            </h3>
            <p style="margin: 5px 0 0 0; color: #475569; font-size: 0.95rem; line-height: 1.5; font-family: Comic Sans MS, serif;">
                Update your authentication password to keep your account safe.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("change_password_form", border=True):
            new_password = st.text_input("🔑 New Password", type="password", placeholder="Enter your new password...")

            confirm_password = st.text_input("🔄 Confirm New Password", type="password", placeholder="Repeat password...")
            
            submit_creds = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            if submit_creds:
                if new_password != confirm_password:
                    st.error("❌ Passwords do not match! Please try again.")
                else:
                    if new_password != "":
                        update_user(st.session_state.current_user, "password", new_password)
                        st.session_state.user_data['pass'] = new_password
                        login_state = {"status": "true", "current_user": st.session_state.current_user, "current_user_name": st.session_state.current_user_name, "pdf_extracted_text": st.session_state.pdf_extracted_text, "txt_extracted_text": st.session_state.txt_extracted_text, "user_data": st.session_state.user_data}
                        #create_session_file(f"{token_activ}/session_state.json")
                        with open(f"{token_activ}/session_state.json", "w") as f:
                            json.dump(login_state, f, indent=4)
                    st.success("✅ Credentials were updated successfully!")
                    
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(254, 242, 242, 0.8) 0%, rgba(254, 226, 226, 0.6) 100%); border-left: 4px solid #ef4444; border-radius: 8px; padding: 15px 20px; margin-top: 40px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #7f1d1d; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; font-family: Arahoni, serif;">
                <span style="font-size: 1.4rem;">🔥</span> Danger Zone
            </h3>
            <p style="margin: 5px 0 0 0; color: #991b1b; font-size: 0.95rem; line-height: 1.5; font-family: Comic Sans MS, serif;">
                Permanently delete your account and all associated data. This action cannot be reversed.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Variabilă de sesiune pentru a reține intenția de ștergere
        if 'delete_user_intent' not in st.session_state:
            st.session_state.delete_user_intent = False

        if not st.session_state.delete_user_intent:
            if st.button("🚨 Delete User Account", type="primary"):
                st.session_state.delete_user_intent = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure? Type 'delete' in the box below to confirm your decision.")
            delete_input = st.text_input("Confirm deletion:", key="delete_user_input")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✔️ Confirm & Delete"):
                    if delete_input.strip() == "delete":

                        delete_user(st.session_state.current_user)
                        st.session_state.logged_in = False
                        shutil.rmtree(token_activ)
                        st.rerun()
                    else:
                        st.error("❌ You must type the word 'delete' to confirm.")
            with c2:
                if st.button("❌ Cancel"):
                    st.session_state.delete_user_intent = False
                    st.rerun()