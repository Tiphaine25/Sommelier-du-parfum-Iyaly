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

df = pd.read_excel("base_parfums.xlsx")
df.fillna("", inplace=True)

if "Sexe" not in df.columns:
    df["Sexe"] = ""

df["Profil"] = (
    df["Famille Olfactive Principale"].astype(str) + " " +
    df["Facette 1"].astype(str) + " " +
    df["Facette 2"].astype(str) + " " +
    df["Notes de Tête 1"].astype(str) + " " +
    df["Notes de Tête 2"].astype(str) + " " +
    df["Notes de Cœur 1"].astype(str) + " " +
    df["Notes de Cœur 2"].astype(str) + " " +
    df["Notes de Fond 1"].astype(str) + " " +
    df["Notes de Fond 2"].astype(str)
)

# Chargement du fichier externe de parfums du monde
try:
    df_fra = pd.read_csv("fra_cleaned.csv")
    df_fra.fillna("", inplace=True)
    df_fra["Profil"] = (
        df_fra["OlfactoryFamily"].astype(str) + " " +
        df_fra["MainAccords"].astype(str) + " " +
        df_fra["TopNotes"].astype(str) + " " +
        df_fra["HeartNotes"].astype(str) + " " +
        df_fra["BaseNotes"].astype(str)
    )
    fra_loaded = True
except:
    fra_loaded = False

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df["Profil"])
similarity = cosine_similarity(X)

note_columns = [
    "Notes de Tête 1", "Notes de Tête 2",
    "Notes de Cœur 1", "Notes de Cœur 2",
    "Notes de Fond 1", "Notes de Fond 2"
]
notes_uniques = pd.unique(
    pd.concat([df[col] for col in note_columns]).dropna().astype(str)
)
notes_uniques = sorted([note for note in notes_uniques if note.strip() != ""])

forced_note = note_query if note_query in notes_uniques else ""

mode = st.radio("Mode de recherche", ["🔎 À partir d'un parfum", "🎯 Par critères", "🌍 Comparer avec un parfum existant"])

if mode == "🌍 Comparer avec un parfum existant" and fra_loaded:
    st.markdown("""
**Sélectionnez un parfum célèbre** pour découvrir les parfums Iyaly qui lui ressemblent le plus :
""")
    df_fra["Intitulé"] = df_fra["Name"] + " – " + df_fra["Brand"]
    search_term = st.text_input("Recherchez un parfum externe par nom ou marque :")
    parfums_visibles = df_fra[df_fra["Intitulé"].str.contains(search_term, case=False, na=False)]
    selection = st.selectbox("Choisissez un parfum externe", parfums_visibles["Intitulé"] if not parfums_visibles.empty else [""])
    if selection:
        idx = df_fra[df_fra["Intitulé"] == selection].index[0]
        parfum_externe = df_fra.iloc[idx]
        st.markdown(f"**Accords dominants :** {parfum_externe['MainAccords']}")
        parfum_externe = df_fra.iloc[idx]
        vect_ext = vectorizer.transform([parfum_externe["Profil"]])
        scores = cosine_similarity(vect_ext, X)[0]
        sorted_indices = scores.argsort()[::-1]

        st.subheader("Parfums Iyaly similaires :")
        suggestions_affichées = 0
        for i in sorted_indices:
            parfum = df.iloc[i]
            score = scores[i]
            if score > 0.5:
                couleur = "🟢"
            elif score > 0.3:
                couleur = "🟠"
            elif score > 0.1:
                couleur = "🔴"
            else:
                continue
            barres = int(score * 10)
            st.progress(int(score * 100), text=f"{score:.2%} de similarité")
            with st.expander(f"{couleur} `{score:.2f}` – {barre_visuelle} – {parfum['Nom du Parfum']} ({parfum['Famille Olfactive Principale']})"):
                st.markdown(f"**Facette 1 :** {parfum['Facette 1']}")
                st.markdown(f"**Facette 2 :** {parfum['Facette 2']}")
                for section, note1, note2 in [("Notes de Tête", "Notes de Tête 1", "Notes de Tête 2"),
                                              ("Notes de Cœur", "Notes de Cœur 1", "Notes de Cœur 2"),
                                              ("Notes de Fond", "Notes de Fond 1", "Notes de Fond 2")]:
                    notes = []
                    for col in [note1, note2]:
                        note = parfum[col]
                        if note:
                            notes.append(f"[{note}](?note={note})")
                    st.markdown(f"**{section} :** " + ", ".join(notes))
            suggestions_affichées += 1
            if suggestions_affichées >= 5:
                break
elif mode == "🌍 Comparer avec un parfum existant":
    st.warning("⚠️ Le fichier de parfums externes est introuvable. Veuillez charger 'fra_cleaned.csv' dans le répertoire de l'app.")
