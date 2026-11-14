import inspect
import streamlit as st

from src import data_loader, preprocessing, visualization, utils
from src import Analysis as analysis   # your file is capitalized

st.set_page_config(page_title="Food Delivery Project", layout="wide")
st.title("Food Delivery Project")

st.subheader("Functions found in src/")
for mod in (data_loader, preprocessing, analysis, visualization, utils):
    funcs = [
        f"{n}{inspect.signature(f)}"
        for n, f in inspect.getmembers(mod, inspect.isfunction)
        if f.__module__ == mod.__name__
    ]
    with st.expander(mod.__name__):
        st.code("\n".join(funcs) or "no functions found")
