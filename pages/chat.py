import streamlit as st
from server_calls import chat_RAG_llm

st.set_page_config(page_title="Chat", layout="wide", page_icon="💬")

# Navbar
st.markdown("""
<style>
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
        margin-top: 60px;
    }
</style>
<div class="top-navbar">
    <a href="/" target="_self">🏠 Home</a>
    <a href="/chat" target="_self">💬 Chat</a>
</div>
""", unsafe_allow_html=True)

# Verifică dacă există un user_id în parametrii URL-ului (pentru ruta dinamică /chat?user=ID)
current_chat_user = st.query_params.get("user")
current_chat_username = st.query_params.get("username", current_chat_user)

if not current_chat_user:
    st.warning("⚠️ Chat-ul nu a putut fi identificat. Te rugăm să accesezi un link valid de chat (ex: /chat?user=ID&username=Nume).")
    st.markdown('<a href="/" target="_self">Întoarce-te la Home 🏠</a>', unsafe_allow_html=True)
    st.stop() # Opresste executia restului paginii

# Continutul paginii Chat pentru vizitatorii acestei rute dinamice
st.title(f"👤 Chat cu Asistentul lui {current_chat_username} 💬")
st.markdown(f"Pune întrebări agentului AI instruit special pe documentele lui **{current_chat_username}**.")

# Initializarea istoricului de chat in session_state, specific acestui user, daca nu exista
chat_history_key = f"chat_history_{current_chat_user}"
if chat_history_key not in st.session_state:
    st.session_state[chat_history_key] = [
        {"role": "assistant", "content": f"Salut! Sunt asistentul AI al lui {current_chat_username}. Cu ce te pot ajuta?"}
    ]

# Lista de raspunsuri moc primite "de la LLM"
mock_responses = [
    f"Conform CV-ului lui {current_chat_user}, are o experiență bogată în domeniu.",
    "Asta este o întrebare foarte interesantă! Lasă-mă să verific datele.",
    f"{current_chat_user} a subliniat că abilitatea sa principală este rezolvarea rapidă a problemelor tehnice.",
    "Nu sunt sigur de detalii, dar pot spune că profilul arată multă dedicare.",
    "În sumarul său, se menționează expertiză în lucrul cu echipe și proiecte de succes."
]

# Initializam un index pentru a roti raspunsurile mock, daca nu exista
mock_index_key = f"mock_index_{current_chat_user}"
if mock_index_key not in st.session_state:
    st.session_state[mock_index_key] = 0

# Afisarea mesajelor anterioare din istoric
for message in st.session_state[chat_history_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caseta de input pentru utilizator
if prompt := st.chat_input("Scrie un mesaj aici..."):
    # 1. Adaugam si afisam mesajul utilizatorului
    st.session_state[chat_history_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generam raspunsul "LLM-ului"
    import time
    
    # Simulam o mica intarziere (gandire)
    with st.spinner("Asistentul tastează..."):
        time.sleep(1.5)
        
        # Luam un raspuns din lista
        current_index = st.session_state[mock_index_key]
        response_text = chat_RAG_llm(current_chat_user, prompt)
        
        # Crestem indexul pentru urmatorul mesaj (si o luam de la capat daca e cazul)
        st.session_state[mock_index_key] = (current_index + 1) % len(mock_responses)

    # 3. Adaugam si afisam raspunsul asistentului
    st.session_state[chat_history_key].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
