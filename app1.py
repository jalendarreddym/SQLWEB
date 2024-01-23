import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import io
from dotenv import load_dotenv

load_dotenv()
import sys
import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([input, prompt])
    return response.text

# Function to connect to the database
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
    except Error as e:
        st.error(f"The error '{e}' occurred")
    return connection

# Function to execute a read query and return results with column names
def execute_read_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        columns = cursor.description
        cursor.close()
        return result, columns
    except Error as e:
        st.error(f"The error '{e}' occurred")
        return None, None

# Streamlit UI
st.title("Database Query Executor")

# Database connection details
host = st.text_input("Host", "localhost")
user = st.text_input("User", "root")
password = st.text_input("Password", "sqlserver")
database = st.text_input("Database", "fmcg")

# Fetch list of tables from the database
# Fetch list of tables and their column names from the database
connection = create_connection(host, user, password, database)
if connection:
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    table_names = [table[0] for table in cursor.fetchall()]

    # Create a dictionary to store table names and column names
    tables_data = {}
    for table_name in table_names:
        cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        columns = [column[0] for column in cursor.fetchall()]
        tables_data[table_name] = columns

    cursor.close()
    connection.close()

    # Create the input_prompt with the list of tables and their columns
    input_prompt = "You are an experienced SQL developer. Your task is to generate a SQL statement based on the provided statement. Please provide a valid SQL query that corresponds to the given statement.\n\n"
    input_prompt += "List of available tables and columns:\n"
    for table_name, columns in tables_data.items():
        input_prompt += f"{table_name}: {', '.join(columns)}\n"


    # Table selection dropdown
    table_name = st.selectbox("Table Name", table_names, index=0)

    connect_button = st.button("Fetch Data")

    if connect_button:
        # Connect to the database
        connection = create_connection(host, user, password, database)

        if connection:
            # Fetch top 10 rows from the specified table
            query = f"SELECT * FROM {table_name} LIMIT 10;"
            results, columns = execute_read_query(connection, query)

            if results:
                # Display the table details
                st.write(f"**Database Name:** {database}")
                st.write(f"**Table Name:** {table_name}")
                st.write("**Join:** No join")  # Modify this as per your requirement

                # Display the results in a table
                df = pd.DataFrame(results)
                df.columns = [x[0] for x in columns]  # Setting column names
                st.table(df.style.set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold')]}]))

            connection.close()



## Streamlit App

st.markdown("# SQL Statement Generator")
st.header("Generate SQL Statements")

input_text = st.text_area("Enter your statement:", key="input")

submit = st.button("Generate SQL Statement")

#input_prompt = """
#You are an experienced SQL developer. Your task is to generate a SQL statement based on the provided statement. Please provide a valid SQL query that corresponds to the given statement.
#"""

if submit:
    if input_text:
        response = get_gemini_response(input_text, input_prompt)
        st.subheader("Generated SQL Statement:")
        st.write(response)
    else:
        st.write("Please enter a statement to generate a SQL statement.")


input_text_sql = st.text_area("Enter your statement:")
SQL_button = st.button("SQL Query")
if SQL_button:
    # Connect to the database
    connection = create_connection(host, user, password, database)

    if connection:
        # Fetch top 10 rows from the specified table
        query = input_text_sql
        results, columns = execute_read_query(connection, query)

        if results:
            # Display the table details
            st.write(f"**Database Name:** {database}")
            # st.write(f"**Table Name:** {table_name}")
            # st.write("**Join:** No join")  # Modify this as per your requirement

            # Display the results in a table
            df = pd.DataFrame(results)
            df.columns = [x[0] for x in columns]  # Setting column names
            st.table(df.style.set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold')]}]))

        connection.close()


