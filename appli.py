import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
    .match-card { background: #1f2937; padding: 15px; border-radius: 12px; border-left: 6px solid #E2001A; margin-bottom: 10px; }
    .bet-ticket { background: #1f2937; padding: 20px; border-radius: 15px; border: 2px solid #E2001A; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state: st.session_state.user = None
if 'active_bet' not in st.session_state: st.session_state.active_bet = None
if 'mise_actuelle' not in st.session_state: st.session_state.mise_actuelle = 1

LISTE_RANGS = ["NC", "40", "30/5", "30/4", "30/3", "30/2", "30/1", "30", "15/5", "15/4", "15/3", "15/2", "15/1", "15"]
CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix", "Extérieur"]

# --- 3. INTERFACE CONNEXION ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Miremont 2026")
    t_login, t_reg = st.tabs(["🔐 Connexion", "📝 Créer un compte"])
    
    with t_login:
        u = st.text_input("Prénom")
        p = st.text_input("Pass", type="password")
        if st.button("Se connecter"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()

    with t_reg:
        new_u = st.text_input("Ton Prénom")
        new_p = st.text_input("Mot de passe ", type="password")
        new_c = st.selectbox("Club", CLUBS_OFFICIELS)
        new_r = st.selectbox("Ton Classement", LISTE_RANGS)
        if st.button("S'inscrire"):
            supabase.table("users").insert({
                "username": new_u, "password": new_p, "club": new_c, "rank": new_r,
                "coins": 10, "victoires_count": 0, "perf_count": 0, "is_admin": False
            }).execute()
            st.success("Compte créé ! Connecte-toi.")

# --- 4. INTERFACE PRINCIPALE ---
else:
    # Refresh user data
    res_u = supabase.table("users").select("*").eq("username", st.session_state.user['username']).execute()
    user = res_u.data[0]
    df_all = pd.DataFrame(supabase.table("users").select("*").execute().data)

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1: 
        st.title(f"🎾 {user['username']} ({user['rank']})")
    with col_h2: 
        st.metric("💰 Solde", f"{user['coins']} 🪙")
        if st.button("Déconnexion"): st.session_state.user = None; st.rerun()

    tabs = st.tabs(["🏠 ACCUEIL", "💰 PARIER", "🏆 CLASSEMENTS", "⚙️ ADMIN" if user.get('is_admin') else " "])

    # --- ACCUEIL & PARIS (Simplifiés pour l'exemple) ---
    with tabs[0]:
        st.subheader("📅 Matchs à venir")
        res_m = supabase.table("matches").select("*").execute()
        if res_m.data:
            for m in res_m.data:
                st.markdown(f'<div class="match-card">{m["player1"]} vs {m["player2"]} ({m["tournament"]})</div>', unsafe_allow_html=True)

    # --- ADMIN (GESTION MANUELLE DES INCONNUS) ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("🛠 Panel Admin")
            
            # 1. CRÉATION DE MATCH (Libre)
            with st.expander("➕ Créer un Match (Joueurs Inscrits ou Inconnus)"):
                t_n = st.text_input("Nom du Tournoi")
                col1, col2 = st.columns(2)
                with col1:
                    j1_mode = st.radio("Joueur 1 :", ["Inscrit", "Inconnu"], key="j1m")
                    j1_name = st.selectbox("Choisir J1", df_all['username'].tolist()) if j1_mode == "Inscrit" else st.text_input("Nom J1 Inconnu")
                with col2:
                    j2_mode = st.radio("Joueur 2 :", ["Inscrit", "Inconnu"], key="j2m")
                    j2_name = st.selectbox("Choisir J2", df_all['username'].tolist()) if j2_mode == "Inscrit" else st.text_input("Nom J2 Inconnu")
                
                if st.button("Publier le match"):
                    supabase.table("matches").insert({
                        "player1": j1_name, "player2": j2_name, "tournament": t_n
                    }).execute()
                    st.success("Match ajouté !")

            # 2. VALIDATION PERF MANUELLE
            st.divider()
            st.subheader("✅ Valider une Victoire & Perf")
            
            # On sélectionne obligatoirement un gagnant INSCRIT (pour lui donner les points)
            gagnant_inscrit = st.selectbox("Joueur du stage qui a gagné :", df_all['username'].tolist())
            
            # On définit l'adversaire (qui peut être n'importe qui)
            adv_name = st.text_input("Nom de l'adversaire battu")
            adv_rank = st.selectbox("Classement de l'adversaire :", LISTE_RANGS)
            
            if st.button("Enregistrer la Victoire"):
                g_data = df_all[df_all['username'] == gagnant_inscrit].iloc[0]
                
                # Calcul de la Perf
                idx_g = LISTE_RANGS.index(g_data['rank'])
                idx_adv = LISTE_RANGS.index(adv_rank)
                
                is_perf = idx_g < idx_adv # Gagnant moins fort que l'adversaire
                
                new_v = int(g_data['victoires_count'] + 1)
                new_p = int(g_data['perf_count'] + (1 if is_perf else 0))
                
                supabase.table("users").update({
                    "victoires_count": new_v, 
                    "perf_count": new_p
                }).eq("username", gagnant_inscrit).execute()
                
                if is_perf:
                    st.balloons()
                    st.success(f"🔥 PERF ! {gagnant_inscrit} ({g_data['rank']}) bat {adv_name} ({adv_rank}) !")
                else:
                    st.success(f"Victoire enregistrée pour {gagnant_inscrit}.")
