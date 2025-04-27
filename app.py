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

df = pd.read_excel("base_parfums.xlsx")
df.fillna("", inplace=True)

if "Sexe" not in df.columns:
    df["Sexe"] = ""

# Création d'une colonne d'affichage combinée pour la liste déroulante
if all(col in df.columns for col in ["Référence", "Nom du Parfum", "Parfumeur"]):
    df["Affichage"] = (
        "[" + df["Référence"].astype(str) + "] " +
        df["Nom du Parfum"].astype(str) + " – " +
        df["Parfumeur"].astype(str)
    )
else:
    df["Affichage"] = df["Nom du Parfum"]

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

mode = st.radio("Mode de recherche", ["🔎 À partir d'un parfum", "🎯 Par critères"], index=1 if forced_note else 0)

if mode == "🔎 À partir d'un parfum":
    parfum_selectionne = st.selectbox("Choisis un parfum", df["Affichage"])

    if parfum_selectionne in df["Affichage"].values:
        idx = df[df["Affichage"] == parfum_selectionne].index[0]
        parfum_ref = df.iloc[idx]
        sexe_ref = parfum_ref["Sexe"]

        scores = list(enumerate(similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        st.subheader("Suggestions similaires :")
        st.markdown("🧠 **Astuce :** choisissez un parfum de la liste ci-dessus pour découvrir les autres fragrances qui lui ressemblent.\n\n\- 🟢 : nombreuses similitudes\n\- 🟠 : similitudes modérées\n\- 🔴 : quelques similitudes\n\nCliquez sur la flèche d'une suggestion pour voir ses facettes et ses notes olfactives.")

        suggestions_affichées = 0
        for i, (index, score) in enumerate(scores[1:]):
            if index == idx:
                continue
            parfum = df.iloc[index]

            if sexe_ref == "Homme" and parfum["Sexe"] not in ["Homme", "Mixte"]:
                continue
            elif sexe_ref == "Femme" and parfum["Sexe"] not in ["Femme", "Mixte"]:
                continue

            if score > 0.5:
                couleur = "🟢"
            elif score > 0.3:
                couleur = "🟠"
            elif score > 0.1:
                couleur = "🔴"
            else:
                continue

            barres = int(score * 10)
            barre_visuelle = "█" * barres + "░" * (10 - barres)
            with st.expander(f"{couleur} `{score:.2f}` – {barre_visuelle} – {parfum['Nom du Parfum']} – {parfum['Marque']} ({parfum['Famille Olfactive Principale']})"):
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

elif mode == "🎯 Par critères":
    col1, col2, col3 = st.columns(3)
    with col1:
        sexe_choisi = st.selectbox("Sexe", ["Tous"] + sorted(df["Sexe"].unique()))
    with col2:
        famille_choisie = st.selectbox("Famille Olfactive Principale", [""] + sorted(df["Famille Olfactive Principale"].unique()))
    with col3:
        facette_choisie = st.selectbox("Facette 1", [""] + sorted(df["Facette 1"].unique()))

    notes_default = [forced_note] if forced_note else []
    notes_choisies = st.multiselect("Notes olfactives (1 à plusieurs)", options=notes_uniques, default=notes_default)

    if forced_note:
        st.markdown(f"🔍 **Parfums contenant : `{forced_note}`**")

    profil_recherche = " ".join([
        famille_choisie,
        facette_choisie,
        " ".join(notes_choisies)
    ])

    if profil_recherche.strip():
        recherche_vect = vectorizer.transform([profil_recherche])
        scores = cosine_similarity(recherche_vect, X)[0]
        sorted_indices = scores.argsort()[::-1]

        st.subheader("Parfums correspondant aux critères :")
        st.markdown("🧠 **Astuce :** sélectionnez des critères pour découvrir les parfums qui s’en rapprochent.\n\n\- 🟢 : très grande proximité\n\- 🟠 : correspondance modérée\n\- 🔴 : points communs limités\n\nCliquez sur la flèche à côté d’un parfum pour afficher ses notes et ses facettes.")

        suggestions_affichées = 0
        for i in sorted_indices:
            parfum = df.iloc[i]
            if sexe_choisi != "Tous" and parfum["Sexe"] != sexe_choisi:
                continue
            if notes_choisies:
                if not all(note in parfum[note_columns].values for note in notes_choisies):
                    continue
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
            barre_visuelle = "█" * barres + "░" * (10 - barres)
            with st.expander(f"{couleur} `{score:.2f}` – {barre_visuelle} – {parfum['Nom du Parfum']} – {parfum['Marque']} ({parfum['Famille Olfactive Principale']})"):
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
            if suggestions_affichées >= 10:
                break
