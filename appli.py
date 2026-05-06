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

CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix"]

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
    
    st.subheader("S'inscrire")
    new_u = st.text_input("Ton Prénom")
    new_p = st.text_input("Mot de passe", type="password")
    new_c = st.selectbox("Ton Club", CLUBS_OFFICIELS)
    if st.button("Créer mon compte"):
        supabase.table("users").insert({
            "username": new_u, "password": new_p, "coins": 10, 
            "club": new_c, "is_admin": False, 
            "victoires_count": 0, "perf_count": 0
        }).execute()
        st.success("Compte créé !")

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

    # --- ONGLETS ---
    tabs = st.tabs(["🏠 Accueil", "💰 Parier", "🏆 Classements", "🛡️ Guerre des Clubs", "⚙️ Admin" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL ---
    with tabs[0]:
        col_main, col_side = st.columns([2, 1])
        with col_main:
            st.subheader("📅 Matchs du jour")
            st.info("Utilisez l'onglet Admin pour publier des matchs.")

        with col_side:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty and df_all['perf_count'].max() > 0:
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                st.markdown(f"""
                    <div style="background:linear-gradient(135deg, #FFD700, #FFA500); padding:15px; border-radius:15px; color:black; text-align:center; font-weight:bold;">
                        🏆 {roi['username']}<br>{roi['perf_count']} Perfs réalisées !
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            st.subheader("🔥 Top du jour (Paris)")
            st.subheader("💀 Flop du jour (Paris)")

    # --- 🏆 CLASSEMENTS ---
    with tabs[2]:
        st.subheader("🎾 Classement des Perfs (Victoires à classement supérieur)")
        st.dataframe(df_all[['username', 'perf_count', 'club']].sort_values("perf_count", ascending=False), use_container_width=True, hide_index=True)
        
        st.subheader("🏆 Classement Général (Toutes victoires)")
        st.dataframe(df_all[['username', 'victoires_count', 'club']].sort_values("victoires_count", ascending=False), use_container_width=True, hide_index=True)

    # --- 🛡️ GUERRE DES CLUBS ---
    with tabs[3]:
        st.header("🛡️ La Guerre des Clubs")
        st.write("Somme de TOUTES les victoires par club.")
        if not df_all.empty:
            guerre = df_all.groupby("club")["victoires_count"].sum().reindex(CLUBS_OFFICIELS, fill_value=0).reset_index()
            st.bar_chart(data=guerre, x="club", y="victoires_count", color="#E2001A")
            st.table(guerre)

    # --- ⚙️ ADMIN ---
    if user.get('is_admin'):
        with tabs[4]:
            st.header("Panel Administrateur")
            
            # --- PUBLIER MATCH ---
            st.subheader("1. Match du jour")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Joueur A")
                st.selectbox("Club A", CLUBS_OFFICIELS)
            with col2:
                st.text_input("Joueur B")
                st.selectbox("Club B", CLUBS_OFFICIELS)
            st.button("Publier")

            st.divider()

            # --- ENREGISTRER RÉSULTAT ---
            st.subheader("2. Valider une Victoire")
            vainqueur = st.selectbox("Vainqueur", df_all['username'].tolist())
            type_v = st.radio("Type de victoire", ["Victoire normale", "PERF (Classement supérieur)"])
            
            if st.button("Enregistrer"):
                v_data = df_all[df_all['username'] == vainqueur].iloc[0]
                
                # Update Victoire (toujours +1)
                new_v = int(v_data['victoires_count'] + 1)
                up_dict = {"victoires_count": new_v}
                
                # Update Perf (seulement si coché)
                if type_v == "PERF (Classement supérieur)":
                    new_p = int(v_data['perf_count'] + 1)
                    up_dict["perf_count"] = new_p
                
                supabase.table("users").update(up_dict).eq("username", vainqueur).execute()
                st.success(f"Compteur mis à jour pour {vainqueur} !")
                st.balloons()
