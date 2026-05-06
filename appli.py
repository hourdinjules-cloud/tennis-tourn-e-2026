import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

# --- 2. CONNEXION SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 3. FONCTIONS ---
def get_all_users():
    res = supabase.table("users").select("*").execute()
    return pd.DataFrame(res.data)

CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix"]

# --- 4. ACCÈS ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Tournoi 2026")
    t1, t2 = st.tabs(["Connexion", "S'inscrire"])
    
    with t1:
        u = st.text_input("Prénom", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Se connecter"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
            else: st.error("Identifiants incorrects.")

    with t2:
        new_u = st.text_input("Ton Prénom", key="reg_u")
        new_p = st.text_input("Mot de passe", type="password", key="reg_p")
        new_c = st.selectbox("Ton Club", CLUBS_OFFICIELS)
        if st.button("Créer mon compte"):
            try:
                supabase.table("users").insert({
                    "username": new_u, "password": new_p, "coins": 10, 
                    "club": new_c, "is_admin": False, 
                    "victoires_count": 0, "perf_count": 0
                }).execute()
                st.success("Compte créé ! Tu peux te connecter.")
            except Exception as e:
                st.error(f"Erreur : Vérifie que les colonnes SQL ont été créées.")

else:
    user = st.session_state.user
    df_all = get_all_users()
    
    # Header simple
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1: st.title("🎾 Tennis Bet 2026")
    with col_h2: 
        st.metric("Tes Coins", f"{user['coins']} 🪙")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- ONGLETS ---
    tabs = st.tabs(["🏠 Accueil", "💰 Parier", "🏆 Classements", "🛡️ Clubs", "⚙️ Admin" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📅 Matchs du jour")
            st.info("Aucun match publié par l'admin.")
        with c2:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty and "perf_count" in df_all.columns:
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                if roi['perf_count'] > 0:
                    st.success(f"🏆 {roi['username']} ({roi['club']}) : {roi['perf_count']} Perfs")
                else: st.write("Aucune perf encore.")

    # --- 🏆 CLASSEMENTS ---
    with tabs[2]:
        st.subheader("🎾 Classement des Perfs (Victoire vs mieux classé)")
        st.table(df_all[['username', 'perf_count', 'club']].sort_values("perf_count", ascending=False))
        st.subheader("🏆 Classement Général (Toutes victoires)")
        st.table(df_all[['username', 'victoires_count', 'club']].sort_values("victoires_count", ascending=False))

    # --- 🛡️ GUERRE DES CLUBS ---
    with tabs[3]:
        st.header("🛡️ La Guerre des Clubs")
        if not df_all.empty:
            guerre = df_all.groupby("club")["victoires_count"].sum().reindex(CLUBS_OFFICIELS, fill_value=0).reset_index()
            st.bar_chart(data=guerre, x="club", y="victoires_count", color="#E2001A")

    # --- ⚙️ ADMIN ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("Gestion des résultats")
            vainqueur = st.selectbox("Vainqueur du match", df_all['username'].tolist())
            type_v = st.radio("Type de gain", ["Victoire normale (+1)", "PERF (+1 Victoire ET +1 Perf)"])
            
            if st.button("Enregistrer la Victoire"):
                v_data = df_all[df_all['username'] == vainqueur].iloc[0]
                new_v = int(v_data.get('victoires_count', 0) + 1)
                updates = {"victoires_count": new_v}
                
                if "PERF" in type_v:
                    updates["perf_count"] = int(v_data.get('perf_count', 0) + 1)
                
                supabase.table("users").update(updates).eq("username", vainqueur).execute()
                st.success("Données mises à jour !")
                st.balloons()
