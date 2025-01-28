import streamlit as st
import pandas as pd
from io import BytesIO

# Function to generate RPS based on Age
def calculate_rps(age):
    if age < 30:
        return 50
    elif 30 <= age <= 45:
        return 30
    elif 45 < age <= 60:
        return 20
    else:
        return 10

# Function to generate anonymized token
def generate_token(name, rps, var):
    # Anonymize initials
    initials = ''.join([char for char in name if char.isalpha()][:5]).upper()
    if len(initials) < 5:
        initials = initials.ljust(5, 'X')  # Pad with 'X' if initials are less than 5
    return f"{initials}-{rps}-{var}"

# Function to convert dataframe to Excel file in-memory
@st.cache_data
def convert_df_to_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Tokens')
    processed_data = output.getvalue()  # Retrieve the in-memory Excel data
    return processed_data

# Streamlit App
st.title("Tokenized Portfolio Risk Management System (PredictRAM)")

st.header("Upload Investor Data")
uploaded_file = st.file_uploader("Upload an Excel file with 'Full Name', 'Age', 'Current Portfolio', 'Portfolio VaR' columns.", type=["xlsx"])

if uploaded_file:
    # Read Excel file
    df = pd.read_excel(uploaded_file)
    
    # Validate required columns
    required_columns = ['Full Name', 'Age', 'Current Portfolio', 'Portfolio VaR']
    if all(col in df.columns for col in required_columns):
        st.success("File uploaded and validated successfully!")
        
        # Calculate RPS and Tokens
        df['RPS'] = df['Age'].apply(calculate_rps)
        df['Token'] = df.apply(lambda row: generate_token(row['Full Name'], row['RPS'], row['Portfolio VaR']), axis=1)
        
        # Display updated data
        st.subheader("Generated Tokens")
        st.dataframe(df[['Full Name', 'Age', 'RPS', 'Portfolio VaR', 'Token']])
        
        # Downloadable Excel
        st.download_button(
            label="Download Results",
            data=convert_df_to_excel(df),
            file_name="Tokenized_Portfolio_Risk_Management.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.error(f"Uploaded file is missing required columns: {', '.join(required_columns)}")
else:
    st.info("Please upload an Excel file to proceed.")
