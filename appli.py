import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DES CLASSEMENTS
CLASSEMENTS = {
    "NC": 0, "40": 1, "30/5": 2, "30/4": 3, "30/3": 4, "30/2": 5, "30/1": 6,
    "30": 7, "15/5": 8, "15/4": 9, "15/3": 10, "15/2": 11, "15/1": 12,
    "15": 13, "5/6": 14, "4/6": 15, "3/6": 16, "2/6": 17, "1/6": 18, "0": 19
}
PASSWORD_ADMIN = "tennis2026"

# 2. INITIALISATION DE LA MÉMOIRE
for key in ['matchs', 'paris', 'clubs', 'club_scores', 'users', 'user_connected']:
    if key not in st.session_state:
        if key in ['matchs', 'paris']: st.session_state[key] = []
        elif key == 'clubs': st.session_state[key] = ["Club A", "Club B"]
        elif key == 'user_connected': st.session_state[key] = None
        else: st.session_state[key] = {}

if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212"
if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
if 'font_size' not in st.session_state: st.session_state.font_size = 16

def calculer_cote(r1, r2):
    diff = CLASSEMENTS[r1] - CLASSEMENTS[r2]
    prob = 1 / (1 + 1.4 ** (-diff))
    return round(1/prob, 2), round(1/(1-prob), 2)

# 3. DESIGN CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color}; color: {st.session_state.text_color}; }}
    html, body, [class*="st-"] {{ font-size: {st.session_state.font_size}px !important; color: {st.session_state.text_color}; }}
    .winamax-card {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid {st.session_state.text_color};
        border-radius: 15px; padding: 15px; margin-bottom: 15px; text-align: center;
    }}
    .result-card {{
        background-color: rgba(0, 255, 0, 0.05);
        border-left: 5px solid #00ff00;
        padding: 10px; margin-bottom: 10px; border-radius: 5px;
    }}
    .live-badge {{
        background-color: #ff4b4b; color: white; padding: 2px 8px;
        border-radius: 4px; font-weight: bold; animation: blinker 1.5s linear infinite;
    }}
    @keyframes blinker {{ 50% {{ opacity: 0; }} }}
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR (COMPTES)
with st.sidebar:
    st.title("👤 Mon Espace")
    if st.session_state.user_connected is None:
        mode = st.radio("Action", ["Connexion", "Créer un compte"])
        u_name = st.text_input("Prénom")
        u_pwd = st.text_input("Mot de passe", type="password")
        if st.button("Valider"):
            if mode == "Créer un compte":
                if u_name and u_pwd and u_name not in st.session_state.users:
                    st.session_state.users[u_name] = {"pwd": u_pwd, "coins": 10, "last_bonus": None}
                    st.success("Compte créé ! (10 coins offerts)")
                else: st.error("Erreur (Nom déjà pris ou vide)")
            else:
                if u_name in st.session_state.users and st.session_state.users[u_name]["pwd"] == u_pwd:
                    st.session_state.user_connected = u_name
                    st.rerun()
                else: st.error("Identifiants incorrects")
    else:
        user = st.session_state.users[st.session_state.user_connected]
        st.write(f"Joueur : **{st.session_state.user_connected}**")
        st.metric("Solde", f"{round(user['coins'], 1)} 🪙")
        
        today = datetime.now().strftime("%Y-%m-%d")
        if user['last_bonus'] != today:
            if st.button("🎁 Bonus du jour (+10)"):
                user['coins'] += 10
                user['last_bonus'] = today
                st.rerun()
        
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()

# 5. ONGLETS
tab_home, tab_parier, tab_ranking, tab_guerre, tab_admin = st.tabs([
    "🏠 Accueil", "💰 Parier", "🏆 Classement", "⚔️ Clubs", "⚙️ Admin"
])

