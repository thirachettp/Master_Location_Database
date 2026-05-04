import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lookup Tool", layout="wide")

uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("📄 Excel Preview")
    st.dataframe(df.head(), use_container_width=True)

    excel_col = st.selectbox("เลือก column จาก Excel", df.columns)

    csv_df = pd.read_csv("Main_MasterSequence.csv")

    csv_col = "Location"
    value_col = "Sequence"

    use_last7 = st.checkbox("Match แค่ 7 ตัวท้าย (CMG offline เช่น SABC01A1 → ABC01A1)")

    if st.button("🚀 Run Lookup"):

        # ===== KEY LOGIC =====
        if use_last7:
            df["_key"] = df[excel_col].astype(str).str[-7:]
            csv_df["_key"] = csv_df[csv_col].astype(str).str[-7:]
        else:
            df["_key"] = df[excel_col].astype(str)
            csv_df["_key"] = csv_df[csv_col].astype(str)

        # ===== MERGE =====
        result = df.merge(
            csv_df[["_key", value_col]],
            on="_key",
            how="left"
        )

        result = result.drop(columns=["_key"])

        # ===== SUMMARY =====
        matched_count = result[value_col].notna().sum()
        total_count = len(result)
        unmatched_count = total_count - matched_count
        match_rate = matched_count / total_count * 100 if total_count else 0

        # ===== KPI UI =====
        col1, col2, col3 = st.columns(3)

        col1.metric("✅ Matched", f"{matched_count:,}")
        col2.metric("❌ Unmatched", f"{unmatched_count:,}")
        col3.metric("📊 Match Rate", f"{match_rate:.2f}%")

        st.divider()

        # ===== RESULT TABLE =====
        st.subheader("📊 Result")
        st.dataframe(result, use_container_width=True)

        # Download
        import io

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result.to_excel(writer, index=False, sheet_name='Result')

        output.seek(0)

        st.download_button(
            label="📥 Download Result (Excel)",
            data=output,
            file_name="lookup_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # ===== SHOW DATA =====
        matched_df = result[result[value_col].notna()]
        unmatched_df = result[result[value_col].isna()]

        st.subheader("📊 Matched Data")
        with st.expander(f"Show Matched ({len(matched_df):,})"):
            st.dataframe(matched_df, use_container_width=True)

        st.subheader("⚠️ Unmatched Data")
        with st.expander(f"Show Unmatched ({len(unmatched_df):,})"):
            st.dataframe(unmatched_df, use_container_width=True)
