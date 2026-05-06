import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- INITIALISATION ---
if 'user_connected' not in st.session_state:
    st.session_state.user_connected = None

# --- CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_users():
    try:
        # On force le rafraîchissement des données (ttl=0)
        df = conn.read(worksheet="users", ttl=0)
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return pd.DataFrame()

# --- LOGIQUE ---
df = get_users()

with st.sidebar:
    st.title("🎾 Connexion")
    
    if st.session_state.user_connected:
        st.success(f"Connecté : {st.session_state.user_connected}")
        if st.button("Se déconnecter"):
            st.session_state.user_connected = None
            st.rerun()
    else:
        # --- PANNEAU DE CONTRÔLE POUR TOI ---
        st.write("---")
        st.write("🔍 **Ce que le site voit dans le Excel :**")
        if not df.empty:
            st.write(df[['username', 'password']]) # On affiche juste les noms et MDP pour vérifier
        else:
            st.error("Tableau vide ! Vérifie tes colonnes.")
        st.write("---")

        u_name = st.text_input("Prénom")
        u_pwd = st.text_input("Mot de passe", type="password")
        
        if st.button("Lancer la connexion"):
            if not df.empty:
                # Nettoyage RADICAL des données
                df['username'] = df['username'].astype(str).str.strip()
                df['password'] = df['password'].astype(str).str.strip()
                
                # On cherche la ligne
                user_match = df[(df['username'].str.lower() == u_name.lower().strip()) & 
                               (df['password'] == u_pwd.strip())]
                
                if not user_match.empty:
                    st.session_state.user_connected = user_match.iloc[0]['username']
                    st.rerun()
                else:
                    st.error("Désolé, ça ne correspond pas.")
            else:
                st.error("Base de données inaccessible.")

# --- AFFICHAGE ---
if st.session_state.user_connected:
    st.balloons()
    st.title(f"Salut {st.session_state.user_connected} ! 🎾")
    user_row = df[df['username'] == st.session_state.user_connected].iloc[0]
    st.metric("Tes Coins", f"{user_row['coins']} 🪙")
else:
    st.header("Bienvenue au Tournoi 2026")
    st.info("Connecte-toi à gauche pour commencer.")
