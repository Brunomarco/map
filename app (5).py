"""
Nuclear Medicine EMEA Manufacturing Dashboard
Executive Presentation | MBB Professional Standard
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, sans-serif; }
    .stApp { background: #F8FAFB; }
    
    .exec-header {
        background: linear-gradient(135deg, #0D3B2E 0%, #1A6B52 50%, #1B4F72 100%);
        padding: 1.2rem 2rem;
        margin: -1rem -1rem 1.2rem -1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
    }
    .exec-header h1 { color: white; font-weight: 600; font-size: 1.7rem; margin: 0 0 0 18px; }
    .exec-header p { color: rgba(255,255,255,0.85); font-size: 0.85rem; margin: 4px 0 0 18px; }
    
    .kpi-row { display: flex; gap: 12px; margin-bottom: 16px; }
    .kpi-box {
        background: white; border-radius: 10px; padding: 14px; flex: 1; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #E5E8EB;
    }
    .kpi-val { font-size: 2.2rem; font-weight: 700; color: #1B4F72; }
    .kpi-lbl { font-size: 0.68rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 4px; }
    
    .section-hdr {
        font-size: 0.9rem; font-weight: 600; color: #1B4F72;
        margin-bottom: 10px; padding-bottom: 6px; border-bottom: 2px solid #28B463;
    }
    .info-box {
        background: #FFFBEB; border-left: 3px solid #F59E0B;
        padding: 10px 12px; margin-top: 10px; font-size: 0.8rem; border-radius: 0 6px 6px 0;
    }
    .footer-bar {
        text-align: center; color: #9CA3AF; font-size: 0.75rem;
        padding: 20px; border-top: 1px solid #E5E8EB; margin-top: 24px; background: white;
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
            radius=120000, color='#DC2626', weight=3, fill=False, opacity=0.9,
            tooltip=f"UPS: {row['Code']} - {row['City']}"
        ).add_to(m)
    
    for _, row in df_map.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f'<div style="background:linear-gradient(135deg,#00B0F0,#0090C8);color:white;font-weight:700;font-size:11px;width:26px;height:22px;display:flex;align-items:center;justify-content:center;border:2px solid #007AAD;border-radius:4px;box-shadow:1px 1px 4px rgba(0,0,0,0.3);transform:translate(-13px,-11px);">{row["ID"]}</div>',
                icon_size=(26, 22)
            ),
            tooltip=f"Site {row['ID']}: {row['Country']}"
        ).add_to(m)
    
    return m

def create_legend_html(df_legend):
    """Create legend as standalone HTML component"""
    items = ""
    for _, row in df_legend.iterrows():
        items += f"""
        <div style="display:flex;align-items:flex-start;padding:5px 8px;border-bottom:1px solid #F0F0F0;gap:8px;">
            <div style="background:linear-gradient(135deg,#00B0F0,#0090C8);color:white;font-weight:700;min-width:26px;height:22px;display:flex;align-items:center;justify-content:center;border-radius:4px;font-size:12px;flex-shrink:0;">{row["ID"]}</div>
            <div style="font-size:11px;color:#374151;line-height:1.35;">{row["Description"]}</div>
        </div>"""
    
    html = f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; }}
        </style>
    </head>
    <body>
        <div style="background:#FEF2F2;border:2px solid #DC2626;border-radius:8px;padding:10px 12px;margin-bottom:12px;display:flex;align-items:center;gap:10px;">
            <div style="width:26px;height:26px;border:3px solid #DC2626;border-radius:50%;flex-shrink:0;"></div>
            <div style="font-size:12px;color:#1F2937;"><strong style="color:#B91C1C;">UPS Origin Gateways</strong><br><span style="font-size:11px;color:#6B7280;">CGN, VIE, BER, BCN</span></div>
        </div>
        <div style="font-weight:600;color:#1B4F72;font-size:13px;margin-bottom:8px;">📍 Manufacturing Sites</div>
        <div style="background:white;border:1px solid #E5E8EB;border-radius:8px;max-height:420px;overflow-y:auto;">
            {items}
        </div>
    </body>
    </html>
    """
    return html

def main():
    st.markdown('''
    <div class="exec-header">
        <svg width="45" height="45" viewBox="0 0 100 100">
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
        st.info("📊 All isotope data extracted from PowerPoint Slide 2")
    
    df_map, df_legend, df_gateways = load_data(uploaded_file)
    
    if df_map is None:
        st.warning("⬆️ Please upload **nm_manufacturers_data.xlsx**")
        return
    
    col_map, col_legend = st.columns([2.2, 1])
    
    with col_map:
        st.markdown('''
        <div class="kpi-row">
            <div class="kpi-box"><div class="kpi-val">18</div><div class="kpi-lbl">Production Sites</div></div>
            <div class="kpi-box"><div class="kpi-val">14</div><div class="kpi-lbl">Countries</div></div>
            <div class="kpi-box"><div class="kpi-val">4</div><div class="kpi-lbl">UPS Gateways</div></div>
            <div class="kpi-box"><div class="kpi-val">12+</div><div class="kpi-lbl">Isotopes</div></div>
        </div>
        ''', unsafe_allow_html=True)
        
        m = create_map(df_map, df_gateways)
        st_folium(m, width=None, height=480, returned_objects=[])
    
    with col_legend:
        # Use components.html for reliable rendering
        legend_html = create_legend_html(df_legend)
        components.html(legend_html, height=550, scrolling=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<p class="section-hdr">📍 Sites by Country</p>', unsafe_allow_html=True)
        country_df = df_map.groupby('Country').agg({'ID': lambda x: ', '.join(map(str, sorted(x.unique())))}).reset_index()
        country_df.columns = ['Country', 'Site IDs']
        st.dataframe(country_df, use_container_width=True, hide_index=True, height=200)
    
    with c2:
        st.markdown('<p class="section-hdr">✈️ UPS Origin Gateways</p>', unsafe_allow_html=True)
        st.dataframe(df_gateways[['Code', 'City', 'Country', 'Status']], use_container_width=True, hide_index=True, height=150)
        st.markdown('<div class="info-box"><b>Gateways:</b> CGN • VIE • BER • BCN</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-bar"><b>Nuclear Medicine EMEA Dashboard</b> • CONFIDENTIAL</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
