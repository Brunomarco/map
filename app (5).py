"""
Nuclear Medicine EMEA Manufacturing Dashboard
Executive Presentation | MBB Professional Standard

DATA SOURCE: All facility names, isotopes, and half-life data extracted 
directly from PowerPoint Slide 2 "NM Origins and Manufacturers"
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════
# EXECUTIVE MBB STYLING
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-dark: #0D3B2E;
        --primary: #1A6B52;
        --primary-light: #28B463;
        --accent-blue: #1B4F72;
        --accent-cyan: #00B0F0;
        --text-dark: #1A1A1A;
        --text-medium: #4A4A4A;
        --text-light: #6B7280;
        --bg-white: #FFFFFF;
        --bg-light: #F8FAFB;
        --border-light: #E5E8EB;
        --danger: #DC2626;
    }
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    
    .stApp { background: var(--bg-light); }
    
    /* ═══ Executive Header ═══ */
    .exec-header {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 50%, var(--accent-blue) 100%);
        padding: 1.75rem 2.5rem;
        margin: -1rem -1rem 1.75rem -1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
    }
    
    .logo-container {
        width: 55px;
        height: 55px;
        margin-right: 24px;
    }
    
    .header-content h1 {
        color: white;
        font-weight: 600;
        font-size: 1.85rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-content .tagline {
        color: rgba(255,255,255,0.88);
        font-size: 0.9rem;
        font-weight: 400;
        margin-top: 6px;
    }
    
    /* ═══ KPI Dashboard ═══ */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin-bottom: 24px;
    }
    
    .kpi-card {
        background: var(--bg-white);
        border-radius: 14px;
        padding: 22px 18px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border: 1px solid var(--border-light);
        transition: all 0.25s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    .kpi-number {
        font-size: 2.75rem;
        font-weight: 700;
        color: var(--accent-blue);
        line-height: 1;
    }
    
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 10px;
    }
    
    /* ═══ Legend Panel ═══ */
    .legend-wrapper {
        background: var(--bg-white);
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border: 1px solid var(--border-light);
        overflow: hidden;
    }
    
    .legend-title {
        background: var(--accent-blue);
        color: white;
        padding: 14px 18px;
        font-weight: 600;
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .legend-body {
        max-height: 465px;
        overflow-y: auto;
    }
    
    .legend-entry {
        display: flex;
        align-items: flex-start;
        padding: 14px 18px;
        border-bottom: 1px solid var(--border-light);
        transition: background 0.15s;
    }
    
    .legend-entry:hover { background: var(--bg-light); }
    .legend-entry:last-child { border-bottom: none; }
    
    .site-num {
        background: linear-gradient(135deg, #00B0F0 0%, #0090C8 100%);
        color: white;
        font-weight: 700;
        min-width: 34px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        margin-right: 16px;
        font-size: 0.88rem;
        flex-shrink: 0;
        box-shadow: 0 2px 6px rgba(0,176,240,0.35);
    }
    
    .site-desc {
        flex: 1;
        font-size: 0.84rem;
        color: var(--text-dark);
        line-height: 1.55;
    }
    
    /* ═══ UPS Gateway Box ═══ */
    .ups-box {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 2px solid var(--danger);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
    }
    
    .ups-icon {
        width: 40px;
        height: 40px;
        border: 3.5px solid var(--danger);
        border-radius: 50%;
        margin-right: 16px;
        flex-shrink: 0;
    }
    
    .ups-content {
        font-size: 0.9rem;
        color: var(--text-dark);
    }
    
    .ups-content strong { color: #B91C1C; }
    .ups-codes { font-size: 0.82rem; color: var(--text-medium); margin-top: 4px; }
    
    /* ═══ Section Headers ═══ */
    .section-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--accent-blue);
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 3px solid var(--primary-light);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* ═══ Info Cards ═══ */
    .info-card {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 4px solid #F59E0B;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-top: 16px;
        font-size: 0.85rem;
        color: #92400E;
    }
    
    .source-card {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid #10B981;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin: 16px 0;
        font-size: 0.85rem;
        color: #065F46;
    }
    
    /* ═══ Footer ═══ */
    .exec-footer {
        background: var(--bg-white);
        text-align: center;
        color: var(--text-light);
        font-size: 0.8rem;
        padding: 28px;
        border-top: 1px solid var(--border-light);
        margin-top: 32px;
    }
    
    .exec-footer strong { color: var(--text-medium); }
    
    /* ═══ Upload Prompt ═══ */
    .upload-prompt {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 2px dashed #3B82F6;
        border-radius: 16px;
        padding: 48px;
        text-align: center;
        margin: 48px auto;
        max-width: 580px;
    }
    
    .upload-prompt h3 { color: #1D4ED8; margin-bottom: 12px; font-weight: 600; }
    .upload-prompt p { color: #2563EB; font-size: 0.95rem; }
    
    /* ═══ Hide Streamlit Elements ═══ */
    #MainMenu, footer, .stDeployButton { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    
    /* ═══ Responsive ═══ */
    @media (max-width: 768px) {
        .kpi-container { grid-template-columns: repeat(2, 1fr); }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            df_map = pd.read_excel(uploaded_file, sheet_name="Manufacturers")
            df_legend = pd.read_excel(uploaded_file, sheet_name="Legend")
            df_gateways = pd.read_excel(uploaded_file, sheet_name="UPS_Gateways")
        else:
            path = Path(__file__).parent / "nm_manufacturers_data.xlsx"
            if path.exists():
                df_map = pd.read_excel(path, sheet_name="Manufacturers")
                df_legend = pd.read_excel(path, sheet_name="Legend")
                df_gateways = pd.read_excel(path, sheet_name="UPS_Gateways")
            else:
                return None, None, None
        return df_map, df_legend, df_gateways
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

# ═══════════════════════════════════════════════════════════════════════════
# MAP CREATION
# ═══════════════════════════════════════════════════════════════════════════
def create_map(df_map, df_gateways):
    m = folium.Map(
        location=[50.0, 10.0],
        zoom_start=4,
        tiles='cartodbpositron',
        control_scale=False
    )
    
    # UPS Gateway red circles (large, matching PPT)
    for _, row in df_gateways.iterrows():
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=130000,
            color='#DC2626',
            weight=3.5,
            fill=False,
            opacity=0.9,
            tooltip=f"<b style='color:#DC2626'>UPS Gateway: {row['Code']}</b><br>{row['City']}, {row['Country']}<br><i>Status: {row['Status']}</i>"
        ).add_to(m)
    
    # Site markers (blue numbered boxes)
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f'''<div style="
                    background: linear-gradient(135deg, #00B0F0 0%, #0090C8 100%);
                    color: white;
                    font-weight: 700;
                    font-size: 12px;
                    font-family: 'Inter', Arial, sans-serif;
                    width: 30px;
                    height: 26px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 2px solid #007AAD;
                    border-radius: 5px;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                    transform: translate(-15px, -13px);
                ">{row["ID"]}</div>''',
                icon_size=(30, 26)
            ),
            tooltip=f"<b>Site {row['ID']}</b><br>{row['Country']}"
        ).add_to(m)
    
    return m

# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════
def main():
    # Executive Header
    st.markdown('''
    <div class="exec-header">
        <div class="logo-container">
            <svg viewBox="0 0 100 100" width="55" height="55">
                <polygon points="50,5 95,30 95,75 50,95 5,75 5,30" fill="#28B463" opacity="0.95"/>
                <polygon points="50,15 85,35 85,70 50,85 15,70 15,35" fill="#1A6B52"/>
                <polygon points="50,25 75,40 75,65 50,75 25,65 25,40" fill="#22A06B"/>
            </svg>
        </div>
        <div class="header-content">
            <h1>NM Origins and Manufacturers</h1>
            <div class="tagline">Advanced Therapies Nuclear Medicine Manufacturing & UPS Origin Locations • EMEA</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Data Source Expander
    with st.expander("📂 Data Source & Information", expanded=False):
        uploaded_file = st.file_uploader("Upload nm_manufacturers_data.xlsx", type=["xlsx"])
        st.markdown('''
        <div class="source-card">
            <strong>📊 Data Source:</strong> All facility names, isotopes, and half-life information 
            is extracted <u>directly from your PowerPoint presentation</u> (Slide 2 - "NM Origins and Manufacturers"). 
            The Excel file preserves this exact data for dashboard visualization.
        </div>
        ''', unsafe_allow_html=True)
    
    # Load Data
    df_map, df_legend, df_gateways = load_data(uploaded_file)
    
    if df_map is None:
        st.markdown('''
        <div class="upload-prompt">
            <h3>📂 Upload Required</h3>
            <p>Please upload <code>nm_manufacturers_data.xlsx</code> using the Data Source section above</p>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Main Layout
    col_map, col_legend = st.columns([2.4, 1])
    
    with col_map:
        # KPI Cards
        st.markdown('''
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-number">18</div>
                <div class="kpi-label">Production Sites</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-number">14</div>
                <div class="kpi-label">Countries</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-number">4</div>
                <div class="kpi-label">UPS Gateways</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-number">12+</div>
                <div class="kpi-label">Isotope Types</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Interactive Map
        m = create_map(df_map, df_gateways)
        st_folium(m, width=None, height=510, returned_objects=[])
    
    with col_legend:
        # UPS Gateway Legend
        st.markdown('''
        <div class="ups-box">
            <div class="ups-icon"></div>
            <div class="ups-content">
                <strong>UPS Origin Gateways</strong>
                <div class="ups-codes">Current & Proposed: CGN, VIE, BER, BCN</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Sites Legend Panel
        legend_html = '''
        <div class="legend-wrapper">
            <div class="legend-title">
                <span>📍</span> Manufacturing Sites & Isotopes
            </div>
            <div class="legend-body">
        '''
        
        for _, row in df_legend.iterrows():
            desc = str(row['Description'])
            legend_html += f'''
            <div class="legend-entry">
                <div class="site-num">{row["ID"]}</div>
                <div class="site-desc">{desc}</div>
            </div>'''
        
        legend_html += '</div></div>'
        st.markdown(legend_html, unsafe_allow_html=True)
    
    # Details Section
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="section-header"><span>📍</span> Sites by Country</div>', unsafe_allow_html=True)
        country_df = df_map.groupby('Country').agg({
            'ID': lambda x: ', '.join(map(str, sorted(x.unique())))
        }).reset_index()
        country_df.columns = ['Country', 'Site IDs']
        st.dataframe(country_df, use_container_width=True, hide_index=True, height=230)
    
    with c2:
        st.markdown('<div class="section-header"><span>✈️</span> UPS Origin Gateways</div>', unsafe_allow_html=True)
        st.dataframe(
            df_gateways[['Code', 'City', 'Country', 'Status']], 
            use_container_width=True, 
            hide_index=True, 
            height=165
        )
        st.markdown('''
        <div class="info-card">
            <strong>Gateway Network:</strong> CGN (Cologne) • VIE (Vienna) • BER (Berlin) • BCN (Barcelona)
        </div>
        ''', unsafe_allow_html=True)
    
    # Executive Footer
    st.markdown('''
    <div class="exec-footer">
        <strong>Nuclear Medicine EMEA Manufacturing Dashboard</strong><br>
        Advanced Therapies • UPS Origin Locations • Executive Summary<br>
        <span style="margin-top: 8px; display: inline-block; color: #9CA3AF;">CONFIDENTIAL</span>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
