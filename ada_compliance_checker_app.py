# ============================================================
# ADA Compliance Checker App
# Developed by: Md Obidul Haque (Developer)
# Mentored by: Dr. Jong Bum Kim
# iLab, Architectural Studies, University of Missouri
# ============================================================

import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ADA Compliance Checker", page_icon="✅", layout="wide")

st.title("♿ ADA Compliance Checker Dashboard")
st.caption("Developed by Md Obidul Haque | Mentored by Dr. Jong Bum Kim")
st.caption("iLab, Architectural Studies, University of Missouri")

uploaded_file = st.file_uploader("📁 Upload ADA_Compliance_Report.json", type=["json"])

if uploaded_file:
    data = json.load(uploaded_file)
    df = pd.DataFrame(data)

    # ✅ Ensure essential columns exist
    defaults = {
        "Element": "Unknown Element",
        "Name": "Unknown",
        "Location": "Unknown",
        "Rule": "N/A",
        "Result": "Unknown",
        "Description": "-",
        "Comments": ""
    }
    
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val

    # ✅ Add emoji status
    df["✅/❌"] = df["Result"].apply(lambda x: "✅" if str(x).lower() == "pass" else "❌")

    # ============ Sidebar Filters ============
    st.sidebar.header("🔍 Filters")

    type_filter = st.sidebar.multiselect(
        "Element Type",
        sorted(df["Element"].unique()),
        default=list(df["Element"].unique())
    )
    result_filter = st.sidebar.multiselect(
        "Compliance Result",
        ["Pass", "Fail", "Unknown"],
        default=["Pass", "Fail"]
    )

    filtered_df = df[
        (df["Element"].isin(type_filter)) &
        (df["Result"].isin(result_filter))
    ]

    # ✅ Display Table
    st.dataframe(
        filtered_df[[
            "✅/❌", "Element", "Name", "Location",
            "Rule", "Result", "Description"
        ]],
        width="stretch"
    )

    st.success(f"✅ Showing {len(filtered_df)} compliance checks")

    # ================== 📊 CHART SECTION ==================
    st.subheader("📊 Compliance Summary")

    result_counts = filtered_df["Result"].value_counts()
    labels = result_counts.index.tolist()
    sizes = result_counts.values.tolist()

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    st.pyplot(fig)
    # ======================================================

    # ✅ Download filtered JSON
    json_output = filtered_df.to_json(orient="records", indent=4)
    st.download_button("💾 Download Filtered ADA Report", data=json_output, file_name="Filtered_ADA_Report.json")

else:
    st.info("⬆️ Upload an ADA JSON report to begin.")







