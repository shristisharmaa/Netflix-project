import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Netflix Analytics", layout="wide")
st.title("📊 Netflix Media Analytics Pipeline")

# File Upload
file = st.file_uploader("Upload Netflix CSV", type=["csv"])

if file is not None:
    df = pd.read_csv(file)

    st.subheader("📌 Raw Data")
    st.dataframe(df)

    # Show columns (for debugging / understanding)
    st.write("Columns in dataset:", df.columns)

    # ---------------- LOAD TO SQLITE ----------------
    conn = sqlite3.connect("netflix.db")
    df.to_sql("netflix", conn, if_exists="replace", index=False)

    st.success("Data loaded into database ✅")

    # Detect correct genre column
    if "genre" in df.columns:
        genre_col = "genre"
    elif "listed_in" in df.columns:
        genre_col = "listed_in"
    else:
        genre_col = df.columns[1]  # fallback

    # ---------------- SQL QUERIES ----------------
    st.markdown("---")
    st.subheader("📊 Insights (SQL)")

    # Top Genres
    if st.button("Top Genres"):
        query = f"""
        SELECT {genre_col}, COUNT(*) as count
        FROM netflix
        GROUP BY {genre_col}
        ORDER BY count DESC;
        """
        result = pd.read_sql_query(query, conn)
        st.dataframe(result)

    # Top Rated Movies/Shows
    if st.button("Top Rated Content"):
        query = """
        SELECT title, rating
        FROM netflix
        ORDER BY rating DESC
        LIMIT 5;
        """
        result = pd.read_sql_query(query, conn)
        st.dataframe(result)

    # Content per Year
    if st.button("Content per Year"):
        query = """
        SELECT release_year, COUNT(*) as total
        FROM netflix
        GROUP BY release_year
        ORDER BY total DESC;
        """
        result = pd.read_sql_query(query, conn)
        st.dataframe(result)

    # ---------------- CUSTOM SQL ----------------
    st.markdown("---")
    st.subheader("🧠 Custom SQL Query")

    query_input = st.text_area("Write SQL query (table name: netflix)")

    if st.button("Run Query"):
        try:
            result = pd.read_sql_query(query_input, conn)
            st.dataframe(result)
        except Exception as e:
            st.error(f"Error: {e}")

    conn.close()