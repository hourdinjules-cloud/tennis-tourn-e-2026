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

def get_matches():
    res = supabase.table("matches").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(res.data)

CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix"]

# --- ACCÈS ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Tournoi 2026")
    t1, t2 = st.tabs(["Connexion", "S'inscrire"])
    with t1:
        u = st.text_input("Prénom")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
    with t2:
        nu, np = st.text_input("Ton Prénom"), st.text_input("Pass", type="password")
        nc = st.selectbox("Club", CLUBS_OFFICIELS)
        if st.button("S'inscrire"):
            supabase.table("users").insert({"username":nu,"password":np,"coins":10,"club":nc,"is_admin":False,"victoires_count":0,"perf_count":0}).execute()
            st.success("Ok !")

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

    tabs = st.tabs(["🏠 Accueil", "💰 Parier", "🏆 Classements", "🛡️ Clubs", "⚙️ Admin" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📅 Matchs à venir")
            df_m = get_matches()
            if not df_m.empty:
                for _, row in df_m.iterrows():
                    st.markdown(f"""
                        <div style="background:#262730; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 5px solid #E2001A;">
                            <b>{row['player1']}</b> ({row['club1']}) <span style="color:#E2001A;">VS</span> <b>{row['player2']}</b> ({row['club2']})
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun match prévu.")
        with c2:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty and df_all['perf_count'].max() > 0:
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                st.success(f"🏆 {roi['username']} ({roi['club']}) : {roi['perf_count']} Perfs")

    # --- 🏆 CLASSEMENTS ---
    with tabs[2]:
        st.subheader("🎾 Classement Perfs")
        st.table(df_all[['username', 'perf_count', 'club']].sort_values("perf_count", ascending=False))
        st.subheader("🏆 Classement Général")
        st.table(df_all[['username', 'victoires_count', 'club']].sort_values("victoires_count", ascending=False))

    # --- 🛡️ GUERRE DES CLUBS ---
    with tabs[3]:
        st.header("🛡️ La Guerre des Clubs")
        guerre = df_all.groupby("club")["victoires_count"].sum().reindex(CLUBS_OFFICIELS, fill_value=0).reset_index()
        st.bar_chart(data=guerre, x="club", y="victoires_count", color="#E2001A")

    # --- ⚙️ ADMIN ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("Panel Admin")
            
            # --- AJOUTER MATCH ---
            st.subheader("1. Ajouter un match à venir")
            col_a, col_b = st.columns(2)
            with col_a:
                nom1 = st.text_input("Joueur 1")
                club1 = st.selectbox("Club 1", CLUBS_OFFICIELS)
            with col_b:
                nom2 = st.text_input("Joueur 2")
                club2 = st.selectbox("Club 2", CLUBS_OFFICIELS)
            
            if st.button("Enregistrer le match"):
                if nom1 and nom2:
                    supabase.table("matches").insert({
                        "player1": nom1, "club1": club1, 
                        "player2": nom2, "club2": club2
                    }).execute()
                    st.success("Match ajouté sur l'accueil !")
                    st.rerun()

            st.divider()

            # --- VALIDER VICTOIRE ---
            st.subheader("2. Valider un résultat")
            vainqueur = st.selectbox("Vainqueur", df_all['username'].tolist())
            is_perf = st.checkbox("C'est une PERF")
            if st.button("Valider la victoire"):
                v_data = df_all[df_all['username'] == vainqueur].iloc[0]
                upd = {"victoires_count": int(v_data['victoires_count'] + 1)}
                if is_perf: upd["perf_count"] = int(v_data['perf_count'] + 1)
                supabase.table("users").update(upd).eq("username", vainqueur).execute()
                st.success("Victoire enregistrée !")
                st.balloons()
