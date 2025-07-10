import streamlit as st
import pandas as pd

st.set_page_config(page_title="2:2 Job Match Tool", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")

def filter_valid_leads(leads_df):
    excluded_statuses = {"Active", "Pending", "Dormant", "Do Not Use"}
    error_rows = []

    def is_valid(row):
        status = str(row.get("Temp Status", "")).strip()
        has_contact = bool(str(row.get("Cell Phone", "")).strip()) or bool(str(row.get("Email", "")).strip())
        if status in excluded_statuses or not has_contact:
            error_rows.append(row)
            return False
        return True

    filtered = leads_df[leads_df.apply(is_valid, axis=1)]
    errors = pd.DataFrame(error_rows)
    return filtered, errors

if jobs_file and leads_file and cert_file:
    jobs_df = pd.read_csv(jobs_file)
    leads_df_raw = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_file)

    leads_df, error_leads = filter_valid_leads(leads_df_raw)

    st.success("✅ All files loaded successfully!")
    st.write("### Jobs Preview", jobs_df.head())
    st.write("### Leads Preview", leads_df.head())
    st.write("### Cert Lookup Preview", cert_lookup.head())

    if not error_leads.empty:
        st.warning("⚠️ Some leads were skipped due to missing email/phone or invalid status.")
        st.write("### Error Leads", error_leads)

    st.info("🔧 Matching logic will run here... (placeholder)")

else:
    st.info("👆 Please upload all 3 CSVs to begin.")
