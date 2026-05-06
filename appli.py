import streamlit as st

# --- 1. CONFIGURATION ET CLASSEMENT ---
if 'page' not in st.session_state:
    st.session_state.page = "Paris"

# --- 2. LE CSS (DESIGN NÉGATIF POUR LA BARRE DE NAV) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stHeader"] {display:none;}
    
    /* Style Winamax pour les matchs de Tennis */
    .match-box {
        background-color: #1A1A1A;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #FFD700;
        margin-bottom: 10px;
    }

    /* FORCER LA BARRE DE BOUTONS EN BAS */
    div[data-testid="stVerticalBlock"] > div:last-child {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #121212;
        padding: 10px 0px;
        border-top: 1px solid #333;
        z-index: 999;
    }
    
    /* Style des boutons pour qu'ils ressemblent à des icônes d'app */
    .stButton > button {
        background-color: transparent !important;
        color: white !important;
        border: none !important;
        font-size: 10px !important;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE DES PAGES ---

# HEADER
col_logo, col_coins = st.columns([2, 1])
with col_logo:
    st.markdown("<h2 style='color:#FFD700; margin:0;'>TENNISBET</h2>", unsafe_allow_html=True)
with col_coins:
    st.markdown("<div style='background:#FFD700; color:black; padding:5px; border-radius:15px; text-align:center; font-weight:bold;'>10 🪙</div>", unsafe_allow_html=True)

# CONTENU SELON LA PAGE
if st.session_state.page == "Paris":
    st.subheader("🎾 Matchs du Tournoi")
    
    # Exemple de match de Tennis
    st.markdown('<div class="match-box"><b>Open de Miremont - Court 1</b><br>Jules vs Alex</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Jules (1.80)", key="jules"):
        st.success("Pari placé sur Jules !")
    if c2.button("Alex (1.80)", key="alex"):
        st.success("Pari placé sur Alex !")

elif st.session_state.page == "Stats":
    st.subheader("🏆 Classement des parieurs")
    st.write("1. Jules - 150 🪙")
    st.write("2. Alex - 120 🪙")

# --- 4. LA BARRE DE NAVIGATION (VRAIS BOUTONS CLIQUABLES) ---
# On crée une ligne de colonnes tout en bas du script
st.write("---") # Séparateur visuel
nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button("🏠\nPARIS"):
        st.session_state.page = "Paris"
        st.rerun()
with nav2:
    if st.button("🏆\nCOINS"):
        st.session_state.page = "Stats"
        st.rerun()
with nav3:
    if st.button("⚙️\nADMIN"):
        st.session_state.page = "Admin"
        st.rerun()
