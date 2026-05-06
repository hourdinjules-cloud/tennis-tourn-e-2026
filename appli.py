import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN "TENNISBET" ---
st.set_page_config(page_title="TennisBet", page_icon="🎾", layout="centered")

st.markdown("""
    <style>
    /* Fond noir total et suppression des éléments Streamlit */
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] {display:none;}
    .block-container {padding-bottom: 120px; padding-top: 20px;} 

    /* Identité TennisBet : Jaune et Blanc sur Noir */
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Impact', sans-serif; text-transform: uppercase; letter-spacing: 1px; }

    /* BARRE DE NAVIGATION FIXE (STYLE APP) */
    .fixed-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #121212;
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        border-top: 1px solid #333;
        z-index: 9999;
    }

    /* Style des boutons du menu bas */
    div.stButton > button {
        border-radius: 0px;
        background-color: transparent !important;
        border: none !important;
        color: #FFFFFF !important;
        font-size: 11px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        height: auto !important;
    }

    /* Cartes des Matchs */
    .match-box {
        background: #1A1A1A;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #333;
        text-align: center;
    }

    /* Input des mises */
    .stNumberInput input {
        background-color: #1A1A1A !important;
        color: white !important;
        border: 1px solid #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Paris"

# --- 3. ACCÈS ---
if st.session_state.user is None:
    st.title("TENNISBET 🎾")
    u = st.text_input("Prénom")
    p = st.text_input("Mot de passe", type="password")
    if st.button("SE CONNECTER"):
        res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
        if res.data:
            st.session_state.user = res.data[0]
            st.rerun()
    st.caption("Contacte l'admin pour obtenir tes accès.")

else:
    # Refresh des données pour éviter l'erreur NameError
    res_users = supabase.table("users").select("*").execute()
    df_all = pd.DataFrame(res_users.data)
    user = df_all[df_all['username'] == st.session_state.user['username']].iloc[0]

    # Header Pro
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <div style="font-size: 24px; font-weight: bold; color: #FFD700;">TENNISBET</div>
            <div style="background: #FFD700; color: black; padding: 6px 16px; border-radius: 25px; font-weight: 900;">
                {user['coins']} 🪙
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- PAGES ---
    if st.session_state.page == "Paris":
        st.subheader("🎾 Matchs en cours")
        res_m = supabase.table("matches").select("*").execute()
        
        if not res_m.data:
            st.info("Aucun match disponible pour le moment.")
        
        for m in res_m.data:
            st.markdown(f'<div class="match-box"><b>{m["tournament"]}</b></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button(f"{m['player1']}\n1.85", key=f"p1_{m['id']}"):
                st.session_state.bet_target = {"id": m['id'], "name": m['player1']}
            if c2.button(f"{m['player2']}\n1.85", key=f"p2_{m['id']}"):
                st.session_state.bet_target = {"id": m['id'], "name": m['player2']}
        
        if 'bet_target' in st.session_state:
            st.markdown("---")
            st.write(f"Mise sur : **{st.session_state.bet_target['name']}**")
            mise = st.number_input("Somme à parier", 1, int(user['coins']), 1)
            if st.button("🔥 PLACER LE PARI"):
                supabase.table("users").update({"coins": user['coins']-mise}).eq("username", user['username']).execute()
                st.balloons()
                st.success("Pari confirmé !")
                del st.session_state.bet_target
                st.rerun()

    elif st.session_state.page == "Stats":
        st.subheader("🏆 Classement Parieurs")
        lb = df_all[['username', 'coins', 'rank']].sort_values("coins", ascending=False)
        for i, row in lb.iterrows():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:15px; border-bottom:1px solid #222; align-items:center;">
                    <span><b>{row['username']}</b> <small style="color:#888;">({row['rank']})</small></span>
                    <span style="color:#FFD700; font-weight:bold; font-size:18px;">{row['coins']} 🪙</span>
                </div>
            """, unsafe_allow_html=True)

    elif st.session_state.page == "Admin":
        st.title("🛡️ ADMIN")
        with st.expander("➕ Ajouter un match"):
            t = st.text_input("Nom du Tournoi")
            j1 = st.text_input("Joueur 1")
            j2 = st.text_input("Joueur 2")
            if st.button("Mettre en ligne"):
                supabase.table("matches").insert({"player1":j1, "player2":j2, "tournament":t}).execute()
                st.rerun()

    # --- NAV BAR FIXE EN BAS (STYLE SMARTPHONE) ---
    st.markdown('<div class="fixed-nav">', unsafe_allow_html=True)
    nav_c1, nav_c2, nav_c3 = st.columns(3)
    
    with nav_c1:
        if st.button("🏠\nPARIS"):
            st.session_state.page = "Paris"
            st.rerun()
    with nav_c2:
        if st.button("📊\nLEADERBOARD"):
            st.session_state.page = "Stats"
            st.rerun()
    with nav_c3:
        if user.get('is_admin'):
            if st.button("⚙️\nADMIN"):
                st.session_state.page = "Admin"
                st.rerun()
        else:
            if st.button("🚪\nQUITTER"):
                st.session_state.user = None
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
