import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# ===================== FILE PATHS =====================
USERS_FILE = "users.xlsx"
INVENTORY_FILE = "inventory.xlsx"
ORDERS_FILE = "orders.xlsx"
ADMIN_FILE = "admin_access.xlsx"
ORDER_DETAILS_FILE = "order_details.xlsx"

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    /* Hide the top header/toolbar */
    header {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    #MainMenu {
        visibility: hidden !important;
    }
    
    footer {
        visibility: hidden !important;
    }
    
    .stDeployButton {
        visibility: hidden !important;
    }
    
    /* Main background - Black */
    .stApp {
        background-color: #171717 !important;
    }
    
    /* Remove/hide the top header bar */
    header[data-testid="stHeader"] {
        background-color: #171717 !important;
    }
    
    .main .block-container {
        padding-top: 1rem !important;
    }
    
    /* All text should be white by default for visibility on black background */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
        color: white !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1f1f1f !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Input boxes styling - white background with white text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #2a2a2a !important;
        border: 2px solid #404040 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        color: white !important;
    }
    
    /* Button styling - #b3865c with white text */
    .stButton > button {
        background-color: #b3865c !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        border: none !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #9a7050 !important;
        box-shadow: 0 4px 6px rgba(179, 134, 92, 0.3) !important;
        color: white !important;
    }
    
    .stButton > button p {
        color: white !important;
    }
    
    .stButton button div p {
        color: white !important;
    }
    
    /* Headers - #b3865c color */
    h1, h2, h3, h4, h5, h6 {
        color: #b3865c !important;
    }
    
    /* Product card styling */
    .product-card {
        background-color: #2a2a2a;
        border: 2px solid #404040;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .product-card:hover {
        border-color: #b3865c;
        box-shadow: 0 4px 12px rgba(179, 134, 92, 0.3);
        transform: translateY(-2px);
    }
    
    .product-card.selected {
        border-color: #b3865c;
        background-color: #2a2520;
    }
    
    .product-name {
        font-size: 18px;
        font-weight: 600;
        color: #b3865c;
        margin-top: 10px;
    }
    
    .product-stock {
        font-size: 14px;
        color: #a0a0a0;
        margin-top: 5px;
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===================== UTILITIES =====================
def generate_auth_key():
    return ''.join(random.choice('0123456789') for _ in range(16))

def email_valid(email):
    return "@" in email and "." in email

def password_valid(password):
    if len(password) < 8:
        return False, "Minimum 8 characters required"
    if not any(c.isdigit() for c in password):
        return False, "Must contain a digit"
    if not any(c.isupper() for c in password):
        return False, "Must contain an uppercase letter"
    return True, "Valid password"

# ===================== USER FUNCTIONS =====================
def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["Name", "Email", "Password", "Auth_Key"])
        df.to_excel(USERS_FILE, index=False)
    else:
        df = pd.read_excel(USERS_FILE)
        if "Auth_Key" not in df.columns:
            df["Auth_Key"] = df.apply(lambda _: generate_auth_key(), axis=1)
            df.to_excel(USERS_FILE, index=False)
    return df

def save_users(df):
    df.to_excel(USERS_FILE, index=False)

def user_exists(email, df):
    return email.lower() in df["Email"].str.lower().values

# ===================== INVENTORY =====================
def load_inventory():
    default_stock = {
        "Coke": 60,
        "Diet Coke": 60,
        "Sprite": 60,
        "Red Bull": 60,
        "Monster": 60
    }

    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame([default_stock]).to_excel(INVENTORY_FILE, index=False)

    return pd.read_excel(INVENTORY_FILE)

def save_inventory(df):
    df.to_excel(INVENTORY_FILE, index=False)

def sell_item(product, qty, df):
    if df.loc[0, product] >= qty:
        df.loc[0, product] -= qty
        if df.loc[0, product] <= 0:
            df.loc[0, product] = 60
        return True
    return False

# ===================== ADMIN =====================
def load_admins():
    if not os.path.exists(ADMIN_FILE):
        admins = pd.DataFrame([
            {"Username": "admin", "Password": "admin123"},
            {"Username": "dishanthv06@admin.com", "Password": "admin123"}
        ])
        admins.to_excel(ADMIN_FILE, index=False)
    return pd.read_excel(ADMIN_FILE)

# ===================== ORDERS =====================
def save_order(order):
    if not os.path.exists(ORDERS_FILE):
        orders = pd.DataFrame(columns=["Email", "Order ID", "Payment", "Address", "Date"])
    else:
        orders = pd.read_excel(ORDERS_FILE)

    orders.loc[len(orders)] = [
        order["Email"], order["OrderID"], order["Payment"],
        order["Address"], order["Date"]
    ]
    orders.to_excel(ORDERS_FILE, index=False)

    if not os.path.exists(ORDER_DETAILS_FILE):
        details = pd.DataFrame(columns=["Order ID", "Item", "Quantity", "Total"])
    else:
        details = pd.read_excel(ORDER_DETAILS_FILE)

    details.loc[len(details)] = [
        order["OrderID"], order["Product"], order["Quantity"], order["Total"]
    ]
    details.to_excel(ORDER_DETAILS_FILE, index=False)

    return pd.DataFrame([order])

