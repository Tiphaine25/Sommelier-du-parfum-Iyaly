import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

st.set_page_config(
    page_title="Sommelier du Parfum Iyaly",
    page_icon="🧴",
    layout="wide"
)

st.title("🧴 Sommelier du Parfum Iyaly")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
Bienvenue dans **Iyaly – le sommelier du parfum**.

Explorez notre collection à travers les familles olfactives, les notes de tête, de cœur et de fond.

Laissez votre nez (et notre moteur de similarité) vous guider vers des fragrances cousines.
""", unsafe_allow_html=True)

query = st.query_params
note_query = query.get("note", "")

import os

st.markdown("### 🔍 Fichiers présents dans le dossier :")
st.code("
".join(os.listdir(".")))
