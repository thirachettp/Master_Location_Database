import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time 

st.title("Hello, Streamlit!")
st.write("This is a simple Streamlit app.")
print("App initialized",time.ctime())


upload_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
if upload_file is not None:
    df = pd.read_excel(upload_file)
    st.write("Example Data from the uploaded file:")
    st.dataframe(df.head(5))

    if st.button("Show Plot"):
        plt.figure(figsize=(10, 5))
        plt.plot(df[df.columns[0]], df[df.columns[1]], marker='o')
        plt.title("Sample Plot")
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.grid()
        st.pyplot(plt)
    
    columns = df.columns.tolist()
    selected_column = st.selectbox("Select a column to display", columns)
    unique_values = df[selected_column].unique()
    selected_value = st.selectbox("Select a value to filter", unique_values)

    filtered_df = df[df[selected_column] == selected_value]
    st.write(f"Filtered Data for {selected_value}:")
    st.dataframe(filtered_df)
    
