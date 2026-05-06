import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. INITIALISATION (SÉCURITÉ ANTI-ERREUR) ---
if 'user_connected' not in st.session_state:
    st.session_state.user_connected = None

# --- 2. CONNEXION BDD ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_users():
    try:
        # Remplace "users" par le nom exact de ton onglet dans Google Sheets
        return conn.read(worksheet="users", ttl=0)
    except:
        return pd.DataFrame(columns=["username", "password", "coins", "is_admin"])

# --- 3. DESIGN & HEADER CSS ---
st.markdown("""
    <style>
    .main-header {
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background-color: #1E1E1E; display: flex; justify-content: space-between;
        align-items: center; padding: 0 20px; z-index: 999; border-bottom: 2px solid #E2001A;
    }
    .coins-badge {
        background: #FFD700; color: black; padding: 4px 12px;
        border-radius: 20px; font-weight: bold; margin-right: 10px;
    }
    .stApp { margin-top: 50px; }
    /* Style des boutons */
    div.stButton > button {
        background-color: #E2001A; color: white; border-radius: 10px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AFFICHAGE DU HEADER ---
if st.session_state.user_connected:
    df_users = get_users()
    user_info = df_users[df_users['username'] == st.session_state.user_connected].iloc[0]
    solde = user_info['coins']
    
    st.markdown(f"""
        <div class="main-header">
            <div style="font-weight: bold; color: #E2001A;">🎾 TENNIS BET 2026</div>
            <div style="display: flex; align-items: center;">
                <span class="coins-badge">{round(float(solde), 1)} 🪙</span>
                <span style="color: white;">👤 {st.session_state.user_connected}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 5. LOGIQUE ADMIN ---
is_admin = False
if st.session_state.user_connected:
    df_users = get_users()
    user_row = df_users[df_users['username'] == st.session_state.user_connected]
    if not user_row.empty:
        # Vérifie si la colonne is_admin existe et est à TRUE
        is_admin = user_row.iloc[0].get('is_admin', False)

# --- 6. CRÉATION DES ONGLETS ---
tabs_list = ["🏠 Accueil", "💰 Parier", "🏆 Classement"]
if is_admin:
    tabs_list.append("⚙️ Admin")

tabs = st.tabs(tabs_list)

with tabs[0]:
    st.title("Bienvenue au Tournoi !")
    if not st.session_state.user_connected:
        st.info("👋 Connecte-toi dans la barre latérale pour commencer à parier.")
    else:
        st.write(f"Prêt à gagner des coins, {st.session_state.user_connected} ?")

with tabs[1]:
    st.header("Matchs en cours")
    if not st.session_state.user_connected:
        st.warning("Connecte-toi pour voir les cotes.")
    else:
        st.write("Les prochains matchs apparaîtront ici.")

with tabs[2]:
    st.header("🏆 Classement Général")
    df_users = get_users()
    if not df_users.empty:
        leaderboard = df_users[['username', 'coins']].sort_values(by='coins', ascending=False)
        st.table(leaderboard)

if is_admin:
    with tabs[3]:
        st.header("🛠 Espace Administrateur")
        st.success("Tu as les droits d'accès. Ici tu pourras créer des matchs.")
        # Ajoute tes boutons de gestion ici

# --- 7. BARRE LATÉRALE (CONNEXION) ---
with st.sidebar:
    st.title("Compte")
    if st.session_state.user_connected is None:
        u_name = st.text_input("Prénom")
        u_pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            df_users = get_users()
            user_check = df_users[(df_users['username'] == u_name) & (df_users['password'] == str(u_pwd))]
            if not user_check.empty:
                st.session_state.user_connected = u_name
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
