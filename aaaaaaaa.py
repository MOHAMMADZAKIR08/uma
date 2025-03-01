import streamlit as st
import pandas as pd
from datetime import datetime
import ast

# Page configuration
st.set_page_config(page_title="Mobile Sales Tracker", layout="wide")
st.write("## In the name of God, the Most Gracious, the Most Merciful")

# Data file
DATA_FILE = "sales_data.csv"

# Helper function to parse payment history
def parse_payment_history(history_str):
    try:
        payments = ast.literal_eval(history_str)
        for payment in payments:
            if isinstance(payment['Date'], str):
                payment['Date'] = datetime.fromisoformat(payment['Date']).date()
        return payments
    except:
        return []

# Load data from CSV
def load_data():
    try:
        data = pd.read_csv(DATA_FILE).to_dict(orient='records')
        for entry in data:
            if 'Payment History' in entry:
                entry['Payment History'] = parse_payment_history(entry['Payment History'])
            else:
                entry['Payment History'] = []
        return data
    except FileNotFoundError:
        return []

# Save data to CSV
def save_data():
    df = pd.DataFrame(st.session_state.data)
    df['Payment History'] = df['Payment History'].apply(
        lambda x: str([{'Date': p['Date'].isoformat(), 'Amount': p['Amount']} for p in x])
    )
    df.to_csv(DATA_FILE, index=False)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'delete_index' not in st.session_state:
    st.session_state.delete_index = None

# Authentication credentials
VALID_USERNAME = "kaka"
VALID_PASSWORD = "#azmatufo"
PASSKEY = "aujac"
REMOVE_PASSKEY = "88899"

# Ensure 'Paid' and 'Payment History' keys exist in each entry
def ensure_paid_key():
    for entry in st.session_state.data:
        if "Paid" not in entry:
            entry["Paid"] = 0
        if "Payment History" not in entry:
            entry["Payment History"] = []

