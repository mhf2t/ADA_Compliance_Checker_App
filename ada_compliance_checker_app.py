# ============================================================
# ADA Compliance Checker App
# Developed by: Md Obidul Haque (Developer)
# Mentored by: Dr. Jong Bum Kim
# iLab, Architectural Studies, University of Missouri
# ============================================================

import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="ADA Compliance Checker", page_icon="✅", layout="wide")

st.title("♿ ADA Compliance Checker Dashboard")
st.caption("Developed by Md Obidul Haque | Mentored by Dr. Jong Bum Kim")
st.caption("iLab, Architectural Studies, University of Missouri")
st.markdown("Visualize and filter compliance results exported from Dynamo.")

uploaded_file = st.file_uploader("📁 Upload ADA_Compliance_Report.json", type=["json"])

if uploaded_file:
    data = json.load(uploaded_file)
    df = pd.DataFrame(data)

    df["✅/❌"] = df["Result"].apply(lambda x: "✅" if str(x).lower() == "pass" else "❌")

    st.sidebar.header("🔍 Filters")
    elements = st.sidebar.multiselect("Select Element Type", options=df["Element"].unique(), default=df["Element"].unique())
    results = st.sidebar.multiselect("Select Result", options=["Pass", "Fail"], default=["Pass", "Fail"])

    filtered_df = df[df["Element"].isin(elements) & df["Result"].isin(results)]

    st.dataframe(filtered_df[["✅/❌", "Element", "Rule", "Result", "Description", "RoomName", "Location"]], use_container_width=True)

    st.success(f"Showing {len(filtered_df)} results")

    json_str = filtered_df.to_json(orient="records", indent=4)
    st.download_button("💾 Download Filtered JSON", data=json_str, file_name="Filtered_ADA_Report.json")

else:
    st.info("⬆️ Upload your ADA_Compliance_Report.json file to get started.")
