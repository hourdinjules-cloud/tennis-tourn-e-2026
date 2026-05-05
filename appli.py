import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
PASSWORD_ADMIN = "tennis2026"
CLASSEMENTS = {"NC": 0, "40": 1, "30/5": 2, "30/4": 3, "30/2": 4, "30/3": 5, "30/2": 6, "30/1": 7, "30": 8, "15/5": 9, "15/4": 10, "15/3": 11, "15/2": 12, "15/1": 13, "15": 14, "5/6": 15, "4/6": 16, "3/6": 17, "2/6": 18, "1/6": 19, "0": 20}

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_users():
    try:
        return conn.read(worksheet="users", ttl=0)
    except:
        return pd.DataFrame(columns=["username", "password", "coins", "last_bonus"])

def save_users(df):
    conn.update(worksheet="users", data=df)

# --- INITIALISATION SESSION ---
if 'user_connected' not in st.session_state: st.session_state.user_connected = None
if 'matchs' not in st.session_state: st.session_state.matchs = []
if 'paris' not in st.session_state: st.session_state.paris = []
if 'clubs' not in st.session_state: st.session_state.clubs = ["Club A", "Club B"]
if 'club_scores' not in st.session_state: st.session_state.club_scores = {}
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212"
if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"

# --- DESIGN CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color}; color: {st.session_state.text_color}; }}
    .winamax-card {{ background-color: rgba(255,255,255,0.05); border: 1px solid {st.session_state.text_color}; border-radius: 15px; padding: 15px; margin-bottom: 15px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (COMPTES) ---
with st.sidebar:
    st.title("👤 Mon Espace")
    df_users = get_users()
    
    if st.session_state.user_connected is None:
        mode = st.radio("Action", ["Connexion", "Inscription"])
        u_name = st.text_input("Prénom")
        u_pwd = st.text_input("MDP", type="password")
        
        if st.button("Valider"):
            if mode == "Inscription":
                if u_name in df_users['username'].values: st.error("Prénom déjà pris")
                else:
                    new_user = pd.DataFrame([{"username": u_name, "password": str(u_pwd), "coins": 10.0, "last_bonus": "Jamais"}])
                    df_users = pd.concat([df_users, new_user], ignore_index=True)
                    save_users(df_users)
                    st.success("Inscrit ! Connecte-toi.")
            else:
                user_row = df_users[(df_users['username'] == u_name) & (df_users['password'] == str(u_pwd))]
                if not user_row.empty:
                    st.session_state.user_connected = u_name
                    st.rerun()
                else: st.error("Erreur identifiants")
    else:
        st.write(f"Bonjour **{st.session_state.user_connected}**")
        solde = df_users.loc[df_users['username'] == st.session_state.user_connected, 'coins'].values[0]
        st.metric("Mon Solde", f"{round(float(solde), 1)} 🪙")
        if st.button("Déconnexion"):
            st.session_state.user_connected = None
            st.rerun()

# --- ONGLETS ---
tab_home, tab_parier, tab_ranking, tab_admin = st.tabs(["🏠 Accueil", "💰 Parier", "🏆 Classement", "⚙️ Admin"])

with tab_home:
    st.subheader("🎾 Résultats du Jour")
    matchs_finis = [m for m in st.session_state.matchs if m['fini']]
    if not matchs_finis: st.write("Aucun résultat pour le moment.")
    for m in matchs_finis:
        st.success(f"**{m['j1']}** {m['score']} **{m['j2']}** (Vainqueur : {m['vainqueur']})")

with tab_parier:
    if st.session_state.user_connected:
        match_dispo = [i for i, m in enumerate(st.session_state.matchs) if not m['fini']]
        for i in match_dispo:
            m = st.session_state.matchs[i]
            st.markdown(f"<div class='winamax-card'><h3>{m['j1']} vs {m['j2']}</h3><p>Cotes : {m['ct1']} | {m['ct2']}</p></div>", unsafe_allow_html=True)
            # Logique de pari... (simplifiée pour le gain de place)
    else: st.warning("Connecte-toi pour parier !")

with tab_ranking:
    st.subheader("🏆 Classement")
    st.dataframe(df_users[['username', 'coins']].sort_values("coins", ascending=False))

with tab_admin:
    if st.text_input("Code Admin", type="password") == PASSWORD_ADMIN:
        st.session_state.bg_color = st.color_picker("Couleur Fond", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("Couleur Texte", st.session_state.text_color)
        # Boutons pour créer des matchs ici...
