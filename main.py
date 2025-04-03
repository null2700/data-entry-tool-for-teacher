import streamlit as st
import mysql.connector
import pandas as pd

# Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",    # Change if MySQL is on another machine
        user="root",         # Replace with your MySQL username
        password="Soham@456",      # Replace with your MySQL password 
        database="soham"     # Replace with your database name
    )

# Fetch Table Names
def get_table_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

# Fetch Student Names
def get_student_names(table):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT Name FROM {table}")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

# Insert or Update Data
def insert_data(table):
    names = get_student_names(table)
    if not names:
        st.error("⚠️ No student names found! Add names first.")
        return

    selected_name = st.selectbox("Select Student", names)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table}")
    columns = [col[0] for col in cursor.fetchall() if col[0] not in ["RollNo", "Name", "Total"]]
    
    data = {"Name": selected_name}
    for col in columns:
        data[col] = st.number_input(f"Enter {col} for {selected_name}", min_value=0, step=1, key=col)

    if st.button("Submit Data"):
        query = f"UPDATE {table} SET {', '.join([f'{col} = %s' for col in columns])} WHERE Name = %s"
        cursor.execute(query, tuple(data[col] for col in columns) + (selected_name,))
        conn.commit()
        st.success(f"✅ Data updated for {selected_name} in {table}")

    conn.close()

# View Data
def view_data(table):
    conn = get_connection()
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Delete Student Data
def delete_data(table):
    names = get_student_names(table)
    if not names:
        st.error("⚠️ No student names found! Add names first.")
        return

    selected_name = st.selectbox("🗑️ Select Student to Delete", names, key="delete_name")

    if st.button("❌ Delete Record"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE Name = %s", (selected_name,))
        conn.commit()
        conn.close()
        st.success(f"🗑️ Deleted {selected_name} from {table}!")

# Export All Data to Excel
def export_all_to_excel():
    conn = get_connection()
    with pd.ExcelWriter("All_Data.xlsx") as writer:
        for table in get_table_names():
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            df.to_excel(writer, sheet_name=table, index=False)
    conn.close()

    with open("All_Data.xlsx", "rb") as f:
        st.download_button(label="📥 Download All Data", data=f, file_name="All_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Streamlit UI
st.title("📊 Student Data Management System")

tables = get_table_names()
st.write("✅ Available Tables:", tables)

table = st.selectbox("🔹 Select Table", tables)

if table:
    st.subheader(f"📌 Add or Update Data in {table}")
    insert_data(table)

    st.subheader(f"📌 View {table} Data")
    st.dataframe(view_data(table))

    st.subheader(f"🗑️ Delete Student Data from {table}")
    delete_data(table)

st.subheader("📥 Download All Data")
export_all_to_excel()