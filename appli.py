import streamlit as st
from supabase import create_client
import pandas as pd

# 1. CONNEXION SUPABASE
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# 2. INITIALISATION DE LA SESSION
if 'user' not in st.session_state:
    st.session_state.user = None

# 3. FONCTIONS
def check_login(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    return res.data

def get_all_users():
    res = supabase.table("users").select("*").execute()
    return pd.DataFrame(res.data)

# 4. INTERFACE PRINCIPALE
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

if st.session_state.user is None:
    # --- ÉCRAN DE CONNEXION / INSCRIPTION ---
    st.title("🎾 Tennis Bet - Tournoi 2026")
    with st.sidebar:
        menu = st.tabs(["Connexion", "S'inscrire"])
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
        with menu[1]:
            new_u = st.text_input("Ton Prénom")
            new_p = st.text_input("Mot de passe ", type="password")
            new_club = st.selectbox("Ton Club", ["Miremont", "Auterive", "Vernet", "Lagardelle"])
            if st.button("Créer mon compte"):
                supabase.table("users").insert({
                    "username": new_u, "password": new_p, 
                    "coins": 10, "club": new_club, "is_admin": False
                }).execute()
                st.success("Compte créé ! Connecte-toi.")

else:
    # --- INTERFACE JOUEUR CONNECTÉ ---
    user = st.session_state.user
    
    # Sidebar de navigation
    st.sidebar.title(f"Joueur : {user['username']}")
    st.sidebar.metric("Ton Solde", f"{user['coins']} 🪙")
    
    pages = ["💰 Parier", "🏆 Classement Individuel", "🛡️ Guerre des Clubs"]
    if user.get('is_admin'):
        pages.append("⚙️ Panel Admin")
    
    choice = st.sidebar.radio("Navigation", pages)

    if st.sidebar.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

    # --- CONTENU DES ONGLETS ---
    
    if choice == "💰 Parier":
        st.header("Matchs du jour")
        st.info("Les paris seront ouverts dès que l'Admin aura ajouté des matchs.")

    elif choice == "🏆 Classement Individuel":
        st.header("Classement Général")
        df = get_all_users()
        if not df.empty:
            df_display = df[['username', 'coins', 'club']].sort_values("coins", ascending=False)
            st.table(df_display)

    elif choice == "🛡️ Guerre des Clubs":
        st.header("La Guerre des Clubs")
        st.write("Le score du club est la moyenne des points de tous ses membres.")
        df = get_all_users()
        if not df.empty:
            guerre = df.groupby("club")["coins"].mean().sort_values(ascending=False).reset_index()
            guerre.columns = ["Club", "Moyenne de Coins"]
            st.dataframe(guerre, use_container_width=True)
            st.balloons() if guerre.iloc[0]['Club'] == user['club'] else None

    elif choice == "⚙️ Panel Admin":
        st.header("Administration du Tournoi")
        st.write("Ici, tu pourras ajouter des matchs et valider les scores.")
        # Espace pour tes futurs formulaires de création de matchs
