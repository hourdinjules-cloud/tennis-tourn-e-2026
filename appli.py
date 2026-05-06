import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

# Injection CSS pour le look Winamax
st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
    .match-card { background: #1f2937; padding: 15px; border-radius: 12px; border-left: 6px solid #E2001A; margin-bottom: 10px; }
    .tournament-header { background: #2d3748; padding: 8px 15px; border-radius: 8px; color: #fbd38d; font-weight: bold; margin: 20px 0 10px 0; border: 1px solid #4a5568; }
    .bet-ticket { background: #1f2937; padding: 20px; border-radius: 15px; border: 2px solid #E2001A; box-shadow: 0 4px 15px rgba(226, 0, 26, 0.2); }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# Initialisation des variables de session
if 'user' not in st.session_state: st.session_state.user = None
if 'active_bet' not in st.session_state: st.session_state.active_bet = None
if 'mise_actuelle' not in st.session_state: st.session_state.mise_actuelle = 1

# --- 3. FONCTIONS ---
def get_all_users():
    res = supabase.table("users").select("*").execute()
    return pd.DataFrame(res.data)

def get_matches():
    res = supabase.table("matches").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(res.data)

CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix"]

# --- 4. INTERFACE DE CONNEXION / INSCRIPTION ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Miremont 2026")
    
    tab_login, tab_register = st.tabs(["🔐 Connexion", "📝 Créer un compte"])
    
    with tab_login:
        u = st.text_input("Prénom (Identifiant)")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("Utilisateur introuvable ou mauvais mot de passe.")

    with tab_register:
        st.subheader("Rejoindre le tournoi")
        new_u = st.text_input("Ton Prénom")
        new_p = st.text_input("Choisis un mot de passe", type="password")
        new_c = st.selectbox("Ton Club", CLUBS_OFFICIELS)
        if st.button("S'inscrire"):
            if new_u and new_p:
                try:
                    supabase.table("users").insert({
                        "username": new_u, "password": new_p, "coins": 10, 
                        "club": new_c, "is_admin": False, 
                        "victoires_count": 0, "perf_count": 0
                    }).execute()
                    st.success("Compte créé avec succès ! Connecte-toi sur l'onglet d'à côté.")
                except:
                    st.error("Erreur : Ce prénom est déjà pris ou la base de données n'est pas prête.")
            else:
                st.warning("Remplis tous les champs !")

# --- 5. INTERFACE PRINCIPALE (Connecté) ---
else:
    # REFRESH AUTO : Correction de la KeyError en utilisant 'username'
    res_u = supabase.table("users").select("*").eq("username", st.session_state.user['username']).execute()
    
    if res_u.data:
        user = res_u.data[0]
    else:
        st.session_state.user = None
        st.rerun()
        
    df_all = get_all_users()

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1: 
        st.title("🎾 Tennis Bet 2026")
        st.write(f"Joueur : **{user['username']}** | Club : **{user['club']}**")
    with col_h2: 
        st.metric("💰 Ton Solde", f"{user['coins']} 🪙")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    tabs = st.tabs(["🏠 ACCUEIL", "💰 PARIER", "🏆 CLASSEMENTS", "🛡️ CLUBS", "⚙️ ADMIN" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📅 Matchs par Tournoi")
            df_m = get_matches()
            if not df_m.empty:
                tournois = df_m['tournament'].unique()
                for tournoi in tournois:
                    st.markdown(f'<div class="tournament-header">🏆 {tournoi}</div>', unsafe_allow_html=True)
                    matchs_t = df_m[df_m['tournament'] == tournoi]
                    for _, row in matchs_t.iterrows():
                        st.markdown(f"""
                            <div class="match-card">
                                <b>{row['player1']}</b> ({row['club1']}) <span style="color:#E2001A;">VS</span> <b>{row['player2']}</b> ({row['club2']})
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Aucun match publié.")
        with c2:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty and df_all['perf_count'].max() > 0:
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                st.success(f"{roi['username']} ({roi['club']}) - {roi['perf_count']} Perfs")

    # --- 💰 PARIER (Style Winamax) ---
    with tabs[1]:
        st.header("🔥 Paris & Cotes")
        col_list, col_ticket = st.columns([2, 1])
        with col_list:
            df_m = get_matches()
            if not df_m.empty:
                for _, row in df_m.iterrows():
                    st.write(f"**{row.get('tournament', 'Match')}**")
                    ca, cvs, cb = st.columns([2, 0.5, 2])
                    with ca:
                        if st.button(f"{row['player1']} (1.80)", key=f"p1_{row['id']}"):
                            st.session_state.active_bet = {"id": row['id'], "player": row['player1'], "odds": 1.80}
                            st.session_state.mise_actuelle = 1
                    with cvs: st.write("VS")
                    with cb:
                        if st.button(f"{row['player2']} (1.80)", key=f"p2_{row['id']}"):
                            st.session_state.active_bet = {"id": row['id'], "player": row['player2'], "odds": 1.80}
                            st.session_state.mise_actuelle = 1
                    st.divider()
        with col_ticket:
            st.subheader("🎟️ Ton Ticket")
            if st.session_state.active_bet:
                bet = st.session_state.active_bet
                st.markdown(f'<div class="bet-ticket">Vainqueur : <b>{bet["player"]}</b><br>Cote : {bet["odds"]}</div>', unsafe_allow_html=True)
                
                # Système + / - pour la mise
                st.write("Mise :")
                cm, cd, cp = st.columns([1,2,1])
                with cm: 
                    if st.button("➖"): 
                        st.session_state.mise_actuelle = max(1, st.session_state.mise_actuelle - 1)
                        st.rerun()
                with cd: st.markdown(f"<h3 style='text-align:center;'>{st.session_state.mise_actuelle}</h3>", unsafe_allow_html=True)
                with cp: 
                    if st.button("➕"): 
                        st.session_state.mise_actuelle = min(user['coins'], st.session_state.mise_actuelle + 1)
                        st.rerun()
                
                if st.button("🚀 VALIDER LE PARI", type="primary"):
                    new_bal = user['coins'] - st.session_state.mise_actuelle
                    supabase.table("users").update({"coins": new_bal}).eq("username", user['username']).execute()
                    supabase.table("bets").insert({
                        "username": user['username'], 
                        "match_id": bet['id'], 
                        "prediction": bet['player'], 
                        "odds": bet['odds'], 
                        "stake": st.session_state.mise_actuelle
                    }).execute()
                    st.success("Pari validé !")
                    st.session_state.active_bet = None
                    st.rerun()
            else:
                st.info("Clique sur une cote pour parier")

    # --- 🏆 CLASSEMENTS ---
    with tabs[2]:
        st.subheader("🏆 Classement Victoires Générales")
        st.dataframe(df_all[['username', 'victoires_count', 'club']].sort_values("victoires_count", ascending=False), use_container_width=True, hide_index=True)
        st.subheader("🎾 Classement Perfs")
        st.dataframe(df_all[['username', 'perf_count', 'club']].sort_values("perf_count", ascending=False), use_container_width=True, hide_index=True)

    # --- 🛡️ CLUBS ---
    with tabs[3]:
        st.header("🛡️ Guerre des Clubs")
        guerre = df_all.groupby("club")["victoires_count"].sum().reindex(CLUBS_OFFICIELS, fill_value=0).reset_index()
        st.bar_chart(data=guerre, x="club", y="victoires_count", color="#E2001A")

    # --- ⚙️ ADMIN ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("🛠 Panel Administrateur")
            with st.expander("➕ Créer un Match"):
                t_n = st.text_input("Tournoi")
                n1, n2 = st.text_input("Joueur 1"), st.text_input("Joueur 2")
                c1, c2 = st.selectbox("Club 1", CLUBS_OFFICIELS), st.selectbox("Club 2", CLUBS_OFFICIELS)
                if st.button("Ajouter Match"):
                    supabase.table("matches").insert({"player1": n1, "club1": c1, "player2": n2, "club2": c2, "tournament": t_n}).execute()
                    st.rerun()
            with st.expander("✅ Valider une Victoire (+1)"):
                v = st.selectbox("Gagnant", df_all['username'].tolist())
                p = st.checkbox("C'est une PERF")
                if st.button("Valider"):
                    v_d = df_all[df_all['username'] == v].iloc[0]
                    up = {"victoires_count": int(v_d['victoires_count'] + 1)}
                    if p: up["perf_count"] = int(v_d['perf_count'] + 1)
                    supabase.table("users").update(up).eq("username", v).execute()
                    st.success("Données mises à jour !")
                    st.balloons()
