import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="2:2 Job Match Tool", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

# Upload files
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if jobs_file and leads_file and cert_file and zip_map_file:
    # Load files
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_file)
    zip_df = pd.read_csv(zip_map_file)

    # Normalize cert lookup headers
    cert_lookup.columns = [col.strip().title() for col in cert_lookup.columns]
    if "Raw Certification" in cert_lookup.columns and "Normalized Certification" in cert_lookup.columns:
        cert_lookup_dict = dict(
            zip(
                cert_lookup["Raw Certification"].str.strip().str.title(),
                cert_lookup["Normalized Certification"].str.strip().str.title()
