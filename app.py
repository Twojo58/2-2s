import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")

if jobs_file and leads_file and cert_file:
    jobs_df = pd.read_csv(jobs_file, dtype=str)
    leads_df = pd.read_csv(leads_file, dtype=str)
    cert_lookup = pd.read_csv(cert_file, dtype=str)

    # Clean column names
    jobs_df.columns = jobs_df.columns.str.strip()
    leads_df.columns = leads_df.columns.str.strip()

    # Cert normalization
    cert_lookup_dict = dict(zip(cert_lookup['Raw Cert'].str.strip().str.title(), cert_lookup['Normalized Cert'].str.strip().str.title()))
    leads_df['Certification'] = leads_df['Certification'].str.strip().str.title().map(cert_lookup_dict).fillna(leads_df['Certification'].str.strip().str.title())
    jobs_df['Certification'] = jobs_df['Certification'].str.strip().str.title().map(cert_lookup_dict).fillna(jobs_df['Certification'].str.strip().str.title())

    # Remove invalid leads (no phone or email or wrong status)
    leads_df['Cell Phone'] = leads_df['Cell Phone'].astype(str)
    leads_df['Email'] = leads_df['Email'].astype(str)
    leads_df = leads_df[leads_df['Temp Status'].str.strip().str.title().isin(['Active', 'Pending', 'Dormant', 'Do Not Use']) == False]
    error_leads = leads_df[(leads_df['Cell Phone'].isna() | leads_df['Cell Phone'].eq('nan')) & (leads_df['Email'].isna() | leads_df['Email'].eq('nan'))]
    leads_cleaned = leads_df[~leads_df.index.isin(error_leads.index)]

    # Flag ZIP errors
    jobs_df['Zip'] = jobs_df['Zip'].astype(str).str.zfill(5)
    leads_cleaned['Zip'] = leads_cleaned['Zip'].astype(str).str.zfill(5)
    jobs_errors = jobs_df[jobs_df['Zip'].str.len() != 5]
    leads_errors = leads_cleaned[leads_cleaned['Zip'].str.len() != 5]

    jobs_cleaned = jobs_df[~jobs_df.index.isin(jobs_errors.index)]
    leads_cleaned = leads_cleaned[~leads_cleaned.index.isin(leads_errors.index)]

    # Summary
    st.success("✅ All files successfully loaded and validated.")
    st.write("### Jobs - To Fix")
    st.dataframe(jobs_errors)

    st.write("### Leads - To Fix")
    st.dataframe(leads_errors)

    st.write("### Error Leads (Missing Contact)")
    st.dataframe(error_leads)

    st.write("### Jobs Cleaned")
    st.dataframe(jobs_cleaned.head())

    st.write("### Leads Cleaned")
    st.dataframe(leads_cleaned.head())

    st.write("### Cert Lookup Preview")
    st.dataframe(cert_lookup.head())

    st.info("🔄 Matching logic will run here next...")

else:
    st.warning("Please upload all three files (Jobs, Leads, Cert Lookup) to continue.")
