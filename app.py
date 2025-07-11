import streamlit as st
import pandas as pd

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

# Uploaders
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")

if jobs_file and leads_file and cert_file:
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup = pd.read_csv(cert_file)

    # Standardize cert lookup column names
    cert_lookup.columns = [col.strip().title() for col in cert_lookup.columns]

    # Normalize certs using lookup
    cert_lookup_dict = dict(zip(
        cert_lookup['Raw Certification'].str.strip().str.title(),
        cert_lookup['Normalized Certification'].str.strip().str.title()
    ))

    # Clean and normalize
    for df, col in [(jobs_df, 'Order Cert'), (leads_df, 'Certification')]:
        df[col] = df[col].astype(str).str.strip().str.title()
        df[col] = df[col].replace(cert_lookup_dict)

    # Convert ZIPs to 5-digit strings
    jobs_df['zip'] = jobs_df['zip'].astype(str).str.zfill(5).str[:5]
    leads_df['Zip'] = leads_df['Zip'].astype(str).str.zfill(5).str[:5]

    # Filter out statuses
    invalid_statuses = ["Active", "Pending", "Dormant", "Do Not Use"]
    leads_df = leads_df[~leads_df["Temp Status"].isin(invalid_statuses)]

    # Filter out behavior roles
    behavior_roles = ["Para", "Paraprofessional", "TA", "Teacher Assistant", "RBT", "BCBA"]
    leads_df = leads_df[~leads_df["Certification"].isin(behavior_roles)]

    # Remove leads missing both email and phone
    leads_df = leads_df[leads_df['Email'].notna() | leads_df['Cell Phone'].notna()]

    # Match logic
    matches = []
    for _, job in jobs_df.iterrows():
        job_cert = job["Order Cert"]
        job_zip = job["zip"]
        for _, lead in leads_df.iterrows():
            lead_cert = lead["Certification"]
            lead_zip = lead["Zip"]
            if job_cert == lead_cert and job_zip == lead_zip:
                matches.append({
                    "Job Order ID": job["Order ID"],
                    "Client": job["Client Name"],
                    "State": job["Client State"],
                    "Lead Name": f"{lead['First Name']} {lead['Last Name']}",
                    "Lead Cert": lead_cert,
                    "Phone": lead["Cell Phone"],
                    "Email": lead["Email"],
                    "ZIP": lead_zip
                })

    matches_df = pd.DataFrame(matches)

    st.success("All files loaded!")
    st.write("Jobs Preview:", jobs_df.head())
    st.write("Leads Preview:", leads_df.head())
    st.write("Cert Lookup Preview:", cert_lookup.head())

    if not matches_df.empty:
        st.subheader("🎯 Matches Found")
        st.dataframe(matches_df)
        csv = matches_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Matches CSV", csv, "matches.csv", "text/csv")
    else:
        st.warning("No matches found.")
