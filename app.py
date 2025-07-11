from math import radians, cos, sin, asin, sqrt

# Haversine formula to calculate distance between two ZIPs
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * asin(sqrt(a))

# Load ZIP -> lat/lon map
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")
if zip_map_file:
    zip_df = pd.read_csv(zip_map_file)
    zip_df.columns = zip_df.columns.str.strip().str.title()
    zip_map = zip_df.set_index("Zip")[["Lat", "Lon"]].to_dict("index")

    match_rows = []
    for _, job in jobs_clean.iterrows():
        job_zip = str(job["Zip"]).zfill(5)
        job_cert = job["Normalized Cert"]
        job_latlon = zip_map.get(job_zip)
        if not job_latlon:
            continue
        for _, lead in leads_clean.iterrows():
            lead_zip = str(lead["Zip"]).zfill(5)
            lead_cert = lead["Normalized Cert"]
            lead_latlon = zip_map.get(lead_zip)
            if not lead_latlon:
                continue
            if job_cert != lead_cert:
                continue
            distance = haversine(job_latlon["Lat"], job_latlon["Lon"], lead_latlon["Lat"], lead_latlon["Lon"])
            if distance <= 30:
                match_rows.append({
                    "Job ID": job.get("Job ID", ""),
                    "Client Name": job.get("Client Name", ""),
                    "AE": job["Account Executive"],
                    "Lead Name": f"{lead.get('First Name', '')} {lead.get('Last Name', '')}".strip(),
                    "Recruiter": lead["Recruiter"],
                    "Certification": job_cert,
                    "Job ZIP": job_zip,
                    "Lead ZIP": lead_zip,
                    "Distance (miles)": round(distance, 2)
                })

    matches_df = pd.DataFrame(match_rows)

    st.subheader("✅ Match Results")
    if not matches_df.empty:
        st.dataframe(matches_df)
        st.download_button("Download Matches", matches_df.to_csv(index=False), "Match_Results.csv")
    else:
        st.warning("No valid matches found within 30-mile radius and matching certification.")
