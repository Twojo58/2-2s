import streamlit as st
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of earth in miles
    return c * r

st.title("2:2 Job Match Validator")
st.markdown("Upload your Jobs and Leads files below:")

jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_lookup_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if jobs_file and leads_file and cert_lookup_file and zip_map_file:
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_lookup_df = pd.read_csv(cert_lookup_file)
    zip_df = pd.read_csv(zip_map_file)

    # Normalize column names to lowercase and strip whitespace
    zip_df.columns = [col.strip().lower() for col in zip_df.columns]
    if not {"zip", "lat", "lon"}.issubset(zip_df.columns):
        st.error("❌ ZIP Map must include 'zip', 'lat', and 'lon' columns.")
        st.stop()

    zip_df["zip"] = zip_df["zip"].astype(str).str.zfill(5)
    zip_coords = zip_df.set_index("zip")[["lat", "lon"]]

    jobs_df.columns = [col.strip().lower() for col in jobs_df.columns]
    leads_df.columns = [col.strip().lower() for col in leads_df.columns]
    cert_lookup_df.columns = [col.strip().lower() for col in cert_lookup_df.columns]

    if "zip" not in jobs_df.columns:
        st.error("❌ Jobs file must include a 'zip' column.")
        st.stop()
    if "zip" not in leads_df.columns:
        st.error("❌ Leads file must include a 'zip' column.")
        st.stop()
    if "certification" not in jobs_df.columns or "certification" not in leads_df.columns:
        st.error("❌ Both Jobs and Leads files must include 'certification' column.")
        st.stop()

    # Normalize zip and cert columns
    jobs_df["zip"] = jobs_df["zip"].astype(str).str.zfill(5)
    leads_df["zip"] = leads_df["zip"].astype(str).str.zfill(5)
    jobs_df["certification"] = jobs_df["certification"].str.title().str.strip()
    leads_df["certification"] = leads_df["certification"].str.title().str.strip()

    # Merge cert normalization
    cert_lookup_df = cert_lookup_df.dropna()
    cert_lookup_df = cert_lookup_df.drop_duplicates(subset="alias")
    cert_map = dict(zip(cert_lookup_df["alias"].str.title().str.strip(), cert_lookup_df["normalized"].str.title().str.strip()))
    jobs_df["normalized_cert"] = jobs_df["certification"].map(cert_map).fillna(jobs_df["certification"])
    leads_df["normalized_cert"] = leads_df["certification"].map(cert_map).fillna(leads_df["certification"])

    st.success("All files validated and normalized. Ready for matching logic.")

    if st.button("Run Matching Logic"):
        match_radius = 50
        matches = []

        for i, job in jobs_df.iterrows():
            job_cert = job["normalized_cert"]
            job_zip = job["zip"]

            if job_zip not in zip_coords.index:
                continue
            job_lat, job_lon = zip_coords.loc[job_zip]

            for j, lead in leads_df.iterrows():
                lead_cert = lead["normalized_cert"]
                lead_zip = lead["zip"]

                if lead_zip not in zip_coords.index:
                    continue
                lead_lat, lead_lon = zip_coords.loc[lead_zip]
                distance = haversine(job_lat, job_lon, lead_lat, lead_lon)

                if distance <= match_radius and lead_cert == job_cert:
                    matches.append({
                        "Job": job.get("position", i),
                        "Lead": lead.get("first name", j),
                        "Cert": job_cert,
                        "Distance (miles)": round(distance, 1)
                    })

        if matches:
            matches_df = pd.DataFrame(matches)
            st.success(f"✅ Found {len(matches)} matches within {match_radius} miles.")
            st.dataframe(matches_df)
        else:
            st.warning(f"No matches found within {match_radius} miles.")
