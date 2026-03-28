import streamlit as st
from streamlit_option_menu import option_menu
import pypdf
from server_calls import register_user, login_user, update_user
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
    # Sidebar cu meniu frumos
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

    # --- LOGICA PAGINILOR ---
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
        st.divider()
        
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
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔗 Check your CV Chat url", expanded=False):
            st.code("http://localhost:8501"+f"{chat_url}")
            
        st.divider()

        # Histograme bazate pe "phrases" și "phrases_text" (lungime în cuvinte)
        col_hist1, spacer, col_hist2 = st.columns([10, 1, 10]) # Am adăugat spațiu între ele
        import altair as alt

        with col_hist1:
            if hasattr(st.session_state, 'pdf_extracted_text') and st.session_state.pdf_extracted_text:
                phrases = st.session_state.pdf_extracted_text.split(".\n")
                
                length_counts = [len(x.split()) for x in phrases]
                pars = zip(phrases, length_counts)
                
                representatin = {
                    "short": [],
                    "medium": [],
                    "long": [],
                    "very long": []
                }
                for p in pars:
                    if p[1] < 5:
                        representatin["short"].append(p[0])
                    elif p[1] < 15:
                        representatin["medium"].append(p[0])
                    elif p[1] < 25:
                        representatin["long"].append(p[0])
                    else:
                        representatin["very long"].append(p[0])
                
                total_fraze = sum(len(lst) for lst in representatin.values())
                if total_fraze > 0:
                    df_phrases = pd.DataFrame({
                        "Lungime (cuvinte)": ["short", "medium", "long", "very long"],
                        "Număr de Fraze": [len(representatin["short"]), len(representatin["medium"]), len(representatin["long"]), len(representatin["very long"])]
                    })
                    
                    st.subheader("📊 Histograma PDF")
                    st.markdown(f"**Total fraze**: {total_fraze}")
                    
                    # Folosim Altair pentru a putea controla grosimea și culoarea exactă a barelor
                    chart1 = alt.Chart(df_phrases).mark_bar(
                        size=60, color='#87CEEB', cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                    ).encode(
                        x=alt.X('Lungime (cuvinte)', sort=None, title=''),
                        y=alt.Y('Număr de Fraze', title='Total Fraze'),
                        tooltip=['Lungime (cuvinte)', 'Număr de Fraze']
                    ).properties(height=350)
                    st.altair_chart(chart1, use_container_width=True)
                else:
                    st.info("💡 Nu am găsit fraze valide în CV-ul PDF.")
            else:
                st.info("💡 CV PDF neîncărcat. Nu putem afișa histograma.")

        with col_hist2:
            text_source = st.session_state.get('txt_extracted_text', '')
            titlu_hist2 = "📊 Histograma TXT/MD"
            
            if not text_source and hasattr(st.session_state, 'pdf_extracted_text') and st.session_state.pdf_extracted_text:
                text_source = st.session_state.pdf_extracted_text
                titlu_hist2 = "📊 Histograma PDF Copie"
            
            if text_source:
                phrases_text = text_source.split(".")
                
                length_counts_text = [len(x.split()) for x in phrases_text]
                pars_text = zip(phrases_text, length_counts_text)
                
                representatin_text = {
                    "short": [],
                    "medium": [],
                    "long": [],
                    "very long": []
                }
                for p in pars_text:
                    if p[1] < 5:
                        representatin_text["short"].append(p[0])
                    elif p[1] < 15:
                        representatin_text["medium"].append(p[0])
                    elif p[1] < 25:
                        representatin_text["long"].append(p[0])
                    else:
                        representatin_text["very long"].append(p[0])
                
                total_fraze_text = sum(len(lst) for lst in representatin_text.values())
                if total_fraze_text > 0:
                    df_phrases_text = pd.DataFrame({
                        "Lungime (cuvinte)": ["short", "medium", "long", "very long"],
                        "Număr de Fraze": [len(representatin_text["short"]), len(representatin_text["medium"]), len(representatin_text["long"]), len(representatin_text["very long"])]
                    })
                    
                    st.subheader(titlu_hist2)
                    st.markdown(f"**Total fraze**: {total_fraze_text}")
                    
                    chart2 = alt.Chart(df_phrases_text).mark_bar(
                        size=60, color='#ADD8E6', cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                    ).encode(
                        x=alt.X('Lungime (cuvinte)', sort=None, title=''),
                        y=alt.Y('Număr de Fraze', title='Total Fraze'),
                        tooltip=['Lungime (cuvinte)', 'Număr de Fraze']
                    ).properties(height=350)
                    st.altair_chart(chart2, use_container_width=True)
                else:
                    st.info("💡 Nu am găsit fraze valide în text.")
            else:
                st.info("💡 Fișier pentru text neîncărcat.")


        st.divider()

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
                                reader = pypdf.PdfReader(uploaded_file)
                                full_text = ""
                                for page in reader.pages:
                                    full_text += page.extract_text()
                            
                                
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
        st.title("📈📊 Analytics Dashboard 🚀✨")
        st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Aici poți vedea o imagine de ansamblu a activității tale. 💡</p>", unsafe_allow_html=True)
        
        # Metrici cu aspect premium
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="📄 Total Documente", value="124", delta="+12 din ultima lună")
        with m2:
            st.metric(label="🎯 Rata de Succes", value="98.5%", delta="2.1%")
        with m3:
            st.metric(label="👥 Utilizatori Activi", value="1,042", delta="-14")
            
        st.divider()
        st.subheader("📈 Evoluția Datelor")
        st.line_chart([10, 25, 13, 40, 33, 45, 50, 42, 60, 75])

    elif selected == "Global Search":
        st.title("🕵️‍♂️🔍 Căutare Globală 🌍")
        st.markdown("<p style='color: #64748b;'>Caută rapid orice document, informație sau setare în întreaga platformă. ⚡</p>", unsafe_allow_html=True)
        st.text_input("🔎 Introdu termenul de căutare...", placeholder="Ex: Factură Ianuarie 2024")
        st.info("💡 Sfat: Poți folosi ghilimele pentru o căutare exactă.")

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
                   