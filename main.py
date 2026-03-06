import streamlit as st
from streamlit_option_menu import option_menu
import pypdf
from server_calls import register_user
# Configurare pagină
st.set_page_config(page_title="Proiect Pro", layout="wide", page_icon="✨")

# --- CSS CUSTOM PENTRU UN DESIGN PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Stiluri globale */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Formulare (Login/Register/Upload) */
    div[data-testid="stForm"] {
        background: #ffffff;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.8);
    }
    
    /* Butoane primare */
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5);
        border: none;
        color: white;
    }

    /* Input-uri de text */
    div[data-testid="stTextInput"] input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
        background-color: #fefefe;
    }
    
    div[data-testid="stTextInput"] input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
    }

    /* Headere */
    h1 {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    h2, h3 {
        color: #334155;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #f1f5f9;
        box-shadow: 5px 0 15px rgba(0,0,0,0.02);
    }
    
    [data-testid="stSidebar"] [data-testid="stImage"] {
        margin-top: 1rem;
        margin-bottom: 2rem;
        padding: 10px;
        border-radius: 20px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Carduri de Informatii */
    div[data-testid="stInfo"] {
        background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%);
        border: none;
        border-radius: 12px;
        color: #1e40af;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        padding: 1rem;
    }
    
    div[data-testid="stSuccess"] {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: none;
        border-radius: 12px;
        color: #166534;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    div[data-testid="stError"] {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: none;
        border-radius: 12px;
        color: #991b1b;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Divizoare */
    hr {
        margin: 2em 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
    }
    
    /* Uploader */
    div[data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 16px;
        padding: 2rem;
        border: 2px dashed #cbd5e1;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #8b5cf6;
        background-color: #f5f3ff;
    }
    
    /* Metrici */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f5f9;
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* Container Tabs */
    div[data-testid="stTabs"] {
        margin-top: 1rem;
    }
    button[data-baseweb="tab"] {
        font-family: inherit;
        font-weight: 500;
        padding: 1rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- STARE SESIUNE (Mock Database) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {"user": "admin", "pass": "1234", "name": "Utilizator Demo"}

# --- FUNCȚII AUXILIARE ---
def login_user(username, password):
    if username:
        st.session_state.logged_in = True
        st.rerun()
    else:
        st.error("Credentiale incorecte!")

# --- INTERFAȚA DE LOGIN / REGISTER ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    
    with cols[1]:
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Welcome Back ✨</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Autentifică-te pentru a accesa platforma</p>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In", use_container_width=True)
                if submit:
                    login_user(u, p)
        
        with tab2:
            with st.form("reg_form"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                reg_submit = st.form_submit_button("Register", use_container_width=True)
                if reg_submit:
                    register_user(new_u, new_p)
                    st.success("Cont înregistrat! Verifică consola.")
                    login_user(new_u, new_p)

# --- INTERFAȚA PRINCIPALĂ (DUPĂ LOGIN) ---
else:
    # Sidebar cu meniu frumos
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown(f"### Salut, {st.session_state.user_data['name']}!")
        
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Analytics", "Global Search", "Settings"],
            icons=["house", "graph-up", "search", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # --- LOGICA PAGINILOR ---
    if selected == "Home":
        st.markdown(f"<h1>👋 Bun venit, {st.session_state.user_data['name']}!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;'>Îți prezentăm noul spațiu de lucru modern și eficient.</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"👤 **Nume Utilizator:**\n\n{st.session_state.user_data['name']}")
        with col2:
            st.info(f"🔑 **Username / Cont:**\n\n{st.session_state.user_data['user']}")
        
        st.divider()
        st.subheader("📄 PDF Text Extractor")
        uploaded_file = st.file_uploader("Încarcă un PDF", type="pdf")
        
        if uploaded_file and st.button("Submit & Print to Console"):
            try:
                reader = pypdf.PdfReader(uploaded_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text()
                
                print("\n--- CONTINUT PDF ---")
                print(full_text)
                print("--------------------\n")
                st.success("Textul a fost trimis în consolă!")
            except Exception as e:
                st.error(f"Eroare: {e}")

    elif selected == "Analytics":
        st.title("📊 Analytics Dashboard")
        st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Aici poți vedea o imagine de ansamblu a activității tale.</p>", unsafe_allow_html=True)
        
        # Metrici cu aspect premium
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="Total Documente", value="124", delta="+12 din ultima lună")
        with m2:
            st.metric(label="Rata de Succes", value="98.5%", delta="2.1%")
        with m3:
            st.metric(label="Utilizatori Activi", value="1,042", delta="-14")
            
        st.divider()
        st.subheader("Evoluția Datelor")
        st.line_chart([10, 25, 13, 40, 33, 45, 50, 42, 60, 75])

    elif selected == "Global Search":
        st.title("🔍 Global Search")
        st.markdown("<p style='color: #64748b;'>Caută rapid orice document, informație sau setare în întreaga platformă.</p>", unsafe_allow_html=True)
        st.text_input("Introdu termenul de căutare...", placeholder="Ex: Factură Ianuarie 2024")
        st.info("💡 Sfat: Poți folosi ghilimele pentru o căutare exactă.")

    elif selected == "Settings":
        st.title("⚙️ Setări Platformă")
        
        tab_pref, tab_cont = st.tabs(["Preferințe", "Securitate Cont"])
        
        with tab_pref:
            st.subheader("Preferințe Notificări")
            st.checkbox("Notificări pe email pentru noutăți", value=True)
            st.checkbox("Alerte de securitate (recomandat)", value=True)
            
            st.divider()
            st.subheader("Personalizare")
            st.color_picker("Alege culoarea de accent (În curând)", value="#6366f1")

        with tab_cont:
            st.subheader("Modifică Datele de Autentificare")
            st.info("💡 Aici îți poți schimba numele de utilizator și parola contului curent.")
            
            with st.form("change_credentials_form"):
                current_username = st.session_state.user_data['user']
                
                new_username = st.text_input("Noul Username", value=current_username)
                new_password = st.text_input("Noua Parolă", type="password", placeholder="Introdu noua parolă (lasă gol pentru a nu o schimba)")
                confirm_password = st.text_input("Confirmă Noua Parolă", type="password", placeholder="Repetă parola...")
                
                submit_creds = st.form_submit_button("Salvează Modificările", use_container_width=True)
                
                if submit_creds:
                    if new_password != confirm_password:
                        st.error("Parolele introduse nu coincid! Încearcă din nou.")
                    elif len(new_password) > 0 and len(new_password) < 4:
                         st.error("Parola nouă trebuie să aibă cel puțin 4 caractere.")
                    else:
                        st.session_state.user_data['user'] = new_username
                        if new_password != "":
                            st.session_state.user_data['pass'] = new_password
                            
                        st.success("Datele de autentificare au fost actualizate cu succes!")
                        st.rerun()