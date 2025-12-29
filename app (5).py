"""
Nuclear Medicine EMEA Manufacturing & Origins Dashboard
Professional MBB-style executive dashboard - matches PowerPoint exactly
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path

st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional MBB Styling
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    
    .main-header {
        background: linear-gradient(135deg, #1a5f4a 0%, #2d8f6f 40%, #1B4F72 100%);
        padding: 1.2rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        display: flex;
        align-items: center;
        box-shadow: 0 3px 12px rgba(0,0,0,0.15);
    }
    
    .header-title {
        color: white;
        font-family: 'Verdana', 'Arial', sans-serif;
        font-weight: 600;
        font-size: 1.7rem;
        margin: 0 0 0 15px;
    }
    
    .ups-box {
        background: #FFF5F5;
        border: 2px solid #FF6B6B;
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    
    .ups-circle {
        width: 30px;
        height: 30px;
        border: 3px solid #FF0000;
        border-radius: 50%;
        margin-right: 12px;
        flex-shrink: 0;
    }
    
    .legend-container {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        max-height: 520px;
        overflow-y: auto;
    }
    
    .legend-item {
        display: flex;
        align-items: flex-start;
        padding: 10px 12px;
        border-bottom: 1px solid #F0F0F0;
        font-size: 0.82rem;
        line-height: 1.45;
    }
    
    .legend-item:nth-child(even) { background: #FAFAFA; }
    .legend-item:last-child { border-bottom: none; }
    
    .legend-num {
        background: #00B0F0;
        color: white;
        font-weight: bold;
        min-width: 28px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 3px;
        margin-right: 12px;
        font-size: 0.8rem;
        flex-shrink: 0;
        border: 1.5px solid #0088BB;
    }
    
    .legend-text { flex: 1; color: #333; }
    
    .metric-row { display: flex; gap: 12px; margin-bottom: 15px; }
    
    .metric-box {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        flex: 1;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    
    .metric-val { font-size: 2rem; font-weight: 700; color: #1B4F72; }
    .metric-lbl { font-size: 0.72rem; color: #7F8C8D; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
    
    .section-hdr {
        font-size: 0.9rem;
        font-weight: 600;
        color: #1B4F72;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid #28B463;
    }
    
    .info-note {
        background: #FFF9E6;
        border-left: 4px solid #F39C12;
        padding: 12px 15px;
        margin-top: 15px;
        font-size: 0.82rem;
        border-radius: 0 6px 6px 0;
    }
    
    .footer-bar {
        text-align: center;
        color: #95A5A6;
        font-size: 0.75rem;
        padding: 20px;
        border-top: 1px solid #EEE;
        margin-top: 25px;
    }
    
    .upload-box {
        background: #F0F7FF;
        border: 2px dashed #3498DB;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        margin: 30px auto;
        max-width: 500px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

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
        st.error(f"Error: {e}")
        return None, None, None

def create_map(df_map, df_gateways):
    m = folium.Map(
        location=[50.0, 10.0],
        zoom_start=4,
        tiles='cartodbpositron',
        control_scale=False
    )
    
    # UPS Gateway red circles
    for _, row in df_gateways.iterrows():
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=80000,
            color='#FF0000',
            weight=3,
            fill=False,
            opacity=0.85,
            tooltip=f"UPS Gateway: {row['Code']} ({row['City']})"
        ).add_to(m)
    
    # Numbered blue markers
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f'''<div style="
                    background: #00B0F0;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    font-family: Arial;
                    width: 24px;
                    height: 22px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 2px solid #0088BB;
                    border-radius: 3px;
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    transform: translate(-12px, -11px);
                ">{row["ID"]}</div>''',
                icon_size=(24, 22)
            ),
            tooltip=f"Site {row['ID']}: {row['Country']}"
        ).add_to(m)
    
    return m

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
    
    with st.expander("📂 Data Source", expanded=False):
        uploaded_file = st.file_uploader("Upload nm_manufacturers_data.xlsx", type=["xlsx"])
    
    df_map, df_legend, df_gateways = load_data(uploaded_file)
    
    if df_map is None:
        st.markdown('''
        <div class="upload-box">
            <h3 style="color: #1B4F72;">📂 Please upload the data file</h3>
            <p style="color: #666;">Upload <code>nm_manufacturers_data.xlsx</code> above</p>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    col_map, col_legend = st.columns([2.2, 1])
    
    with col_map:
        st.markdown('''
        <div class="metric-row">
            <div class="metric-box"><div class="metric-val">18</div><div class="metric-lbl">Production Sites</div></div>
            <div class="metric-box"><div class="metric-val">14</div><div class="metric-lbl">Countries</div></div>
            <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">UPS Gateways</div></div>
            <div class="metric-box"><div class="metric-val">12+</div><div class="metric-lbl">Isotopes</div></div>
        </div>
        ''', unsafe_allow_html=True)
        
        m = create_map(df_map, df_gateways)
        st_folium(m, width=None, height=530, returned_objects=[])
    
    with col_legend:
        # UPS Gateway legend box
        st.markdown('''
        <div class="ups-box">
            <div class="ups-circle"></div>
            <div style="font-size: 0.85rem;">
                <b>UPS Origin Gateways</b><br>
                <span style="font-size: 0.75rem; color: #666;">(Current and proposed – CGN, VIE, BER, BCN)</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Build legend from data
        legend_html = '<div class="legend-container">'
        for _, row in df_legend.iterrows():
            desc = str(row['Description']).replace('\n', '<br>')
            legend_html += f'''
            <div class="legend-item">
                <div class="legend-num">{row["ID"]}</div>
                <div class="legend-text">{desc}</div>
            </div>'''
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<p class="section-hdr">📍 Sites by Country</p>', unsafe_allow_html=True)
        country_summary = df_map.groupby('Country').agg({'ID': lambda x: ', '.join(map(str, sorted(x.unique())))}).reset_index()
        country_summary.columns = ['Country', 'Site IDs']
        st.dataframe(country_summary, use_container_width=True, hide_index=True, height=220)
    
    with c2:
        st.markdown('<p class="section-hdr">✈️ UPS Origin Gateways</p>', unsafe_allow_html=True)
        st.dataframe(df_gateways[['Code', 'City', 'Country', 'Status']], use_container_width=True, hide_index=True, height=150)
        st.markdown('''
        <div class="info-note">
            <b>Gateway Codes:</b> CGN (Cologne) • VIE (Vienna) • BER (Berlin) • BCN (Barcelona)
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="footer-bar">
        Advanced Therapies Nuclear Medicine Manufacturing and UPS Origin Locations • EMEA Region • CONFIDENTIAL
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
