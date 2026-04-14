import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Netflix Analytics", layout="wide")
st.title("📊 Netflix Media Analytics Pipeline")

# ---------------- FILE UPLOAD ----------------
file = st.file_uploader("Upload Netflix CSV", type=["csv"])

if file is not None:

    try:
        df = pd.read_csv(file)

        # ----------- VALIDATION -----------
        if df.empty:
            st.error("Uploaded file is empty ❌")
            st.stop()

        st.subheader("📌 Raw Data")
        st.dataframe(df)

        # Show columns for debugging
        st.write("📊 Available Columns:", df.columns.tolist())

        # ----------- BASIC CLEANING -----------
        df = df.drop_duplicates()
        df = df.fillna("Unknown")

        # Convert date column if exists
        if "date_added" in df.columns:
            df["date_added"] = pd.to_datetime(df["date_added"], errors='coerce')

        st.subheader("🧹 Cleaned Data")
        st.dataframe(df)

        # ---------------- LOAD TO SQLITE ----------------
        conn = sqlite3.connect("netflix.db")
        df.to_sql("netflix", conn, if_exists="replace", index=False)

        st.success("Data loaded into database ✅")

        # ----------- DETECT GENRE COLUMN -----------
        if "genre" in df.columns:
            genre_col = "genre"
        elif "listed_in" in df.columns:
            genre_col = "listed_in"
        else:
            genre_col = df.columns[1]

        # ---------------- SQL INSIGHTS ----------------
        st.markdown("---")
        st.subheader("📊 Insights (SQL + Visualization)")

        # ----------- TOP GENRES -----------
        if st.button("Top Genres"):
            try:
                query = f"""
                SELECT {genre_col} as genre, COUNT(*) as count
                FROM netflix
                GROUP BY genre
                ORDER BY count DESC;
                """
                result = pd.read_sql_query(query, conn)
                st.dataframe(result)
                st.bar_chart(result.set_index("genre"))
            except Exception as e:
                st.error(f"Error: {e}")

        # ----------- TOP RATED CONTENT -----------
        if st.button("Top Rated Content"):
            try:
                if "rating" in df.columns:
                    query = """
                    SELECT title, rating
                    FROM netflix
                    ORDER BY rating DESC
                    LIMIT 5;
                    """
                    result = pd.read_sql_query(query, conn)
                    st.dataframe(result)
                else:
                    st.error("Column 'rating' not found ❌")
            except Exception as e:
                st.error(f"Error: {e}")

        # ----------- CONTENT PER YEAR -----------
        if st.button("Content per Year"):
            try:
                if "release_year" in df.columns:
                    query = """
                    SELECT release_year, COUNT(*) as total
                    FROM netflix
                    GROUP BY release_year
                    ORDER BY total DESC;
                    """
                    result = pd.read_sql_query(query, conn)
                    st.dataframe(result)
                    st.bar_chart(result.set_index("release_year"))
                else:
                    st.error("Column 'release_year' not found ❌")
            except Exception as e:
                st.error(f"Error: {e}")

        # ---------------- CUSTOM SQL ----------------
        st.markdown("---")
        st.subheader("🧠 Custom SQL Query")

        st.info("👉 Run queries on table: netflix")

        query_input = st.text_area("Write SQL query")

        if st.button("Run Query"):
            try:
                result = pd.read_sql_query(query_input, conn)
                st.dataframe(result)
            except Exception as e:
                st.error(f"Error: {e}")

        conn.close()

    except Exception as e:
        st.error(f"File Error: {e}")