# --- ACCUEIL ---
with tab_home:
    st.subheader("🎾 Résultats du Jour")
    matchs_finis = [m for m in st.session_state.matchs if m['fini']]
    if not matchs_finis:
        st.info("Aucun match terminé pour le moment.")
    else:
        for m in matchs_finis:
            st.markdown(f"""
            <div class="result-card">
                <small>{m['tournoi']}</small><br>
                <b>{m['j1']}</b> vs <b>{m['j2']}</b><br>
                <span style="color: #00ff00;">Victoire : {m['vainqueur']}</span><br>
                <small>Score : {m.get('score', 'Non renseigné')}</small>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("🔴 Matchs en cours")
    maintenant = datetime.now().strftime("%H:%M")
    lives = [m for m in st.session_state.matchs if not m['fini'] and m['heure'] <= maintenant]
    if lives:
        for m in lives:
            st.markdown(f"<span class='live-badge'>LIVE</span> **{m['j1']} vs {m['j2']}**", unsafe_allow_html=True)
    else: st.write("Pas de direct.")

# --- PARIER ---
with tab_parier:
    if st.session_state.user_connected is None:
        st.warning("Connecte-toi pour parier !")
    else:
        match_dispo = [i for i, m in enumerate(st.session_state.matchs) if not m['fini']]
        for i in match_dispo:
            m = st.session_state.matchs[i]
            st.markdown(f"<div class='winamax-card'><h3>{m['j1']} vs {m['j2']}</h3><p>{m['ct1']} | {m['ct2']}</p></div>", unsafe_allow_html=True)
            with st.expander("Parier sur ce match"):
                choix = st.radio("Vainqueur", [m['j1'], m['j2']], key=f"c_{i}")
                mise = st.number_input("Mise", 1.0, float(st.session_state.users[st.session_state.user_connected]['coins']), key=f"m_{i}")
                if st.button("Valider le pari", key=f"b_{i}"):
                    st.session_state.users[st.session_state.user_connected]['coins'] -= mise
                    cote = m['ct1'] if choix == m['j1'] else m['ct2']
                    st.session_state.paris.append({"parieur": st.session_state.user_connected, "match_idx": i, "choix": choix, "mise": mise, "cote": cote})
                    st.success("Pari pris !"); st.rerun()

# --- CLASSEMENT ---
with tab_ranking:
    st.subheader("🏆 Les plus riches")
    if st.session_state.users:
        data = [{"Joueur": k, "Coins": round(v["coins"], 1)} for k, v in st.session_state.users.items()]
        st.table(pd.DataFrame(data).sort_values("Coins", ascending=False))

# --- CLUBS ---
with tab_guerre:
    st.subheader("⚔️ Score des Clubs")
    for club in st.session_state.clubs:
        pts = st.session_state.club_scores.get(club, 0)
        st.write(f"**{club}** : {pts} victoires")
        st.progress(min(pts/20, 1.0))

# --- ADMIN ---
with tab_admin:
    if st.text_input("Code Admin", type="password") == PASSWORD_ADMIN:
        # PERSONNALISATION
        with st.expander("🎨 Design & Clubs"):
            st.session_state.bg_color = st.color_picker("Fond", st.session_state.bg_color)
            st.session_state.text_color = st.color_picker("Texte", st.session_state.text_color)
            st.session_state.font_size = st.slider("Police", 12, 24, st.session_state.font_size)
            new_c = st.text_input("Ajouter Club")
            if st.button("Ajouter"): st.session_state.clubs.append(new_c); st.rerun()
            del_c = st.selectbox("Supprimer Club", st.session_state.clubs)
            if st.button("Supprimer"): st.session_state.clubs.remove(del_c); st.rerun()

        # MATCHS
        with st.expander("🎾 Créer Match"):
            j1 = st.text_input("Nom J1"); r1 = st.selectbox("Classement J1", list(CLASSEMENTS.keys()), key="r1")
            cl1 = st.selectbox("Club J1", st.session_state.clubs, key="cl1")
            j2 = st.text_input("Nom J2"); r2 = st.selectbox("Classement J2", list(CLASSEMENTS.keys()), key="r2")
            cl2 = st.selectbox("Club J2", st.session_state.clubs, key="cl2")
            h = st.text_input("Heure", "14:00")
            if st.button("Publier Match"):
                c1, c2 = calculer_cote(r1, r2)
                st.session_state.matchs.append({"j1": j1, "j2": j2, "club1": cl1, "club2": cl2, "ct1": c1, "ct2": c2, "heure": h, "tournoi": "Stage Tennis", "fini": False})
                st.rerun()

        # VALIDATION
        with st.expander("🏁 Valider un Score"):
            en_cours = [i for i, m in enumerate(st.session_state.matchs) if not m['fini']]
            if en_cours:
                idx = st.selectbox("Sélectionner", en_cours, format_func=lambda x: f"{st.session_state.matchs[x]['j1']} vs {st.session_state.matchs[x]['j2']}")
                sc = st.text_input("Score final")
                win = st.radio("Vainqueur", [st.session_state.matchs[idx]['j1'], st.session_state.matchs[idx]['j2']])
                if st.button("Payer les parieurs"):
                    m = st.session_state.matchs[idx]
                    m['fini'] = True; m['vainqueur'] = win; m['score'] = sc
                    v_club = m['club1'] if win == m['j1'] else m['club2']
                    st.session_state.club_scores[v_club] = st.session_state.club_scores.get(v_club, 0) + 1
                    for p in st.session_state.paris:
                        if p['match_idx'] == idx and p['choix'] == win:
                            st.session_state.users[p['parieur']]['coins'] += (p['mise'] * p['cote'])
                    st.balloons(); st.rerun()
