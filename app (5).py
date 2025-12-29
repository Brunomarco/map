"""
Nuclear Medicine EMEA Manufacturing & Origins Dashboard
Professional executive dashboard for nuclear medicine supply chain visualization
"""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS - MBB PROFESSIONAL STYLE
# =============================================================================
st.markdown("""
<style>
    /* Main background and fonts */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1B4F72 0%, #2E86AB 50%, #28B463 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-family: 'Verdana', 'Segoe UI', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1B4F72;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #1B4F72;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card .value {
        color: #2C3E50;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Legend styling */
    .legend-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        padding: 0.4rem 0;
        font-size: 0.85rem;
    }
    
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
        border: 2px solid white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E5E5E5;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        color: #1B4F72;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.85rem !important;
    }
    
    /* Section headers */
    .section-header {
        color: #1B4F72;
        font-size: 1.1rem;
        font-weight: 600;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #28B463;
        margin-bottom: 1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #E8F6F3 0%, #EBF5FB 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #28B463;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #7F8C8D;
        font-size: 0.8rem;
        padding: 1rem;
        border-top: 1px solid #E5E5E5;
        margin-top: 2rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING FUNCTION
# =============================================================================
@st.cache_data
def load_data(uploaded_file=None):
    """Load manufacturer data from Excel file"""
    if uploaded_file is not None:
        df_manufacturers = pd.read_excel(uploaded_file, sheet_name="Manufacturers")
        df_gateways = pd.read_excel(uploaded_file, sheet_name="UPS_Gateways")
        df_isotopes = pd.read_excel(uploaded_file, sheet_name="Isotopes_Reference")
    else:
        # Try to load from default location
        default_path = Path(__file__).parent / "nm_manufacturers_data.xlsx"
        if default_path.exists():
            df_manufacturers = pd.read_excel(default_path, sheet_name="Manufacturers")
            df_gateways = pd.read_excel(default_path, sheet_name="UPS_Gateways")
            df_isotopes = pd.read_excel(default_path, sheet_name="Isotopes_Reference")
        else:
            st.error("Please upload the data file (nm_manufacturers_data.xlsx)")
            return None, None, None
    
    return df_manufacturers, df_gateways, df_isotopes

# =============================================================================
# MAP CREATION FUNCTION
# =============================================================================
def create_map(df_manufacturers, df_gateways, selected_countries, selected_types, selected_isotopes):
    """Create interactive Folium map with markers"""
    
    # Filter data based on selections
    df_filtered = df_manufacturers.copy()
    
    if selected_countries and "All" not in selected_countries:
        df_filtered = df_filtered[df_filtered["Country"].isin(selected_countries)]
    
    if selected_types and "All" not in selected_types:
        df_filtered = df_filtered[df_filtered["Facility Type"].isin(selected_types)]
    
    if selected_isotopes and "All" not in selected_isotopes:
        # Filter by isotopes (check if any selected isotope is in the Isotopes column)
        mask = df_filtered["Isotopes"].apply(
            lambda x: any(iso in str(x) for iso in selected_isotopes)
        )
        df_filtered = df_filtered[mask]
    
    # Create base map centered on Europe
    m = folium.Map(
        location=[50.0, 10.0],
        zoom_start=4,
        tiles=None,
        control_scale=True
    )
    
    # Add clean tile layer
    folium.TileLayer(
        tiles='cartodbpositron',
        name='Light Map',
        control=False
    ).add_to(m)
    
    # Color mapping for facility types
    type_colors = {
        "Research Reactor": "#E74C3C",           # Red
        "Radiopharmaceutical Producer": "#3498DB", # Blue
        "Therapeutic Producer": "#9B59B6",        # Purple
        "PET Producer": "#F39C12",                # Orange
        "Alpha Therapy Producer": "#C0392B",      # Dark Red
        "Cyclotron": "#27AE60",                   # Green
        "Generator Producer": "#1ABC9C",          # Teal
        "Research Institute": "#E67E22",          # Dark Orange
        "Accelerator-based": "#16A085"            # Dark Teal
    }
    
    # Add manufacturer markers
    for idx, row in df_filtered.iterrows():
        facility_type = row["Facility Type"]
        color = type_colors.get(facility_type, "#34495E")
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; width: 280px;">
            <div style="background: linear-gradient(135deg, #1B4F72, #2E86AB); color: white; 
                        padding: 10px; border-radius: 8px 8px 0 0; margin: -13px -20px 10px -20px;">
                <h4 style="margin: 0; font-size: 14px;">{row['Facility Name']}</h4>
                <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.9;">
                    <b>ID {row['ID']}</b> • {row['Country']}
                </p>
            </div>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                <tr>
                    <td style="padding: 4px 0; color: #7F8C8D;"><b>Location</b></td>
                    <td style="padding: 4px 0;">{row['City/Region']}, {row['Country']}</td>
                </tr>
                <tr style="background: #F8F9FA;">
                    <td style="padding: 4px 0; color: #7F8C8D;"><b>Type</b></td>
                    <td style="padding: 4px 0;">{row['Facility Type']}</td>
                </tr>
                <tr>
                    <td style="padding: 4px 0; color: #7F8C8D;"><b>Isotopes</b></td>
                    <td style="padding: 4px 0; color: #E74C3C; font-weight: 600;">{row['Isotopes']}</td>
                </tr>
                <tr style="background: #F8F9FA;">
                    <td style="padding: 4px 0; color: #7F8C8D;"><b>Half-Lives</b></td>
                    <td style="padding: 4px 0;">{row['Half-Lives']}</td>
                </tr>
            </table>
            <p style="font-size: 10px; color: #95A5A6; margin-top: 10px; font-style: italic;">
                {row['Notes'] if pd.notna(row['Notes']) else ''}
            </p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=10,
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"<b>{row['Facility Name']}</b><br>{row['Country']}",
            color="#FFFFFF",
            weight=2,
            fill=True,
            fillColor=color,
            fillOpacity=0.85
        ).add_to(m)
        
        # Add ID label
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background: #00B0F0;
                    color: white;
                    font-weight: bold;
                    font-size: 10px;
                    width: 18px;
                    height: 18px;
                    border-radius: 3px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 1px solid white;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
                    transform: translate(-9px, -25px);
                ">{row['ID']}</div>
                """,
                icon_size=(18, 18)
            )
        ).add_to(m)
    
    # Add UPS Gateway markers (red circles as in original)
    for idx, row in df_gateways.iterrows():
        gateway_color = "#FF0000" if row["Status"] == "Current" else "#FF6B6B"
        
        popup_html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; width: 200px;">
            <div style="background: #FF0000; color: white; padding: 8px; 
                        border-radius: 8px 8px 0 0; margin: -13px -20px 10px -20px;">
                <h4 style="margin: 0; font-size: 13px;">UPS Gateway: {row['Code']}</h4>
            </div>
            <p style="margin: 5px 0; font-size: 12px;">
                <b>City:</b> {row['City']}<br>
                <b>Country:</b> {row['Country']}<br>
                <b>Status:</b> <span style="color: {'#27AE60' if row['Status'] == 'Current' else '#F39C12'};">
                    {row['Status']}</span>
            </p>
        </div>
        """
        
        # Large red circle (like in original PowerPoint)
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=40000,  # 40km radius
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"<b>UPS Gateway: {row['Code']}</b><br>{row['City']} ({row['Status']})",
            color=gateway_color,
            weight=3,
            fill=False,
            opacity=0.8
        ).add_to(m)
    
    return m, df_filtered

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔬 NM Origins and Manufacturers</h1>
        <p>Advanced Therapies Nuclear Medicine Manufacturing and UPS Origin Locations • EMEA Region</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📂 Data Source")
        uploaded_file = st.file_uploader(
            "Upload Excel data file",
            type=["xlsx"],
            help="Upload the nm_manufacturers_data.xlsx file"
        )
        
        # Load data
        df_manufacturers, df_gateways, df_isotopes = load_data(uploaded_file)
        
        if df_manufacturers is None:
            st.warning("⚠️ Please upload the data file to continue")
            st.markdown("""
            **Expected file:** `nm_manufacturers_data.xlsx`
            
            The file should contain sheets:
            - Manufacturers
            - UPS_Gateways
            - Isotopes_Reference
            """)
            return
        
        st.success(f"✅ Loaded {len(df_manufacturers)} facilities")
        
        st.markdown("---")
        st.markdown("### 🎛️ Filters")
        
        # Country filter
        countries = ["All"] + sorted(df_manufacturers["Country"].unique().tolist())
        selected_countries = st.multiselect(
            "Country",
            options=countries,
            default=["All"],
            help="Filter facilities by country"
        )
        
        # Facility type filter
        types = ["All"] + sorted(df_manufacturers["Facility Type"].unique().tolist())
        selected_types = st.multiselect(
            "Facility Type",
            options=types,
            default=["All"],
            help="Filter by facility type"
        )
        
        # Isotope filter
        all_isotopes = set()
        for isotopes in df_manufacturers["Isotopes"].dropna():
            for iso in str(isotopes).replace(";", ",").split(","):
                iso_clean = iso.strip().split()[0]  # Get just the isotope name
                if iso_clean and len(iso_clean) > 1:
                    all_isotopes.add(iso_clean)
        
        isotopes_list = ["All"] + sorted(list(all_isotopes))
        selected_isotopes = st.multiselect(
            "Isotope",
            options=isotopes_list,
            default=["All"],
            help="Filter by isotope produced"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Legend")
        
        # Facility type legend
        st.markdown("**Facility Types**")
        type_colors = {
            "Research Reactor": "#E74C3C",
            "Radiopharmaceutical Producer": "#3498DB",
            "Therapeutic Producer": "#9B59B6",
            "PET Producer": "#F39C12",
            "Alpha Therapy Producer": "#C0392B",
            "Cyclotron": "#27AE60",
            "Generator Producer": "#1ABC9C",
            "Research Institute": "#E67E22",
            "Accelerator-based": "#16A085"
        }
        
        for ftype, color in type_colors.items():
            st.markdown(f"""
            <div class="legend-item">
                <div class="legend-dot" style="background-color: {color};"></div>
                <span>{ftype}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**UPS Gateways**")
        st.markdown("""
        <div class="legend-item">
            <div style="width: 20px; height: 20px; border: 3px solid #FF0000; 
                        border-radius: 50%; margin-right: 10px;"></div>
            <span>UPS Origin Gateway</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Facilities</h3>
            <div class="value">{len(df_manufacturers)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Countries</h3>
            <div class="value">{df_manufacturers['Country'].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>UPS Gateways</h3>
            <div class="value">{len(df_gateways)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        unique_isotopes = set()
        for isotopes in df_manufacturers["Isotopes"].dropna():
            for iso in str(isotopes).replace(";", ",").split(","):
                iso_clean = iso.strip().split()[0]
                if iso_clean and len(iso_clean) > 1:
                    unique_isotopes.add(iso_clean)
        st.markdown(f"""
        <div class="metric-card">
            <h3>Isotope Types</h3>
            <div class="value">{len(unique_isotopes)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Map section
    st.markdown('<p class="section-header">🗺️ Interactive Map - Nuclear Medicine Manufacturing Sites</p>', unsafe_allow_html=True)
    
    # Create and display map
    m, df_filtered = create_map(
        df_manufacturers, df_gateways,
        selected_countries, selected_types, selected_isotopes
    )
    
    st.markdown(f"""
    <div class="info-box">
        <b>Currently showing:</b> {len(df_filtered)} facilities | 
        <b>UPS Gateways:</b> CGN (Cologne), VIE (Vienna), BER (Berlin), BCN (Barcelona)
    </div>
    """, unsafe_allow_html=True)
    
    # Display map
    st_folium(m, width=None, height=550, returned_objects=[])
    
    # Data tables section
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown('<p class="section-header">📋 Facility Details</p>', unsafe_allow_html=True)
        
        # Display filtered data
        display_df = df_filtered[["ID", "Facility Name", "Country", "City/Region", 
                                   "Isotopes", "Half-Lives", "Facility Type"]].copy()
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    with col_right:
        st.markdown('<p class="section-header">📊 Distribution by Country</p>', unsafe_allow_html=True)
        
        # Country distribution chart
        country_counts = df_filtered["Country"].value_counts()
        
        fig = go.Figure(go.Bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation='h',
            marker_color='#1B4F72',
            text=country_counts.values,
            textposition='outside'
        ))
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=20, t=10, b=0),
            xaxis_title="Number of Facilities",
            yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Isotopes reference section
    with st.expander("📖 Isotope Reference Guide", expanded=False):
        st.markdown('<p class="section-header">Medical Isotopes Reference</p>', unsafe_allow_html=True)
        
        col_iso1, col_iso2 = st.columns(2)
        
        with col_iso1:
            st.markdown("**Diagnostic Isotopes**")
            diagnostic_iso = df_isotopes[df_isotopes["Primary Use"].str.contains("Diagnostic|PET", na=False)]
            st.dataframe(diagnostic_iso, use_container_width=True, hide_index=True)
        
        with col_iso2:
            st.markdown("**Therapeutic Isotopes**")
            therapeutic_iso = df_isotopes[df_isotopes["Primary Use"].str.contains("Therapeutic|Alpha|Pain", na=False)]
            st.dataframe(therapeutic_iso, use_container_width=True, hide_index=True)
    
    # UPS Gateways section
    with st.expander("✈️ UPS Origin Gateways", expanded=False):
        st.markdown('<p class="section-header">UPS Origin Gateway Locations (Current and Proposed)</p>', unsafe_allow_html=True)
        
        st.dataframe(df_gateways, use_container_width=True, hide_index=True)
        
        st.markdown("""
        <div class="info-box">
            <b>Gateway Codes:</b><br>
            • <b>CGN</b> - Cologne, Germany (Current)<br>
            • <b>VIE</b> - Vienna, Austria (Proposed)<br>
            • <b>BER</b> - Berlin, Germany (Proposed)<br>
            • <b>BCN</b> - Barcelona, Spain (Proposed)
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        Nuclear Medicine EMEA Manufacturing Dashboard | Data visualization for executive review
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
