import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

# --- CONNEXION ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state:
    st.session_state.user = None

# --- FONCTIONS ---
def get_all_users():
    res = supabase.table("users").select("*").execute()
    return pd.DataFrame(res.data)

# --- ACCÈS ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Tournoi 2026")
    u = st.sidebar.text_input("Prénom")
    p = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("Connexion"):
        res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
        if res.data:
            st.session_state.user = res.data[0]
            st.rerun()
    # Option Inscription simplifiée ici...

else:
    user = st.session_state.user
    df_all = get_all_users()
    
    # Header
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1: st.title("🎾 Tennis Bet 2026")
    with col_h2: 
        st.metric("Tes Coins", f"{user['coins']} 🪙")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- ONGLETS TOUT EN HAUT ---
    tabs = st.tabs(["🏠 Accueil", "💰 Parier", "🏆 Classements", "🛡️ Clubs", "⚙️ Admin" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL ---
    with tabs[0]:
        col_main, col_side = st.columns([2, 1])
        with col_main:
            st.subheader("📺 Match en cours")
            st.divider()
            st.subheader("📅 Matchs du jour")
            st.info("Aucun match publié.")

        with col_side:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty:
                # On récupère celui qui a le plus de perf_count
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                st.markdown(f"""
                    <div style="background:linear-gradient(135deg, #FFD700, #FFA500); padding:20px; border-radius:15px; color:black; text-align:center; font-weight:bold;">
                        <span style="font-size:40px;">🏆</span><br>
                        <span style="font-size:24px;">{roi['username']}</span><br>
                        <span style="font-size:18px;">{roi['perf_count']} Victoires</span><br>
                        <small>Club : {roi['club']}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            st.subheader("🔥 Top du jour (Paris)")
            st.subheader("💀 Flop du jour (Paris)")

    # --- 🏆 CLASSEMENTS ---
    with tabs[2]:
        st.header("🏆 Classement Individuel")
        st.write("Classement basé sur les coins (Paris).")
        st.dataframe(df_all[['username', 'coins', 'club']].sort_values("coins", ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()
        st.header("🎾 Classement des Perfs")
        st.write("Nombre de matchs gagnés sur le terrain.")
        st.dataframe(df_all[['username', 'perf_count', 'club']].sort_values("perf_count", ascending=False), use_container_width=True, hide_index=True)

    # --- 🛡️ CLUBS ---
    with tabs[3]:
        st.header("🛡️ La Guerre des Clubs")
        guerre = df_all.groupby("club")["coins"].mean().sort_values(ascending=False).reset_index()
        st.bar_chart(data=guerre, x="club", y="coins")

    # --- ⚙️ ADMIN ---
    if user.get('is_admin'):
        with tabs[4]:
            st.header("Panel Administrateur")
            
            # --- BLOC VALIDATION RÉSULTAT ---
            st.subheader("✅ Valider un Résultat de Match")
            st.write("Cela ajoutera +1 au compteur de performance du vainqueur.")
            
            vainqueur = st.selectbox("Qui a gagné son match ?", df_all['username'].tolist())
            score_final = st.text_input("Score final (ex: 6-4 6-2)")
            
            if st.button("Confirmer la victoire"):
                # 1. Récupérer les infos actuelles du vainqueur
                v_data = df_all[df_all['username'] == vainqueur].iloc[0]
                nouveau_compte = v_data['perf_count'] + 1
                
                # 2. Update dans Supabase
                supabase.table("users").update({"perf_count": nouveau_compte}).eq("username", vainqueur).execute()
                
                st.success(f"Bravo ! {vainqueur} a maintenant {nouveau_compte} victoires au compteur.")
                st.balloons()
