import streamlit as st


def apply_style():

    st.markdown(
        """
        <style>

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1 {
            font-size: 2.2rem !important;
        }

        h2 {
            margin-top: 1.5rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,0.2);
            border-radius: 12px;
            padding: 15px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )