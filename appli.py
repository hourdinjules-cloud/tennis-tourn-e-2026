import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

st.markdown("""
    <style>
    /* Style Winamax */
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
    .odds-btn { background-color: #374151 !important; color: #fbbf24 !important; border: 1px solid #fbbf24 !important; }
    .bet-ticket { 
        background: #1f2937; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #E2001A;
        box-shadow: 0 4px 15px rgba(226, 0, 26, 0.2);
    }
    .mise-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 15px 0;
    }
    .mise-display {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION ---
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

# --- 4. ACCÈS ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Tournoi 2026")
    u = st.text_input("Prénom")
    p = st.text_input("Pass", type="password")
    if st.button("Connexion"):
        res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
        if res.data:
            st.session_state.user = res.data[0]
            st.rerun()
else:
    # Refresh user data (pour le solde après pari)
    res_u = supabase.table("users").select("*").eq("id", st.session_state.user['id']).execute()
    user = res_u.data[0]
    df_all = get_all_users()

    # Header
    colh1, colh2 = st.columns([3, 1])
    with colh1: 
        st.title("🎾 Tennis Bet 2026")
        st.caption(f"Connecté : {user['username']} | Club : {user['club']}")
    with colh2: st.metric("💰 Ton Solde", f"{user['coins']} 🪙")

    tabs = st.tabs(["🏠 ACCUEIL", "💰 PARIER", "🏆 CLASSEMENTS", "🛡️ CLUBS", "⚙️ ADMIN" if user.get('is_admin') else " "])

    # --- 💰 ONGLET PARIER ---
    with tabs[1]:
        st.header("🔥 Cotes du Jour")
        col_matches, col_ticket = st.columns([2, 1])
        
        with col_matches:
            df_m = get_matches()
            if not df_m.empty:
                for _, row in df_m.iterrows():
                    with st.container():
                        st.write(f"🏆 **{row.get('tournament', 'Match')}**")
                        c1, cvs, c2 = st.columns([2, 0.5, 2])
                        
                        with c1:
                            st.write(f"**{row['player1']}**")
                            if st.button(f"1.80", key=f"o1_{row['id']}"):
                                st.session_state.active_bet = {"id": row['id'], "player": row['player1'], "odds": 1.80}
                                st.session_state.mise_actuelle = 1 # Reset mise
                        
                        with cvs: st.markdown("<h4 style='text-align:center;'>VS</h4>", unsafe_allow_html=True)
                        
                        with c2:
                            st.write(f"**{row['player2']}**")
                            if st.button(f"1.80", key=f"o2_{row['id']}"):
                                st.session_state.active_bet = {"id": row['id'], "player": row['player2'], "odds": 1.80}
                                st.session_state.mise_actuelle = 1 # Reset mise
                        st.divider()
            else:
                st.info("Aucun match disponible.")

        with col_ticket:
            st.subheader("🎟️ Ticket de Pari")
            if st.session_state.active_bet:
                bet = st.session_state.active_bet
                
                with st.container():
                    st.markdown(f"""
                    <div class="bet-ticket">
                        <h4 style="margin:0; color:#E2001A;">Vainqueur : {bet['player']}</h4>
                        <p style="margin:5px 0;">Cote : <b>{bet['odds']}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("Choisir ta mise :")
                    # Système de boutons + / -
                    col_moins, col_val, col_plus = st.columns([1, 2, 1])
                    
                    with col_moins:
                        if st.button("➖"):
                            if st.session_state.mise_actuelle > 1:
                                st.session_state.mise_actuelle -= 1
                                st.rerun()
                    
                    with col_val:
                        st.markdown(f"<div style='text-align:center; font-size:30px; font-weight:bold;'>{st.session_state.mise_actuelle} 🪙</div>", unsafe_allow_html=True)
                    
                    with col_plus:
                        if st.button("➕"):
                            if st.session_state.mise_actuelle < user['coins']:
                                st.session_state.mise_actuelle += 1
                                st.rerun()
                    
                    gain_pot = round(st.session_state.mise_actuelle * bet['odds'], 1)
                    st.markdown(f"<p style='text-align:center;'>Gain potentiel : <b>{gain_pot} 🪙</b></p>", unsafe_allow_html=True)
                    
                    if st.button("🚀 VALIDER LE PARI", type="primary"):
                        if st.session_state.mise_actuelle <= user['coins']:
                            # Update BDD
                            new_bal = user['coins'] - st.session_state.mise_actuelle
                            supabase.table("users").update({"coins": new_bal}).eq("id", user['id']).execute()
                            
                            supabase.table("bets").insert({
                                "username": user['username'],
                                "match_id": bet['id'],
                                "prediction": bet['player'],
                                "odds": bet['odds'],
                                "stake": st.session_state.mise_actuelle
                            }).execute()
                            
                            st.success(f"Pari de {st.session_state.mise_actuelle} coins validé !")
                            st.session_state.active_bet = None
                            st.balloons()
                            st.rerun()
                    
                    if st.button("Vider le ticket"):
                        st.session_state.active_bet = None
                        st.rerun()
            else:
                st.info("Clique sur une cote pour parier")

    # --- LES AUTRES ONGLETS RESTENT ICI ---
    # (Accueil, Classement, Clubs, Admin...)
