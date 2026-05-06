import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN "TENNISBET" ---
st.set_page_config(page_title="TennisBet", page_icon="🎾", layout="centered")

# Injection CSS pour le style Winamax et la fixation des éléments
st.markdown("""
    <style>
    /* Fond noir total */
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] {display:none;}
    
    /* Titres Jaunes Impact */
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Impact', sans-serif; 
        text-transform: uppercase; 
        text-align: center;
    }

    /* Cartes de Matchs */
    .match-box {
        background: #1A1A1A;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #333;
        text-align: center;
        border-left: 5px solid #FFD700;
    }

    /* Boutons de Mise et Navigation */
    .stButton > button {
        width: 100%;
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #444 !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border-radius: 8px;
    }
    
    /* Hover bouton */
    .stButton > button:hover {
        border-color: #FFD700 !important;
        color: #FFD700 !important;
    }

    /* Barre de navigation en bas (on utilise des colonnes standards pour éviter les bugs de clic) */
    .nav-spacer { margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION SUPABASE ---
# Assure-toi que ces secrets sont configurés dans ton Streamlit Cloud
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# Initialisation des variables de session
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Paris"

LISTE_RANGS = ["NC", "40", "30/5", "30/4", "30/3", "30/2", "30/1", "30", "15/5", "15/4", "15/3", "15/2", "15/1", "15"]

# --- 3. SYSTÈME DE CONNEXION ---
if st.session_state.user is None:
    st.title("TENNISBET 🎾")
    u = st.text_input("Prénom")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
        if res.data:
            st.session_state.user = res.data[0]
            st.rerun()
    st.info("Utilise tes identifiants du stage pour parier.")

else:
    # Récupération des données fraîches à chaque refresh
    res_u = supabase.table("users").select("*").execute()
    df_all = pd.DataFrame(res_u.data)
    user = df_all[df_all['username'] == st.session_state.user['username']].iloc[0]

    # Header Mobile : Nom + Solde
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 20px; font-weight: bold;">{user['username']}</div>
            <div style="background: #FFD700; color: black; padding: 5px 15px; border-radius: 20px; font-weight: 900;">
                {user['coins']} 🪙
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. NAVIGATION PAR ONGLETS ---
    # Affichage du contenu selon la page sélectionnée
    
    if st.session_state.page == "Paris":
        st.subheader("🎾 Paris Disponibles")
        res_m = supabase.table("matches").select("*").execute()
        
        for m in res_m.data:
            st.markdown(f'<div class="match-box"><b>{m["tournament"]}</b></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button(f"{m['player1']} (1.85)", key=f"p1_{m['id']}"):
                if user['coins'] >= 1:
                    supabase.table("users").update({"coins": user['coins']-1}).eq("username", user['username']).execute()
                    st.toast(f"Pari de 1🪙 placé sur {m['player1']} !")
                    st.rerun()
                else: st.error("Pas assez de coins !")
            
            if c2.button(f"{m['player2']} (1.85)", key=f"p2_{m['id']}"):
                if user['coins'] >= 1:
                    supabase.table("users").update({"coins": user['coins']-1}).eq("username", user['username']).execute()
                    st.toast(f"Pari de 1🪙 placé sur {m['player2']} !")
                    st.rerun()
                else: st.error("Pas assez de coins !")

    elif st.session_state.page == "Stats":
        st.subheader("🏆 Classement des Coins")
        # On trie par Coins pour voir qui est le meilleur parieur
        lb = df_all[['username', 'coins', 'rank']].sort_values("coins", ascending=False)
        for i, row in lb.iterrows():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:12px; border-bottom:1px solid #222;">
                    <span><b>{row['username']}</b> <small>({row['rank']})</small></span>
                    <span style="color:#FFD700; font-weight:bold;">{row['coins']} 🪙</span>
                </div>
            """, unsafe_allow_html=True)

    elif st.session_state.page == "Admin" and user.get('is_admin'):
        st.subheader("⚙️ Panel Admin")
        with st.expander("➕ Créer un Match"):
            t = st.text_input("Nom du Tournoi")
            j1 = st.text_input("Joueur 1")
            j2 = st.text_input("Joueur 2")
            if st.button("Publier le match"):
                supabase.table("matches").insert({"player1":j1, "player2":j2, "tournament":t}).execute()
                st.rerun()

        with st.expander("✅ Valider Résultat & Perf"):
            gagnant = st.selectbox("Vainqueur", df_all['username'].tolist())
            p_rank = st.selectbox("Classement de l'adversaire (pour Perf)", LISTE_RANGS)
            if st.button("Clôturer le match"):
                # Ici on peut ajouter la logique de gain de coins pour les parieurs
                st.success("Résultat enregistré !")

    # --- 5. BARRE DE NAVIGATION FIXE (VRAIS BOUTONS) ---
    st.markdown('<div class="nav-spacer"></div>', unsafe_allow_html=True)
    st.divider()
    nav1, nav2, nav3 = st.columns(3)
    
    with nav1:
        if st.button("🏠 PARIS"):
            st.session_state.page = "Paris"
            st.rerun()
    with nav2:
        if st.button("🏆 COINS"):
            st.session_state.page = "Stats"
            st.rerun()
    with nav3:
        if user.get('is_admin'):
            if st.button("⚙️ ADMIN"):
                st.session_state.page = "Admin"
                st.rerun()
        else:
            if st.button("🚪 SORTIR"):
                st.session_state.user = None
                st.rerun()
        st.rerun()
