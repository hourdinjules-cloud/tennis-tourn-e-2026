if st.session_state.user is None:
    with st.sidebar:
        # On crée deux onglets dans la barre latérale
        menu = st.tabs(["Connexion", "S'inscrire"])
        
        # --- ONGLET CONNEXION ---
        with menu[0]:
            u = st.text_input("Prénom")
            p = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                user_data = check_login(u, p)
                if user_data:
                    st.session_state.user = user_data[0]
                    st.rerun()
                else:
                    st.error("Identifiants incorrects...")

        # --- ONGLET INSCRIPTION ---
        with menu[1]:
            new_u = st.text_input("Ton Prénom (ex: Jules)")
            new_p = st.text_input("Choisis un mot de passe", type="password")
            new_club = st.selectbox("Ton Club", ["Club A", "Club B", "Autre"])
            
            if st.button("Créer mon compte"):
                if new_u and new_p:
                    try:
                        # On insère le nouveau joueur dans Supabase
                        supabase.table("users").insert({
                            "username": new_u,
                            "password": new_p,
                            "coins": 10,  # Cadeau de bienvenue !
                            "club": new_club,
                            "is_admin": False
                        }).execute()
                        st.success("Compte créé ! Connecte-toi à gauche.")
                    except Exception as e:
                        st.error("Ce nom est déjà pris ou il y a une erreur.")
                else:
                    st.warning("Remplis tous les champs !")
