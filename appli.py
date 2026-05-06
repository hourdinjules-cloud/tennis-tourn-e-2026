import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. INITIALISATION SÉCURISÉE ---
if 'user_connected' not in st.session_state:
    st.session_state.user_connected = None

# --- 2. CONNEXION BDD ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_users():
    try:
        return conn.read(worksheet="users", ttl=0)
    except:
        # Si la feuille est vide, on crée la structure de base
        return pd.DataFrame(columns=["username", "password", "coins", "is_admin", "club"])

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
        border-radius: 20px; font-weight: bold;
    }
    .stApp { margin-top: 50px; }
    .club-card {
        padding: 15px; border-radius: 10px; border: 1px solid #444; margin-bottom: 10px;
        background-color: rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AFFICHAGE DU HEADER ---
if st.session_state.user_connected:
    df_users = get_users()
    user_data = df_users[df_users['username'] == st.session_state.user_connected]
    if not user_data.empty:
        solde = user_data.iloc[0]['coins']
        st.markdown(f"""
            <div class="main-header">
                <div style="font-weight: bold; color: #E2001A;">🎾 TENNIS BET</div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span class="coins-badge">{round(float(solde), 1)} 🪙</span>
                    <span style="color: white;">👤 {st.session_state.user_connected}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- 5. LOGIQUE DES DROITS ---
is_admin = False
if st.session_state.user_connected:
    df_users = get_users()
    user_row = df_users[df_users['username'] == st.session_state.user_connected]
    if not user_row.empty:
        is_admin = user_row.iloc[0].get('is_admin', False)

# --- 6. CRÉATION DES ONGLETS ---
tabs_list = ["🏠 Accueil", "💰 Parier", "🏆 Classement", "⚔️ Guerre des Clubs"]
if is_admin:
    tabs_list.append("⚙️ Admin")

tabs = st.tabs(tabs_list)

with tabs[0]:
    st.title("Tournoi de Tennis 2026")
    st.write("Bienvenue ! Crée ton compte dans la barre de gauche pour recevoir tes 10 premiers coins.")

with tabs[1]:
    st.header("💰 Paris Sportifs")
    if not st.session_state.user_connected:
        st.warning("Connecte-toi pour voir les cotes.")
    else:
        st.info("Les matchs arriveront dès que l'admin les aura créés.")

with tabs[2]:
    st.header("🏆 Classement Individuel")
    df_users = get_users()
    if not df_users.empty:
        st.dataframe(df_users[['username', 'coins', 'club']].sort_values("coins", ascending=False), use_container_width=True)

with tabs[3]:
    st.header("⚔️ La Guerre des Clubs")
    df_users = get_users()
    if not df_users.empty and 'club' in df_users.columns:
        stats_clubs = df_users.groupby('club')['coins'].sum().reset_index()
        for _, row in stats_clubs.iterrows():
            st.markdown(f"""
                <div class="club-card">
                    <h3 style='margin:0;'>{row['club']}</h3>
                    <p style='font-size:20px; color:#FFD700;'>{round(row['coins'], 1)} points cumulés</p>
                </div>
                """, unsafe_allow_html=True)

if is_admin:
    with tabs[len(tabs_list)-1]:
        st.header("⚙️ Zone Administrateur")
        st.write("Gestion des matchs et des utilisateurs.")

# --- 7. SIDEBAR (CONNEXION & INSCRIPTION) ---
with st.sidebar:
    if st.session_state.user_connected:
        st.success(f"Connecté : {st.session_state.user_connected}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        mode = st.radio("Compte", ["Connexion", "Créer un compte"])
        u_name = st.text_input("Prénom (ou Pseudo)")
        u_pwd = st.text_input("Mot de passe", type="password")
        
        if mode == "Créer un compte":
            u_club = st.selectbox("Ton Club", ["Club A", "Club B", "Indépendant"])
            if st.button("S'inscrire"):
                df_users = get_users()
                if u_name in df_users['username'].values:
                    st.error("Ce nom est déjà pris !")
                elif u_name == "" or u_pwd == "":
                    st.error("Remplis tous les champs !")
                else:
                    # Création du nouvel utilisateur
                    new_user = pd.DataFrame([{
                        "username": u_name, 
                        "password": str(u_pwd), 
                        "coins": 10.0, 
                        "is_admin": False, 
                        "club": u_club
                    }])
                    updated_df = pd.concat([df_users, new_user], ignore_index=True)
                    conn.update(worksheet="users", data=updated_df)
                    st.success("Compte créé ! Tu peux maintenant te connecter.")
        
        else:
            if st.button("Se connecter"):
                df_users = get_users()
                check = df_users[(df_users['username'] == u_name) & (df_users['password'] == str(u_pwd))]
                if not check.empty:
                    st.session_state.user_connected = u_name
                    st.rerun()
                else:
                    st.error("Mauvais identifiants")
