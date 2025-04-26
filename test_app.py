import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
    layout="wide"
)

st.title("Test Streamlit App")
st.write("This is a simple test app to verify Streamlit functionality")

st.header("Basic Components")
st.subheader("Text Input")
name = st.text_input("Enter your name")
if name:
    st.write(f"Hello, {name}!")

st.subheader("Button")
if st.button("Click me"):
    st.write("Button clicked!")

st.subheader("Slider")
number = st.slider("Select a number", 0, 100, 50)
st.write(f"Selected number: {number}")