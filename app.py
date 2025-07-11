import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from geopy.distance import geodesic

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")

# --- Upload Section ---
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_lookup_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if not all([jobs_file, leads_file, cert_lookup_file, zip_map_file]):
    st.warning("🚨 Please upload all four required files to proceed.")
    st.stop()

# --- Load CSVs ---
jobs_df = pd.read_csv(jobs_file)
leads_df = pd.read_csv(leads_file)
cert_lookup_df = pd.read_csv(cert_lookup_file)
zip_df = pd.read_csv(zip_map_file)

# --- Normalize column names for certification ---
def normalize_cert_column(df):
    for col in df.columns:
        if col.strip().lower() in ["certification", "cert", "cert type", "cert_type"]:
            df.rename(columns={col: "certification"}, inplace=True)
            return df
    return None

if normalize_cert_column(jobs_df) is None or normalize_cert_column(leads_df) is None:
    st.error("❌ Both Jobs and Leads files must include a 'certification' column (or variation like 'Cert', 'Cert Type').")
    st.stop()

# --- Normalize ZIP columns ---
for df in [jobs_df, leads_df, zip_df]:
    zip_col = next((col for col in df.columns if col.strip().lower() == "zip"), None)
    if zip_col:
        df["Zip"] = df[zip_col].astype(str).str.zfill(5)
    else:
        st.error("❌ All files must include a 'Zip' column.")
        st.stop()

# --- Normalize Cert Lookup ---
cert_lookup_df.columns = [col.strip().lower() for col in cert_lookup_df.columns]
cert_lookup_dict = dict(zip(cert_lookup_df["alias"].str.title(), cert_lookup_df["normalized"].str.title()))
jobs_df["certification"] = jobs_df["certification"].str.title().replace(cert_lookup_dict)
leads_df["certification"] = leads_df["certification"].str.title().replace(cert_lookup_dict)

# --- Map ZIPs to Coordinates ---
zip_coords = zip_df.set_index("Zip")[['Lat', 'Lon']].to_dict("index")

def get_coords(zip_code):
    return zip_coords.get(zip_code, {"Lat": None, "Lon": None})

jobs_df[["JobLat", "JobLon"]] = jobs_df["Zip"].apply(lambda z: pd.Series([get_coords(z)["Lat"], get_coords(z)["Lon"]]))
leads_df[["LeadLat", "LeadLon"]] = leads_df["Zip"].apply(lambda z: pd.Series([get_coords(z)["Lat"], get_coords(z)["Lon"]]))

# --- Filter incomplete ---
jobs_df.dropna(subset=["JobLat", "JobLon"], inplace=True)
leads_df.dropna(subset=["LeadLat", "LeadLon"], inplace=True)

# --- Matching Logic ---
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).miles

matches = []
for _, job in jobs_df.iterrows():
    for _, lead in leads_df.iterrows():
        if job["certification"] == lead["certification"]:
            distance = calculate_distance(job["JobLat"], job["JobLon"], lead["LeadLat"], lead["LeadLon"])
            if distance <= 50:  # updated radius to 50 miles
                matches.append({
                    "Job": job.get("Position", "Unknown"),
                    "Lead": lead.get("First Name", "Unknown") + " " + lead.get("Last Name", "Unknown"),
                    "Distance (mi)": round(distance, 1),
                    "Cert": job["certification"],
                    "Job ZIP": job["Zip"],
                    "Lead ZIP": lead["Zip"]
                })

# --- Output Section ---
if matches:
    st.success(f"✅ {len(matches)} match(es) found within 50 miles.")
    st.dataframe(pd.DataFrame(matches))
else:
    st.warning("⚠️ No matches found within 50 miles.")
