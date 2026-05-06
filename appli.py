import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- INITIALISATION ---
if 'user_connected' not in st.session_state:
    st.session_state.user_connected = None

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_users():
    try:
        # Lit la feuille "users"
        return conn.read(worksheet="users", ttl=0)
    except:
        return pd.DataFrame()

# --- DESIGN CSS ---
st.markdown("""
    <style>
    .main-header {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #1E1E1E; display: flex; justify-content: space-between;
        align-items: center; padding: 0 20px; z-index: 999; border-bottom: 2px solid #E2001A;
    }
    .coins-badge { background: #FFD700; color: black; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .stApp { margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
if st.session_state.user_connected:
    df_users = get_users()
    if not df_users.empty:
        user_row = df_users[df_users['username'].astype(str) == st.session_state.user_connected]
        if not user_row.empty:
            solde = user_row.iloc[0]['coins']
            st.markdown(f"""
                <div class="main-header">
                    <div style="font-weight: bold; color: #E2001A;">🎾 TENNIS BET</div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span class="coins-badge">{solde} 🪙</span>
                        <span style="color: white;">👤 {st.session_state.user_connected}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- ONGLETS ---
df_users = get_users()
is_admin = False
if st.session_state.user_connected and not df_users.empty:
    user_row = df_users[df_users['username'].astype(str) == st.session_state.user_connected]
    is_admin = user_row.iloc[0].get('is_admin', False)

tabs_list = ["🏠 Accueil", "💰 Parier", "🏆 Classement", "⚔️ Guerre des Clubs"]
if is_admin: tabs_list.append("⚙️ Admin")
tabs = st.tabs(tabs_list)

with tabs[0]:
    st.title("Tournoi de Tennis 2026")
    if not st.session_state.user_connected:
        st.info("👋 Bienvenue ! Connecte-toi sur le côté pour accéder à tes paris.")

with tabs[2]:
    st.header("🏆 Classement")
    if not df_users.empty:
        st.dataframe(df_users[['username', 'coins', 'club']].sort_values("coins", ascending=False))

# --- SIDEBAR (CONNEXION UNIQUEMENT) ---
with st.sidebar:
    if st.session_state.user_connected:
        st.success(f"Connecté : {st.session_state.user_connected}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        st.subheader("Espace Joueur")
        u_name = st.text_input("Prénom")
        u_pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if not df_users.empty:
                # On compare en texte brut pour éviter les bugs de types
                check = df_users[(df_users['username'].astype(str) == u_name) & (df_users['password'].astype(str) == u_pwd)]
                if not check.empty:
                    st.session_state.user_connected = u_name
                    st.rerun()
                else:
                    st.error("Identifiants inconnus. Demande à Jules de te créer un compte !")
