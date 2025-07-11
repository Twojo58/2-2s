import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")

st.markdown("Upload your Jobs and Leads files below:")

jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_lookup_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if jobs_file and leads_file and cert_lookup_file and zip_map_file:
    # Load and normalize data
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_lookup_file)
    zip_df = pd.read_csv(zip_map_file)

    # Normalize column names
    def normalize_columns(df):
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '').str.replace('_', '')
        return df

    jobs_df = normalize_columns(jobs_df)
    leads_df = normalize_columns(leads_df)
    cert_lookup = normalize_columns(cert_lookup)
    zip_df = normalize_columns(zip_df)

    # Validate required columns exist
    required_job_cols = ["zip", "ordercert"]
    required_lead_cols = ["zip", "certification", "cellphone", "email"]
    required_cert_cols = ["rawcertification", "normalizedcertification"]
    required_zip_cols = ["zip", "lat", "lon"]

    for col in required_job_cols:
        if col not in jobs_df.columns:
            st.error(f"Jobs file must include '{col}' column.")
            st.stop()

    for col in required_lead_cols:
        if col not in leads_df.columns:
            st.error(f"Leads file must include '{col}' column.")
            st.stop()

    for col in required_cert_cols:
        if col not in cert_lookup.columns:
            st.error(f"Cert Lookup must include '{col}' column.")
            st.stop()

    for col in required_zip_cols:
        if col not in zip_df.columns:
            st.error(f"ZIP Map must include '{col}' column.")
            st.stop()

    # Pad zip codes with zeros to ensure 5-digit format
    jobs_df["zip"] = jobs_df["zip"].astype(str).str.zfill(5)
    leads_df["zip"] = leads_df["zip"].astype(str).str.zfill(5)
    zip_df["zip"] = zip_df["zip"].astype(str).str.zfill(5)

    # Map certifications
    cert_lookup_dict = dict(zip(cert_lookup["rawcertification"].str.strip().str.title(), cert_lookup["normalizedcertification"].str.strip().str.title()))

    jobs_df["normalized_cert"] = jobs_df["ordercert"].str.strip().str.title().map(cert_lookup_dict)
    leads_df["normalized_cert"] = leads_df["certification"].str.strip().str.title().map(cert_lookup_dict)

    # Drop leads missing both phone and email
    leads_df = leads_df[leads_df["email"].notna() | leads_df["cellphone"].notna()]

    # TODO: Match logic goes here
    st.success("All files validated and normalized. Ready for matching logic.")

else:
    st.warning("\U0001F4E6 Please upload all four required files to proceed.")
