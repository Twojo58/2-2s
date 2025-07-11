import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")

st.markdown("### Upload your Jobs and Leads files below:")

# File uploads
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_lookup_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

# Exit early if not all files uploaded
if not all([jobs_file, leads_file, cert_lookup_file, zip_map_file]):
    st.warning("📥 Please upload all four required files to proceed.")
    st.stop()

# ------------------------------
# Load and Normalize Cert Lookup
# ------------------------------
cert_lookup = pd.read_csv(cert_lookup_file)
cert_lookup.columns = cert_lookup.columns.str.strip().str.title()
if 'Raw Certification' not in cert_lookup.columns or 'Normalized Certification' not in cert_lookup.columns:
    st.error("❌ Cert lookup file must contain 'Raw Certification' and 'Normalized Certification' columns.")
    st.stop()

cert_lookup_dict = dict(
    zip(cert_lookup['Raw Certification'].str.strip().str.title(), cert_lookup['Normalized Certification'].str.strip().str.title())
)

# ------------------------------
# Load and Normalize ZIP Map
# ------------------------------
zip_df = pd.read_csv(zip_map_file)
zip_df.columns = zip_df.columns.str.strip().str.title()
if 'Zip' not in zip_df.columns or 'Lat' not in zip_df.columns or 'Lon' not in zip_df.columns:
    st.error("❌ ZIP map file must contain 'Zip', 'Lat', and 'Lon' columns.")
    st.stop()

zip_df['Zip'] = zip_df['Zip'].astype(str).str.zfill(5)

# ------------------------------
# Load and Normalize Jobs
# ------------------------------
jobs_df = pd.read_csv(jobs_file)
jobs_df.columns = jobs_df.columns.str.strip().str.title()
if 'Zip' not in jobs_df.columns or 'Order Cert' not in jobs_df.columns:
    st.error("❌ Jobs file must include 'Zip' and 'Order Cert' columns.")
    st.stop()

jobs_df['Zip'] = jobs_df['Zip'].astype(str).str.zfill(5)
jobs_df['Order Cert'] = jobs_df['Order Cert'].astype(str).str.strip().str.title()
jobs_df['Normalized Cert'] = jobs_df['Order Cert'].map(cert_lookup_dict).fillna(jobs_df['Order Cert'])

# ------------------------------
# Load and Normalize Leads
# ------------------------------
leads_df = pd.read_csv(leads_file)
leads_df.columns = leads_df.columns.str.strip().str.title()
if 'Zip' not in leads_df.columns or 'Certification' not in leads_df.columns:
    st.error("❌ Leads file must include 'Zip' and 'Certification' columns.")
    st.stop()

leads_df['Zip'] = leads_df['Zip'].astype(str).str.zfill(5)
leads_df['Certification'] = leads_df['Certification'].astype(str).str.strip().str.title()
leads_df['Normalized Cert'] = leads_df['Certification'].map(cert_lookup_dict).fillna(leads_df['Certification'])

# Drop leads with no phone and no email
if 'Cell Phone' in leads_df.columns and 'Email' in leads_df.columns:
    leads_df = leads_df[leads_df['Cell Phone'].notna() | leads_df['Email'].notna()]

# ------------------------------
# Behavior Cert Exclusion
# ------------------------------
behavior_roles = ["Para", "Paraprofessional", "Ta", "Teacher Assistant", "Rbt", "Bcba"]
leads_df = leads_df[~leads_df['Normalized Cert'].isin(behavior_roles)]

# ------------------------------
# Confirmation Message
# ------------------------------
st.success("✅ All files validated and normalized. Ready for matching logic.")
