import streamlit as st
from data import get_all_scores, get_not_declined_scores, load_name_frequencies
import polars as pl


st.markdown("# Niðurstöður")


with st.expander("Atkvæði - round 1"):
    df = get_not_declined_scores()
    freq1, freq2 = load_name_frequencies()
    df2 = df.with_columns(
        [
            pl.col("name").replace(freq1, default=-1).alias("num 1nd"),
            pl.col("name").replace(freq2, default=-1).alias("num 2nd"),

        ]
    )
    st.table(df2)

