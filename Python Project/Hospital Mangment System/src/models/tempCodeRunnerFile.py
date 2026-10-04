import streamlit as st

st.title("🎮 My First Streamlit App")

st.write("Welcome to my application!")

st.header("User Information")

name = st.text_input("Enter your name:")

age = st.number_input("Enter your age:", min_value=1, max_value=100)

if st.button("Click Me"):
    st.success(f"Hello {name}! You are {age} years old.")