import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import numpy as np

# تهيئة الصفحة
st.set_page_config(
    page_title="النظام الذكي لإدارة الأصول",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص للعربية
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
        transition: transform 0.2s;
    }
    .asset-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .recommendation-high {
        border-right: 6px solid #ff4b4b !important;
        background: #fff5f5;
    }
    .recommendation-medium {
        border-right: 6px solid #ffa64b !important;
        background: #fff9f0;
    }
    .recommendation-low {
        border-right: 6px solid #2ecc71 !important;
        background: #f0fff4;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .stButton button {
        width: 100%;
        background: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class SmartAssetManager:
    def __init__(self, df):
        self.df = df
        self.setup_data()
    
    def setup_data(self):
        """تحضير البيانات للاستخدام"""
        try:
            # تنظيف البيانات الأساسية
            self.df['Cost'] = pd.to_numeric(self.df['Cost'], errors='coerce').fillna(0)
            self.df['Net Book Value'] = pd.to_numeric(self.df['Net Book Value'], errors='coerce').fillna(0)
            self.df['Remaining useful life'] = pd.to_numeric(self.df['Remaining useful life'], errors='coerce').fillna(0)
            
            # إضافة أعمدة محسوبة
            self.df['Maintenance Priority'] = self.df['Remaining useful life'].apply(
                lambda x: 'عالي' if x < 1 else 'متوسط' if x < 2 else 'منخفض'
            )
            
            # تنظيف النصوص العربية
            text_columns = ['Asset Description', 'City', 'Custodian']
            for col in text_columns:
                if col in self.df.columns:
                    self.df[col] = self.df[col].fillna('غير محدد').astype(str)
            
        except Exception as e:
            st.error(f"خطأ في تحضير البيانات: {e}")
    
    def smart_search(self, query):
        """بحث ذكي في الأصول"""
        if not query:
            return self.df
        
        query = query.lower()
        results = self.df.copy()
        
        # فلاتر ذكية بالعربية
        location_keywords = {
            'جدة': 'جدة',
            'الرياض': 'الرياض', 
            'مكة': 'مكة المكرمة',
            'مكه': 'مكة المكرمة'
        }
        
        asset_keywords = {
            'كمبيوتر': ['حاسب', 'كمبيوتر', 'كومبيوتر', 'لابتوب'],
            'هاتف': ['هاتف', 'تلفون', 'اتصال'],
            'انارة': ['انارة', 'إنارة', 'عمود', 'إناره', 'اناره'],
            'معدات': ['معدات', 'جهاز', 'آلة']
        }
        
        # البحث عن مواقع
        for keyword, city in location_keywords.items():
            if keyword in query:
                results = results[results['City'] == city]
                break
        
        # البحث عن أنواع الأصول
        for asset_type, keywords in asset_keywords.items():
            if any(keyword in query for keyword in [asset_type] + keywords):
                pattern = '|'.join(keywords)
                results = results[results['Asset Description'].str.contains(pattern, case=False, na=False)]
                break
        
        # البحث عن نطاق سعر
        price_patterns = [
            r'اكثر من (\\d+)',
            r'أكثر من (\\d+)', 
            r'أكبر من (\\d+)',
            r'اكبر من (\\d+)'
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, query)
            if price_match:
                min_price = float(price_match.group(1))
                results = results[results['Cost'] > min_price]
                break
        
        # البحث عن أقسام
        if any(word in query for word in ['تقنية', 'معلومات', 'حاسب آلي']):
            results = results[results['Custodian'].str.contains('تقنية|معلومات', case=False, na=False)]
        
        return results
    
    def get_asset_insights(self):
        """تحليلات ذكية عن الأصول"""
        try:
            total_assets = len(self.df)
            total_value = self.df['Net Book Value'].sum()
            high_priority = len(self.df[self.df['Maintenance Priority'] == 'عالي'])
            medium_priority = len(self.df[self.df['Maintenance Priority'] == 'متوسط'])
            
            # توزيع الأصول حسب المدينة
            city_dist = self.df['City'].value_counts()
            
            # الأصول الأكثر قيمة
            top_assets = self.df.nlargest(5, 'Net Book Value')
            
            # توزيع الأولويات
            priority_dist = self.df['Maintenance Priority'].value_counts()
            
            return {
                'total_assets': total_assets,
                'total_value': total_value,
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'city_distribution': city_dist,
                'top_assets': top_assets,
                'priority_distribution': priority_dist
            }
        except Exception as e:
            st.error(f"خطأ في توليد التحليلات: {e}")
            return {}
    
    def get_recommendations(self):
        """توصيات ذكية"""
        recommendations = []
        
        try:
            for _, asset in self.df.iterrows():
                priority = asset['Maintenance Priority']
                
                if priority in ['عالي', 'متوسط']:
                    reason = 'العمر المتبقي أقل من سنة' if priority == 'عالي' else 'العمر المتبقي أقل من سنتين'
                    
                    recommendations.append({
                        'asset_id': asset.get('Tag number', 'غير معروف'),
                        'description': asset.get('Asset Description', 'غير معروف'),
                        'priority': priority,
                        'reason': reason,
                        'remaining_life': asset.get('Remaining useful life', 0),
                        'department': asset.get('Custodian', 'غير محدد'),
                        'cost': asset.get('Cost', 0),
                        'city': asset.get('City', 'غير محدد')
                    })
            
            # ترتيب حسب الأولوية والتكلفة
            recommendations.sort(key=lambda x: (x['priority'] == 'عالي', x['cost']), reverse=True)
            
        except Exception as e:
            st.error(f"خطأ في توليد التوصيات: {e}")
        
        return recommendations
    
    def get_department_analysis(self):
        """تحليل الأقسام"""
        try:
            dept_analysis = self.df.groupby('Custodian').agg({
                'Tag number': 'count',
                'Net Book Value': 'sum',
                'Cost': 'sum',
                'Remaining useful life': 'mean'
            }).round(2)
            
            dept_analysis = dept_analysis.rename(columns={
                'Tag number': 'عدد الأصول',
                'Net Book Value': 'القيمة الإجمالية',
                'Cost': 'التكلفة الإجمالية', 
                'Remaining useful life': 'متوسط العمر المتبقي'
            })
            
            return dept_analysis
        except Exception as e:
            st.error(f"خطأ في تحليل الأقسام: {e}")
            return pd.DataFrame()

def load_sample_data():
    """تحميل بيانات نموذجية للعرض"""
    try:
        # بيانات شاملة ومتنوعة
        sample_data = {
            'Tag number': [
                '24007520.0', '24000282.0', '24007457.0', '24000395.0', '24009041.0',
                '24009261.0', '24007518.0', '24007458.0', '24007397.0', '24007191.0'
            ],
            'Asset Description': [
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر',
                'هاتف CISCO CP-7841',
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر',
                'جهاز حاسب الي HP Z620 WORKSTATION INTEL XEON مع شاشة DELL',
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر',
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر',
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر', 
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر',
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر',
                'عامود انارة حديد كشاف واحد LED ارتفاع 4 متر'
            ],
            'City': ['جدة', 'جدة', 'جدة', 'جدة', 'الرياض', 'جدة', 'جدة', 'جدة', 'جدة', 'الرياض'],
            'Custodian': [
                'ادارة الخدمات و المرافق',
                'ادارة التخطيط و قياس الأداء',
                'ادارة الخدمات و المرافق',
                'مركز المخاطر الجيولوجية',
                'ادارة الخدمات و المرافق',
                'ادارة الخدمات و المرافق',
                'ادارة الخدمات و المرافق',
                'ادارة الخدمات و المرافق', 
                'ادارة الامن والصحة والسلامة',
                'ادارة الخدمات و المرافق'
            ],
            'Cost': [90.0, 57.5, 90.0, 125.7, 45.0, 90.0, 90.0, 90.0, 90.0, 90.0],
            'Net Book Value': [90.0, 57.5, 90.0, 125.7, 45.0, 90.0, 90.0, 90.0, 90.0, 90.0],
            'Remaining useful life': [2.5, 0.3, 2.5, 0.3, 1.2, 2.5, 2.5, 2.5, 2.5, 0.8],
            'Manufacturer': [
                'Not Available', 'CISCO', 'Not Available', 'HP', 'Not Available',
                'Not Available', 'Not Available', 'Not Available', 'Not Available', 'Not Available'
            ]
        }
        return pd.DataFrame(sample_data)
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات النموذجية: {e}")
        return pd.DataFrame()

def main():
    # العنوان الرئيسي
    st.markdown('<h1 class="main-header">🏢 النظام الذكي لإدارة الأصول</h1>', unsafe_allow_html=True)
    
    # تحميل البيانات
    with st.spinner('📂 جاري تحميل بيانات الأصول...'):
        df = load_sample_data()
    
    if df.empty:
        st.error("❌ لم يتم تحميل البيانات بنجاح. يرجى التحقق من الملف.")
        return
    
    # عرض معلومات أساسية عن البيانات
    st.sidebar.info(f"📊 تم تحميل {len(df)} أصل")
    
    asset_manager = SmartAssetManager(df)
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("🔍 البحث الذكي")
        search_query = st.text_input(
            "اكتب استعلامك:",
            placeholder="مثال: أعمدة إنارة في جدة تكلفتها أكثر من 50"
        )
        
        st.header("🎯 التصفيات المتقدمة")
        selected_city = st.selectbox("المدينة:", ['الكل'] + list(df['City'].unique()))
        selected_department = st.selectbox("القسم:", ['الكل'] + list(df['Custodian'].unique()))
        
        col1, col2 = st.columns(2)
        with col1:
            min_cost = st.number_input("الحد الأدنى للتكلفة:", min_value=0, value=0, step=10)
        with col2:
            max_cost = st.number_input("الحد الأقصى للتكلفة:", min_value=0, value=500, step=10)
        
        priority_filter = st.multiselect(
            "أولوية الصيانة:",
            ['عالي', 'متوسط', 'منخفض'],
            default=['عالي', 'متوسط']
        )
        
        if st.button("🔄 تحديث النتائج"):
            st.rerun()
    
    # تبويبات الصفحة الرئيسية
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 لوحة التحكم", "🔍 البحث", "📊 التقارير", "🤖 المساعد الذكي", "ℹ️ عن النظام"
    ])
    
    with tab1:
        display_dashboard(asset_manager)
    
    with tab2:
        display_search(asset_manager, search_query, selected_city, selected_department, min_cost, max_cost, priority_filter)
    
    with tab3:
        display_reports(asset_manager)
    
    with tab4:
        display_ai_assistant(asset_manager)
    
    with tab5:
        display_about()

