import streamlit as st
import pandas as pd

st.set_page_config(page_title="2:2 Job Match Tool", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

# File uploaders
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")

if jobs_file and leads_file and cert_file:
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_file)

    st.success("All files loaded!")

    # Preview
    st.write("Jobs Preview:", jobs_df.head())
    st.write("Leads Preview:", leads_df.head())
    st.write("Cert Lookup Preview:", cert_lookup.head())

    # --- Normalize certification lookup dict ---
    raw_cert_col = [col for col in cert_lookup.columns if "raw" in col.lower()][0]
    norm_cert_col = [col for col in cert_lookup.columns if "normalized" in col.lower()][0]
    cert_lookup_dict = dict(
        zip(
            cert_lookup[raw_cert_col].astype(str).str.strip().str.title(),
            cert_lookup[norm_cert_col].astype(str).str.strip().str.title(),
        )
    )

    # --- Clean leads ---
    leads_df.columns = leads_df.columns.str.strip()

    if 'Temp Status' in leads_df.columns:
        leads_df = leads_df[~leads_df['Temp Status'].str.strip().isin(["Active", "Pending", "Dormant", "Do Not Use"])]

    email_col = [col for col in leads_df.columns if 'email' in col.lower()]
    phone_col = [col for col in leads_df.columns if 'phone' in col.lower() or 'cell' in col.lower()]

    if email_col and phone_col:
        leads_df = leads_df[
            leads_df[email_col[0]].notna() | leads_df[phone_col[0]].notna()
        ]
    else:
        st.error("Missing required 'Email' or 'Phone' column in Leads file.")
        st.stop()

    # Placeholder — matching logic will run here next
    st.info("✅ Files validated and cleaned. Matching logic will run next...")
