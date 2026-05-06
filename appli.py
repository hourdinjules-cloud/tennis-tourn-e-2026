import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

# Injection de CSS pour le look & feel
st.markdown("""
    <style>
    /* Fond général et police */
    .main { background-color: #0e1117; }
    
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #E2001A !important; }

    /* Cartes pour les matchs */
    .match-card {
        background: #1f2937;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #E2001A;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Style du solde Coins */
    .stMetric {
        background: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    </style>
""", unsafe_allow_html=True)

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

def get_matches():
    res = supabase.table("matches").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(res.data)

CLUBS_OFFICIELS = ["Le Vernet", "Saubens", "Lacroix"]

# --- 4. ACCÈS ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Tournoi 2026")
    t1, t2 = st.tabs(["🔐 Connexion", "📝 S'inscrire"])
    with t1:
        u = st.text_input("Prénom")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state.user = res.data[0]
                st.rerun()
    with t2:
        nu, np = st.text_input("Ton Prénom"), st.text_input("Pass", type="password")
        nc = st.selectbox("Club", CLUBS_OFFICIELS)
        if st.button("Créer mon compte", use_container_width=True):
            supabase.table("users").insert({"username":nu,"password":np,"coins":10,"club":nc,"is_admin":False,"victoires_count":0,"perf_count":0}).execute()
            st.success("Compte créé ! Connecte-toi.")

else:
    user = st.session_state.user
    df_all = get_all_users()
    
    # Header élégant
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1: 
        st.title("🎾 Tennis Bet 2026")
        st.caption(f"Bienvenue, **{user['username']}** | Club : {user['club']}")
    with col_h2: 
        st.metric("💰 Ton Solde", f"{user['coins']} 🪙")
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- ONGLETS ---
    tabs = st.tabs(["🏠 ACCUEIL", "💰 PARIER", "🏆 CLASSEMENTS", "🛡️ GUERRE DES CLUBS", "⚙️ ADMIN" if user.get('is_admin') else " "])

    # --- 🏠 ACCUEIL ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📅 Prochains Matchs")
            df_m = get_matches()
            if not df_m.empty:
                for _, row in df_m.iterrows():
                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div style="text-align:center; flex:1;">
                                    <span style="font-size:18px; font-weight:bold;">{row['player1']}</span><br>
                                    <small style="color:#aaa;">{row['club1']}</small>
                                </div>
                                <div style="color:#E2001A; font-weight:bold; font-size:20px; padding:0 20px;">VS</div>
                                <div style="text-align:center; flex:1;">
                                    <span style="font-size:18px; font-weight:bold;">{row['player2']}</span><br>
                                    <small style="color:#aaa;">{row['club2']}</small>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun match prévu pour le moment.")
        
        with c2:
            st.subheader("👑 Roi de la Perf")
            if not df_all.empty and df_all['perf_count'].max() > 0:
                roi = df_all.sort_values("perf_count", ascending=False).iloc[0]
                st.markdown(f"""
                    <div style="background:linear-gradient(135deg, #FFD700, #FFA500); padding:25px; border-radius:15px; color:black; text-align:center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                        <div style="font-size:50px;">🏆</div>
                        <div style="font-size:22px; font-weight:bold; margin:10px 0;">{roi['username']}</div>
                        <div style="font-size:16px;">{roi['perf_count']} PERFS</div>
                        <div style="font-size:14px; opacity:0.8;">{roi['club']}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            st.subheader("📊 Tendances")
            st.success("🔥 Top Pari : Axel (+45)")
            st.error("💀 Flop Pari : Jules (-20)")

    # --- 🏆 CLASSEMENTS ---
    with tabs[2]:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("🏆 Classement Général (Victoires)")
            st.dataframe(df_all[['username', 'victoires_count', 'club']].sort_values("victoires_count", ascending=False), use_container_width=True, hide_index=True)
        with col_c2:
            st.subheader("🎾 Classement Perfs")
            st.dataframe(df_all[['username', 'perf_count', 'club']].sort_values("perf_count", ascending=False), use_container_width=True, hide_index=True)

    # --- 🛡️ GUERRE DES CLUBS ---
    with tabs[3]:
        st.header("🛡️ La Guerre des Clubs")
        if not df_all.empty:
            guerre = df_all.groupby("club")["victoires_count"].sum().reindex(CLUBS_OFFICIELS, fill_value=0).reset_index()
            guerre.columns = ["Club", "Victoires Totales"]
            st.bar_chart(data=guerre, x="Club", y="Victoires Totales", color="#E2001A")
            st.table(guerre)

    # --- ⚙️ ADMIN ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("🛠 Panel Administrateur")
            exp1 = st.expander("➕ Publier un nouveau Match")
            with exp1:
                col_a, col_b = st.columns(2)
                with col_a:
                    nom1 = st.text_input("Joueur 1")
                    club1 = st.selectbox("Club 1", CLUBS_OFFICIELS)
                with col_b:
                    nom2 = st.text_input("Joueur 2")
                    club2 = st.selectbox("Club 2", CLUBS_OFFICIELS)
                if st.button("Enregistrer le match", use_container_width=True):
                    if nom1 and nom2:
                        supabase.table("matches").insert({"player1": nom1, "club1": club1, "player2": nom2, "club2": club2}).execute()
                        st.success("Match en ligne !")
                        st.rerun()

            exp2 = st.expander("✅ Valider un Résultat")
            with exp2:
                vainqueur = st.selectbox("Vainqueur", df_all['username'].tolist())
                type_v = st.radio("Type", ["Victoire Normale", "PERF (+1 Victoire et +1 Perf)"])
                if st.button("Valider la Victoire", use_container_width=True):
                    v_data = df_all[df_all['username'] == vainqueur].iloc[0]
                    upd = {"victoires_count": int(v_data['victoires_count'] + 1)}
                    if "PERF" in type_v: upd["perf_count"] = int(v_data['perf_count'] + 1)
                    supabase.table("users").update(upd).eq("username", vainqueur).execute()
                    st.success("Compteurs mis à jour !")
                    st.balloons()
