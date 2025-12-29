"""
Nuclear Medicine EMEA Manufacturing & Origins Dashboard
Professional MBB-style executive dashboard
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# PROFESSIONAL MBB STYLING
# =============================================================================
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a5f4a 0%, #2d8f6f 40%, #1B4F72 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-family: 'Verdana', 'Arial', sans-serif;
        font-weight: 600;
        font-size: 1.6rem;
        margin: 0;
        margin-left: 15px;
    }
    
    .legend-row {
        display: flex;
        align-items: flex-start;
        padding: 8px 12px;
        border-bottom: 1px solid #EEEEEE;
        font-size: 0.78rem;
        line-height: 1.4;
    }
    
    .legend-row:nth-child(even) {
        background: #F8F9FA;
    }
    
    .legend-id {
        background: #00B0F0;
        color: white;
        font-weight: bold;
        min-width: 26px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 3px;
        margin-right: 12px;
        font-size: 0.75rem;
        flex-shrink: 0;
        border: 1px solid #0088CC;
    }
    
    .legend-content {
        flex: 1;
        color: #2C3E50;
    }
    
    .legend-facility {
        font-weight: 600;
        color: #1B4F72;
    }
    
    .legend-isotope {
        color: #C0392B;
        font-size: 0.72rem;
    }
    
    .ups-legend {
        display: flex;
        align-items: center;
        padding: 12px 15px;
        background: #FFF5F5;
        border: 2px solid #FF6B6B;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    
    .ups-circle {
        width: 32px;
        height: 32px;
        border: 3px solid #FF0000;
        border-radius: 50%;
        margin-right: 15px;
        flex-shrink: 0;
    }
    
    .ups-text {
        font-size: 0.8rem;
        color: #333;
        line-height: 1.4;
    }
    
    .metric-row {
        display: flex;
        gap: 12px;
        margin-bottom: 15px;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px 20px;
        flex: 1;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1B4F72;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #7F8C8D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 3px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .legend-scroll {
        max-height: 480px;
        overflow-y: auto;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        background: white;
    }
    
    .section-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #1B4F72;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid #28B463;
    }
    
    .footer-text {
        text-align: center;
        color: #95A5A6;
        font-size: 0.75rem;
        padding: 20px;
        border-top: 1px solid #EEEEEE;
        margin-top: 25px;
    }
    
    .upload-section {
        background: #F0F7FF;
        border: 2px dashed #3498DB;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        margin: 30px auto;
        max-width: 500px;
    }
    
    .info-box {
        background: #FFF9E6;
        border-left: 4px solid #F39C12;
        padding: 12px 15px;
        margin-top: 15px;
        font-size: 0.8rem;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            df_map = pd.read_excel(uploaded_file, sheet_name="Manufacturers")
            df_legend = pd.read_excel(uploaded_file, sheet_name="Legend")
            df_gateways = pd.read_excel(uploaded_file, sheet_name="UPS_Gateways")
        else:
            default_path = Path(__file__).parent / "nm_manufacturers_data.xlsx"
            if default_path.exists():
                df_map = pd.read_excel(default_path, sheet_name="Manufacturers")
                df_legend = pd.read_excel(default_path, sheet_name="Legend")
                df_gateways = pd.read_excel(default_path, sheet_name="UPS_Gateways")
            else:
                return None, None, None
        return df_map, df_legend, df_gateways
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

# =============================================================================
# MAP CREATION
# =============================================================================
def create_map(df_map, df_gateways):
    m = folium.Map(
        location=[50.0, 10.0],
        zoom_start=4,
        tiles=None,
        control_scale=False
    )
    
    folium.TileLayer(
        tiles='cartodbpositron',
        name='Map',
        control=False,
        opacity=0.95
    ).add_to(m)
    
    # UPS Gateway circles (large red circles)
    for _, row in df_gateways.iterrows():
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=75000,
            color='#FF0000',
            weight=3,
            fill=False,
            opacity=0.85,
            tooltip=f"<b>UPS Gateway: {row['Code']}</b><br>{row['City']}, {row['Country']}<br>Status: {row['Status']}"
        ).add_to(m)
    
    # Manufacturer markers (blue numbered boxes)
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f'''
                <div style="
                    background: #00B0F0;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    font-family: Arial, sans-serif;
                    width: 24px;
                    height: 22px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 2px solid #0088CC;
                    border-radius: 3px;
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    transform: translate(-12px, -11px);
                ">{row['ID']}</div>
                ''',
                icon_size=(24, 22)
            ),
            tooltip=f"<b>Site {row['ID']}</b>: {row['Facility_Group']}<br>{row['Country']}"
        ).add_to(m)
    
    return m

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Header
    st.markdown('''
    <div class="main-header">
        <svg width="45" height="45" viewBox="0 0 100 100">
            <polygon points="50,5 95,30 95,75 50,95 5,75 5,30" fill="#28B463" opacity="0.9"/>
            <polygon points="50,15 85,35 85,70 50,85 15,70 15,35" fill="#1a5f4a"/>
            <polygon points="50,25 75,40 75,65 50,75 25,65 25,40" fill="#2d8f6f"/>
        </svg>
        <h1 class="header-title">NM Origins and Manufacturers</h1>
    </div>
    ''', unsafe_allow_html=True)
    
    # File upload
    with st.expander("📂 Data Source", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload nm_manufacturers_data.xlsx",
            type=["xlsx"],
            help="Upload the Excel data file to display the dashboard"
        )
    
    df_map, df_legend, df_gateways = load_data(uploaded_file)
    
    if df_map is None:
        st.markdown('''
        <div class="upload-section">
            <h3 style="color: #1B4F72;">📂 Please upload the data file</h3>
            <p style="color: #666;">Upload <code>nm_manufacturers_data.xlsx</code> using the Data Source section above</p>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Layout: Map (left) + Legend (right)
    col_map, col_legend = st.columns([2.2, 1])
    
    with col_map:
        st.markdown('''
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value">18</div>
                <div class="metric-label">Production Sites</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">14</div>
                <div class="metric-label">Countries</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">4</div>
                <div class="metric-label">UPS Gateways</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">12+</div>
                <div class="metric-label">Isotopes</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        m = create_map(df_map, df_gateways)
        st_folium(m, width=None, height=530, returned_objects=[])
    
    with col_legend:
        st.markdown('''
        <div class="ups-legend">
            <div class="ups-circle"></div>
            <div class="ups-text">
                <b>UPS Origin Gateways</b><br>
                <span style="font-size: 0.75rem;">(Current and proposed – CGN, VIE, BER, BCN)</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        legend_html = '<div class="legend-scroll">'
        for _, row in df_legend.iterrows():
            legend_html += f'''
            <div class="legend-row">
                <div class="legend-id">{row['ID']}</div>
                <div class="legend-content">
                    <span class="legend-facility">{row['Facilities']}</span><br>
                    <span class="legend-isotope">{row['Isotopes']}</span><br>
                    <span style="color: #666; font-size: 0.68rem;">{row['Half_Lives']}</span>
                </div>
            </div>
            '''
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)
    
    # Details section
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<p class="section-title">📍 Sites by Country</p>', unsafe_allow_html=True)
        country_summary = df_map.groupby('Country').agg({
            'ID': lambda x: ', '.join(map(str, sorted(x.unique())))
        }).reset_index()
        country_summary.columns = ['Country', 'Site IDs']
        st.dataframe(country_summary, use_container_width=True, hide_index=True, height=220)
    
    with c2:
        st.markdown('<p class="section-title">✈️ UPS Origin Gateways</p>', unsafe_allow_html=True)
        st.dataframe(df_gateways[['Code', 'City', 'Country', 'Status']], use_container_width=True, hide_index=True, height=150)
        st.markdown('''
        <div class="info-box">
            <b>Gateway Codes:</b> CGN (Cologne) • VIE (Vienna) • BER (Berlin) • BCN (Barcelona)
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="footer-text">
        Advanced Therapies Nuclear Medicine Manufacturing and UPS Origin Locations • EMEA Region • CONFIDENTIAL
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
