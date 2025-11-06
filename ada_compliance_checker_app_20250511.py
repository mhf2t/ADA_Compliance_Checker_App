# ============================================================
# ADA Compliance Checker Dashboard (Multi-File Enhanced Version)
# Developed by: Md Obidul Haque
# Mentored by: Dr. Jong Bum Kim
# iLab, Architectural Studies, University of Missouri
# ============================================================

import streamlit as st
import json
import pandas as pd
import plotly.express as px

# ✅ Page Setup
st.set_page_config(page_title="ADA Compliance Checker", page_icon="♿", layout="wide")

st.title("♿ ADA Compliance Checker Dashboard")
st.caption("Developed by Md Obidul Haque | Mentored by Dr. Jong Bum Kim")
st.caption("iLab, Architectural Studies, University of Missouri")

# ✅ Ensure essential columns exist BEFORE loading files
defaults = {
    "Element": "Unknown",
    "Name": "Unknown",
    "RoomName": "",
    "Space": "",
    "Location": "",
    "Rule": "N/A",
    "Result": "Unknown",
    "Description": "-",
    "ValueMeasured": "",
    "ValueRequired": "",
    "Comments": ""
}

# ✅ Multi-file upload enabled
uploaded_files = st.file_uploader(
    "📁 Upload one or more ADA_Compliance_Report.json files",
    type=["json"],
    accept_multiple_files=True
)

if uploaded_files:
    df_list = []

    for uploaded_file in uploaded_files:
        try:
            data = json.load(uploaded_file)
            temp_df = pd.DataFrame(data)

            # ✅ Ensure essential columns exist
            for col, default_val in defaults.items():
                if col not in temp_df.columns:
                    temp_df[col] = default_val

            # ✅ Track file source
            temp_df["Source_File"] = uploaded_file.name

            df_list.append(temp_df)

        except Exception as e:
            st.warning(f"⚠️ Failed to load {uploaded_file.name}: {e}")

    # ✅ Ensure at least one valid file loaded
    if not df_list:
        st.error("❌ No valid JSON data read. Please upload correct reports.")
        st.stop()

    # ✅ Merge all uploaded reports
    df = pd.concat(df_list, ignore_index=True)

    # ✅ Unified display name
    df["Display_Name"] = df.apply(
        lambda r: r["RoomName"] if isinstance(r["RoomName"], str) and r["RoomName"].strip()
        else (r["Space"] if isinstance(r["Space"], str) and r["Space"].strip()
              else r["Name"]),
        axis=1
    )

    # ✅ Unified display location
    df["Display_Location"] = df.apply(
        lambda r: r["Location"] if isinstance(r["Location"], str) and r["Location"].strip()
        else r["Display_Name"],
        axis=1
    )

    # ✅ Emoji results column
    df["✅/❌"] = df["Result"].apply(lambda x: "✅" if str(x).lower() == "pass" else "❌")

    # ==================================================
    # 📊 KPIs
    # ==================================================
    st.subheader("📊 Compliance Overview")

    total_checks = len(df)
    total_pass = len(df[df["Result"].str.lower() == "pass"])
    total_fail = len(df[df["Result"].str.lower() == "fail"])
    pass_rate = (total_pass / total_checks * 100) if total_checks > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Checks", total_checks)
    k2.metric("✅ Passed", total_pass)
    k3.metric("❌ Failed", total_fail)
    k4.metric("Pass Rate", f"{pass_rate:.1f}%")

    # ==================================================
    # 🔍 Filters
    # ==================================================
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

    file_filter = st.sidebar.multiselect(
        "Source File",
        sorted(df["Source_File"].unique()),
        default=list(df["Source_File"].unique())
    )

    filtered_df = df[
        (df["Element"].isin(type_filter)) &
        (df["Result"].isin(result_filter)) &
        (df["Source_File"].isin(file_filter))
    ]

    # ==================================================
    # 📋 Results Table
    # ==================================================
    st.subheader("📋 Compliance Results Table")

    st.dataframe(
        filtered_df[[
            "✅/❌", "Source_File", "Element", "Display_Name", "Display_Location",
            "Rule", "Result", "Description"
        ]],
        use_container_width=True
    )
    st.info(f"✅ Showing {len(filtered_df)} filtered results")

    # ✅ JSON Export Button
    st.download_button(
        label="💾 Download Filtered ADA Report",
        data=filtered_df.to_json(orient="records", indent=4),
        file_name="Filtered_ADA_Report.json"
    )

    # ==================================================
    # 📈 Analytics: Charts
    # ==================================================
    show_charts = st.checkbox("📈 Show Compliance Analytics", value=False)

    if show_charts:
        st.subheader("📈 Compliance Analytics")

        color_map = {
            "Pass": "rgba(160, 231, 229, 0.85)",
            "Fail": "rgba(255, 174, 174, 0.85)",
            "Unknown": "rgba(200, 200, 200, 0.6)"
        }

        # ✅ Pie Chart
        overview_df = pd.DataFrame({
            "Status": ["Pass", "Fail"],
            "Count": [total_pass, total_fail]
        })

        pie_fig = px.pie(
            overview_df,
            names="Status",
            values="Count",
            title="Pass vs Fail Distribution",
            color="Status",
            color_discrete_map=color_map
        )
        st.plotly_chart(pie_fig, use_container_width=True)

        # ✅ Bar Chart
        bar_df = filtered_df.groupby(["Element", "Result"]).size().reset_index(name="Count")

        bar_fig = px.bar(
            bar_df,
            x="Element",
            y="Count",
            color="Result",
            title="Compliance by Element Type",
            barmode="group",
            color_discrete_map=color_map
        )
        st.plotly_chart(bar_fig, use_container_width=True)

else:
    st.info("⬆️ Upload one or more ADA JSON reports to begin.")
