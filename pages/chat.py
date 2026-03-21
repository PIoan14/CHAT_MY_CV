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

    /* Fereastra de chat cu umbra mai tare si contur solid */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1.5px solid rgba(130, 140, 150, 0.45) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
        background-color: rgba(255, 255, 255, 0.01) !important;
        transition: box-shadow 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3) !important;
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
    
    /* CSS pentru cardurile rotative (Flip Cards) */
    .instructions-container {
        display: flex;
        flex-direction: column;
        gap: 25px;
        margin-top: 10px;
    }
    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 190px;
        perspective: 1000px;
        cursor: pointer;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.7s cubic-bezier(0.4, 0.2, 0.2, 1);
        transform-style: preserve-3d;
    }
    .flip-card input[type="checkbox"] {
        display: none;
    }
    /* Cand apăsăm, inner-ul se va roti 180 grade */
    .flip-card input[type="checkbox"]:checked ~ .flip-card-inner {
        transform: rotateY(180deg);
    }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .flip-card-front {
        /* Gradient bleu deschis spre alb pentru faza frontală */
        background: linear-gradient(135deg, rgba(215, 240, 255, 0.95) 0%, rgba(255, 255, 255, 0.95) 100%);
        backdrop-filter: blur(8px);
        color: #0f265c;
    }
    .flip-card-front h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        font-family: sans-serif;
    }
    .flip-card-front .icon {
        font-size: 2.8rem;
        margin-bottom: 10px;
    }
    .flip-card-front .flip-btn {
        border: 1px solid rgba(15, 38, 92, 0.25);
        background: rgba(15, 38, 92, 0.05);
        color: #0f265c;
    }
    .flip-card-back {
        /* Gradient luminos pentru verso */
        background: linear-gradient(135deg, rgba(142, 197, 252, 0.95) 0%, rgba(194, 233, 251, 0.95) 100%);
        color: #222;
        transform: rotateY(180deg);
        backdrop-filter: blur(8px);
    }
    .flip-card-back p {
        font-size: 0.95rem;
        font-weight: 500;
        line-height: 1.5;
        margin: 0 0 15px 0;
        font-family: sans-serif;
    }
    .flip-btn {
        margin-top: auto;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.3s;
        border: 1px solid rgba(255,255,255,0.3);
        background: rgba(255,255,255,0.1);
        color: white;
        display: inline-block;
    }
    .flip-card:hover .flip-card-front .flip-btn {
        background: rgba(15, 38, 92, 0.15);
    }
    .flip-card-back .flip-btn {
        border: 1px solid rgba(0,0,0,0.2);
        background: rgba(0,0,0,0.05);
        color: #222;
    }
    .flip-card:hover .flip-card-back .flip-btn {
        background: rgba(0,0,0,0.15);
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

# Layout cu coloane (Chat mai mic la stanga, Carduri interactive la dreapta)
col1, spacer, col2 = st.columns([6, 0.5, 3.5])

with col1:
    # Container cu inălțime fixă pentru a oferi scroll flexibil dar controlat spațiului de chat
    chat_container = st.container(height=550, border=True)
    
    with chat_container:
        # Afișarea mesajelor anterioare
        for message in st.session_state[chat_history_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input-ul de chat sub container in interiorul coloanei
    if prompt := st.chat_input("Scrie un mesaj aici..."):
        # Adăugăm și afișăm mesajul de la utilizator
        st.session_state[chat_history_key].append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Generăm răspunsul LLM integrat tot in container direct
        with chat_container:
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

with col2:
    
    # Adăugăm cardurile rotative (Flip Cards) fără indentare pentru a evita parsing-ul Markdown
    cards_html = """
<div class="instructions-container">
    <!-- Card 1 -->
    <label class="flip-card">
        <input type="checkbox">
        <div class="flip-card-inner">
            <div class="flip-card-front">
                <div class="icon">✨</div>
                <h3>Pune Întrebări Clare</h3>
                <div class="flip-btn">Vezi Detalii</div>
            </div>
            <div class="flip-card-back">
                <p>Fii cât mai specific pentru a obține răspunsuri precise din CV, ex: "Ce rol a avut la compania X?"</p>
                <div class="flip-btn">Rotire Înapoi</div>
            </div>
        </div>
    </label>
    
    <!-- Card 2 -->
    <label class="flip-card">
        <input type="checkbox">
        <div class="flip-card-inner">
            <div class="flip-card-front">
                <div class="icon">🧠</div>
                <h3>Inteligență Artificială</h3>
                <div class="flip-btn">Vezi Mod de Lucru</div>
            </div>
            <div class="flip-card-back">
                <p>Asistentul preia informații exclusiv din documentele furnizate cu un model RAG.</p>
                <div class="flip-btn">Rotire Înapoi</div>
            </div>
        </div>
    </label>

    <!-- Card 3 -->
    <label class="flip-card">
        <input type="checkbox">
        <div class="flip-card-inner">
            <div class="flip-card-front">
                <div class="icon">🚀</div>
                <h3>Află Mai Multe</h3>
                <div class="flip-btn">Vezi Cum</div>
            </div>
            <div class="flip-card-back">
                <p>Poți cere asistentului să-ți rezume întregul profil profesional sau competențele.</p>
                <div class="flip-btn">Rotire Înapoi</div>
            </div>
        </div>
    </label>
</div>
"""
    # Folosim st.html daca este disponibil pe Streamlit 1.34+, altfel recurgem la markdown
    if hasattr(st, "html"):
        st.html(cards_html)
    else:
        st.markdown(cards_html, unsafe_allow_html=True)
