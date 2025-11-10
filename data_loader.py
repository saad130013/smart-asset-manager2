import pandas as pd
import streamlit as st
import os

def load_asset_data(file_path: str = "SGS_AutoGPT_Assets_Template_MoF.xlsx") -> pd.DataFrame:
    """
    تحميل بيانات الأصول من ملف Excel أو Google Sheet (إذا تم توفير الرابط).
    تُعيد DataFrame نظيفة جاهزة للاستخدام في النظام.
    file_path: يمكن أن يكون مسار ملف .xlsx محلي أو رابط Google Sheets.
    """
    try:
        # تحميل من Google Sheets إذا أعطي رابط
        if isinstance(file_path, str) and file_path.startswith("https://docs.google.com/spreadsheets/"):
            try:
                sheet_id = file_path.split("/d/")[1].split("/")[0]
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                df = pd.read_excel(url, sheet_name="Assets")
            except Exception as e:
                st.error(f"تعذر قراءة Google Sheets: {e}")
                return pd.DataFrame()
        else:
            if not os.path.exists(file_path):
                st.warning(f"⚠️ لم يتم العثور على الملف: {file_path}")
                return pd.DataFrame()
            df = pd.read_excel(file_path, sheet_name="Assets")

        # تنظيف الأعمدة
        df.columns = df.columns.str.strip()
        df = df.dropna(how="all")

        # تحويل القيم الرقمية
        numeric_cols = ["Cost", "Net Book Value", "Depreciation amount",
                        "Accumulated Depreciation", "Remaining useful life"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # معالجة النصوص الفارغة
        text_cols = ["Asset Description", "City", "Custodian", "Tag number", "Manufacturer"]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].fillna("غير محدد").astype(str)

        st.success("✅ تم تحميل بيانات الأصول بنجاح!")
        return df

    except Exception as e:
        st.error(f"❌ خطأ أثناء تحميل البيانات: {e}")
        return pd.DataFrame()
