
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AI Business Intelligence Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Business Intelligence Assistant")
st.write("Ask questions about your sales data in plain English.")

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "ai_bi_assistant_sales_data - GET.csv"
DB_FILE = BASE_DIR / "sales.db"


@st.cache_data
def load_sales_data():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found: {CSV_FILE.name}"
        )

    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip()

    required = [
        "Transaction_Id", "Order_date", "Product", "Category",
        "Region", "Sales_channel", "Quantity", "Unit_price",
        "Discount_amount", "Status"
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["Order_date"] = pd.to_datetime(
        df["Order_date"], dayfirst=True, errors="coerce"
    )

    for col in ["Quantity", "Unit_price", "Discount_amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Exclude invalid, returned, or incomplete transactions.
    df = df.dropna(subset=[
        "Transaction_Id", "Order_date", "Product", "Region",
        "Quantity", "Unit_price", "Discount_amount", "Status"
    ])

    df = df[
        (df["Quantity"] > 0)
        & (df["Unit_price"] >= 0)
        & (df["Discount_amount"] >= 0)
        & (df["Discount_amount"] <=
           df["Quantity"] * df["Unit_price"])
        & (df["Status"].str.strip().str.lower() == "completed")
    ].copy()

    df["Revenue"] = (
        df["Quantity"] * df["Unit_price"]
        - df["Discount_amount"]
    )

    df["Month"] = df["Order_date"].dt.to_period("M").astype(str)

    # Store the cleaned data in a local SQLite database.
    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)

    return df


def answer_question(question, df):
    q = question.lower().strip()

    if not q:
        return "Please enter a question.", pd.DataFrame()

    if any(word in q for word in [
        "delete", "drop table", "update database",
        "remove records", "truncate"
    ]):
        return "Database modification requests are not supported.", pd.DataFrame()

    if any(word in q for word in [
        "total revenue", "overall revenue", "revenue generated",
        "total sales", "overall sales", "how much revenue"
    ]):
        total = df["Revenue"].sum()
        return (
            f"Total revenue from valid completed transactions is "
            f"₹{total:,.2f}.",
            pd.DataFrame({"Metric": ["Total revenue"], "Value": [total]})
        )

    if "product" in q and any(word in q for word in [
        "highest", "top", "best", "maximum"
    ]) and "revenue" in q:
        result = (
            df.groupby("Product", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=False)
        )
        top = result.iloc[0]
        return (
            f"{top['Product']} generated the highest revenue: "
            f"₹{top['Revenue']:,.2f}.",
            result
        )

    if "month" in q and any(word in q for word in [
        "trend", "monthly", "each month", "over time"
    ]):
        result = (
            df.groupby("Month", as_index=False)["Revenue"]
            .sum()
            .sort_values("Month")
        )
        return "Here is the monthly revenue trend.", result

    if "region" in q and any(word in q for word in [
        "highest", "top", "best", "sales", "revenue"
    ]):
        result = (
            df.groupby("Region", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=False)
        )
        top = result.iloc[0]
        return (
            f"{top['Region']} generated the highest regional revenue: "
            f"₹{top['Revenue']:,.2f}.",
            result
        )


    if "change" in q and "revenue" in q and "between" in q:
        import re

        months = re.findall(r"\b\d{4}-\d{2}\b", q)

        if len(months) != 2:
            return (
                "Please include two months in YYYY-MM format, "
                "for example: How did revenue change between "
                "2026-01 and 2026-02?",
                pd.DataFrame()
            )

        first, second = months

        available_months = set(df["Month"].unique())

        if first not in available_months or second not in available_months:
            return (
                "One or both months are not available in the sales data.",
                pd.DataFrame()
            )

        totals = df.groupby("Month")["Revenue"].sum()
        change = totals[second] - totals[first]

        percentage = (
            change / totals[first] * 100
            if totals[first] != 0 else None
        )

        result = pd.DataFrame({
            "Month": [first, second],
            "Revenue": [totals[first], totals[second]]
        })

        message = (
            f"Revenue changed by ₹{change:,.2f} "
            f"from {first} to {second}."
        )

        if percentage is not None:
            message += f" Percentage change: {percentage:.2f}%."

        return message, result


    return (
        "I couldn't identify that question. Try one of the "
        "example questions shown below.",
        pd.DataFrame()
    )


try:
    sales = load_sales_data()

    st.success(
        f"Sales database ready | {len(sales)} valid transactions"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹{sales['Revenue'].sum():,.2f}")
    col2.metric("Transactions", f"{len(sales):,}")
    col3.metric("Products", f"{sales['Product'].nunique():,}")

    st.subheader("Ask a business question")

    question = st.text_input(
        "Enter your question",
        placeholder="What is the total revenue?"
    )

    st.caption(
        "Try: What is the total revenue? | Which product generated "
        "the highest revenue? | Show monthly revenue trend | "
        "Which region generated the highest sales?"
    )

    if st.button("Get Answer", type="primary"):
        answer, result = answer_question(question, sales)
        st.subheader("Answer")
        st.write(answer)

        if not result.empty:
            st.subheader("Supporting data")
            st.dataframe(result, use_container_width=True)

            if "Revenue" in result.columns and len(result) > 1:
                st.bar_chart(result.set_index(result.columns[0])["Revenue"])

    with st.expander("View cleaned sales data"):
        st.dataframe(sales, use_container_width=True)

    with st.expander("Database information"):
        st.write("Database: SQLite")
        st.write("Table: sales")
        st.write("Revenue = Quantity × Unit Price − Discount")
        st.write("Only valid completed transactions are included.")

except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(str(error))
except Exception as error:
    st.error(f"An unexpected error occurred: {error}")


