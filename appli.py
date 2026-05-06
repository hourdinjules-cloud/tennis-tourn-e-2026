import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONNEXION SUPABASE (Doit être en haut)
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# 2. INITIALISATION DE LA SESSION
if 'user' not in st.session_state:
    st.session_state.user = None

# 3. FONCTION DE VÉRIFICATION
def check_login(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    return res.data

# 4. INTERFACE
st.title("🎾 Tennis Bet - Tournoi 2026")

if st.session_state.user is None:
    with st.sidebar:
        st.subheader("Bienvenue !")
        menu = st.tabs(["Connexion", "S'inscrire"])
        
        # --- ONGLET CONNEXION ---
        with menu[0]:
            u = st.text_input("Prénom")
            p = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                user_data = check_login(u, p)
                if user_data:
                    st.session_state.user = user_data[0]
                    st.rerun()
                else:
                    st.error("Identifiants incorrects...")

        # --- ONGLET INSCRIPTION ---
        with menu[1]:
            new_u = st.text_input("Ton Prénom (ex: Jules)")
            new_p = st.text_input("Choisis un mot de passe", type="password")
            new_club = st.selectbox("Ton Club", ["Club A", "Club B", "Autre"])
            
            if st.button("Créer mon compte"):
                if new_u and new_p:
                    try:
                        supabase.table("users").insert({
                            "username": new_u,
                            "password": new_p,
                            "coins": 10,
                            "club": new_club,
                            "is_admin": False
                        }).execute()
                        st.success("Compte créé ! Connecte-toi à gauche.")
                    except Exception as e:
                        st.error("Erreur : Ce nom est peut-être déjà pris.")
                else:
                    st.warning("Remplis tous les champs !")

else:
    # --- INTERFACE UNE FOIS CONNECTÉ ---
    u_info = st.session_state.user
    st.sidebar.success(f"Connecté : {u_info['username']}")
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()

    st.header(f"Salut {u_info['username']} ! 👋")
    st.metric("Tes Coins", f"{u_info['coins']} 🪙")
    
    tab_pari, tab_classement = st.tabs(["💰 Parier", "🏆 Classement"])
    
    with tab_classement:
        res = supabase.table("users").select("username, coins, club").execute()
        df = pd.DataFrame(res.data)
        st.table(df.sort_values("coins", ascending=False))
