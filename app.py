import streamlit as st
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import datetime as dt

# Constants
MATCH_RADIUS = 50  # Radius in miles for zip-to-zip matching
EXCLUDED_TEMP_STATUSES = ['Active', 'Pending', 'Dormant', 'Do Not Use']
BEHAVIOR_ROLES = ['Para', 'Paraprofessional', 'TA', 'Teacher Assistant', 'RBT', 'BCBA']
TRIGGER_DAYS = [1, 2, 4, 5, 10, 20, 25, 30]
AFTER_HOUR_CUTOFF = dt.time(15, 0)  # 3:00 PM

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of Earth in miles
    return c * r

# Load ZIP Map
def load_zip_map(zip_file):
    zip_df = pd.read_csv(zip_file)
    zip_df["Zip"] = zip_df["Zip"].astype(str).str.zfill(5)
    return zip_df.set_index("Zip")

# Normalize certs
def normalize_cert(cert):
    return cert.strip().title() if pd.notna(cert) else ""

# Clean jobs data
def clean_jobs(df):
    df.columns = df.columns.str.strip()
    if "zip" in df.columns:
        df.rename(columns={"zip": "Zip"}, inplace=True)
    df["Zip"] = df["Zip"].astype(str).str.zfill(5)
    df["Order Cert"] = df["Order Cert"].apply(normalize_cert)
    return df

# Clean leads data
def clean_leads(df):
    df.columns = df.columns.str.strip()
    if "zip" in df.columns:
        df.rename(columns={"zip": "Zip"}, inplace=True)
    df = df[df['Temp Status'].isin(EXCLUDED_TEMP_STATUSES) == False]
    df = df[~df['Certification'].isin(BEHAVIOR_ROLES)]
    df = df[df['Email'].notna() | df['Cell Phone'].notna()]
    df["Zip"] = df["Zip"].astype(str).str.zfill(5)
    df["Certification"] = df["Certification"].apply(normalize_cert)
    return df

# Match logic
def find_matches(jobs_df, leads_df, zip_map):
    matches = []
    for _, job in jobs_df.iterrows():
        job_zip = job['Zip']
        job_cert = job['Order Cert']

        if job_zip not in zip_map.index:
            continue

        job_lat, job_lon = zip_map.loc[job_zip, ['Lat', 'Lon']]

        for _, lead in leads_df.iterrows():
            lead_zip = lead['Zip']
            lead_cert = lead['Certification']

            if lead_zip not in zip_map.index:
                continue

            if lead_cert != job_cert:
                continue

            lead_lat, lead_lon = zip_map.loc[lead_zip, ['Lat', 'Lon']]
            distance = haversine(job_lat, job_lon, lead_lat, lead_lon)

            if distance <= MATCH_RADIUS:
                matches.append({
                    'Lead Name': lead['First Name'] + ' ' + lead['Last Name'],
                    'Lead Zip': lead_zip,
                    'Lead Cert': lead_cert,
                    'Job Zip': job_zip,
                    'Job Cert': job_cert,
                    'Distance (mi)': round(distance, 1),
                    'Order ID': job['Order ID'],
                    'Client Name': job['Client Name'],
                })
    return pd.DataFrame(matches)

# Streamlit UI
st.title("2:2 Job Match Validator")

jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_lookup_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if all([jobs_file, leads_file, cert_lookup_file, zip_map_file]):
    try:
        jobs_df = clean_jobs(pd.read_csv(jobs_file))
        leads_df = clean_leads(pd.read_csv(leads_file))
        zip_map = load_zip_map(zip_map_file)

        st.success("All files validated and normalized. Ready for matching logic.")

        if st.button("Run Matching Logic"):
            match_df = find_matches(jobs_df, leads_df, zip_map)
            if match_df.empty:
                st.warning("No matches found within 50 miles.")
            else:
                st.success(f"Found {len(match_df)} match(es) within 50 miles.")
                st.dataframe(match_df)
                csv = match_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Matches CSV", csv, "matched_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Error during file processing or match logic: {e}")
else:
    st.warning("\ud83d\udea8 Please upload all four required files to proceed.")
