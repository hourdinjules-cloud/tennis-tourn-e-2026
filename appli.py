import streamlit as st

# --- 1. LE DESIGN (CSS) ---
# On définit le look "App Mobile" ici
st.markdown("""
    <style>
    /* Forcer le fond noir */
    .stApp { background-color: #000000; }
    
    /* Cacher le menu Streamlit et le header pour faire "App" */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style Winamax pour les cartes de matchs */
    .match-card {
        background-color: #1A1A1A;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    /* LA BARRE DE NAVIGATION FIXE EN BAS */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #121212;
        display: flex;
        justify-content: space-around;
        padding: 10px 0;
        border-top: 1px solid #444;
        z-index: 99;
    }
    
    .nav-item {
        color: #888;
        text-align: center;
        font-size: 12px;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. L'AFFICHAGE (HTML + Streamlit) ---
st.title("TENNISBET 🎾")

# Exemple de carte de match stylisée en HTML
st.markdown("""
    <div class="match-card">
        <div style="color: #888; font-size: 12px;">Ligue des Champions</div>
        <div style="font-weight: bold; margin-top: 5px;">Bayern Munich vs Real Madrid</div>
    </div>
""", unsafe_allow_html=True)

# Boutons Streamlit normaux (ils seront stylisés par ton CSS)
col1, col2 = st.columns(2)
with col1:
    st.button("1.85", key="m1")
with col2:
    st.button("2.10", key="m2")

# --- 3. LA BARRE DE NAV (Injection HTML direct) ---
# Note: Pour que les boutons de la barre marchent dans Streamlit, 
# il vaut mieux utiliser les boutons natifs de Streamlit dans des colonnes en bas,
# OU utiliser des liens HTML si tu as plusieurs fichiers .py
st.markdown("""
    <div class="nav-bar">
        <div class="nav-item">🏠<br>PARIS</div>
        <div class="nav-item">📊<br>LIVE</div>
        <div class="nav-item" style="color: #FFD700;">🏆<br>STATS</div>
        <div class="nav-item">⚙️<br>PROFIL</div>
    </div>
""", unsafe_allow_html=True)
