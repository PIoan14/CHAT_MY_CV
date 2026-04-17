import streamlit as st
from streamlit_option_menu import option_menu
import pypdf
from server_calls import register_user, login_user, update_user, delete_user
import markdown
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from collections import Counter
import re
import streamlit as st
import re
from collections import Counter
import altair as alt
from web_search import search_on_internet



st.set_page_config(page_title="Proiect Pro", layout="wide", page_icon="🤗")

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
    .stApp {{
        margin-top: 50px;
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
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🤗 Welcome Back! ✨</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Autentifică-te pentru a accesa platforma 🔐</p>", unsafe_allow_html=True)
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
                        st.rerun()
                    else:
                        st.error("❌ Credentiale incorecte!")
        
        with tab2:
            with st.form("reg_form"):
                new_u = st.text_input("👤 New Username")
                new_p = st.text_input("🔒 New Password", type="password")
                reg_submit = st.form_submit_button("Register ✨", use_container_width=True)
                if reg_submit:
                    
                    if register_user(new_u, new_p) != 400:
                        st.success("✅ Cont înregistrat! Verifică consola.")
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
                            st.rerun()
                        else:
                            st.error("❌ Credentiale incorecte!")
                    
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
        )
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
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
                }
            </style>
            """

        # Titlu mai mic, neincadrat in card
        #st.markdown(f"<h3 style='margin-bottom: 0;'>Welcome, {st.session_state.user_data['name']}! 👋🎉</h3>", unsafe_allow_html=True)
        
        # Paragraf stilizat descriptiv despre aplicatie, cu emoji-uri si design premium
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(200, 225, 255, 0.95) 100%); 
                    backdrop-filter: blur(4px);
                    padding: 18px 25px; 
                    border-radius: 12px; 
                    border-left: 5px solid #0f265c;
                    margin-top: 15px;
                    margin-bottom: 25px; 
                    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                    color: #0f265c; 
                    font-size: 1.05rem; 
                    line-height: 1.6;
                    font-weight: 500;'>
                <h3 style='margin-bottom: 0;'>Welcome, {st.session_state.user_data['name']}! 👋🎉</h3>
            ✨ <strong>Transform your standard CV into a powerful AI-driven interactive experience!</strong> 🚀<br> 
            Simply upload your document 📄, highlight your best skills 💡, and our intelligent engine 🤖 will craft a personalized knowledge base instantly. Generate your unique link 🔗 and share it with recruiters so they can chat directly with your virtual profile and discover why you're the perfect fit! 🎯
        </div>
        """, unsafe_allow_html=True)

        
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
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(200, 225, 255, 0.95) 100%);
                backdrop-filter: blur(8px);
                color: #0f265c;
            }
            .flip-card-front h3 {
                margin: 0;
                font-size: 1rem;
                font-weight: 600;
                font-family: inherit;
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
        
        # Textul impartit in carduri rotative (pentru un text mai mare si estetic pe spate)
        card_1 = """
<label class="flip-card">
    <input type="checkbox">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="icon">📄</div>
            <h3>Upload CV</h3>
            <div class="flip-btn">Vezi</div>
        </div>
        <div class="flip-card-back">
            <p>Ready? <b>Upload PDF</b><br>+ extra details to forge your AI 🤖</p>
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
            <div class="flip-btn">Vezi</div>
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
            <h3>Highlight</h3>
            <div class="flip-btn">Vezi</div>
        </div>
        <div class="flip-card-back">
            <p>Tech skills 🧠<br>Projects 🚀<br>Experience 💼</p>
        </div>
    </div>
</label>
"""

        card_4 = """
<label class="flip-card">
    <input type="checkbox">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="icon">🚀</div>
            <h3>Why use it</h3>
            <div class="flip-btn">Vezi</div>
        </div>
        <div class="flip-card-back">
            <p>Stand Out 📢<br><b>Interactive AI</b> ⚡<br>Enable Q&A 💬</p>
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
        with st.expander("🔗 Check your CV Chat url", expanded=False):
            st.code("http://localhost:8501"+f"{chat_url}")
            
    

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
            background: linear-gradient(135deg, rgba(240, 248, 255, 0.98) 0%, rgba(200, 230, 255, 0.95) 100%);
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
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0) 100%);
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
                    <p>Your CV is synced! The intelligent assistant is ready for interviews.</p>
                </div>
                <div class="banner-action">
                    Test Live Chat ⚡
                </div>
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        st.subheader("Upload area:")
        col1, col2 = st.columns(2)
        
        with col1:
            #st.divider()
            #st.subheader("📄 PDF Text Extractor 🚀")

            with st.expander("📄 PDF Text Extractor 🚀", expanded=False):
                with st.container(border=True):
                    st.subheader("📄 PDF Text Extractor 🚀")
                    uploaded_file = st.file_uploader("📂 Încarcă un PDF", type="pdf")
                
                    if st.button("✅ Submit PDF & Print to Console"):
                        if uploaded_file:
                            try:
                                print(uploaded_file)
                                reader = pypdf.PdfReader(uploaded_file)
                                full_text = ""
                                for page in reader.pages:
                                    
                                    full_text += page.extract_text()
                                    print(full_text)
                            
                                
                                st.success("✅ Textul PDF-ului a fost trimis în consolă!")

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


                            except Exception as e:

                                st.error(f"❌ Eroare la citirea PDF-ului: {e}")
                        else:
                            st.warning("⚠️ Te rog să încarci un fișier PDF înainte de a apăsa butonul!")

        with col2:
            #st.divider()

            with st.expander("� Markdown/TXT Extractor 🚀", expanded=False):

                with st.container(border=True):
                    st.subheader("📝 Markdown/TXT Extractor 🚀")
                    uploaded_txt_file = st.file_uploader("📂 Încarcă un fisier markdown/text", type=["md", "txt"])
                    
                    if st.button("✅ Submit File & Print"):
                        if uploaded_txt_file:
                            try:
                                txt_full_text = uploaded_txt_file.getvalue().decode("utf-8")
                                
                            
                                update_user(st.session_state.current_user, "text_summary", txt_full_text)
                                
                                st.success("✅ Textul fișierului a fost trimis în consolă!")
                                
                                # Salveaza textul extras in session state pentru a fi editat
                                st.session_state.txt_extracted_text = txt_full_text

                            except Exception as e:
                                st.error(f"❌ Eroare la citirea fișierului: {e}")
                        else:
                            st.warning("⚠️ Te rog să încarci un fișier înainte de a apăsa butonul!")
                        
        st.subheader("Edit area:")
        st.text("In the case of the first upload of some documents, you will be able to see the extracted content after you refresh the page!")
        with st.expander("✏️ Editează textul extras din PDF:", expanded=False):

            pdf_edited_text = st.text_area("Câmp Text Editable", value=st.session_state.pdf_extracted_text, height=400, key="pdf_editor", label_visibility="collapsed")
            if st.button("💾 Change PDF Content"):
                st.session_state.pdf_extracted_text = pdf_edited_text
                update_user(st.session_state.current_user, "CV_content", pdf_edited_text)
                st.success("✅ Conținutul PDF a fost actualizat!")

        #st.divider()
        with st.expander("✏️ Editează textul extras din Markdown/Text:", expanded=False):

            txt_edited_text = st.text_area("Câmp Text Editable", value=st.session_state.txt_extracted_text, height=400, key="txt_editor", label_visibility="collapsed")
            if st.button("💾 Change TXT Content"):
                st.session_state.txt_extracted_text = txt_edited_text
                update_user(st.session_state.current_user, "text_summary", txt_edited_text)
                st.success("✅ Conținutul TXT/MD a fost actualizat!")

        st.divider()
        
    elif selected == "Analytics":
        st.title("📈📊 Analytics Dashboard")
        
        #st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Aici poți vedea o imagine de ansamblu a activității tale. 💡</p>", unsafe_allow_html=True)
        st.divider()
        st.subheader("🤖 LLM Summary Insights (Auto-Generated):")
        with st.container(border=False):
            st.markdown("""
            
            În urma analizei datelor, se observă un nivel excelent de angajament al utilizatorilor. Întrebările tehnice domină sesiunile de chat, semnificând focusul pe competențele de bază. Mai mult, rata de selecție se menține la un solid **75%**, demonstrând o aliniere puternică între profil și oportunități. Traficul pe pagină a înregistrat o creștere stabilă în această lună, corelată cu ratele de adopție ale interviurilor RAG.
            """)
        
        # Metrici personalizate în cartonașe premium albe
        m1, m2, m3 = st.columns(3)
        with m1:
            with st.container(border=True):
                st.metric(label="❓ Total Asked Questions", value="1,342", delta="Live computed")
        with m2:
            with st.container(border=True):
                st.metric(label="👀 Page Accesses", value="12.5K", delta="Live computed")
        with m3:
            with st.container(border=True):
                st.metric(label="✅ Selectivity Rate", value="75%", delta="Live computed")
            
        st.divider()
        col_pie, col_hist = st.columns(2)
        
        with col_pie:
            st.subheader("📊 Category Distribution")
            
            # Dictionar Dummy pentru Pie Chart
            dummy_data = {
                "Tehnical Questions": 45,
                "Behavioral Questions": 25,
                "General Info": 15,
                "Off-topic": 15
            }
            
            df_pie = pd.DataFrame(list(dummy_data.items()), columns=["Category", "Value"])
            
            # Pie chart Altair elegant (donut chart) cu paletă albastră personalizată
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Value", type="quantitative"),
                color=alt.Color(field="Category", type="nominal", scale=alt.Scale(range=["#c7d2fe", "#818cf8", "#4f46e5", "#1e3a8a"])),
                tooltip=["Category", "Value"]
            ).properties(
                title="Overview of Interacted Question Types",
                height=350
            )
            
            with st.container(border=True):
                st.altair_chart(pie_chart, use_container_width=True, theme="streamlit")
                
        with col_hist:
            st.subheader("📊 Success Metrics")
            
            # Dictionar Dummy pentru Histograma (doar 2 chei)
            dummy_hist = {
                "Hired": 125,
                "Not A Fit": 13
            }
            
            df_hist = pd.DataFrame(list(dummy_hist.items()), columns=["Status", "Total"])
            
            bar_chart = alt.Chart(df_hist).mark_bar(size=60, cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                x=alt.X('Status', sort=None, title=''),
                y=alt.Y('Total', title='Candidates / Users'),
                color=alt.Color('Status', scale=alt.Scale(range=["#c7d2fe", "#818cf8"])),
                tooltip=['Status', 'Total']
            ).properties(
                title="Current Selection Ratios",
                height=350
            )
            
            with st.container(border=True):
                st.altair_chart(bar_chart, use_container_width=True, theme="streamlit")
        
        st.divider()
        col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
        with col_r2:
            if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
                st.rerun()

    elif selected == "Global Search":
        st.title("🕵️‍♂️🔍 Căutare Globală 🌍")
        st.markdown("<p style='color: #64748b;'>Caută rapid orice document, informație sau setare în întreaga platformă. ⚡</p>", unsafe_allow_html=True)
        query = st.text_input("🔎 Introdu termenul de căutare...", placeholder="Ex: Factură Ianuarie 2024")
        
        st.info("💡 Sfat: Poți folosi ghilimele pentru o căutare exactă.")

        if query:
            with st.spinner("Caut informații pe internet... 🌐"):
                try:
                    query_results = search_on_internet(query)
                except Exception as e:
                    query_results = []
                    st.error(f"Eroare la comanda de search: {e}")
                
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
                st.success(f"✅ Am găsit {len(query_results)} rezultate relevante pentru căutarea ta:")
            else:
                st.warning("⚠️ Nu s-a găsit niciun rezultat. Încearcă alte cuvinte cheie.")
            



    elif selected == "Settings":
        st.title("⚙️🛠️ Setări Platformă 🛡️")
        
    
        st.subheader("🔐 Modifică Datele de Autentificare")
        st.info("💡 Aici îți poți schimba numele de utilizator și parola contului curent.")
        
        st.divider()
        st.subheader("👤 Username change ")
        with st.form("change_username_form"):
            current_username = st.session_state.user_data['name']
            
            new_username = st.text_input("👤 Noul Username", value=current_username)
            
            submit_creds = st.form_submit_button("💾 Salvează Modificările", use_container_width=True)

            if submit_creds:
                if new_username != "":
                    update_user(st.session_state.current_user, "username", new_username)
                    
                    st.session_state.user_data['name'] = new_username
                    st.success("✅ Numele de utilizator a fost actualizat!")
            
        st.divider()
        st.subheader("🔒 Password change ")
        with st.form("change_password_form"):
            new_password = st.text_input("🔑 Noua Parolă", type="password", placeholder="Introdu noua parolă (lasă gol pentru a nu o schimba)")

            confirm_password = st.text_input("🔄 Confirmă Noua Parolă", type="password", placeholder="Repetă parola...")
            
            submit_creds = st.form_submit_button("💾 Salvează Modificările", use_container_width=True)
            
            if submit_creds:
                if new_password != confirm_password:
                    st.error("❌ Parolele introduse nu coincid! Încearcă din nou.")
                else:
                    if new_password != "":
                        update_user(st.session_state.current_user, "password", new_password)
                        st.session_state.user_data['pass'] = new_password
                        
                    st.success("✅ Datele de autentificare au fost actualizate cu succes!")
                    
        st.divider()
        st.subheader("🗑️ Delete User Account")
        
        # Variabilă de sesiune pentru a reține intenția de ștergere
        if 'delete_user_intent' not in st.session_state:
            st.session_state.delete_user_intent = False

        if not st.session_state.delete_user_intent:
            if st.button("🚨 Delete User", type="primary"):
                st.session_state.delete_user_intent = True
                st.rerun()
        else:
            st.warning("⚠️ Ești sigur? Tastează 'delete' în căsuța de mai jos pentru a confirma.")
            delete_input = st.text_input("Confirmă ștergerea:", key="delete_user_input")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✔️ Confirm"):
                    if delete_input.strip() == "delete":

                        delete_user(st.session_state.current_user)

                        st.success("Deleted!")
                        st.session_state.logged_in = False
                        #st.session_state.delete_user_intent = False
                        st.rerun()
                    else:
                        st.error("❌ Trebuie să scrii cuvântul 'delete' pentru a confirma.")
            with c2:
                if st.button("❌ Cancel"):
                    st.session_state.delete_user_intent = False
                    st.rerun()