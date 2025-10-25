import streamlit as st

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa fazer o login para acessar esta página!")
    st.stop()