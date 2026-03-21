import streamlit as st
from server_calls import chat_RAG_llm
import time

# OBLIGATORIU: set_page_config trebuie să fie prima comandă Streamlit
st.set_page_config(page_title="Chat", layout="wide", page_icon="💬")

# CSS personalizat: 
# 1. Ascunde sidebar doar pe această pagină
# 2. Navbar existent
# 3. Styling atractiv pentru mesaje
# 4. Animații 3D Flip pentru carduri (pure CSS)
st.markdown("""
<style>
    /* Ascunde Sidebar-ul doar pe această pagină */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Navbar existent complet păstrat */
    .top-navbar {
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
    }
    .top-navbar a {
        color: white !important;
        text-decoration: none;
        font-weight: 600;
        font-family: sans-serif;
        margin-left: 20px;
        font-size: 16px;
        transition: color 0.2s ease;
    }
    .top-navbar a:hover {
        color: #ffd21e !important;
    }
    .stApp > header {
        display: none !important;
    }
    .stApp {
        /* Mutam continutul mai sus (aproape de navbar) */
        margin-top: 40px;
    }
    
    /* Ridicam titlul eliminand din spatiul gol implicit al Streamlit */
    [data-testid="stMainBlockContainer"] {
        padding-top: 2.5rem !important; 
    }

    /* Fundalul putin mai inchis (overlay transparent, universal pentru orice tema dark/light) */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.055);
        pointer-events: none;
        z-index: -1;
    }


    /* CSS pentru Mesajele de Chat */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 15px !important;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
    }
    

</style>
<div class="top-navbar">
    <a href="/" target="_self">🏠 Home</a>
    <a href="/chat" target="_self">💬 Chat</a>
</div>
""", unsafe_allow_html=True)

# Verifică dacă există un user_id în parametrii URL-ului
current_chat_user = st.query_params.get("user")
current_chat_username = st.query_params.get("username", current_chat_user)

if not current_chat_user:
    st.warning("⚠️ Chat-ul nu a putut fi identificat. Te rugăm să accesezi un link valid de chat (ex: /chat?user=ID&username=Nume).")
    st.markdown('<a href="/" target="_self">Întoarce-te la Home 🏠</a>', unsafe_allow_html=True)
    st.stop()

# Header al paginii
st.subheader(f"👤 Chat cu Asistentul lui {current_chat_username} 💬")
st.markdown(f"Pune întrebări agentului AI instruit special pe documentele lui **{current_chat_username}**.")


# Inițializarea istoricului de chat în session_state dacă nu există
chat_history_key = f"chat_history_{current_chat_user}"
if chat_history_key not in st.session_state:
    st.session_state[chat_history_key] = [
        {"role": "assistant", "content": f"Hello! I am the AI assistant of {current_chat_username}. I know everything about {current_chat_username}'s CV and additional information based. How can I help you?"}
    ]

# Variabile pentru simularea unor logici secundare (ex. mock index daca ar fi nevoie)
mock_responses = [
    f"Conform CV-ului lui {current_chat_user}, are o experiență bogată în domeniu.",
    "Asta este o întrebare foarte interesantă! Lasă-mă să verific datele.",
    f"{current_chat_user} a subliniat că abilitatea sa principală este rezolvarea rapidă a problemelor tehnice.",
    "Nu sunt sigur de detalii, dar pot spune că profilul arată multă dedicare.",
    "În sumarul său, se menționează expertiză în lucrul cu echipe și proiecte de succes."
]
mock_index_key = f"mock_index_{current_chat_user}"
if mock_index_key not in st.session_state:
    st.session_state[mock_index_key] = 0

# Afișarea mesajelor anterioare
for message in st.session_state[chat_history_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input-ul de chat ocupand toata latimea
if prompt := st.chat_input("Scrie un mesaj aici..."):
    # Adăugăm și afișăm mesajul de la utilizator
    st.session_state[chat_history_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generăm răspunsul LLM
    with st.spinner("Asistentul tastează..."):
        time.sleep(1.0) # Mică latență simlată UX
        
        # Menținem complet funcționalitatea existentă RAG_llm
        current_index = st.session_state[mock_index_key]
        response_text = chat_RAG_llm(current_chat_user, prompt)
        st.session_state[mock_index_key] = (current_index + 1) % len(mock_responses)
    
    # Adăugăm și afișăm răspunsul de la asistent
    st.session_state[chat_history_key].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
