import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

st.set_page_config(page_title="2:2 Job Match Validator", layout="wide")
st.title("2:2 Job Match Validator")

# --------------------- Haversine Function ---------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 3959  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# --------------------- File Uploaders ---------------------
jobs_file = st.file_uploader("Upload Jobs CSV", type="csv")
leads_file = st.file_uploader("Upload Leads CSV", type="csv")
cert_file = st.file_uploader("Upload Cert Lookup CSV", type="csv")
zip_map_file = st.file_uploader("Upload ZIP Map CSV (with Zip, Lat, Lon)", type="csv")

if jobs_file and leads_file and cert_file and zip_map_file:
    try:
        jobs_df = pd.read_csv(jobs_file)
        leads_df = pd.read_csv(leads_file)
        cert_lookup_df = pd.read_csv(cert_file)
        zip_df = pd.read_csv(zip_map_file)

        # Normalize column headers
        jobs_df.columns = [col.strip().title() for col in jobs_df.columns]
        leads_df.columns = [col.strip().title() for col in leads_df.columns]
        cert_lookup_df.columns = [col.strip().title() for col in cert_lookup_df.columns]
        zip_df.columns = [col.strip().title() for col in zip_df.columns]

        # Cert Normalization
        cert_lookup_df['Raw Certification'] = cert_lookup_df['Raw Certification'].str.strip().str.title()
        cert_lookup_df['Normalized Certification'] = cert_lookup_df['Normalized Certification'].str.strip().str.title()

        cert_dict = dict(zip(cert_lookup_df['Raw Certification'], cert_lookup_df['Normalized Certification']))
        jobs_df['Normalized Certification'] = jobs_df['Order Cert'].map(cert_dict).fillna(jobs_df['Order Cert'])
        leads_df['Normalized Certification'] = leads_df['Certification'].map(cert_dict).fillna(leads_df['Certification'])

        # ZIP formatting
        jobs_df['Zip'] = jobs_df['Zip'].astype(str).str.zfill(5)
        leads_df['Zip'] = leads_df['Zip'].astype(str).str.zfill(5)
        zip_df['Zip'] = zip_df['Zip'].astype(str).str.zfill(5)

        st.success("All files validated and normalized. Ready for matching logic.")

        # --------------------- Matching Logic ---------------------
        if st.button("Run Matching Logic"):
            behavior_keywords = ['para', 'paraprofessional', 'ta', 'teacher assistant', 'rbt', 'bcba']
            leads_df['Normalized Certification'] = leads_df['Normalized Certification'].fillna("").str.lower()
            non_behavior_leads = leads_df[~leads_df['Normalized Certification'].str.contains('|'.join(behavior_keywords), case=False, na=False)]

            jobs_with_zip = jobs_df[['Order Id', 'Normalized Certification', 'Zip']].dropna()
            leads_with_zip = non_behavior_leads[['First Name', 'Last Name', 'Normalized Certification', 'Zip']].dropna()

            matches = []

            for _, job in jobs_with_zip.iterrows():
                job_zip = str(job['Zip']).zfill(5)
                job_cert = job['Normalized Certification'].title()

                if job_zip in zip_df['Zip'].values:
                    job_lat = zip_df.loc[zip_df['Zip'] == job_zip, 'Lat'].values[0]
                    job_lon = zip_df.loc[zip_df['Zip'] == job_zip, 'Lon'].values[0]

                    for _, lead in leads_with_zip.iterrows():
                        lead_zip = str(lead['Zip']).zfill(5)
                        lead_cert = lead['Normalized Certification'].title()

                        if lead_zip in zip_df['Zip'].values and lead_cert == job_cert:
                            lead_lat = zip_df.loc[zip_df['Zip'] == lead_zip, 'Lat'].values[0]
                            lead_lon = zip_df.loc[zip_df['Zip'] == lead_zip, 'Lon'].values[0]

                            distance = haversine(job_lat, job_lon, lead_lat, lead_lon)
                            if distance <= 30:
                                matches.append({
                                    "Job Order ID": job['Order Id'],
                                    "Job Cert": job_cert,
                                    "Job ZIP": job_zip,
                                    "Lead Name": f"{lead['First Name']} {lead['Last Name']}",
                                    "Lead Cert": lead_cert,
                                    "Lead ZIP": lead_zip,
                                    "Distance (mi)": round(distance, 1)
                                })

            if matches:
                match_df = pd.DataFrame(matches)
                st.success(f"{len(match_df)} matches found!")
                st.dataframe(match_df)
                st.download_button("Download Matches CSV", match_df.to_csv(index=False), "matches.csv", "text/csv")
            else:
                st.warning("No matches found within 30 miles.")
    except Exception as e:
        st.error(f"Error processing files: {e}")
else:
    st.info("📂 Please upload all four required files to proceed.")
