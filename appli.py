import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN MOBILE DARK ---
st.set_page_config(page_title="TennisBet", page_icon="🎾", layout="centered")

st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Cacher le menu Streamlit et le header pour faire "App" */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style Winamax : Noir et Jaune */
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Impact', sans-serif; text-transform: uppercase; }
    
    /* Boutons de Paris */
    .stButton > button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        height: 50px;
        font-weight: bold;
    }
    .stButton > button:hover { border: 1px solid #FFD700 !important; color: #FFD700 !important; }

    /* Barre de Navigation en Bas (Simulée) */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #121212;
        border-top: 2px solid #FFD700;
        display: flex;
        justify-content: space-around;
        padding: 10px 0;
        z-index: 1000;
    }

    /* Cards de matchs */
    .match-box {
        background-color: #1A1A1A;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-bottom: 2px solid #333;
    }
    
    /* Classement Coins */
    .rank-item {
        display: flex;
        justify-content: space-between;
        padding: 10px;
        border-bottom: 1px solid #222;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Paris"

LISTE_RANGS = ["NC", "40", "30/5", "30/4", "30/3", "30/2", "30/1", "30", "15/5", "15/4", "15/3", "15/2", "15/1", "15"]

# --- 3. LOGIQUE CONNEXION ---
if st.session_state.user is None:
    st.title("WINAMIREMONT 🎾")
    t1, t2 = st.tabs(["LOG IN", "SIGN UP"])
    with t1:
        u = st.text_input("Prénom")
        p = st.text_input("Pass", type="password")
        if st.button("SE CONNECTER"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Prénom")
        np = st.text_input("Mdp", type="password")
        nr = st.selectbox("Classement", LISTE_RANGS)
        if st.button("CRÉER COMPTE"):
            supabase.table("users").insert({"username":nu, "password":np, "rank":nr, "coins":50}).execute()
            st.success("Compte prêt ! Connecte-toi.")

# --- 4. APP INTERFACE ---
else:
    # Refresh data
    res_u = supabase.table("users").select("*").eq("username", st.session_state.user['username']).execute()
    user = res_u.data[0]
    
    # Header Mobile
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
            <span style="font-size: 20px; font-weight: bold;">{user['username']}</span>
            <span style="background: #FFD700; color: black; padding: 5px 12px; border-radius: 20px; font-weight: bold;">
                {user['coins']} 🪙
            </span>
        </div>
    """, unsafe_allow_html=True)

    # --- NAVIGATION BASSE (Simulée avec des boutons) ---
    st.divider()
    
    # Contenu selon la page
    if st.session_state.page == "🏠 Paris":
        st.subheader("Matchs en direct / à venir")
        res_m = supabase.table("matches").select("*").execute()
        for m in res_m.data:
            with st.container():
                st.markdown(f"""<div class="match-box"><b>{m['tournament']}</b></div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button(f"{m['player1']}\n1.85", key=f"p1_{m['id']}"):
                    st.session_state.bet_target = {"id": m['id'], "name": m['player1']}
                if c2.button(f"{m['player2']}\n1.85", key=f"p2_{m['id']}"):
                    st.session_state.bet_target = {"id": m['id'], "name": m['player2']}
        
        # Overlay de pari si sélectionné
        if 'bet_target' in st.session_state:
            st.markdown("---")
            st.warning(f"Parier sur : {st.session_state.bet_target['name']}")
            mise = st.number_input("Somme à miser", min_value=1, max_value=user['coins'], value=1)
            if st.button("CONFIRMER LE PARI"):
                if user['coins'] >= mise:
                    new_coins = user['coins'] - mise
                    supabase.table("users").update({"coins": new_coins}).eq("username", user['username']).execute()
                    # Enregistrer le pari ici (table bets)
                    st.success("Pari placé !")
                    del st.session_state.bet_target
                    st.rerun()

    elif st.session_state.page == "🏆 Leaderboard":
        st.subheader("Classement des parieurs")
        df_all = pd.DataFrame(supabase.table("users").select("username", "coins", "rank").execute().data)
        df_all = df_all.sort_values("coins", ascending=False)
        
        for i, row in df_all.iterrows():
            st.markdown(f"""
                <div class="rank-item">
                    <span><b>{row['username']}</b> ({row['rank']})</span>
                    <span style="color:#FFD700;">{row['coins']} 🪙</span>
                </div>
            """, unsafe_allow_html=True)

    elif st.session_state.page == "⚙️ Admin" and user.get('is_admin'):
        st.subheader("Panel Admin")
        with st.expander("Créer un match"):
            t = st.text_input("Tournoi")
            j1 = st.text_input("Joueur 1")
            j2 = st.text_input("Joueur 2")
            if st.button("Publier"):
                supabase.table("matches").insert({"player1":j1, "player2":j2, "tournament":t}).execute()
                st.rerun()
        
        with st.expander("Valider Résultat & Perf"):
            gagnant = st.selectbox("Qui a gagné ?", df_all['username'].tolist())
            # Choix du perdant pour le calcul de la perf
            type_adv = st.radio("Adversaire :", ["Inscrit", "Extérieur"])
            if type_adv == "Inscrit":
                perdant = st.selectbox("Perdant", df_all['username'].tolist())
                p_rank = df_all[df_all['username']==perdant].iloc[0]['rank']
            else:
                perdant = st.text_input("Nom Inconnu")
                p_rank = st.selectbox("Son classement", LISTE_RANGS)
            
            if st.button("Clôturer le match"):
                # Ici tu peux ajouter la logique pour créditer les coins aux gagnants des paris
                st.success("Résultat enregistré !")

    # BARRE DE NAVIGATION FIXE EN BAS (HTML/CSS)
    # Comme Streamlit ne permet pas de vrais boutons fixes facilement, on utilise des colonnes en bas
    st.write("<br><br><br>", unsafe_allow_html=True) # Espace pour ne pas cacher le contenu
    
    # Navigation simulant une App
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        if st.button("🏠 Paris"): st.session_state.page = "🏠 Paris"; st.rerun()
    with nav_col2:
        if st.button("🏆 Coins"): st.session_state.page = "🏆 Leaderboard"; st.rerun()
    with nav_col3:
        if user.get('is_admin'):
            if st.button("⚙️ Admin"): st.session_state.page = "⚙️ Admin"; st.rerun()
        else:
            if st.button("🚪 Logout"): st.session_state.user = None; st.rerun()
