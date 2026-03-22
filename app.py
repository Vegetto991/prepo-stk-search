import streamlit as st
import pandas as pd
import io

st.title("Master Serial Filter App")

st.write("""
Upload your **WORKING COPY.xlsx** once.  
Then upload **one or more Excel files** containing Serial Number, Room, and Lot.  
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

        # Validate master file columns
        required_master_cols = [
            "Main work center",
            "Model number",
            "Material Description",
            "Material",
            "Serial Number"
        ]

        if not all(col in df_master.columns for col in required_master_cols):
            st.error("Master file is missing required columns.")
            st.stop()

        # Normalize serial number column
        df_master["Serial Number"] = df_master["Serial Number"].astype(str)

        # Build lookup for fast matching
        master_lookup = df_master.groupby("Serial Number")

        # Combined list of serial entries
        combined_entries = []

        for f in serial_files:
            df = pd.read_excel(f)

            # Validate required columns
            required_cols = ["Serial Number", "Room", "Lot"]
            if not all(col in df.columns for col in required_cols):
                st.error(f"File {f.name} is missing required columns.")
                st.stop()

            # Append entries
            for _, row in df.iterrows():
                combined_entries.append({
                    "Serial Number": str(row["Serial Number"]),
                    "Room": row["Room"],
                    "Lot": row["Lot"]
                })

        # Build output rows
        output_rows = []
        missing_serials = []
        found_count = 0

        for entry in combined_entries:
            sn = entry["Serial Number"]
            room = entry["Room"]
            lot = entry["Lot"]

            if sn in master_lookup.groups:
                matches = master_lookup.get_group(sn)
                found_count += 1

                # First match gets Room + Lot
                first = matches.iloc[0].copy()
                first["Room"] = room
                first["Lot"] = lot
                output_rows.append(first.to_dict())

                # Add blank rows for duplicates
                for _ in range(len(matches) - 1):
                    blank = {col: None for col in df_master.columns}
                    blank["Serial Number"] = sn
                    blank["Room"] = None
                    blank["Lot"] = None
                    output_rows.append(blank)

            else:
                # Serial not found → blank row but keep Room + Lot
                missing_serials.append(sn)

                blank = {
                    "Main work center": None,
                    "Model number": None,
                    "Material Description": None,
                    "Material": None,
                    "Serial Number": sn,
                    "Room": room,
                    "Lot": lot
                }
                output_rows.append(blank)

        # Build final DataFrame
        output_df = pd.DataFrame(output_rows)[[
            "Main work center",
            "Model number",
            "Material Description",
            "Material",
            "Serial Number",
            "Room",
            "Lot"
        ]]

        # Format Material column as 9-digit text
        output_df["Material"] = (
            output_df["Material"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(9)
        )

        # Summary statistics
        total_serials = len(combined_entries)
        missing_count = len(missing_serials)

        st.subheader("Summary")
        st.write(f"**Total serial numbers processed:** {total_serials}")
        st.write(f"**Found in master file:** {found_count}")
        st.write(f"**Not found:** {missing_count}")

        if missing_count > 0:
            st.write("### Missing Serial Numbers:")
            st.write(", ".join(missing_serials))

        # Export to Excel in memory
        buffer = io.BytesIO()
        output_df.to_excel(buffer, index=False)
        buffer.seek(0)

        st.success("File generated successfully!")

        st.download_button(
            label="Download Output File",
            data=buffer,
            file_name="filtered_serials_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
