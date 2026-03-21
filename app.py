import streamlit as st
import pandas as pd

st.title("Master Serial Filter App")

st.write("""
Upload your **WORKING COPY.xlsx** once.  
Then upload **one or more Excel files** containing serial numbers.  
The app will merge all serial lists, filter the master file, and generate a clean output.
""")

# Upload master file
master_file = st.file_uploader("Upload WORKING COPY.xlsx (Master File)", type=["xlsx"])

# Upload multiple serial list files
serial_files = st.file_uploader(
    "Upload one or more Excel files containing serial numbers",
    type=["xlsx"],
    accept_multiple_files=True
)

if master_file and serial_files:
    if st.button("Generate Output File"):
        # Load master dataset
        df_master = pd.read_excel(master_file)

        # Combine all serial numbers from all uploaded files
        combined_serials = []

        for f in serial_files:
            df = pd.read_excel(f)
            if "Serial Number" in df.columns:
                serials = df["Serial Number"].dropna().astype(str).tolist()
                combined_serials.extend(serials)

        # Prepare output rows
        output_rows = []

        for sn in combined_serials:
            matches = df_master[df_master["Serial Number"].astype(str) == sn]

            if len(matches) > 0:
                # Add the first match
                output_rows.append(matches.iloc[0])

                # Add blank rows for duplicates
                for _ in range(len(matches) - 1):
                    output_rows.append(pd.Series())
            else:
                # Serial not found → blank row
                output_rows.append(pd.Series())

        # Build final DataFrame
        output_df = pd.DataFrame(output_rows)[[
            "Main work center",
            "Model number",
            "Material Description",
            "Material",
            "Serial Number"
        ]]

        # Format Material column as 9-digit text
        output_df["Material"] = (
            output_df["Material"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(9)
        )

        # Export to Excel
        output_filename = "filtered_serials_output.xlsx"
        output_df.to_excel(output_filename, index=False)

        st.success("File generated successfully!")

        with open(output_filename, "rb") as f:
            st.download_button(
                label="Download Output File",
                data=f,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
