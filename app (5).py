"""
Nuclear Medicine EMEA Manufacturing Dashboard
Executive Presentation | MBB Professional Standard
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path

st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stApp { background: #F8FAFB; }
    
    .exec-header {
        background: linear-gradient(135deg, #0D3B2E 0%, #1A6B52 50%, #1B4F72 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
    }
    
    .exec-header h1 {
        color: white;
        font-weight: 600;
        font-size: 1.8rem;
        margin: 0 0 0 20px;
    }
    
    .exec-header p {
        color: rgba(255,255,255,0.85);
        font-size: 0.88rem;
        margin: 5px 0 0 20px;
    }
    
    .kpi-row { display: flex; gap: 15px; margin-bottom: 20px; }
    
    .kpi-box {
        background: white;
        border-radius: 12px;
        padding: 18px;
        flex: 1;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #E5E8EB;
    }
    
    .kpi-val { font-size: 2.5rem; font-weight: 700; color: #1B4F72; }
    .kpi-lbl { font-size: 0.7rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 6px; }
    
    .section-hdr {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1B4F72;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 3px solid #28B463;
    }
    
    .info-box {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 12px 15px;
        margin-top: 12px;
        font-size: 0.85rem;
        border-radius: 0 8px 8px 0;
    }
    
    .footer-bar {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.78rem;
        padding: 25px;
        border-top: 1px solid #E5E8EB;
        margin-top: 30px;
        background: white;
    }
    
    #MainMenu, footer, .stDeployButton { display: none !important; }
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
            path = Path(__file__).parent / "nm_manufacturers_data.xlsx"
            if path.exists():
                df_map = pd.read_excel(path, sheet_name="Manufacturers")
                df_legend = pd.read_excel(path, sheet_name="Legend")
                df_gateways = pd.read_excel(path, sheet_name="UPS_Gateways")
            else:
                return None, None, None
        return df_map, df_legend, df_gateways
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None, None

def create_map(df_map, df_gateways):
    m = folium.Map(location=[50.0, 10.0], zoom_start=4, tiles='cartodbpositron')
    
    for _, row in df_gateways.iterrows():
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=130000,
            color='#DC2626',
            weight=3.5,
            fill=False,
            opacity=0.9,
            tooltip=f"UPS Gateway: {row['Code']} - {row['City']}"
        ).add_to(m)
    
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f'<div style="background:linear-gradient(135deg,#00B0F0,#0090C8);color:white;font-weight:700;font-size:12px;width:28px;height:24px;display:flex;align-items:center;justify-content:center;border:2px solid #007AAD;border-radius:4px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);transform:translate(-14px,-12px);">{row["ID"]}</div>',
                icon_size=(28, 24)
            ),
            tooltip=f"Site {row['ID']}: {row['Country']}"
        ).add_to(m)
    
    return m

def main():
    # Header
    st.markdown('''
    <div class="exec-header">
        <svg width="50" height="50" viewBox="0 0 100 100">
            <polygon points="50,5 95,30 95,75 50,95 5,75 5,30" fill="#28B463" opacity="0.95"/>
            <polygon points="50,15 85,35 85,70 50,85 15,70 15,35" fill="#1A6B52"/>
            <polygon points="50,25 75,40 75,65 50,75 25,65 25,40" fill="#22A06B"/>
        </svg>
        <div>
            <h1>NM Origins and Manufacturers</h1>
            <p>Advanced Therapies Nuclear Medicine Manufacturing & UPS Origin Locations • EMEA</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    with st.expander("📂 Data Source", expanded=False):
        uploaded_file = st.file_uploader("Upload nm_manufacturers_data.xlsx", type=["xlsx"])
        st.info("📊 **Data Source:** All isotope information is extracted directly from your PowerPoint Slide 2.")
    
    df_map, df_legend, df_gateways = load_data(uploaded_file)
    
    if df_map is None:
        st.warning("⬆️ Please upload **nm_manufacturers_data.xlsx** using the Data Source section above.")
        return
    
    col_map, col_legend = st.columns([2.3, 1])
    
    with col_map:
        st.markdown('''
        <div class="kpi-row">
            <div class="kpi-box"><div class="kpi-val">18</div><div class="kpi-lbl">Production Sites</div></div>
            <div class="kpi-box"><div class="kpi-val">14</div><div class="kpi-lbl">Countries</div></div>
            <div class="kpi-box"><div class="kpi-val">4</div><div class="kpi-lbl">UPS Gateways</div></div>
            <div class="kpi-box"><div class="kpi-val">12+</div><div class="kpi-lbl">Isotope Types</div></div>
        </div>
        ''', unsafe_allow_html=True)
        
        m = create_map(df_map, df_gateways)
        st_folium(m, width=None, height=500, returned_objects=[])
    
    with col_legend:
        # UPS Gateway indicator using Streamlit native
        st.markdown("#### 🔴 UPS Origin Gateways")
        st.caption("Current & Proposed: CGN, VIE, BER, BCN")
        
        st.markdown("---")
        
        # Legend using Streamlit native components
        st.markdown("#### 📍 Manufacturing Sites")
        
        # Create scrollable container for legend
        legend_container = st.container()
        with legend_container:
            for _, row in df_legend.iterrows():
                site_id = row['ID']
                desc = row['Description']
                
                # Use columns for better layout
                c1, c2 = st.columns([0.12, 0.88])
                with c1:
                    st.markdown(f"<div style='background:linear-gradient(135deg,#00B0F0,#0090C8);color:white;font-weight:700;font-size:13px;width:32px;height:28px;display:flex;align-items:center;justify-content:center;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.2);'>{site_id}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='font-size:0.82rem;line-height:1.4;'>{desc}</span>", unsafe_allow_html=True)
                
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<p class="section-hdr">📍 Sites by Country</p>', unsafe_allow_html=True)
        country_df = df_map.groupby('Country').agg({'ID': lambda x: ', '.join(map(str, sorted(x.unique())))}).reset_index()
        country_df.columns = ['Country', 'Site IDs']
        st.dataframe(country_df, use_container_width=True, hide_index=True, height=220)
    
    with c2:
        st.markdown('<p class="section-hdr">✈️ UPS Origin Gateways</p>', unsafe_allow_html=True)
        st.dataframe(df_gateways[['Code', 'City', 'Country', 'Status']], use_container_width=True, hide_index=True, height=160)
        st.markdown('<div class="info-box"><b>Gateways:</b> CGN (Cologne) • VIE (Vienna) • BER (Berlin) • BCN (Barcelona)</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-bar"><b>Nuclear Medicine EMEA Manufacturing Dashboard</b><br>Advanced Therapies • UPS Origin Locations • CONFIDENTIAL</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
