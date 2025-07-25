import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mini Expense Tracker 💸", layout="centered")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar login
st.sidebar.title("🔐 Welcome!")
username = st.sidebar.text_input("Enter your username", max_chars=20)
if not username:
    st.warning("Please enter a username in the sidebar to continue.")
    st.stop()

# Create a unique CSV per user
CSV_FILE = f"data_{username}.csv"
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
        category = st.selectbox("Category", ["🍜 Food", "💼 Shopping", "🚕 Travel", "🎉 Fun", "📌 Other"])

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

# Filter Section
st.subheader("📅 Filter by Date Range")
df["Date"] = pd.to_datetime(df["Date"])
date_min, date_max = df["Date"].min(), df["Date"].max()
start_date = st.date_input("From", date_min.date() if pd.notnull(date_min) else datetime.today())
end_date = st.date_input("To", date_max.date() if pd.notnull(date_max) else datetime.today())

mask = (df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask]

total = df_filtered["Amount"].sum()
st.markdown(f"<div class='total'>Total Spent: ₹{total:.2f}</div>", unsafe_allow_html=True)

if not df_filtered.empty and df_filtered["Amount"].sum() > 0:
    pie_data = df_filtered.groupby("Category")["Amount"].sum()

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
    st.info("No expenses to chart in this date range. Add one!")

with st.expander("📜 View all expenses"):
    st.dataframe(df_filtered[::-1], use_container_width=True)
    st.download_button("📂 Export CSV", df_filtered.to_csv(index=False), file_name=f"{username}_expenses.csv", mime="text/csv")

# Monthly Top Spending
if not df.empty:
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    monthly_summary = df.groupby(["Month", "Category"])["Amount"].sum().reset_index()
    top_spends = monthly_summary.loc[monthly_summary.groupby("Month")["Amount"].idxmax()]

    with st.expander("📊 Top Spending Category Each Month"):
        st.dataframe(top_spends, use_container_width=True)
