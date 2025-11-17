# ============================================================
# ADA Compliance Checker Dashboard 
# Developed by: Md Obidul Haque
# Mentored by: Dr. Jong Bum Kim
# iLab, Architectural Studies, University of Missouri
# ============================================================

import streamlit as st
import json
import pandas as pd
import plotly.express as px
from streamlit_sortables import sort_items

# 🔧 Page Setup
st.set_page_config(page_title="ADA Compliance Checker", page_icon="♿", layout="wide")

st.title("♿ ADA Compliance Checker Dashboard")
st.caption("Developed by Md Obidul Haque | Mentored by: Dr. Jong Bum Kim")
st.caption("iLab, Architectural Studies, University of Missouri")

# 🔧 Default column values (ensures JSON from any category works)
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

# ==============================
# 📁 Upload JSON (Collapsible)
# ==============================
st.markdown("### 📁 Upload ADA Compliance Reports")

with st.expander("➕ Click to Upload JSON Files", expanded=True):
    uploaded_files = st.file_uploader(
        "Upload one or more ADA_Compliance_Report.json files",
        type=["json"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

if uploaded_files:
    df_list = []

    for uploaded_file in uploaded_files:
        try:
            data = json.load(uploaded_file)
            temp_df = pd.DataFrame(data)

            # Add missing columns
            for col, default_val in defaults.items():
                if col not in temp_df.columns:
                    temp_df[col] = default_val

            temp_df["Source_File"] = uploaded_file.name
            df_list.append(temp_df)

        except Exception as e:
            st.warning(f"⚠️ Failed to load {uploaded_file.name}: {e}")

    if not df_list:
        st.error("❌ No valid JSON data read. Please upload valid reports.")
        st.stop()

    df = pd.concat(df_list, ignore_index=True)

    # Readable "Display Name" & "Location"
    df["Display_Name"] = df.apply(
        lambda r: r["RoomName"] if r["RoomName"].strip() else (r["Space"] if r["Space"].strip() else r["Name"]),
        axis=1
    )
    df["Display_Location"] = df.apply(
        lambda r: r["Location"] if r["Location"].strip() else r["Display_Name"],
        axis=1
    )

    df["Status_Icon"] = df["Result"].apply(lambda x: "✅" if str(x).lower()=="pass" else "❌")

    # ===================================
    # 📊 KPI Overview
    # ===================================
    st.subheader("📊 Compliance Overview")

    total_checks = len(df)
    total_pass = len(df[df["Result"].str.lower()=="pass"])
    total_fail = len(df[df["Result"].str.lower()=="fail"])
    pass_rate = (total_pass / total_checks * 100) if total_checks > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Checks", total_checks)
    k2.metric("✅ Passed", total_pass)
    k3.metric("❌ Failed", total_fail)
    k4.metric("Pass Rate", f"{pass_rate:.1f}%")

    # ===================================
    # 🔍 Filters
    # ===================================
    st.sidebar.header("🔍 Filters")

    type_filter = st.sidebar.multiselect(
        "Element Type", sorted(df["Element"].unique()),
        default=list(df["Element"].unique())
    )

    result_filter = st.sidebar.multiselect(
        "Compliance Result", ["Pass", "Fail", "Unknown"],
        default=["Pass", "Fail"]
    )

    file_filter = st.sidebar.multiselect(
        "Source File", sorted(df["Source_File"].unique()),
        default=list(df["Source_File"].unique())
    )

    filtered_df = df[
        (df["Element"].isin(type_filter)) &
        (df["Result"].isin(result_filter)) &
        (df["Source_File"].isin(file_filter))
    ]

    # ===================================
    # 📋 Results Table
    # ===================================
    st.subheader("📋 Compliance Results Table")

    st.dataframe(
        filtered_df[[
            "Status_Icon", "Source_File", "Element", "Display_Name",
            "Display_Location", "Rule", "Result", "Description"
        ]],
        use_container_width=True
    )

    st.info(f"📌 Showing {len(filtered_df)} filtered results")

    st.download_button(
        label="💾 Download Filtered ADA Report",
        data=filtered_df.to_json(orient="records", indent=4),
        file_name="Filtered_ADA_Report.json"
    )

    # ===================================
    # 📈 Analytics Charts (Drag & Sort)
    # ===================================
    controls1, controls2, controls3 = st.columns([1, 1, 2])

    with controls1:
        show_charts = st.toggle("📈 Analytics", value=False)

    with controls2:
        orientation = st.radio(
            "Bar Orientation", ["Vertical", "Horizontal"],
            horizontal=True, label_visibility="collapsed"
        )

    with controls3:
        layout_mode = st.radio(
            "Layout Mode", ["Side-by-Side", "Vertical Stack"],
            horizontal=True, label_visibility="collapsed"
        )

    if show_charts:
        color_map = {
            "Pass": "rgba(160,231,229,0.85)",
            "Fail": "rgba(255,174,174,0.85)",
            "Unknown": "rgba(200,200,200,0.6)"
        }

        # Pie Chart
        pie_fig = px.pie(
            pd.DataFrame({"Status": ["Pass", "Fail"], "Count": [total_pass, total_fail]}),
            names="Status", values="Count",
            title="Pass vs Fail Distribution",
            color="Status", color_discrete_map=color_map
        )

        # Bar Chart
        bar_df = filtered_df.groupby(["Element", "Result"]).size().reset_index(name="Count")
        bar_fig = px.bar(
            bar_df,
            x="Element" if orientation=="Vertical" else "Count",
            y="Count" if orientation=="Vertical" else "Element",
            color="Result", title="Compliance by Element Type",
            barmode="group", orientation="v" if orientation=="Vertical" else "h",
            color_discrete_map=color_map
        )

        st.subheader("📊 Drag charts to rearrange")
        chart_items = {"Pass vs Fail Distribution": pie_fig, "Compliance by Element Type": bar_fig}

        if layout_mode == "Side-by-Side":
            order = sort_items(list(chart_items.keys()), direction="horizontal", key="sort_h")
            colA, colB = st.columns(2)
            for i, name in enumerate(order):
                (colA if i == 0 else colB).plotly_chart(chart_items[name], use_container_width=True)
        else:
            order = sort_items(list(chart_items.keys()), direction="vertical", key="sort_v")
            for name in order:
                st.plotly_chart(chart_items[name], use_container_width=True)