# Authenticate user
def authenticate(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

# Login form
def login_form():
    with st.form("Login"):
        st.write("## 🔒 Login to Access System")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

# Add a new mobile sale entry
def add_entry(date, holder_name, mobile_name, mobile_rate, paid):
    remaining_amount = max(0, mobile_rate - paid)
    new_entry = {
        "Date": date,
        "Holder Name": holder_name,
        "Mobile Name": mobile_name,
        "Mobile Rate": mobile_rate,
        "Remaining Amount": remaining_amount,
        "Paid": paid,
        "Payment History": [{"Date": date, "Amount": paid}]
    }
    st.session_state.data.append(new_entry)
    save_data()

# Update remaining amount and add payment history
def update_remaining_amount(index, amount_paid):
    if amount_paid <= st.session_state.data[index]["Remaining Amount"]:
        st.session_state.data[index]["Remaining Amount"] -= amount_paid
        st.session_state.data[index]["Paid"] += amount_paid
        payment_date = datetime.today().date()
        st.session_state.data[index]["Payment History"].append({"Date": payment_date, "Amount": amount_paid})
        st.success(f"₹{amount_paid} paid for {st.session_state.data[index]['Holder Name']} on {payment_date}!")
        save_data()
    else:
        st.error("Amount paid cannot exceed the remaining amount!")

# Calculate summary metrics
def calculate_summary():
    ensure_paid_key()
    total_sold = len(st.session_state.data)
    total_remaining = sum(entry["Remaining Amount"] for entry in st.session_state.data)
    total_collected = sum(entry["Paid"] for entry in st.session_state.data)
    return total_sold, total_remaining, total_collected

# Clear all data
def clear_data():
    st.session_state.data = []
    save_data()
    st.success("All data cleared successfully!")

# Handle entry deletion with passkey
def handle_entry_deletion():
    if st.session_state.delete_index is not None:
        with st.form(key="delete_confirmation"):
            st.warning("⚠️ Confirm Entry Deletion")
            passkey = st.text_input("Enter Delete Passkey", type="password")
            submitted = st.form_submit_button("🔥 Confirm Permanent Delete")
            
            if submitted:
                if passkey == REMOVE_PASSKEY:
                    del st.session_state.data[st.session_state.delete_index]
                    save_data()
                    st.success("Entry permanently deleted!")
                    st.session_state.delete_index = None
                    st.experimental_rerun()
                else:
                    st.error("Incorrect passkey! Deletion failed.")
                    st.session_state.delete_index = None

# Login check
if not st.session_state.logged_in:
    login_form()
    st.stop()

# Sidebar for logout
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Main app
st.title("📱 Mobile Sales DATA")
st.write("DBS")

# Display summary metrics
total_sold, total_remaining, total_collected = calculate_summary()
col1, col2, col3 = st.columns(3)
col1.metric("📦 New Mobiles Sold", total_sold)
col2.metric("💰 Total Remaining Cash", f"₹{total_remaining}")
col3.metric("💵 Total Cash Collected", f"₹{total_collected}")

# Add new mobile sale
with st.expander("📝 Add New Mobile Sale", expanded=True):
    with st.form("entry_form"):
        date = st.date_input("Date", datetime.today())
        holder_name = st.text_input("Holder Name")
        mobile_name = st.text_input("Mobile Name")
        mobile_rate = st.number_input("Mobile Rate (₹)", min_value=0)
        paid = st.number_input("Paid (₹)", min_value=0)
        passkey = st.text_input("Enter Passkey to Add New Mobile", type="password")
        
        submitted = st.form_submit_button("💾 Save as Voucher")
        if submitted:
            if passkey == PASSKEY:
                add_entry(date, holder_name, mobile_name, mobile_rate, paid)
                st.success("Voucher saved successfully!")
            else:
                st.error("Incorrect passkey! Access denied.")
    
    if st.button("🧹 Clear All Data"):
        if st.session_state.data:
            st.warning("Are you sure you want to clear all data? This action cannot be undone.")
            if st.button("✅ Confirm Clear Data"):
                clear_data()
                st.experimental_rerun()
        else:
            st.info("No data to clear.")

# Display existing entries
st.write("### 📜 Existing Entries")
if st.session_state.data:
    ensure_paid_key()
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)
    
    for i, entry in enumerate(st.session_state.data):
        with st.expander(f"🗂 {entry['Holder Name']} - {entry['Mobile Name']}"):
            st.write(f"**Date:** {entry['Date']}")
            st.write(f"**Mobile Rate:** ₹{entry['Mobile Rate']}")
            st.write(f"**Remaining Amount:** ₹{entry['Remaining Amount']}")
            st.write(f"**Paid:** ₹{entry['Paid']}")
            
            st.write("### Payment History")
            if entry['Payment History']:
                for payment in entry['Payment History']:
                    st.write(f"- **Date:** {payment['Date']}, **Amount:** ₹{payment['Amount']}")
            else:
                st.info("No payment history yet.")
            
            if st.button("❌ Remove Entry", key=f"remove_{i}"):
                st.session_state.delete_index = i
                st.experimental_rerun()

    handle_entry_deletion()

    # Add cash collection
    with st.sidebar:
        st.write("### 💵 Add Cash Collection")
        holder_names = [entry["Holder Name"] for entry in st.session_state.data]
        selected_holder = st.selectbox("Select Holder Name", holder_names)
        selected_index = next(i for i, entry in enumerate(st.session_state.data) if entry["Holder Name"] == selected_holder)
        
        st.write(f"**Mobile Name:** {st.session_state.data[selected_index]['Mobile Name']}")
        st.write(f"**Remaining Amount:** ₹{st.session_state.data[selected_index]['Remaining Amount']}")
        st.write(f"**Paid:** ₹{st.session_state.data[selected_index]['Paid']}")
        
        with st.form("cash_form"):
            amount_paid = st.number_input("Amount Paid (₹)", min_value=0)
            passkey = st.text_input("Enter Passkey to Add Cash", type="password")
            submitted = st.form_submit_button("💸 Add Cash")
            if submitted:
                if passkey == PASSKEY:
                    update_remaining_amount(selected_index, amount_paid)
                    st.experimental_rerun()
                else:
                    st.error("Incorrect passkey! Access denied.")
else:
    st.info("No entries yet. Add a new mobile sale to get started!")