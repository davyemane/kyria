import streamlit as st
import requests
import uuid
from supabase import create_client, Client
import time
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="KYRIA - Assistant IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look professionnel
st.markdown("""
<style>
    html, body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f4f6f8;
    }

    .main-header {
        background: linear-gradient(90deg, #5e60ce 0%, #3a0ca3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }

    .kyria-logo {
        font-size: 3.2rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    }

    .kyria-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.85;
        margin: 0;
    }

    .auth-container, .chat-container, .status-card, .metric-card {
        animation: fadeIn 0.6s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stButton > button {
        border-radius: 12px !important;
        font-size: 16px;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(135deg, #5e60ce 0%, #3a0ca3 100%);
        color: white;
        font-weight: 600;
        border: none;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3a0ca3 0%, #5e60ce 100%);
        transform: scale(1.03);
        transition: all 0.3s ease;
    }

    .metric-card {
        background: linear-gradient(135deg, #5e60ce 0%, #3a0ca3 100%);
    }

    .sidebar-header {
        background: linear-gradient(135deg, #5e60ce 0%, #3a0ca3 100%);
    }
</style>

""", unsafe_allow_html=True)

# Supabase setup
SUPABASE_URL = "https://xqstiwaswctfopwddtkv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc3Rpd2Fzd2N0Zm9wd2RkdGt2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDc5MDU3NiwiZXhwIjoyMDY2MzY2NTc2fQ.nXvMIhqlhqBcofgIhWaIgo4uln8h7Z02rfrOAarScHY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Webhook URL
WEBHOOK_URL = "https://davyemane2.app.n8n.cloud/webhook/invoke-supabase-agent"

def display_header():
    """Affiche l'en-tête professionnel de KYRIA"""
    st.markdown("""
    <div class="main-header">
        <div class="kyria-logo">🤖 KYRIA</div>
        <div class="kyria-subtitle">Votre Assistant IA Intelligent</div>
    </div>
    """, unsafe_allow_html=True)

def check_user_status(email: str):
    """Vérifie le statut de l'utilisateur dans Supabase"""
    try:
        response = supabase.auth.admin.list_users()
        users = response.data
        
        for user in users:
            if user.email == email:
                st.success(f"✅ Utilisateur trouvé: {user.email}")
                confirmed = "✅ Confirmé" if user.email_confirmed_at else "❌ Non confirmé"
                st.info(f"📧 Statut email: {confirmed}")
                return user
        
        st.warning("⚠️ Utilisateur non trouvé dans la base")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors de la vérification: {e}")
        return None

def login(email: str, password: str):
    """Connexion utilisateur avec feedback amélioré"""
    try:
        with st.spinner("🔐 Connexion en cours..."):
            time.sleep(1)  # Effet visuel
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        st.success("🎉 Connexion réussie ! Bienvenue !")
        st.balloons()
        return res
    except Exception as e:
        st.error(f"❌ Échec de la connexion: {str(e)}")
        
        if "Invalid login credentials" in str(e):
            st.warning("🔍 Identifiants invalides. Vérifiez votre email et mot de passe.")
            check_user_status(email)
        elif "Email not confirmed" in str(e):
            st.warning("📧 Email non confirmé. Vérifiez votre boîte mail.")
        
        return None

def signup(email: str, password: str):
    """Inscription utilisateur avec feedback amélioré"""
    try:
        with st.spinner("✨ Création de votre compte..."):
            time.sleep(1)
            res = supabase.auth.sign_up({"email": email, "password": password})
        
        if res.user:
            st.success("🎊 Compte créé avec succès !")
            if res.user.email_confirmed_at is None:
                st.warning("📧 Vérifiez votre email pour activer votre compte")
            else:
                st.success("✅ Compte activé automatiquement !")
            st.balloons()
        else:
            st.error("❌ Erreur lors de la création du compte")
            
        return res
    except Exception as e:
        st.error(f"❌ Échec de l'inscription: {str(e)}")
        return None

def manual_confirm_user(email: str):
    """Confirme manuellement un utilisateur"""
    try:
        response = supabase.auth.admin.list_users()
        users = response.data
        
        for user in users:
            if user.email == email:
                supabase.auth.admin.update_user_by_id(
                    user.id, 
                    {"email_confirmed_at": "now()"}
                )
                st.success(f"✅ {email} confirmé manuellement !")
                return True
                
        st.error("❌ Utilisateur non trouvé")
        return False
    except Exception as e:
        st.error(f"❌ Erreur lors de la confirmation: {e}")
        return False

def generate_session_id():
    return str(uuid.uuid4())

def init_session_state():
    """Initialise les variables de session"""
    if "auth" not in st.session_state:
        st.session_state.auth = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "total_messages" not in st.session_state:
        st.session_state.total_messages = 0

def display_welcome_message():
    """Affiche le message de bienvenue de KYRIA"""
    st.markdown("""
    <div class="welcome-message">
        <h2>👋 Bonjour ! Je suis KYRIA</h2>
        <p>Votre assistant IA personnel spécialisé dans l'analyse de documents.<br>
        Posez-moi vos questions et je vous aiderai à trouver les réponses dans vos documents !</p>
    </div>
    """, unsafe_allow_html=True)

def display_chat():
    """Affiche l'historique du chat avec style"""
    if not st.session_state.messages:
        display_welcome_message()
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**KYRIA:** {message['content']}")

