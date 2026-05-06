import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

# Custom CSS pour masquer les menus Streamlit inutiles et styliser les onglets
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- 3. INITIALISATION DE LA SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. FONCTIONS ---
def check_login(username, password):
    res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
    return res.data

def get_all_users():
    res = supabase.table("users").select("*").execute()
    return pd.DataFrame(res.data)

# --- 5. INTERFACE D'ACCÈS (CONNEXION / INSCRIPTION) ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Miremont 2026")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Se connecter")
        u = st.text_input("Prénom")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            user_data = check_login(u, p)
            if user_data:
                st.session_state.user = user_data[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with col_r:
        st.subheader("Créer un compte")
        new_u = st.text_input("Ton Prénom")
        new_p = st.text_input("Choisis un mot de passe", type="password")
        new_club = st.selectbox("Ton Club", ["Miremont", "Auterive", "Vernet", "Lagardelle", "Autre"])
        if st.button("S'inscrire"):
            if new_u and new_p:
                try:
                    supabase.table("users").insert({
                        "username": new_u, "password": new_p, 
                        "coins": 10, "club": new_club, "is_admin": False
                    }).execute()
                    st.success("Compte créé ! Connecte-toi à gauche.")
                except:
                    st.error("Erreur lors de l'inscription.")

# --- 6. INTERFACE PRINCIPALE (UNE FOIS CONNECTÉ) ---
else:
    user = st.session_state.user
    
    # Header du site
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.title(f"🎾 Tennis Bet 2026")
    with col_h2:
        st.metric("Ton Solde", f"{user['coins']} 🪙")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- ONGLETS HORIZONTAUX TOUT EN HAUT ---
    menu_labels = ["🏠 Accueil", "💰 Parier", "🏆 Classements", "🛡️ Guerre des Clubs"]
    if user.get('is_admin'):
        menu_labels.append("⚙️ Admin")
    
    tabs = st.tabs(menu_labels)

    # --- 🏠 ONGLET ACCUEIL ---
    with tabs[0]:
        st.header("Tableau de bord")
        col_m, col_s = st.columns([2, 1])
        
        with col_m:
            st.subheader("📺 Match en cours")
            st.info("Aucun match en direct. Repasse plus tard !")
            
            st.subheader("📅 Matchs du jour")
            st.write("- **14h30** : Pierre vs Paul (Court Central)")
            st.write("- **16h00** : Jacques vs Thomas (Court 2)")
            
            st.subheader("✅ Résultats récents")
            st.write("- **Hier** : Jules bat Antoine (6-2, 6-4)")

        with col_s:
            st.subheader("👑 Roi de la Perf")
            st.markdown(f"""
                <div style="background:#FFD700; padding:15px; border-radius:15px; color:black; text-align:center; border: 2px solid #DAA520;">
                    <span style="font-size: 1.2em;">⭐ <b>{user['username']}</b> ⭐</span><br>
                    <small>+30 coins sur le dernier match</small>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            st.subheader("🔥 Top du jour")
            st.success("1. Paul (+25)")
            st.success("2. Marc (+12)")
            
            st.subheader("💀 Flop du jour")
            st.error("1. Jacques (-10)")
            st.error("2. Thomas (-8)")

    # --- 💰 ONGLET PARIER ---
    with tabs[1]:
        st.header("💰 Placer un pari")
        st.write("Sélectionne un match pour miser tes coins.")
        st.info("L'administrateur n'a pas encore ouvert de paris.")

    # --- 🏆 ONGLET CLASSEMENTS ---
    with tabs[2]:
        st.header("🏆 Classement Général")
        df_users = get_all_users()
        if not df_users.empty:
            df_rank = df_users[['username', 'coins', 'club']].sort_values("coins", ascending=False)
            st.table(df_rank)

    # --- 🛡️ ONGLET CLUBS ---
    with tabs[3]:
        st.header("🛡️ La Guerre des Clubs")
        df_users = get_all_users()
        if not df_users.empty:
            guerre = df_users.groupby("club")["coins"].mean().sort_values(ascending=False).reset_index()
            guerre.columns = ["Club", "Moyenne de Coins"]
            
            st.bar_chart(data=guerre, x="Club", y="Moyenne de Coins", color="#E2001A")
            st.write("Classement détaillé par moyenne :")
            st.dataframe(guerre, use_container_width=True, hide_index=True)
            
            if guerre.iloc[0]['Club'] == user['club']:
                st.balloons()
                st.success(f"Ton club ({user['club']}) domine le tournoi ! 🔥")

    # --- ⚙️ ONGLET ADMIN ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("Panel Administrateur")
            st.subheader("Créer un match")
            j1 = st.text_input("Joueur 1")
            j2 = st.text_input("Joueur 2")
            if st.button("Ajouter le match"):
                st.success(f"Match {j1} vs {j2} créé !")
