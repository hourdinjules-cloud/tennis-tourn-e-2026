import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN (Blanc, Jaune, Noir) ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

st.markdown("""
    <style>
    /* Fond blanc et texte noir */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    
    /* Titres et textes importants en noir */
    h1, h2, h3, p, span, label {
        color: #000000 !important;
    }

    /* Boutons et détails en Jaune */
    .stButton > button {
        background-color: #FFD700 !important; /* Jaune Or */
        color: #000000 !important;
        border: 1px solid #000000;
        font-weight: bold;
        border-radius: 8px;
    }

    /* Cartes des matchs */
    .match-card {
        background-color: #F0F0F0;
        padding: 15px;
        border-radius: 12px;
        border-left: 8px solid #FFD700;
        margin-bottom: 15px;
        color: #000000;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    /* Encadré Roi de la Perf */
    .roi-card {
        background: linear-gradient(135deg, #FFD700, #FFFACD);
        padding: 20px;
        border-radius: 15px;
        color: #000000;
        text-align: center;
        border: 2px solid #000000;
    }

    /* Ticket de pari */
    .bet-ticket {
        background-color: #FFFDE7;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        color: #000000;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F0F0;
        color: #000000;
        border-radius: 5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION SUPABASE ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state: st.session_state.user = None
if 'active_bet' not in st.session_state: st.session_state.active_bet = None
if 'mise_actuelle' not in st.session_state: st.session_state.mise_actuelle = 1

LISTE_RANGS = ["NC", "40", "30/5", "30/4", "30/3", "30/2", "30/1", "30", "15/5", "15/4", "15/3", "15/2", "15/1", "15"]
CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix", "Extérieur"]

# --- 3. ACCÈS ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Miremont 2026")
    t1, t2 = st.tabs(["🔐 Connexion", "📝 S'inscrire"])
    with t1:
        u = st.text_input("Prénom")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
    with t2:
        nu = st.text_input("Ton Prénom")
        np = st.text_input("Pass", type="password")
        nc = st.selectbox("Club", CLUBS_OFFICIELS)
        nr = st.selectbox("Ton Classement", LISTE_RANGS)
        if st.button("Créer mon compte"):
            supabase.table("users").insert({"username":nu,"password":np,"coins":10,"club":nc,"rank":nr,"is_admin":False,"victoires_count":0,"perf_count":0}).execute()
            st.success("Compte créé !")

else:
    # Refresh user
    res_u = supabase.table("users").select("*").eq("username", st.session_state.user['username']).execute()
    user = res_u.data[0]
    df_all = pd.DataFrame(supabase.table("users").select("*").execute().data)

    colh1, colh2 = st.columns([3, 1])
    with colh1: 
        st.title(f"🎾 {user['username']} ({user['rank']})")
    with colh2: 
        st.metric("💰 Solde", f"{user['coins']} 🪙")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    tabs = st.tabs(["🏠 ACCUEIL", "💰 PARIER", "🏆 CLASSEMENT", "🛡️ CLUBS", "⚙️ ADMIN" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL (Avec Roi de la Perf & Matchs) ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📅 Prochains Matchs")
            res_m = supabase.table("matches").select("*").order("created_at", desc=True).execute()
            if res_m.data:
                for row in res_m.data:
                    st.markdown(f"""
                        <div class="match-card">
                            <b>{row.get('tournament', 'Match')}</b><br>
                            {row['player1']} <span style="color:#FFD700;">VS</span> {row['player2']}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun match prévu.")

        with c2:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty and df_all['perf_count'].max() > 0:
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                st.markdown(f"""
                    <div class="roi-card">
                        <div style="font-size:40px;">🏆</div>
                        <div style="font-size:22px; font-weight:bold;">{roi['username']}</div>
                        <div style="font-size:18px;">{roi['perf_count']} PERFS</div>
                        <small>{roi['club']} | {roi['rank']}</small>
                    </div>
                """, unsafe_allow_html=True)

    # --- 💰 PARIER (Winamax Style) ---
    with tabs[1]:
        col_m, col_t = st.columns([2, 1])
        with col_m:
            st.subheader("🔥 Cotes")
            res_m = supabase.table("matches").select("*").execute()
            for row in res_m.data:
                st.write(f"**{row.get('tournament', 'Match')}**")
                ca, cvs, cb = st.columns([2, 0.5, 2])
                with ca:
                    if st.button(f"{row['player1']} (1.80)", key=f"p1_{row['id']}"):
                        st.session_state.active_bet = {"id": row['id'], "player": row['player1'], "odds": 1.80}
                        st.session_state.mise_actuelle = 1
                with cb:
                    if st.button(f"{row['player2']} (1.80)", key=f"p2_{row['id']}"):
                        st.session_state.active_bet = {"id": row['id'], "player": row['player2'], "odds": 1.80}
                        st.session_state.mise_actuelle = 1
                st.divider()
        with col_t:
            if st.session_state.active_bet:
                bet = st.session_state.active_bet
                st.markdown(f'<div class="bet-ticket"><b>{bet["player"]}</b> (Cote: {bet["odds"]})</div>', unsafe_allow_html=True)
                cm, cd, cp = st.columns([1,2,1])
                with cm: 
                    if st.button("➖"): st.session_state.mise_actuelle = max(1, st.session_state.mise_actuelle - 1); st.rerun()
                with cd: st.markdown(f"<h3 style='text-align:center;'>{st.session_state.mise_actuelle}</h3>", unsafe_allow_html=True)
                with cp: 
                    if st.button("➕"): st.session_state.mise_actuelle = min(user['coins'], st.session_state.mise_actuelle + 1); st.rerun()
                if st.button("VALIDER LE PARI", type="primary"):
                    new_bal = user['coins'] - st.session_state.mise_actuelle
                    supabase.table("users").update({"coins": new_bal}).eq("username", user['username']).execute()
                    supabase.table("bets").insert({"username": user['username'], "match_id": bet['id'], "prediction": bet['player'], "odds": bet['odds'], "stake": st.session_state.mise_actuelle}).execute()
                    st.success("Pari envoyé !")
                    st.session_state.active_bet = None; st.rerun()

    # --- 🏆 CLASSEMENT (Uniquement victoires générales) ---
    with tabs[2]:
        st.subheader("🏆 Classement du Stage")
        st.dataframe(df_all[['username', 'victoires_count', 'rank', 'club']].sort_values("victoires_count", ascending=False), use_container_width=True, hide_index=True)

    # --- 🛡️ CLUBS ---
    with tabs[3]:
        guerre = df_all.groupby("club")["victoires_count"].sum().reindex(CLUBS_OFFICIELS, fill_value=0).reset_index()
        st.bar_chart(data=guerre, x="club", y="victoires_count", color="#FFD700")

    # --- ⚙️ ADMIN (Validation Matchs + Inconnus) ---
    if user.get('is_admin'):
        with tabs[-1]:
            with st.expander("➕ Créer un Match"):
                tn = st.text_input("Tournoi"); j1 = st.text_input("Joueur 1"); j2 = st.text_input("Joueur 2")
                if st.button("Publier"):
                    supabase.table("matches").insert({"player1":j1, "player2":j2, "tournament":tn}).execute()
                    st.rerun()
            
            with st.expander("✅ Valider un Résultat (Gestion Inconnus/Perfs)"):
                gagnant = st.selectbox("Gagnant (Inscrit)", df_all['username'].tolist())
                mode_adv = st.radio("Adversaire :", ["Inscrit", "Inconnu (Extérieur)"])
                if mode_adv == "Inscrit":
                    perdant = st.selectbox("Adversaire inscrit", df_all['username'].tolist())
                    p_rank = df_all[df_all['username'] == perdant].iloc[0]['rank']
                else:
                    perdant = st.text_input("Nom de l'inconnu")
                    p_rank = st.selectbox("Classement de l'inconnu", LISTE_RANGS)
                
                if st.button("Enregistrer Victoire"):
                    g_data = df_all[df_all['username'] == gagnant].iloc[0]
                    is_perf = LISTE_RANGS.index(g_data['rank']) < LISTE_RANGS.index(p_rank)
                    up = {"victoires_count": int(g_data['victoires_count'] + 1)}
                    if is_perf: up["perf_count"] = int(g_data['perf_count'] + 1)
                    supabase.table("users").update(up).eq("username", gagnant).execute()
                    st.success(f"Victoire {'(PERF!)' if is_perf else ''} validée pour {gagnant}")
                    st.rerun()