def handle_logout():
    """Gère la déconnexion avec style"""
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    st.session_state.auth = None
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.total_messages = 0
    
    st.success("👋 À bientôt !")
    time.sleep(1)
    st.rerun()

def display_sidebar():
    """Affiche la sidebar avec informations utilisateur"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h3>🤖 KYRIA Dashboard</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Informations utilisateur
        user_email = st.session_state.auth.user.email
        st.markdown(f"""
        <div class="status-card">
            <strong>👤 Utilisateur:</strong><br>
            {user_email}
        </div>
        """, unsafe_allow_html=True)
        
        # Informations de session
        session_short = st.session_state.session_id[:8] if st.session_state.session_id else "N/A"
        st.markdown(f"""
        <div class="status-card">
            <strong>📊 Session:</strong><br>
            {session_short}...
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques
        st.markdown(f"""
        <div class="metric-card">
            <h4>💬 Messages envoyés</h4>
            <h2>{st.session_state.total_messages}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actions
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄", help="Nouvelle session", use_container_width=True):
                st.session_state.session_id = generate_session_id()
                st.session_state.messages = []
                st.session_state.total_messages = 0
                st.rerun()
        
        with col2:
            if st.button("🚪", help="Déconnexion", use_container_width=True):
                handle_logout()

def auth_ui():
    """Interface d'authentification améliorée"""
    display_header()
    
    st.markdown("""
    <div class="auth-container">
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Connexion", "✨ Inscription", "🔧 Debug"])
    
    with tab1:
        st.markdown("### Connectez-vous à KYRIA")
        email = st.text_input("📧 Adresse email", key="login_email", placeholder="votre@email.com")
        password = st.text_input("🔒 Mot de passe", type="password", key="login_password")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🚀 Se connecter", type="primary", use_container_width=True):
                if email and password:
                    auth = login(email, password)
                    if auth and auth.user:
                        st.session_state.auth = auth
                        st.session_state.session_id = generate_session_id()
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("⚠️ Veuillez remplir tous les champs")
        
        with col2:
            if st.button("🔧 Confirmer", help="Confirmer email manuellement", use_container_width=True):
                if email:
                    manual_confirm_user(email)

    with tab2:
        st.markdown("### Créer un compte KYRIA")
        email = st.text_input("📧 Adresse email", key="signup_email", placeholder="votre@email.com")
        password = st.text_input("🔒 Mot de passe", type="password", key="signup_password")
        
        if password:
            strength = "💪 Fort" if len(password) >= 8 else "⚠️ Faible"
            st.caption(f"Force du mot de passe: {strength}")
        
        if st.button("✨ Créer mon compte", type="primary", use_container_width=True):
            if email and password:
                if len(password) >= 6:
                    signup(email, password)
                else:
                    st.error("🔒 Le mot de passe doit contenir au moins 6 caractères")
            else:
                st.error("⚠️ Veuillez remplir tous les champs")

    with tab3:
        st.markdown("### 🔍 Outils de diagnostic")
        debug_email = st.text_input("Email à vérifier", key="debug_email")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Vérifier utilisateur", use_container_width=True):
                if debug_email:
                    check_user_status(debug_email)
        
        with col2:
            if st.button("📋 Lister utilisateurs", use_container_width=True):
                try:
                    response = supabase.auth.admin.list_users()
                    users = response.data
                    st.success(f"✅ {len(users)} utilisateurs trouvés")
                    
                    for user in users:
                        confirmed = "✅" if user.email_confirmed_at else "❌"
                        st.write(f"{confirmed} {user.email}")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def send_message_to_kyria(session_id: str, message: str, access_token: str):
    """Envoie un message à KYRIA avec gestion d'erreurs améliorée"""
    payload = {
        "chatInput": message,
        "sessionId": session_id
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("output", "Désolé, je n'ai pas pu générer de réponse.")
        else:
            return f"❌ Erreur {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return "⏰ Désolé, ma réponse prend plus de temps que prévu. Pouvez-vous réessayer ?"
    except Exception as e:
        return f"❌ Erreur de connexion: {e}"

def main():
    """Fonction principale"""
    init_session_state()

    if st.session_state.auth is None:
        auth_ui()
    else:
        # Interface utilisateur connecté
        display_header()
        display_sidebar()
        
        # Zone de chat principale
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Affichage du chat
        display_chat()
        
        # Interface de saisie
        if prompt := st.chat_input("💭 Posez votre question à KYRIA..."):
            # Incrémenter le compteur de messages
            st.session_state.total_messages += 1
            
            # Ajouter le message utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            # Obtenir le token d'accès
            access_token = st.session_state.auth.session.access_token
            
            # Réponse de KYRIA
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🤖 KYRIA analyse votre demande..."):
                    response = send_message_to_kyria(
                        st.session_state.session_id, 
                        prompt, 
                        access_token
                    )
                    
                    # Effet de frappe
                    placeholder = st.empty()
                    full_response = f"**KYRIA:** {response}"
                    
                    # Animation de typing
                    for i in range(len(full_response) + 1):
                        placeholder.markdown(full_response[:i] + "▌")
                        time.sleep(0.02)
                    
                    placeholder.markdown(full_response)
                    
            # Ajouter la réponse à l'historique
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; padding: 1rem;'>"
            "🤖 <strong>KYRIA</strong> - Assistant IA alimenté par l'intelligence artificielle"
            "</div>", 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()