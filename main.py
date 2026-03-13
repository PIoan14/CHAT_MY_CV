import streamlit as st
from streamlit_option_menu import option_menu
import pypdf
from server_calls import register_user, login_user, update_user
import markdown

st.set_page_config(page_title="Proiect Pro", layout="wide", page_icon="🤗")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


# Determina link-ul dinamic catre sectiunea de chat
chat_url = f"/chat?user={st.session_state.current_user}" if st.session_state.logged_in and st.session_state.current_user else "/chat"

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
                        if 'user_data' not in st.session_state:
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
                            st.session_state.pdf_extracted_text = response.json()["CV_content"]
                            st.session_state.text_extracted_text = response.json()["text_summary"]
                            
                            st.session_state.logged_in = True
                            st.rerun()
                        else:
                            st.warning("⚠️ Username or password already exists!")
                    

# --- INTERFAȚA PRINCIPALĂ (DUPĂ LOGIN) ---
else:
    # Sidebar cu meniu frumos
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown(f"### 👋 Salut, {st.session_state.user_data['name']}! 🌟")
        
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

        st.markdown(f"<h1>🤗 Bun venit, {st.session_state.user_data['name']}! 🎉</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns([6, 4])
        with col1:
            st.divider()
            app_description = """
            Upload your **CV in PDF format** and add a short **text summary with additional details** about your skills, experience, or projects.
            The application will use this information to create an **AI-powered assistant** that can answer questions about your professional profile.

            ### How it works
            - 📄 Upload your **CV as a PDF**
            - ✍️ Add a **short summary with extra information about your skills**
            - 🤖 The system builds a **knowledge base for an AI assistant**
            - 🔗 Receive a **unique chat link**
            - 💬 Anyone with the link can **chat with the AI about your profile**

            This makes it easy to **share your experience in an interactive way**, allowing others to explore your background through a simple conversation with AI.
            """
            st.markdown(app_description)
            
            
            #st.write("<p style='font-size: 1.1rem; color: #64748b; margin-top: 2rem;'><strong>Welcome to your intelligent workspace! ✨</strong><br> This application leverages fast text parsing and artificial intelligence algorithms to securely extract, structure, and edit information from your Resumes, CVs, and technical markdown documents in real time. Get started by uploading your files below.</p>", unsafe_allow_html=True)
        with col2:
            st.image("/Users/paulnicola/.gemini/antigravity/brain/5c0bbdc3-bff9-40a2-ae3c-df362b66c478/cv_processing_illustration_1773403713997.png")

        
        col1, col2 = st.columns(2)
        
        with col1:
            st.divider()
            st.subheader("📄 PDF Text Extractor 🚀")
            with st.container(border=True):
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

                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Eroare la citirea PDF-ului: {e}")
                    else:
                        st.warning("⚠️ Te rog să încarci un fișier PDF înainte de a apăsa butonul!")

        with col2:
            st.divider()
            st.subheader("📝 Markdown/TXT Extractor 🚀")
            with st.container(border=True):
                uploaded_txt_file = st.file_uploader("📂 Încarcă un fisier markdown/text", type=["md", "txt"])
                
                if st.button("✅ Submit File & Print"):
                    if uploaded_txt_file:
                        try:
                            txt_full_text = uploaded_txt_file.getvalue().decode("utf-8")
                            
                           
                            update_user(st.session_state.current_user, "text_summary", txt_full_text)
                            
                            st.success("✅ Textul fișierului a fost trimis în consolă!")
                            
                            # Salveaza textul extras in session state pentru a fi editat
                            st.session_state.txt_extracted_text = txt_full_text
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Eroare la citirea fișierului: {e}")
                    else:
                        st.warning("⚠️ Te rog să încarci un fișier înainte de a apăsa butonul!")
                        
        st.divider()
        with st.expander("✏️ Editează textul extras din PDF:", expanded=False):
            pdf_edited_text = st.text_area("Câmp Text Editable", value=st.session_state.pdf_extracted_text, height=400, key="pdf_editor", label_visibility="collapsed")
            if st.button("💾 Change PDF Content"):
                st.session_state.pdf_extracted_text = pdf_edited_text
                update_user(st.session_state.current_user, "CV_content", pdf_edited_text)
                st.success("✅ Conținutul PDF a fost actualizat!")

        st.divider()
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
        
        tab_pref, tab_cont = st.tabs(["🎨 Preferințe", "🔐 Securitate Cont"])
        
        with tab_pref:
            st.subheader("🔔 Preferințe Notificări")
            st.checkbox("📧 Notificări pe email pentru noutăți", value=True)
            st.checkbox("🛡️ Alerte de securitate (recomandat)", value=True)
            
            st.divider()
            st.subheader("🎨 Personalizare")
            st.color_picker("Alege culoarea de accent (În curând) 🖌️", value="#ffd21e")

        with tab_cont:
            st.subheader("🔐 Modifică Datele de Autentificare")
            st.info("💡 Aici îți poți schimba numele de utilizator și parola contului curent.")
            
            with st.form("change_credentials_form"):
                current_username = st.session_state.user_data['user']
                
                new_username = st.text_input("👤 Noul Username", value=current_username)
                new_password = st.text_input("🔑 Noua Parolă", type="password", placeholder="Introdu noua parolă (lasă gol pentru a nu o schimba)")
                confirm_password = st.text_input("🔄 Confirmă Noua Parolă", type="password", placeholder="Repetă parola...")
                
                submit_creds = st.form_submit_button("💾 Salvează Modificările", use_container_width=True)
                
                if submit_creds:
                    if new_password != confirm_password:
                        st.error("❌ Parolele introduse nu coincid! Încearcă din nou.")
                    elif len(new_password) > 0 and len(new_password) < 4:
                         st.error("❌ Parola nouă trebuie să aibă cel puțin 4 caractere.")
                    else:
                        st.session_state.user_data['user'] = new_username
                        if new_password != "":
                            st.session_state.user_data['pass'] = new_password
                            
                        st.success("✅ Datele de autentificare au fost actualizate cu succes!")
                        st.rerun()