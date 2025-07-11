import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="2:2 Job Match Tool", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

# Uploads
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if jobs_file and leads_file and cert_file and zip_map_file:
    # Read all files
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_file)
    zip_df = pd.read_csv(zip_map_file)

    # Cert Lookup column safety
    cert_lookup.columns = [col.strip().title() for col in cert_lookup.columns]
    if "Raw Certification" in cert_lookup.columns and "Normalized Certification" in cert_lookup.columns:
        cert_lookup_dict = dict(zip(
            cert_lookup["Raw Certification"].str.strip().str.title(),
            cert_lookup["Normalized Certification"].str.strip().str.title()
        ))
    else:
        st.error("❌ Cert Lookup CSV must include 'Raw Certification' and 'Normalized Certification' columns.")
        st.stop()

    # ZIP map check
    zip_df.columns = [col.strip().lower() for col in zip_df.columns]
    if "zip" in zip_df.columns:
        zip_df["Zip"] = zip_df["zip"].astype(str).str.zfill(5)
    else:
        st.error("❌ ZIP map must include a 'zip' column.")
        st.stop()

    # Cert normalization for leads
    if "Certification" in leads_df.columns:
        leads_df["Certification"] = leads_df["Certification"].astype(str).str.strip().str.title()
        leads_df["Normalized Cert"] = leads_df["Certification"].map(cert_lookup_dict).fillna(leads_df["Certification"])
    else:
        st.error("❌ Leads file must include 'Certification' column.")
        st.stop()

    # Cert normalization for jobs
    if "Order Cert" in jobs_df.columns:
        jobs_df["Order Cert"] = jobs_df["Order Cert"].astype(str).str.strip().str.title()
        jobs_df["Normalized Cert"] = jobs_df["Order Cert"].map(cert_lookup_dict).fillna(jobs_df["Order Cert"])
    else:
        st.error("❌ Jobs file must include 'Order Cert' column.")
        st.stop()

    # Zip cleanup in jobs and leads
    for df, label in [(leads_df, "Leads"), (jobs_df, "Jobs")]:
        if "Zip" in df.columns:
            df["Zip"] = df["Zip"].astype(str).str.zfill(5)
        else:
            st.error(f"❌ {label} file must include 'Zip' column.")
            st.stop()

    # Leads must have at least one contact method
    if "Email" in leads_df.columns and "Cell Phone" in leads_df.columns:
        leads_df = leads_df[leads_df["Email"].notna() | leads_df["Cell Phone"].notna()]
    else:
        st.error("❌ Leads file must include both 'Email' and 'Cell Phone' columns.")
        st.stop()

    # Preview tables
    st.success("✅ All files loaded successfully.")
    st.write("Jobs Preview:", jobs_df.head())
    st.write("Leads Preview:", leads_df.head())
    st.write("Cert Lookup Preview:", cert_lookup.head())
    st.write("ZIP Map Preview:", zip_df.head())

    st.info("🚧 Next: Add match logic for cert + zip radius matching...")

else:
    st.warning("📥 Please upload all four required files to proceed.")
