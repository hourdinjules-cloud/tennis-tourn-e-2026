import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN MOBILE DARK ---
st.set_page_config(page_title="Winamiremont", page_icon="🎾", layout="centered")

st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] {display:none;}
    
    /* Style Winamax */
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Impact', sans-serif; }
    
    /* Boutons de Paris */
    .stButton > button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        height: 60px;
        font-weight: bold;
        font-size: 18px;
    }
    
    /* Navbar fixe en bas */
    .footer-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #121212;
        display: flex;
        justify-content: space-around;
        padding: 10px 0;
        border-top: 2px solid #FFD700;
        z-index: 999;
    }

    /* Cards */
    .match-box {
        background-color: #1A1A1A;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        border-left: 4px solid #FFD700;
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

# --- 3. GESTION CONNEXION ---
if st.session_state.user is None:
    st.title("WINAMIREMONT 🎾")
    t1, t2 = st.tabs(["LOG IN", "SIGN UP"])
    with t1:
        u = st.text_input("Prénom")
        p = st.text_input("Mdp", type="password")
        if st.button("SE CONNECTER"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Prénom")
        np = st.text_input("Pass", type="password")
        nr = st.selectbox("Classement", LISTE_RANGS)
        if st.button("CRÉER COMPTE"):
            supabase.table("users").insert({"username":nu, "password":np, "rank":nr, "coins":10, "victoires_count":0, "perf_count":0}).execute()
            st.success("Compte créé !")
else:
    # --- RÉCUPÉRATION DES DONNÉES (Fix NameError) ---
    res_users = supabase.table("users").select("*").execute()
    df_all = pd.DataFrame(res_users.data)
    user = df_all[df_all['username'] == st.session_state.user['username']].iloc[0]

    # Header
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom:20px;">
            <h2 style="margin:0;">{user['username']}</h2>
            <div style="background:#FFD700; color:black; padding:5px 15px; border-radius:15px; font-weight:bold; font-size:20px;">
                {user['coins']} 🪙
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- PAGES ---
    if st.session_state.page == "🏠 Paris":
        st.subheader("PARIS DISPONIBLES")
        res_m = supabase.table("matches").select("*").execute()
        for m in res_m.data:
            st.markdown(f'<div class="match-box">{m["tournament"]}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button(f"{m['player1']}\n1.85", key=f"p1_{m['id']}"):
                st.session_state.bet = {"id": m['id'], "name": m['player1']}
            if c2.button(f"{m['player2']}\n1.85", key=f"p2_{m['id']}"):
                st.session_state.bet = {"id": m['id'], "name": m['player2']}
        
        if 'bet' in st.session_state:
            st.divider()
            st.write(f"Ton pari : **{st.session_state.bet['name']}**")
            mise = st.number_input("Mise", 1, int(user['coins']), 1)
            if st.button("VALIDER LE PARI"):
                supabase.table("users").update({"coins": user['coins']-mise}).eq("username", user['username']).execute()
                st.success("C'est parti !")
                del st.session_state.bet
                st.rerun()

    elif st.session_state.page == "🏆 Classement":
        st.subheader("CLASSEMENT COINS")
        # Classement par jetons (Coins)
        leaderboard = df_all[['username', 'coins', 'rank']].sort_values("coins", ascending=False)
        for i, row in leaderboard.iterrows():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #222;">
                    <span><b>{row['username']}</b> ({row['rank']})</span>
                    <span style="color:#FFD700;">{row['coins']} 🪙</span>
                </div>
            """, unsafe_allow_html=True)

    elif st.session_state.page == "⚙️ Admin":
        st.title("PANEL ADMIN")
        with st.expander("Créer un match"):
            t = st.text_input("Tournoi")
            j1 = st.text_input("J1")
            j2 = st.text_input("J2")
            if st.button("Ajouter Match"):
                supabase.table("matches").insert({"player1":j1, "player2":j2, "tournament":t}).execute()
                st.rerun()

        with st.expander("Valider Résultat & Perf"):
            # Ici df_all existe bien maintenant !
            gagnant = st.selectbox("Vainqueur", df_all['username'].tolist())
            mode_adv = st.radio("Adversaire", ["Inscrit", "Inconnu"])
            
            if mode_adv == "Inscrit":
                perdant = st.selectbox("Perdant", df_all['username'].tolist())
                p_rank = df_all[df_all['username'] == perdant].iloc[0]['rank']
            else:
                perdant = st.text_input("Nom de l'inconnu")
                p_rank = st.selectbox("Son classement", LISTE_RANGS)

            if st.button("Clôturer"):
                # Logique de Perf
                idx_g = LISTE_RANGS.index(user['rank'])
                idx_p = LISTE_RANGS.index(p_rank)
                is_perf = idx_g < idx_p
                
                # Mise à jour des stats (Optionnel selon ton besoin)
                supabase.table("users").update({
                    "victoires_count": int(user['victoires_count']+1),
                    "perf_count": int(user['perf_count'] + (1 if is_perf else 0))
                }).eq("username", gagnant).execute()
                st.success("Match terminé !")

    # --- BARRE DE NAVIGATION (Bas de l'écran) ---
    st.write("<br><br><br><br>", unsafe_allow_html=True)
    
    # On utilise des colonnes Streamlit en bas du code
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("🏠 PARIS"): st.session_state.page = "🏠 Paris"; st.rerun()
    with nav2:
        if st.button("🏆 COINS"): st.session_state.page = "🏆 Classement"; st.rerun()
    with nav3:
        if user.get('is_admin'):
            if st.button("⚙️ ADMIN"): st.session_state.page = "⚙️ Admin"; st.rerun()
        else:
            if st.button("🚪 LOGOUT"): st.session_state.user = None; st.rerun()
