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

# Determina link-ul dinamic catre sectiunea de chat
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

        st.markdown(f"<div class='bs-card'><h2>Welcome, {st.session_state.user_data['name']}! 👋🎉</h2></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([5, 5])
        with col1:
            #st.divider()
            
            # CSS pre-definit pentru o structură card-like responsive (Bootstrap-like)
            css_stil_carduri = """
            <style>
                .bs-card {
                    background-color: var(--background-color);
                    border-radius: 8px;
                    border: 1px solid rgba(128, 128, 128, 0.2);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                    color: var(--text-color);
                }
            </style>
            """
            
            st.markdown(css_stil_carduri, unsafe_allow_html=True)
            
            # Textul impartit in doua carduri
            card_1 = """
            <div class="bs-card">
                <p style="font-size: 16px; margin-bottom: 0;">Upload your <b>CV in PDF format</b> and add a short <b>text summary with additional details</b> about your skills, experience, or projects. <br>The application will use this information to create an <b>AI-powered assistant</b> that can answer questions about your professional profile.</p>
            </div>
            """
            
            card_2 = """
            <div class="bs-card">
                <h4 style="margin-top: 0; margin-bottom: 12px;">⚙️ How it works</h4>
                <ul style="line-height: 1.6; margin-bottom: 10px; padding-left: 20px;">
                    <li>📄 Upload your <b>CV as a PDF</b></li>
                    <li>✍️ Add a <b>short summary with extra information about your skills</b></li>
                    <li>🤖 The system builds a <b>knowledge base for an AI assistant</b></li>
                    <li>🔗 Receive a <b>unique chat link</b></li>
                    <li>💬 Anyone with the link can <b>chat with the AI about your profile</b></li>
                </ul>
                <p>This makes it easy to <b>share your experience in an interactive way</b>, allowing others to explore your background through a simple conversation with AI.</p>
            </div>
            """

            card_3 = """
                <div class="bs-card">
                    <h4 style="margin-top: 0; margin-bottom: 12px;">✨ What you can highlight</h4>
                    <ul style="line-height: 1.6; margin-bottom: 10px; padding-left: 20px;">
                        <li>🧠 Your <b>technical skills and technologies</b> (e.g. Python, AI, Web)</li>
                        <li>🚀 <b>Projects or products</b> you’ve worked on</li>
                        <li>💼 <b>Professional experience</b> and responsibilities</li>
                        <li>🏆 <b>Certifications</b> and achievements</li>
                        <li>🌱 <b>Personal interests</b> or areas you're currently learning</li>
                    </ul>
                    <p>This helps the AI provide <b>more accurate and personalized answers</b> about your profile.</p>
                </div>
                """

            card_4 = """
            <div class="bs-card">
                <h4 style="margin-top: 0; margin-bottom: 12px;">🚀 Why use it</h4>
                <ul style="line-height: 1.6; margin-bottom: 10px; padding-left: 20px;">
                    <li>🤖 Turn your CV into an <b>interactive AI experience</b></li>
                    <li>⚡ Let others quickly <b>understand your profile</b> without reading long documents</li>
                    <li>📢 <b>Stand out</b> in interviews or job applications</li>
                    <li>🌐 Easily <b>share your profile</b> with a simple link</li>
                    <li>💬 Enable <b>real-time Q&A</b> about your skills and experience</li>
                </ul>
                <p>A modern way to present yourself — more engaging than a traditional CV.</p>
            </div>
            """
            
            st.markdown(card_1, unsafe_allow_html=True)
            st.markdown(card_2, unsafe_allow_html=True)
            # st.markdown(card_3, unsafe_allow_html=True)
            # st.markdown(card_4, unsafe_allow_html=True)
            
            #st.write("<p style='font-size: 1.1rem; color: #64748b; margin-top: 2rem;'><strong>Welcome to your intelligent workspace! ✨</strong><br> This application leverages fast text parsing and artificial intelligence algorithms to securely extract, structure, and edit information from your Resumes, CVs, and technical markdown documents in real time. Get started by uploading your files below.</p>", unsafe_allow_html=True)
        with col2:

            #st.markdown(card_3, unsafe_allow_html=True)
            #if st.session_state.pdf_extracted_text:
                # Curățăm textul: păstrăm doar cuvinte
            words = re.findall(r'\b\w+\b', st.session_state.pdf_extracted_text)
            if words != []:
                word_lengths = [len(word) for word in words]

                from collections import Counter
                length_counts = Counter(word_lengths)

                hist_data = {str(length): count for length, count in sorted(length_counts.items()) if length > 3}

                df = pd.DataFrame({
                    "word_length": list(hist_data.keys()),
                    "count": list(hist_data.values())
                })

                df = df.set_index("word_length")

                st.subheader("Your CV words length histogram")
                st.bar_chart(df)
            else:
                print("No words found")
                st.divider()
                st.markdown(card_4, unsafe_allow_html=True)
            with st.expander("🔗 Check your CV Chat url : ", expanded=False):
                st.code("http://localhost:8501"+f"{chat_url}")
            
            with st.expander("What you can highlight...: ", expanded=False):
                st.markdown(card_3, unsafe_allow_html=True)
            
            # st.markdown(
            #     "<div style='text-align:center; font-size:100px;'>📄➞💬</div>",
            #     unsafe_allow_html=True
            # )
            
            #st.image("/Users/paulnicola/.gemini/antigravity/brain/5c0bbdc3-bff9-40a2-ae3c-df362b66c478/cv_processing_illustration_1773403713997.png")

        # st.info(f"Your url : {chat_url}")

        #st.image("/Users/paulnicola/.gemini/antigravity/brain/5c0bbdc3-bff9-40a2-ae3c-df362b66c478/cv_processing_illustration_1773403713997.png")


        st.divider()

        # if st.session_state.pdf_extracted_text:
        #     # Curățăm textul: păstrăm doar cuvinte
        #     words = re.findall(r'\b\w+\b', st.session_state.pdf_extracted_text)

        #     word_lengths = [len(word) for word in words]

        #     # Numărăm câte apariții are fiecare lungime
        #     length_counts = Counter(word_lengths)

        #     # Pregătim datele pentru Streamlit
        #     hist_data = {str(length): count for length, count in sorted(length_counts.items())}

        #     st.subheader("Histogramă lungime cuvinte")
        #     st.bar_chart(hist_data)


        # st.markdown("### Your CV Chat url : ")
        # col1, col2 = st.columns([5, 5])
        # with col1:
        #     with st.expander("🔗 Check your CV Chat url : ", expanded=False):
        #         st.code("http://localhost:8501"+f"{chat_url}")
        # with col2:
        #     with st.expander("What you can highlight...: ", expanded=False):
        #         st.markdown(card_3, unsafe_allow_html=True)
        # st.divider()
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
                                

                                update_user(st.session_state.current_user, "CV_content", full_text)
                                
                                st.success("✅ Textul PDF-ului a fost trimis în consolă!")

                                st.session_state.pdf_extracted_text = full_text

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
        #st.image("/Users/paulnicola/.gemini/antigravity/brain/5c0bbdc3-bff9-40a2-ae3c-df362b66c478/cv_processing_illustration_1773403713997.png", use_container_width=True)

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
        
        #tab_cont = st.tabs(["🔐 Securitate Cont"])
        
        # with tab_pref:
        #     st.subheader("🔔 Preferințe Notificări")
        #     st.checkbox("📧 Notificări pe email pentru noutăți", value=True)
        #     st.checkbox("🛡️ Alerte de securitate (recomandat)", value=True)
            
        #     st.divider()
        #     st.subheader("🎨 Personalizare")
        #     st.color_picker("Alege culoarea de accent (În curând) 🖌️", value="#ffd21e")

        #with tab_cont:
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
                   