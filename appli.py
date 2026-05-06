import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURATION SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- FONCTIONS ---
def check_login(username, password):
    # Cherche l'utilisateur dans la table
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    return res.data

# --- INTERFACE ---
st.title("🎾 Tennis Bet - Tournoi 2026")

if st.session_state.user is None:
    # --- FORMULAIRE DE CONNEXION ---
    with st.sidebar:
        st.subheader("Connexion")
        u = st.text_input("Prénom")
        p = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            user_data = check_login(u, p)
            if user_data:
                st.session_state.user = user_data[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects...")
    
    st.info("👈 Connecte-toi sur le côté pour accéder aux paris.")

else:
    # --- INTERFACE CONNECTÉE ---
    u_info = st.session_state.user
    
    # Header stylé
    st.markdown(f"""
        <div style="background:#1E1E1E; padding:20px; border-radius:10px; border-left: 5px solid #E2001A;">
            <h2 style="margin:0;">Salut {u_info['username']} ! 👋</h2>
            <p style="font-size:20px; color:#FFD700;">Solde : <b>{u_info['coins']} 🪙</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()

    # Tes onglets
    tab1, tab2 = st.tabs(["💰 Parier", "🏆 Classement"])
    
    with tab2:
        # On récupère tous les utilisateurs pour le classement
        all_users = supabase.table("users").select("username, coins, club").execute()
        df = pd.DataFrame(all_users.data)
        st.table(df.sort_values("coins", ascending=False))