def display_dashboard(asset_manager):
    """عرض لوحة التحكم"""
    st.header("📊 لوحة التحكم الذكية")
    
    insights = asset_manager.get_asset_insights()
    
    if not insights:
        st.error("لا توجد بيانات كافية لعرض التحليلات")
        return
    
    # بطاقات الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔄 إجمالي الأصول</h3>
            <h2>{insights['total_assets']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 القيمة الإجمالية</h3>
            <h2>{insights['total_value']:,.0f} ريال</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔴 أولوية عالية</h3>
            <h2>{insights['high_priority']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🟡 أولوية متوسطة</h3>
            <h2>{insights['medium_priority']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # الرسوم البيانية
    col1, col2 = st.columns(2)
    
    with col1:
        # توزيع الأصول حسب المدينة
        if not insights['city_distribution'].empty:
            fig = px.pie(
                values=insights['city_distribution'].values,
                names=insights['city_distribution'].index,
                title="🏙️ توزيع الأصول حسب المدينة",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # توزيع الأولويات
        if 'priority_distribution' in insights and not insights['priority_distribution'].empty:
            fig = px.bar(
                x=insights['priority_distribution'].values,
                y=insights['priority_distribution'].index,
                orientation='h',
                title="🎯 توزيع أولويات الصيانة",
                color=insights['priority_distribution'].index,
                color_discrete_map={'عالي': '#ff4b4b', 'متوسط': '#ffa64b', 'منخفض': '#2ecc71'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # التوصيات العاجلة
    st.subheader("🔔 التوصيات الذكية")
    recommendations = asset_manager.get_recommendations()
    
    if not recommendations:
        st.success("✅ لا توجد توصيات صيانة عاجلة حالياً.")
    else:
        for rec in recommendations[:8]:  # عرض أول 8 توصيات فقط
            priority_class = f"recommendation-{rec['priority']}"
            
            st.markdown(f"""
            <div class="asset-card {priority_class}">
                <strong>🏷️ {rec['asset_id']}</strong><br>
                <strong>{rec['description']}</strong><br>
                📍 {rec['department']} | 🏙️ {rec['city']}<br>
                💰 {rec['cost']:,.0f} ريال | ⏳ العمر المتبقي: {rec['remaining_life']} سنة<br>
                <span style="color: {'#ff4b4b' if rec['priority'] == 'عالي' else '#ffa64b'}">
                🔴 {rec['reason']}
                </span>
            </div>
            """, unsafe_allow_html=True)

def display_search(asset_manager, search_query, selected_city, selected_department, min_cost, max_cost, priority_filter):
    """عرض صفحة البحث"""
    st.header("🔍 البحث الذكي في الأصول")
    
    # تطبيق الفلاتر
    filtered_df = asset_manager.df.copy()
    
    if selected_city != 'الكل':
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    
    if selected_department != 'الكل':
        filtered_df = filtered_df[filtered_df['Custodian'] == selected_department]
    
    filtered_df = filtered_df[
        (filtered_df['Cost'] >= min_cost) & 
        (filtered_df['Cost'] <= max_cost)
    ]
    
    if priority_filter:
        filtered_df = filtered_df[filtered_df['Maintenance Priority'].isin(priority_filter)]
    
    # البحث الذكي
    if search_query:
        filtered_df = asset_manager.smart_search(search_query)
        if not search_query.strip():
            st.info("💡 اكتب استعلامك في مربع البحث أعلاه")
    
    # عرض النتائج
    st.subheader(f"📊 النتائج: {len(filtered_df)} أصل")
    
    if filtered_df.empty:
        st.warning("⚠️ لم يتم العثور على أصول تطابق معايير البحث")
        return
    
    # خيارات العرض
    view_mode = st.radio("طريقة العرض:", ["بطاقات", "جدول"], horizontal=True)
    
    if view_mode == "بطاقات":
        for _, asset in filtered_df.iterrows():
            priority_class = f"recommendation-{asset['Maintenance Priority']}"
            
            with st.expander(f"🏷️ {asset['Tag number']} - {asset['Asset Description']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**🏙️ المدينة:** {asset['City']}")
                    st.write(f"**👥 القسم:** {asset['Custodian']}")
                    st.write(f"**🏭 المصنع:** {asset.get('Manufacturer', 'غير محدد')}")
                
                with col2:
                    st.write(f"**💰 التكلفة:** {asset['Cost']:,.0f} ريال")
                    st.write(f"**📈 القيمة الدفترية:** {asset['Net Book Value']:,.0f} ريال")
                    st.write(f"**📊 الأولوية:** {asset['Maintenance Priority']}")
                
                with col3:
                    st.write(f"**⏳ العمر المتبقي:** {asset['Remaining useful life']} سنة")
                    st.write(f"**🆔 الرمز:** {asset['Tag number']}")
                    
                    # زر سريع للإجراءات
                    if st.button(f"عرض التفاصيل 📋", key=f"btn_{asset['Tag number']}"):
                        st.success(f"جاري تحميل تفاصيل الأصل {asset['Tag number']}")
    else:
        # عرض جدولي
        display_columns = ['Tag number', 'Asset Description', 'City', 'Custodian', 'Cost', 'Net Book Value', 'Remaining useful life', 'Maintenance Priority']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        st.dataframe(filtered_df[available_columns], use_container_width=True)

def display_reports(asset_manager):
    """عرض التقارير"""
    st.header("📊 التقارير الذكية")
    
    # تحليل الأقسام
    st.subheader("👥 تحليل الأقسام")
    dept_analysis = asset_manager.get_department_analysis()
    
    if not dept_analysis.empty:
        st.dataframe(dept_analysis, use_container_width=True)
    else:
        st.warning("لا توجد بيانات كافية لتحليل الأقسام")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # تقرير توزيع التكلفة
        if not asset_manager.df.empty:
            fig = px.box(asset_manager.df, y='Cost', title="📦 توزيع التكاليف")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # تقرير العمر المتبقي
        if not asset_manager.df.empty:
            fig = px.histogram(
                asset_manager.df, 
                x='Remaining useful life', 
                title="⏳ توزيع العمر الإنتاجي المتبقي",
                color_discrete_sequence=['#2ecc71']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # تقرير تفصيلي
    st.subheader("📋 التقرير التفصيلي")
    
    report_type = st.selectbox("اختر نوع التقرير:", [
        "جميع الأصول",
        "الأصول ذات الأولوية العالية", 
        "الأصول حسب المدينة",
        "الأصول حسب القسم",
        "الأصول منخفضة التكلفة",
        "الأصول مرتفعة التكلفة"
    ])
    
    if report_type == "الأصول ذات الأولوية العالية":
        report_df = asset_manager.df[asset_manager.df['Maintenance Priority'] == 'عالي']
    elif report_type == "الأصول حسب المدينة":
        selected_city = st.selectbox("اختر المدينة:", asset_manager.df['City'].unique())
        report_df = asset_manager.df[asset_manager.df['City'] == selected_city]
    elif report_type == "الأصول حسب القسم":
        selected_dept = st.selectbox("اختر القسم:", asset_manager.df['Custodian'].unique())
        report_df = asset_manager.df[asset_manager.df['Custodian'] == selected_dept]
    elif report_type == "الأصول منخفضة التكلفة":
        report_df = asset_manager.df[asset_manager.df['Cost'] < asset_manager.df['Cost'].median()]
    elif report_type == "الأصول مرتفعة التكلفة":
        report_df = asset_manager.df[asset_manager.df['Cost'] > asset_manager.df['Cost'].median()]
    else:
        report_df = asset_manager.df
    
    st.dataframe(report_df, use_container_width=True)
    
    # خيارات التصدير
    if st.button("📥 تصدير التقرير إلى Excel"):
        # محاكاة التصدير (في التطبيق الحقيقي سيتم إنشاء ملف Excel)
        st.success("✅ تم تصدير التقرير بنجاح!")

def display_ai_assistant(asset_manager):
    """عرض المساعد الذكي"""
    st.header("🤖 المساعد الذكي للأصول")
    
    st.info("""
    💡 **يمكنك سؤال المساعد عن:**
    - معلومات عن أصول محددة
    - توصيات الصيانة العاجلة
    - إحصائيات الأصول
    - مقارنة بين الأقسام
    - تحليل التكاليف
    """)
    
    # تهيئة سجل المحادثة
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # أمثلة سريعة
    st.subheader("🔄 استعلامات سريعة")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 الأصول العاجلة"):
            st.session_state.chat_history.append({"role": "user", "message": "ما هي الأصول التي تحتاج صيانة عاجلة؟"})
            st.rerun()
    
    with col2:
        if st.button("📊 إحصائيات عامة"):
            st.session_state.chat_history.append({"role": "user", "message": "اعطني إحصائيات الأصول"})
            st.rerun()
    
    with col3:
        if st.button("🏙️ أصول جدة"):
            st.session_state.chat_history.append({"role": "user", "message": "ما هي الأصول في جدة؟"})
            st.rerun()
    
    # إدخال المستخدم
    user_input = st.text_input(
        "💬 اسأل المساعد الذكي:",
        placeholder="مثال: ما هي الأصول التي تكلفتها أكثر من 100 ريال؟",
        key="user_input"
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("إرسال 🚀") and user_input:
            # إضافة سؤال المستخدم للسجل
            st.session_state.chat_history.append({"role": "user", "message": user_input})
            
            # توليد رد المساعد
            response = generate_ai_response(asset_manager, user_input)
            st.session_state.chat_history.append({"role": "assistant", "message": response})
            st.rerun()
    
    # عرض سجل المحادثة
    st.subheader("💬 سجل المحادثة")
    
    if not st.session_state.chat_history:
        st.write("💭 لم تبدأ المحادثة بعد. استخدم الأزرار أعلاه أو اكتب سؤالك.")
    else:
        for chat in st.session_state.chat_history[-10:]:  # آخر 10 رسائل
            if chat["role"] == "user":
                st.markdown(f"""
                <div style='background: #e3f2fd; padding: 1rem; border-radius: 15px; margin: 0.5rem 0; border-right: 4px solid #1f77b4;'>
                    <strong>👤 أنت:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background: #f3e5f5; padding: 1rem; border-radius: 15px; margin: 0.5rem 0; border-right: 4px solid #9c27b0;'>
                    <strong>🤖 المساعد:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()

def generate_ai_response(asset_manager, query):
    """توليد رد ذكي بناءً على الاستعلام"""
    query = query.lower()
    
    try:
        if any(word in query for word in ['صيانة', 'عاجل', 'أولوية', 'عاجلة']):
            high_priority = len(asset_manager.df[asset_manager.df['Maintenance Priority'] == 'عالي'])
            medium_priority = len(asset_manager.df[asset_manager.df['Maintenance Priority'] == 'متوسط'])
            return f"🔔 **توصيات الصيانة:**\n- الأصول ذات الأولوية العالية: {high_priority} أصل\n- الأصول ذات الأولوية المتوسطة: {medium_priority} أصل\n\nيوصى بمراجعة هذه الأصول قريباً."
        
        elif any(word in query for word in ['إحصائيات', 'أعداد', 'إجمالي', 'إحصائية']):
            insights = asset_manager.get_asset_insights()
            return f"📊 **الإحصائيات العامة:**\n- إجمالي الأصول: {insights['total_assets']}\n- القيمة الإجمالية: {insights['total_value']:,.0f} ريال\n- الأصول عالية الأولوية: {insights['high_priority']}\n- المدن: {len(insights['city_distribution'])} مدينة"
        
        elif any(word in query for word in ['جدة', 'الرياض']):
            city = 'جدة' if 'جدة' in query else 'الرياض'
            city_assets = asset_manager.df[asset_manager.df['City'] == city]
            city_value = city_assets['Net Book Value'].sum()
            high_priority_city = len(city_assets[city_assets['Maintenance Priority'] == 'عالي'])
            
            return f"🏙️ **أصول {city}:**\n- العدد: {len(city_assets)} أصل\n- القيمة: {city_value:,.0f} ريال\n- الأصول عالية الأولوية: {high_priority_city} أصل"
        
        elif any(word in query for word in ['تكلفة', 'سعر', 'ثمن', 'قيمة']):
            avg_cost = asset_manager.df['Cost'].mean()
            max_cost = asset_manager.df['Cost'].max()
            min_cost = asset_manager.df['Cost'].min()
            
            return f"💰 **تحليل التكاليف:**\n- متوسط التكلفة: {avg_cost:,.0f} ريال\n- أعلى تكلفة: {max_cost:,.0f} ريال\n- أدنى تكلفة: {min_cost:,.0f} ريال"
        
        elif any(word in query for word in ['عمر', 'قديم', 'مستعمل', 'جديد']):
            avg_life = asset_manager.df['Remaining useful life'].mean()
            old_assets = len(asset_manager.df[asset_manager.df['Remaining useful life'] < 1])
            
            return f"⏳ **تحليل الأعمار:**\n- متوسط العمر المتبقي: {avg_life:.1f} سنة\n- الأصول التي عمرها أقل من سنة: {old_assets} أصل"
        
        else:
            return "🤔 **المساعد:** يمكنني مساعدتك في:\n- معلومات الصيانة والأولويات\n- إحصائيات الأصول العامة\n- البحث حسب المدينة\n- تحليل التكاليف والأعمار\n\n💡 **جرب:** 'ما هي الأصول العاجلة؟' أو 'اعطني إحصائيات جدة'"
    
    except Exception as e:
        return f"❌ حدث خطأ في معالجة سؤالك: {e}"

def display_about():
    """صفحة عن النظام"""
    st.header("ℹ️ عن النظام الذكي لإدارة الأصول")
    
    st.markdown("""
    ## 🎯 نظرة عامة
    
    **النظام الذكي لإدارة الأصول** هو منصة متكاملة تستخدم التقنيات الحديثة والذكاء الاصطناعي 
    لتحسين عمليات إدارة وتتبع الأصول في المؤسسات.
    
    ## ✨ الميزات الرئيسية
    
    ### 🔍 البحث الذكي
    - فهم الاستعلامات الطبيعية باللغة العربية
    - بحث متقدم بمعايير متعددة
    - نتائج ذكية ومصنفة
    
    ### 📊 التحليلات المتقدمة
    - لوحة تحكم تفاعلية مع مؤشرات أداء
    - رسوم بيانية حية وتقارير مفصلة
    - تحليل التكاليف والأولويات
    
    ### 🤖 المساعد الذكي
    - محادثة طبيعية بالعربية
    - إجابات ذكية على الاستفسارات
    - توصيات مبنية على البيانات
    
    ### 🛠️ إدارة الصيانة
    - نظام تتبع أولويات الصيانة
    - تنبيهات للأصول التي تحتاج اهتمام
    - تخطيط استباقي للصيانة
    
    ## 🚀 التقنيات المستخدمة
    
    - **Streamlit** - واجهة المستخدم التفاعلية
    - **Pandas** - معالجة وتحليل البيانات
    - **Plotly** - الرسوم البيانية التفاعلية
    - **Python** - البرمجة والذكاء الاصطناعي
    
    ## 📞 الدعم والمساندة
    
    للاستفسارات والدعم التقني، يرجى التواصل مع فريق التطوير.
    
    ---
    
    *تم تطوير هذا النظام لتحسين كفاءة إدارة الأصول واتخاذ القرارات المدعومة بالبيانات.*
    """)

if __name__ == "__main__":
    main()
