import streamlit as st
# ... (tes imports habituels)

# 1. Vérification du rôle au début
def check_admin(username):
    df_users = get_users()
    user_data = df_users[df_users['username'] == username]
    if not user_data.empty:
        # On vérifie si la colonne 'is_admin' est à True
        return user_data.iloc[0].get('is_admin', False)
    return False

# 2. Le Design du Header (CSS)
st.markdown("""
    <style>
    .main-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background-color: #1E1E1E;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        z-index: 999;
        border-bottom: 2px solid #E2001A;
    }
    .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
    }
    .coins-badge {
        background: #FFD700;
        color: black;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .profile-icon {
        background: #E2001A;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    /* On décale le contenu pour ne pas qu'il soit sous le header */
    .stApp { margin-top: 60px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Affichage du Header
if st.session_state.user_connected:
    # On récupère les infos de l'utilisateur connecté
    df_users = get_users()
    solde = df_users.loc[df_users['username'] == st.session_state.user_connected, 'coins'].values[0]
    
    st.markdown(f"""
        <div class="main-header">
            <div style="font-weight: bold; color: #E2001A;">🎾 TENNIS BET</div>
            <div class="user-info">
                <span class="coins-badge">{round(float(solde), 1)} 🪙</span>
                <div class="profile-icon">👤</div>
                <span>{st.session_state.user_connected}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 4. Gestion des Onglets Dynamiques
tabs_list = ["🏠 Accueil", "💰 Parier", "🏆 Classement"]

# On vérifie si le mec est admin pour ajouter l'onglet secret
is_admin = False
if st.session_state.user_connected:
    is_admin = check_admin(st.session_state.user_connected)

if is_admin:
    tabs_list.append("⚙️ Admin")

# Création des onglets
tabs = st.tabs(tabs_list)

with tabs[0]:
    st.write("Bienvenue sur l'accueil")
    # ... ton code

with tabs[1]:
    # ... ton code parier

with tabs[2]:
    # ... ton code classement

# L'onglet admin n'existe que si is_admin est True
if is_admin:
    with tabs[3]:
        st.subheader("🛠 Panneau de contrôle")
        # Ici tu mets ton code pour gérer les matchs et les comptes
        st.write("Bonjour Grand Administrateur")