# ===================== PRODUCT IMAGES =====================
PRODUCT_IMAGES = {
    "Coke": "images/coke.jpg",
    "Diet Coke": "images/diet_coke.jpg",
    "Sprite": "images/sprite.jpg",
    "Red Bull": "images/redbull.jpg",
    "Monster": "images/monster.jpg"
}

# ===================== UI CONFIG =====================
st.set_page_config(
    page_title="DV Store", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ===================== SIDEBAR =====================
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Sign Up", "Sign In", "Forgot Password", "Shop", "Admin Login"]
)

# ===================== HOME =====================
if page == "Home":
    st.title("DV Store")
    
    # Display logo
    if os.path.exists("images/Logo.jpg"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("images/Logo.jpg", width=500)
    
    st.write("### Your one-stop shop for cool drinks.")
    st.write("Browse our selection of refreshing beverages and get them delivered to your doorstep!")

# ===================== SIGN UP =====================
elif page == "Sign Up":
    st.header("User Registration")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        users = load_users()

        if not name or not email or not pwd:
            st.error("All fields required")
        elif not email_valid(email):
            st.error("Invalid email")
        elif pwd != confirm:
            st.error("Passwords do not match")
        elif user_exists(email, users):
            st.error("Email already registered")
        else:
            valid, msg = password_valid(pwd)
            if not valid:
                st.error(msg)
            else:
                auth_key = generate_auth_key()
                users.loc[len(users)] = [name, email, pwd, auth_key]
                save_users(users)
                st.success("Registration successful")
                st.info(f"Authentication Key: {auth_key}")

# ===================== SIGN IN =====================
elif page == "Sign In":
    st.header("Login")

    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        user = users[users["Email"].str.lower() == email.lower()]

        if user.empty:
            st.error("User not found")
        elif user.iloc[0]["Password"] != pwd:
            st.error("Incorrect password")
        else:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Login successful")

# ===================== FORGOT PASSWORD =====================
elif page == "Forgot Password":
    st.header("Reset Password")

    email = st.text_input("Email")
    auth = st.text_input("Auth Key")
    new_pwd = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Reset"):
        users = load_users()
        user = users[users["Email"].str.lower() == email.lower()]

        if user.empty:
            st.error("Email not registered")
        elif user.iloc[0]["Auth_Key"] != auth:
            st.error("Invalid authentication key")
        elif new_pwd != confirm:
            st.error("Passwords mismatch")
        else:
            valid, msg = password_valid(new_pwd)
            if not valid:
                st.error(msg)
            else:
                users.loc[user.index, "Password"] = new_pwd
                save_users(users)
                st.success("Password updated")

# ===================== SHOP =====================
elif page == "Shop":
    if not st.session_state.get("logged_in"):
        st.warning("Login required")
    else:
        st.header("Shop Our Products")
        
        inventory = load_inventory()
        
        # Initialize selected product in session state
        if 'selected_product' not in st.session_state:
            st.session_state.selected_product = None
        
        st.write("### Select a Product")
        
        # Display products in grid
        cols = st.columns(5)
        
        for idx, product in enumerate(inventory.columns):
            with cols[idx]:
                if os.path.exists(PRODUCT_IMAGES[product]):
                    st.image(PRODUCT_IMAGES[product], width=150)
                st.write(f"**{product}**")
                st.write(f"Stock: {int(inventory.loc[0, product])}")
                
                if st.button(f"Select", key=f"btn_{product}"):
                    st.session_state.selected_product = product
        
        st.write("---")
        
        # Order form
        if st.session_state.selected_product:
            selected = st.session_state.selected_product
            st.write(f"### Selected: {selected}")
            
            if os.path.exists(PRODUCT_IMAGES[selected]):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(PRODUCT_IMAGES[selected], width=300)
            
            max_qty = int(inventory.loc[0, selected])
            qty = st.number_input("Quantity", 1, max_qty, 1)
            st.write(f"**Total Price: ₹{qty * 50}**")
            
            address = st.text_area("Delivery Address")
            payment = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])

            if st.button("Place Order"):
                if not address:
                    st.error("Address required")
                elif sell_item(selected, qty, inventory):
                    save_inventory(inventory)

                    order = {
                        "OrderID": random.randint(100000, 999999),
                        "Email": st.session_state.user_email,
                        "Product": selected,
                        "Quantity": qty,
                        "Total": qty * 50,
                        "Payment": payment,
                        "Address": address,
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    save_order(order)
                    st.success("Order placed successfully!")
                    st.balloons()
                    
                    # Display order details
                    st.write("### Order Details")
                    st.write(f"**Order ID:** {order['OrderID']}")
                    st.write(f"**Product:** {order['Product']}")
                    st.write(f"**Quantity:** {order['Quantity']}")
                    st.write(f"**Total:** ₹{order['Total']}")
                    st.write(f"**Payment Method:** {order['Payment']}")
                    st.write(f"**Date:** {order['Date']}")
                    
                    # Reset selection
                    st.session_state.selected_product = None
        else:
            st.info("👆 Please select a product from above")

# ===================== ADMIN =====================
elif page == "Admin Login":
    st.header("Admin Access")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        admins = load_admins()
        if ((admins["Username"] == user) & (admins["Password"] == pwd)).any():
            st.success("Admin Logged In")
            st.subheader("Inventory")
            st.dataframe(load_inventory())
            st.subheader("Orders")
            if os.path.exists(ORDERS_FILE):
                st.dataframe(pd.read_excel(ORDERS_FILE))
        else:
            st.error("Invalid admin credentials")