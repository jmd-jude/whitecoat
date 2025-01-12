import streamlit as st
from supabase.client import Client

def render_auth_ui(supabase: Client):
    """Render authentication UI with name fields."""
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    
    # Toggle between login/signup
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True, 
                    type="primary" if st.session_state.auth_view == "login" else "secondary"):
            st.session_state.auth_view = "login"
    with col2:
        if st.button("Sign Up", use_container_width=True,
                    type="primary" if st.session_state.auth_view == "signup" else "secondary"):
            st.session_state.auth_view = "signup"
    
    # Login form
    if st.session_state.auth_view == "login":
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state.user = res.user
                    st.session_state.authenticated = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
    
    # Signup form
    else:
        with st.form("signup_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Sign Up", use_container_width=True):
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif not first_name or not last_name:
                    st.error("Please enter your full name")
                else:
                    try:
                        # Sign up with name metadata
                        res = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "full_name": f"{first_name} {last_name}"
                                }
                            }
                        })
                        
                        if res.user:
                            st.session_state.user = res.user
                            st.session_state.authenticated = True
                            st.success("Account created successfully!")
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"Signup failed: {str(e)}")

def render_user_menu(supabase: Client):
    """Render user menu when logged in."""
    if st.session_state.get("authenticated"):
        user = st.session_state.user
        name = user.user_metadata.get("full_name", user.email)
        
        # User menu in sidebar
        with st.sidebar:
            st.write(f"👤 {name}")
            if st.button("Logout", use_container_width=True):
                supabase.auth.sign_out()
                st.session_state.clear()
                st.rerun()
