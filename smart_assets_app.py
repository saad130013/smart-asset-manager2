import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import numpy as np
from data_loader import load_asset_data

# تهيئة الصفحة
st.set_page_config(
    page_title="النظام الذكي لإدارة الأصول",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
}
.asset-card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-right: 6px solid #1f77b4;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.25s;
}
.asset-card:hover {
    transform: scale(1.01);
}
</style>
""")

# تحميل البيانات
@st.cache_data
def load_data():
    try:
        df = load_asset_data("SGS_AutoGPT_Assets_Template_MoF.xlsx")
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")
        return pd.DataFrame()

# كلاس إدارة الأصول الذكية
class SmartAssetManager:
    def __init__(self, df):
        self.df = df

    def smart_search(self, keyword):
        if keyword.strip() == "":
            return self.df
        mask = self.df.apply(lambda x: x.astype(str).str.contains(keyword, case=False, na=False)).any(axis=1)
        return self.df[mask]

    def get_asset_insights(self):
        try:
            df = self.df.copy()
            summary = {
                "إجمالي الأصول": len(df),
                "إجمالي التكلفة": df["Cost"].sum() if "Cost" in df else 0,
                "إجمالي القيمة الدفترية": df["Net Book Value"].sum() if "Net Book Value" in df else 0,
                "عدد المدن": df["City"].nunique() if "City" in df else 0
            }
            return summary
        except Exception:
            return {}

# واجهة Streamlit
def main():
    st.title("🏢 النظام الذكي لإدارة الأصول")
    st.write("نظام متكامل للبحث والتحليل وعرض بيانات الأصول باستخدام الذكاء الاصطناعي.")

    df = load_data()
    if df.empty:
        st.warning("لم يتم تحميل أي بيانات من ملف الإكسل.")
        return

    manager = SmartAssetManager(df)

    st.subheader("🔍 البحث الذكي")
    keyword = st.text_input("أدخل كلمة البحث (اسم الأصل، الرقم، أو الجهة):")
    results = manager.smart_search(keyword)

    st.write(f"عدد النتائج: {len(results)}")
    st.dataframe(results, use_container_width=True)

    st.subheader("📊 ملخص الأصول")
    insights = manager.get_asset_insights()
    if insights:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي الأصول", insights["إجمالي الأصول"])
        c2.metric("إجمالي التكلفة", f"{insights['إجمالي التكلفة']:,}")
        c3.metric("إجمالي القيمة الدفترية", f"{insights['إجمالي القيمة الدفترية']:,}")
        c4.metric("عدد المدن", insights["عدد المدن"])

    st.subheader("📈 التحليل الجغرافي")
    if "City" in df.columns:
        city_chart = df["City"].value_counts().reset_index()
        city_chart.columns = ["City", "Count"]
        st.plotly_chart(px.bar(city_chart, x="City", y="Count", title="توزيع الأصول حسب المدن"))

if __name__ == "__main__":
    main()
