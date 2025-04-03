import streamlit as st
import mysql.connector
import pandas as pd

# MySQL Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",    # e.g., "localhost" or your server IP
        user="root",    # Replace with your MySQL username
        password="Soham@456",  # Replace with your MySQL password
        database="soham"   # Replace with your database name
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
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows] if rows else []

# Insert or Update Data
def insert_data(table):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch names
    names = get_student_names(table)

    if not names:
        st.error("⚠️ No student names found! Add names first.")
        return

    selected_name = st.selectbox("Select Student", names)

    # Fetch column names excluding primary keys and 'Total'
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

# Fetch and Display Data
def view_data(table):
    conn = get_connection()
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Export Data to Excel
#def export_to_excel(table):
    df = view_data(table)
    df.to_excel(f"{table}.xlsx", index=False)
    st.success(f"📂 {table}.xlsx exported successfully!")
def delete_data(table):
    conn = get_connection()
    cursor = conn.cursor()
def download_full_excel():
    tables = get_table_names()

    if not tables:
        st.error("⚠️ No tables found in the database!")
        return None

    # Create an Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for table in tables:
            df = get_table_data(table)
            df.to_excel(writer, sheet_name=table, index=False)

    output.seek(0)
    return output

# Streamlit UI
st.title("📊 Student Data Management System")

st.subheader("📥 Download Full Database as Excel")
if st.button("🔽 Download Entire Database"):
    excel_data = download_full_excel()
    if excel_data:
        st.download_button(
            label="📂 Click to Download mira_db.xlsx",
            data=excel_data,
            file_name="mira_db.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
def delete_data(table):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch names
    names = get_student_names(table)

    if not names:
        st.error("⚠️ No student names found! Add names first.")
        return

    selected_name = st.selectbox("🗑️ Select Student to Delete", names, key="delete_name")

    if st.button("❌ Delete Record"):
        cursor.execute(f"DELETE FROM {table} WHERE Name = %s", (selected_name,))
        conn.commit()
        st.success(f"🗑️ Deleted {selected_name} from {table}!")

    conn.close()

#st.title("📊 Student Data Entry System")

# Debugging: Print existing tables
tables = get_table_names()
st.write("✅ Available Tables in DB:", tables)

# Select Table
table = st.selectbox("🔹 Select Table", tables)

if table:
    st.subheader(f"📌 Add or Update Data in {table}")
    insert_data(table)

    st.subheader(f"📌 {table} Data")
    st.dataframe(view_data(table))

    st.subheader(f"🗑️ Delete Student Data from {table}")
    delete_data(table)

    if st.button("📥 Export to Excel"):
        export_to_excel(table)