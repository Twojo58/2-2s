import streamlit as st
import pandas as pd

st.set_page_config(page_title="2:2 Job Match Tool", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

# Upload section
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")

if jobs_file and leads_file and cert_file:
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_file)

    # Normalize Cert Lookup Columns (future-proof)
    raw_cert_col = 'Raw Certification' if 'Raw Certification' in cert_lookup.columns else 'Raw Cert'
    norm_cert_col = 'Normalized Certification' if 'Normalized Certification' in cert_lookup.columns else 'Normalized Cert'

    cert_lookup_dict = dict(
        zip(
            cert_lookup[raw_cert_col].astype(str).str.strip().str.title(),
            cert_lookup[norm_cert_col].astype(str).str.strip().str.title()
        )
    )

    st.success("All files loaded!")
    st.write("Jobs Preview:", jobs_df.head())
    st.write("Leads Preview:", leads_df.head())
    st.write("Cert Lookup Preview:", cert_lookup.head())

    st.info("Matching logic will run here...")
