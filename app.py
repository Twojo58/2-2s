import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")
st.write("Upload your Jobs and Leads files below:")

# ---- File Uploads ----
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if all([jobs_file, leads_file, cert_file, zip_map_file]):
    # ---- Load Files ----
    jobs_df = pd.read_csv(jobs_file)
    leads_df = pd.read_csv(leads_file)
    cert_df = pd.read_csv(cert_file)
    zip_df = pd.read_csv(zip_map_file)

    # ---- Normalize ZIP codes ----
    zip_df["Zip"] = zip_df["Zip"].astype(str).str.zfill(5)
    jobs_df["zip"] = jobs_df["zip"].astype(str).str.zfill(5)
    leads_df["zip"] = leads_df["zip"].astype(str).str.zfill(5)

    # ---- Cert Normalization ----
    cert_lookup = dict(zip(cert_df["Raw Certification"].str.strip().str.title(), cert_df["Normalized Certification"].str.strip().str.title()))
    jobs_df["Normalized Cert"] = jobs_df["Order Cert"].str.strip().str.title().map(cert_lookup)
    leads_df["Normalized Cert"] = leads_df["Certification"].str.strip().str.title().map(cert_lookup)

    # ---- Merge ZIP Coordinates ----
    zip_coords = zip_df.set_index("Zip")[["Lat", "Lon"]]
    jobs_df = jobs_df.merge(zip_coords, how="left", left_on="zip", right_index=True).rename(columns={"Lat": "Job_Lat", "Lon": "Job_Lon"})
    leads_df = leads_df.merge(zip_coords, how="left", left_on="zip", right_index=True).rename(columns={"Lat": "Lead_Lat", "Lon": "Lead_Lon"})

    # ---- Drop Incomplete Rows ----
    jobs_df.dropna(subset=["Job_Lat", "Job_Lon", "Normalized Cert"], inplace=True)
    leads_df.dropna(subset=["Lead_Lat", "Lead_Lon", "Normalized Cert"], inplace=True)

    st.success("All files validated and normalized. Ready for matching logic.")

    # ---- Run Match Logic ----
    if st.button("Run Matching Logic"):
        match_results = []

        for _, job_row in jobs_df.iterrows():
            for _, lead_row in leads_df.iterrows():
                if job_row["Normalized Cert"] == lead_row["Normalized Cert"]:
                    job_coords = (job_row["Job_Lat"], job_row["Job_Lon"])
                    lead_coords = (lead_row["Lead_Lat"], lead_row["Lead_Lon"])
                    dist = geodesic(job_coords, lead_coords).miles
                    if dist <= 50:
                        match_results.append({
                            "Job Order ID": job_row["Order ID"],
                            "Job Cert": job_row["Normalized Cert"],
                            "Job Zip": job_row["zip"],
                            "Lead Name": f"{lead_row['First Name']} {lead_row['Last Name']}",
                            "Lead Zip": lead_row["zip"],
                            "Distance (mi)": round(dist, 1)
                        })

        if match_results:
            match_df = pd.DataFrame(match_results)
            st.success(f"✅ {len(match_df)} matches found within 50 miles.")
            st.dataframe(match_df)
        else:
            st.warning("No matches found within 50 miles.")

else:
    st.info("📂 Please upload all four required files to proceed.")
