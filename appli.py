import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Tennis Bet 2026", page_icon="🎾", layout="wide")

# --- 2. CONNEXION ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

if 'user' not in st.session_state: st.session_state.user = None

# Échelle des classements pour le calcul automatique des perfs
LISTE_RANGS = ["NC", "40", "30/5", "30/4", "30/3", "30/2", "30/1", "30", "15/5", "15/4", "15/3", "15/2", "15/1", "15"]

# --- 3. CONNEXION / INSCRIPTION ---
if st.session_state.user is None:
    st.title("🎾 Tennis Bet - Inscription")
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        u = st.text_input("Prénom")
        p = st.text_input("Mdp", type="password")
        if st.button("Go"):
            res = supabase.table("users").select("*").eq("username", u).eq("password", p).execute()
            if res.data: 
                st.session_state.user = res.data[0]
                st.rerun()
    with t2:
        nu = st.text_input("Ton Prénom")
        np = st.text_input("Mot de passe", type="password")
        nr = st.selectbox("Ton Classement actuel", LISTE_RANGS)
        if st.button("S'inscrire"):
            supabase.table("users").insert({"username":nu, "password":np, "rank":nr, "coins":10, "victoires_count":0, "perf_count":0}).execute()
            st.success("Compte créé !")

# --- 4. INTERFACE PRINCIPALE ---
else:
    # On refresh l'utilisateur pour avoir son classement à jour
    res_u = supabase.table("users").select("*").eq("username", st.session_state.user['username']).execute()
    user = res_u.data[0]
    df_all = pd.DataFrame(supabase.table("users").select("*").execute().data)

    st.title(f"🎾 Profil : {user['username']} ({user['rank']})")
    
    tabs = st.tabs(["🏠 Accueil", "🏆 Classements", "⚙️ Admin" if user.get('is_admin') else " "])

    # --- ONGLET ADMIN (LA PARTIE IMPORTANTE) ---
    if user.get('is_admin'):
        with tabs[-1]:
            st.header("🛠 Validation des résultats")
            
            with st.form("valid_match"):
                st.subheader("Enregistrer une victoire")
                
                # 1. Sélectionner le gagnant (forcément quelqu'un du stage/inscrit)
                gagnant = st.selectbox("Vainqueur (Inscrit)", df_all['username'].tolist())
                
                st.divider()
                
                # 2. Saisie de l'adversaire (Inconnu ou Inscrit)
                mode_adv = st.radio("L'adversaire est-il inscrit ?", ["Non (Joueur extérieur)", "Oui (Joueur du stage)"])
                
                if mode_adv == "Oui (Joueur du stage)":
                    perdant_name = st.selectbox("Sélectionner l'adversaire", df_all['username'].tolist())
                    # On récupère son rang automatiquement
                    p_data = df_all[df_all['username'] == perdant_name].iloc[0]
                    perdant_rank = p_data['rank']
                    st.info(f"Classement détecté : {perdant_rank}")
                else:
                    perdant_name = st.text_input("Nom du joueur inconnu")
                    perdant_rank = st.selectbox("Classement du joueur inconnu", LISTE_RANGS)

                submit = st.form_submit_button("Valider le résultat")

                if submit:
                    g_data = df_all[df_all['username'] == gagnant].iloc[0]
                    
                    # LOGIQUE DE PERF
                    # On compare les positions dans LISTE_RANGS
                    idx_gagnant = LISTE_RANGS.index(g_data['rank'])
                    idx_perdant = LISTE_RANGS.index(perdant_rank)
                    
                    # Si l'index du gagnant est plus petit, il est moins bien classé -> PERF
                    is_perf = idx_gagnant < idx_perdant
                    
                    # Mise à jour des compteurs
                    new_v = int(g_data['victoires_count'] + 1)
                    new_p = int(g_data['perf_count'] + (1 if is_perf else 0))
                    
                    supabase.table("users").update({
                        "victoires_count": new_v,
                        "perf_count": new_p
                    }).eq("username", gagnant).execute()
                    
                    if is_perf:
                        st.balloons()
                        st.success(f"🔥 PERF ! {gagnant} ({g_data['rank']}) bat {perdant_name} ({perdant_rank})")
                    else:
                        st.success(f"Victoire enregistrée pour {gagnant}")
                    
                    st.rerun()

    # --- CLASSEMENTS ---
    with tabs[1]:
        st.subheader("Classement général")
        st.dataframe(df_all[['username', 'rank', 'victoires_count', 'perf_count']].sort_values("victoires_count", ascending=False), use_container_width=True, hide_index=True)
