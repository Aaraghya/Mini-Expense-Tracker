import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mini Expense Tracker 💸", layout="centered")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

CSV_FILE = "data.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Date", "Amount", "Category", "Note"])
    df_init.to_csv(CSV_FILE, index=False)

df = pd.read_csv(CSV_FILE)

st.markdown("<h1>✨ Mini Expense Tracker ✨</h1>", unsafe_allow_html=True)
st.caption("track your little spends in style!💳")

with st.form("expense_form"):
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount (₹)", min_value=1)
    with col2:
        category = st.selectbox("Category", ["🍜 Food", "🛍️ Shopping", "🚕 Travel", "🎉 Fun", "📎 Other"])

    note = st.text_input("Note / Emoji (optional)")
    submit = st.form_submit_button("➕ Add Expense")

    if submit:
        new_entry = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Amount": amount,
            "Category": category,
            "Note": note
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("✨ Added! Be mindful with your expenses!✨")
        st.rerun()

total = df["Amount"].sum()
st.markdown(f"<div class='total'>Total Spent: ₹{total:.2f}</div>", unsafe_allow_html=True)

if not df.empty and df["Amount"].sum() > 0:
    pie_data = df.groupby("Category")["Amount"].sum()

    def actual_rupees(pct, allvals):
        total = sum(allvals)
        val = int(round(pct * total / 100.0))
        return f"₹{val}"

    fig, ax = plt.subplots()
    ax.pie(
        pie_data,
        labels=pie_data.index,
        autopct=lambda pct: actual_rupees(pct, pie_data),
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("No expenses to chart yet. Add your first one!")

with st.expander("📜 View all expenses"):
    st.dataframe(df[::-1], use_container_width=True)
