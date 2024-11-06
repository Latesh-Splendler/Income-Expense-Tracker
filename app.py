import calendar
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import psycopg2
from psycopg2.extras import Json
import plotly.graph_objects as go

# Page configuration
income_categories = ["Salary", "Other income"]
expense_categories = ["MMF", "Groceries", "Utilities", "Other Expenses"]
currency = "KSH"
page_title = "George's Income and Expense Tracker"
layout = "centered"

st.set_page_config(page_title=page_title, layout=layout)
st.title(page_title)

years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="income_expense_tracker",
        user="your_username",
        password="your_password"
    )

# Function to save data into the database
def save_data(month, year, income_data, expense_data, comment):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO data_entries (month, year, income, expenses, comment)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (month, year, Json(income_data), Json(expense_data), comment))
    conn.commit()
    cursor.close()
    conn.close()
    st.success("Data saved successfully!")

# Function to retrieve data from the database
def get_data(period):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT income, expenses, comment FROM data_entries WHERE month = %s AND year = %s"
    cursor.execute(query, (period.split("_")[1], int(period.split("_")[0])))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result if result else ({}, {}, "")

selected = option_menu(
    menu_title="George's Data",
    options=["Data Entry", "Data Visualization"],
    orientation="horizontal",
)

if selected == "Data Entry":
    st.header(f"Data entry in {currency}")

    # Initialize session state for each income and expense category
    for income in income_categories:
        if f"income_{income}" not in st.session_state:
            st.session_state[f"income_{income}"] = 0
    for expense in expense_categories:
        if f"expense_{expense}" not in st.session_state:
            st.session_state[f"expense_{expense}"] = 0

    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        month = col1.selectbox("Select Month:", months, key="month")
        year = col2.selectbox("Select Year:", years, key="year")

        "---"

        with st.expander("Income"):
            income_data = {}
            for income in income_categories:
                income_data[income] = st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=f"income_{income}")
        with st.expander("Expenses"):
            expense_data = {}
            for expense in expense_categories:
                expense_data[expense] = st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=f"expense_{expense}")
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here .......")

        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            save_data(month, year, income_data, expense_data, comment)

if selected == "Data Visualization":
    st.header("Data Visualization")    
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", ["2024_November"])  # You may want to query unique periods from the database dynamically
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            income, expenses, comment = get_data(period)
            if income and expenses:
                total_income = sum(income.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"{total_income} {currency}")
                col2.metric("Total Expense", f"{total_expense} {currency}")
                col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
                st.text(f"Comment: {comment}")

                # Visualization logic here
                # Example: Sankey or Pie Chart (adjust as needed for your data)
            else:
                st.warning("No data available for this period.")
