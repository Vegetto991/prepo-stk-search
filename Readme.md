# Master Serial Filter App

This Streamlit app filters a master WORKING COPY.xlsx file using one or more uploaded
serial list files that contain:

- Serial Number  
- Room  
- Lot  

The app:

- Preserves the order of uploaded serial lists  
- Merges multiple serial list files  
- Inserts blank rows for duplicate serial numbers  
- Formats Material as a 9-digit text field  
- Produces a clean Excel output  

## How to Deploy on Streamlit Cloud

1. Create a GitHub repository and upload:
   - app.py
   - requirements.txt
   - README.md

2. Go to https://share.streamlit.io

3. Click **New App**

4. Select your repository

5. Choose:
   - Branch: main
   - File: app.py

6. Click **Deploy**

Your hosted link will be ready in seconds.
