"""
Nuclear Medicine EMEA Manufacturing Dashboard v2
Executive Presentation | MBB Professional Standard
Enhanced with Isotope Serviceability Analysis
"""

import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
from pathlib import Path
import streamlit.components.v1 as components
import re

st.set_page_config(
    page_title="NM Origins & Manufacturers | EMEA",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Marken UPS Healthcare Logistics Color Palette
COLORS = {
    'marken_deep_green': '#0D3B2E',
    'marken_green': '#1A6B52',
    'marken_accent': '#28B463',
    'marken_blue': '#1B4F72',
    'ups_brown': '#351C15',
    'can_serve': '#22A06B',       # Green - can serve (≥6h half-life)
    'cannot_serve': '#DC2626',    # Red - cannot serve (<6h half-life)
    'partial_serve': '#F59E0B',   # Amber - mixed isotopes
    'gateway_red': '#DC2626',
}

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
    .kpi-val { font-size: 2rem; font-weight: 700; color: #1B4F72; }
    .kpi-lbl { font-size: 0.68rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 4px; }
    
    .section-hdr {
        font-size: 0.9rem; font-weight: 600; color: #1B4F72;
        margin-bottom: 10px; padding-bottom: 6px; border-bottom: 2px solid #28B463;
    }
    .info-box {
        background: #FFFBEB; border-left: 3px solid #F59E0B;
        padding: 10px 12px; margin-top: 10px; font-size: 0.8rem; border-radius: 0 6px 6px 0;
    }
    .serve-badge {
        display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600;
    }
    .can-serve { background: #D1FAE5; color: #065F46; }
    .cannot-serve { background: #FEE2E2; color: #991B1B; }
    .footer-bar {
        text-align: center; color: #9CA3AF; font-size: 0.75rem;
        padding: 20px; border-top: 1px solid #E5E8EB; margin-top: 24px; background: white;
    }
    
    #MainMenu, footer, .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Isotope half-life database (in hours for comparison)
ISOTOPE_HALFLIVES = {
    'Mo-99': 65.9,
    'Lu-177': 159.6,      # ~6.65 days
    'I-131': 192.0,       # 8 days
    'Ac-225': 237.6,      # ~9.9 days
    'Tc-99m': 6.0,
    'Tb-161': 166.8,      # 6.95 days
    'Ga-68': 1.13,        # 67.8 min
    'Y-90': 64.1,
    'F-18': 1.83,         # 109.7 min
    'Ho-166': 26.8,
    'Re-188': 17.0,
    'I-125': 1425.6,      # 59.4 days
    'Sm-153': 46.3,
    'Ra-223': 273.6,      # 11.4 days
}

SERVICE_THRESHOLD_HOURS = 6.0

def parse_isotopes_from_description(description):
    """Extract isotopes and their half-lives from description text.
    Prioritizes reference database for accuracy over potentially ambiguous parsed values."""
    isotopes = []
    found_isotopes = set()
    
    # Find all isotopes mentioned in the description
    all_isotope_names = list(dict.fromkeys(re.findall(r'([A-Z][a-z]?-\d+m?)', description)))
    
    # For known isotopes, always use reference database (more reliable than parsing)
    for isotope in all_isotope_names:
        if isotope in ISOTOPE_HALFLIVES:
            hours = ISOTOPE_HALFLIVES[isotope]
            if hours < 1:
                display = f"{hours*60:.1f} min"
            elif hours < 24:
                display = f"{hours:.1f} h"
            else:
                display = f"{hours/24:.1f} d"
            
            can_serve = hours >= SERVICE_THRESHOLD_HOURS
            isotopes.append({
                'name': isotope,
                'halflife_hours': round(hours, 2),
                'halflife_display': display,
                'can_serve': can_serve
            })
            found_isotopes.add(isotope)
        else:
            # For unknown isotopes, try to parse from description
            direct_pattern = rf'{re.escape(isotope)}\s*[~]?([\d.]+(?:–[\d.]+)?)\s*(min|h|d)'
            match = re.search(direct_pattern, description)
            if match:
                value_str = match.group(1)
                unit = match.group(2)
                if '–' in value_str:
                    value_str = value_str.split('–')[0]
                try:
                    value = float(value_str)
                    if unit == 'min':
                        hours = value / 60
                    elif unit == 'd':
                        hours = value * 24
                    else:
                        hours = value
                    
                    can_serve = hours >= SERVICE_THRESHOLD_HOURS
                    isotopes.append({
                        'name': isotope,
                        'halflife_hours': round(hours, 2),
                        'halflife_display': f"{value_str} {unit}",
                        'can_serve': can_serve
                    })
                    found_isotopes.add(isotope)
                except:
                    pass
    
    # Sort: can serve first, then cannot serve, then by name
    isotopes.sort(key=lambda x: (not x['can_serve'], x['name']))
    
    return isotopes

def get_site_serviceability(isotopes):
    """Determine overall site serviceability based on isotopes."""
    if not isotopes:
        return 'unknown'
    
    can_serve_count = sum(1 for i in isotopes if i['can_serve'])
    cannot_serve_count = len(isotopes) - can_serve_count
    
    if cannot_serve_count == 0:
        return 'can_serve'
    elif can_serve_count == 0:
        return 'cannot_serve'
    else:
        return 'partial_serve'

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

def create_popup_html(site_id, description, isotopes, serviceability):
    """Create rich HTML popup for map markers."""
    # Site header with serviceability color
    if serviceability == 'can_serve':
        header_color = COLORS['can_serve']
        status_text = '✓ SERVICEABLE'
        status_bg = '#D1FAE5'
    elif serviceability == 'cannot_serve':
        header_color = COLORS['cannot_serve']
        status_text = '✗ NOT SERVICEABLE'
        status_bg = '#FEE2E2'
    else:
        header_color = COLORS['partial_serve']
        status_text = '◐ PARTIAL'
        status_bg = '#FEF3C7'
    
    # Extract site name from description (before first parenthesis or semicolon)
    site_name = description.split('(')[0].split(';')[0].strip()
    if len(site_name) > 40:
        site_name = site_name[:37] + "..."
    
    isotope_rows = ""
    for iso in isotopes:
        serve_badge = f'<span style="background:{("#D1FAE5" if iso["can_serve"] else "#FEE2E2")};color:{("#065F46" if iso["can_serve"] else "#991B1B")};padding:1px 6px;border-radius:8px;font-size:9px;font-weight:600;">{"✓" if iso["can_serve"] else "✗"}</span>'
        isotope_rows += f'''
        <tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:4px 6px;font-weight:600;color:#1B4F72;">{iso["name"]}</td>
            <td style="padding:4px 6px;text-align:center;">{iso["halflife_display"]}</td>
            <td style="padding:4px 6px;text-align:center;">{serve_badge}</td>
        </tr>'''
    
    popup_html = f'''
    <div style="font-family:Inter,-apple-system,sans-serif;width:280px;padding:0;margin:0;">
        <div style="background:linear-gradient(135deg,{COLORS['marken_deep_green']},{COLORS['marken_green']});padding:10px 12px;border-radius:8px 8px 0 0;">
            <div style="color:white;font-size:18px;font-weight:700;">Site {site_id}</div>
            <div style="color:rgba(255,255,255,0.9);font-size:11px;margin-top:2px;">{site_name}</div>
        </div>
        <div style="background:{status_bg};padding:6px 12px;text-align:center;">
            <span style="color:{header_color};font-weight:700;font-size:11px;">{status_text}</span>
        </div>
        <div style="background:white;padding:8px;border-radius:0 0 8px 8px;border:1px solid #e5e5e5;border-top:none;">
            <div style="font-size:10px;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Isotopes & Half-Lives</div>
            <table style="width:100%;border-collapse:collapse;font-size:10px;">
                <tr style="background:#f9fafb;">
                    <th style="padding:4px 6px;text-align:left;color:#374151;">Isotope</th>
                    <th style="padding:4px 6px;text-align:center;color:#374151;">T½</th>
                    <th style="padding:4px 6px;text-align:center;color:#374151;">Service</th>
                </tr>
                {isotope_rows}
            </table>
            <div style="margin-top:8px;padding:6px;background:#F3F4F6;border-radius:4px;font-size:9px;color:#6B7280;">
                <strong>Threshold:</strong> ≥6h half-life required for Marken service
            </div>
        </div>
    </div>
    '''
    return popup_html

def create_map(df_map, df_legend, df_gateways):
    m = folium.Map(location=[50.0, 10.0], zoom_start=4, tiles='cartodbpositron')
    
    # Add UPS Gateways
    for _, row in df_gateways.iterrows():
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=120000, color=COLORS['gateway_red'], weight=3, fill=False, opacity=0.9,
            tooltip=f"UPS Gateway: {row['Code']} - {row['City']}"
        ).add_to(m)
    
    # Create legend lookup
    legend_dict = df_legend.set_index('ID')['Description'].to_dict()
    
    # Process each manufacturing site
    for _, row in df_map.iterrows():
        site_id = row['ID']
        description = legend_dict.get(site_id, "No description available")
        
        # Parse isotopes and determine serviceability
        isotopes = parse_isotopes_from_description(description)
        serviceability = get_site_serviceability(isotopes)
        
        # Choose marker color based on serviceability
        if serviceability == 'can_serve':
            marker_color = COLORS['can_serve']
            border_color = '#065F46'
        elif serviceability == 'cannot_serve':
            marker_color = COLORS['cannot_serve']
            border_color = '#7F1D1D'
        else:
            marker_color = COLORS['partial_serve']
            border_color = '#92400E'
        
        # Create popup
        popup_html = create_popup_html(site_id, description, isotopes, serviceability)
        popup = folium.Popup(popup_html, max_width=300)
        
        # Create marker with serviceability color
        icon_html = f'''
        <div style="
            background:{marker_color};
            color:white;
            font-weight:700;
            font-size:11px;
            width:26px;
            height:22px;
            display:flex;
            align-items:center;
            justify-content:center;
            border:2px solid {border_color};
            border-radius:4px;
            box-shadow:1px 1px 4px rgba(0,0,0,0.3);
            transform:translate(-13px,-11px);
        ">{site_id}</div>
        '''
        
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(html=icon_html, icon_size=(26, 22)),
            popup=popup,
            tooltip=f"Site {site_id}: {row['Country']} (Click for details)"
        ).add_to(m)
    
    return m

def create_isotope_summary(df_legend):
    """Create a summary dataframe of all sites with isotope serviceability."""
    summary_data = []
    
    for _, row in df_legend.iterrows():
        site_id = row['ID']
        description = row['Description']
        isotopes = parse_isotopes_from_description(description)
        serviceability = get_site_serviceability(isotopes)
        
        # Extract site name
        site_name = description.split('(')[0].split(';')[0].strip()
        if '–' in site_name:
            site_name = site_name.split('–')[0].strip()
        
        # Create isotope strings
        can_serve_isotopes = [i['name'] for i in isotopes if i['can_serve']]
        cannot_serve_isotopes = [i['name'] for i in isotopes if not i['can_serve']]
        
        summary_data.append({
            'Site': site_id,
            'Name': site_name[:30] + ('...' if len(site_name) > 30 else ''),
            'Can Serve (≥6h)': ', '.join(can_serve_isotopes) if can_serve_isotopes else '—',
            'Cannot Serve (<6h)': ', '.join(cannot_serve_isotopes) if cannot_serve_isotopes else '—',
            'Status': '✓ Full' if serviceability == 'can_serve' else ('✗ None' if serviceability == 'cannot_serve' else '◐ Partial')
        })
    
    return pd.DataFrame(summary_data)

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
    
    # Calculate KPIs
    total_sites = df_legend['ID'].nunique()
    total_countries = df_map['Country'].nunique()
    total_gateways = len(df_gateways)
    
    # Count isotopes and serviceability
    all_isotopes = set()
    serviceable_count = 0
    for _, row in df_legend.iterrows():
        isotopes = parse_isotopes_from_description(row['Description'])
        for iso in isotopes:
            all_isotopes.add(iso['name'])
        serviceability = get_site_serviceability(isotopes)
        if serviceability in ['can_serve', 'partial_serve']:
            serviceable_count += 1
    
    # KPI Row
    st.markdown(f'''
    <div class="kpi-row">
        <div class="kpi-box"><div class="kpi-val">{total_sites}</div><div class="kpi-lbl">Production Sites</div></div>
        <div class="kpi-box"><div class="kpi-val">{total_countries}</div><div class="kpi-lbl">Countries</div></div>
        <div class="kpi-box"><div class="kpi-val">{total_gateways}</div><div class="kpi-lbl">UPS Gateways</div></div>
        <div class="kpi-box"><div class="kpi-val">{len(all_isotopes)}</div><div class="kpi-lbl">Isotopes</div></div>
        <div class="kpi-box"><div class="kpi-val" style="color:#22A06B;">{serviceable_count}</div><div class="kpi-lbl">Serviceable Sites</div></div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Color Legend
    st.markdown('''
    <div style="display:flex;gap:20px;margin-bottom:12px;padding:8px 12px;background:white;border-radius:8px;border:1px solid #E5E8EB;">
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;">
            <div style="width:20px;height:16px;background:#22A06B;border-radius:3px;border:2px solid #065F46;"></div>
            <span><strong>Can Serve</strong> (all isotopes ≥6h)</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;">
            <div style="width:20px;height:16px;background:#F59E0B;border-radius:3px;border:2px solid #92400E;"></div>
            <span><strong>Partial</strong> (mixed isotopes)</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;">
            <div style="width:20px;height:16px;background:#DC2626;border-radius:3px;border:2px solid #7F1D1D;"></div>
            <span><strong>Cannot Serve</strong> (all isotopes <6h)</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;">
            <div style="width:20px;height:20px;border:3px solid #DC2626;border-radius:50%;"></div>
            <span><strong>UPS Gateway</strong></span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Map
    m = create_map(df_map, df_legend, df_gateways)
    st_folium(m, width=None, height=520, returned_objects=[])
    
    st.markdown("---")
    
    # Collapsible Legend Panel
    with st.expander("📋 Site Legend & Isotope Details (Click to Expand)", expanded=False):
        # Build legend HTML
        items_html = ""
        for _, row in df_legend.iterrows():
            isotopes = parse_isotopes_from_description(row['Description'])
            serviceability = get_site_serviceability(isotopes)
            
            if serviceability == 'can_serve':
                bg_color = COLORS['can_serve']
                border_color = '#065F46'
            elif serviceability == 'cannot_serve':
                bg_color = COLORS['cannot_serve']
                border_color = '#7F1D1D'
            else:
                bg_color = COLORS['partial_serve']
                border_color = '#92400E'
            
            # Create isotope badges
            isotope_badges = ""
            for iso in isotopes:
                iso_bg = '#D1FAE5' if iso['can_serve'] else '#FEE2E2'
                iso_color = '#065F46' if iso['can_serve'] else '#991B1B'
                isotope_badges += f'<span style="background:{iso_bg};color:{iso_color};padding:1px 5px;border-radius:6px;font-size:9px;margin-right:3px;white-space:nowrap;">{iso["name"]} ({iso["halflife_display"]})</span>'
            
            items_html += f'''<div style="display:flex;align-items:flex-start;padding:8px 10px;border-bottom:1px solid #F0F0F0;gap:8px;">
                <div style="background:{bg_color};color:white;font-weight:700;min-width:28px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:4px;font-size:12px;flex-shrink:0;border:2px solid {border_color};">{row["ID"]}</div>
                <div style="flex:1;">
                    <div style="font-size:11px;color:#374151;line-height:1.4;margin-bottom:4px;">{row["Description"][:80]}{'...' if len(row["Description"]) > 80 else ''}</div>
                    <div style="display:flex;flex-wrap:wrap;gap:2px;">{isotope_badges}</div>
                </div>
            </div>'''
        
        legend_html = f'''<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ font-family: 'Inter', -apple-system, sans-serif; margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: transparent; }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb {{ background: #c1c1c1; border-radius: 3px; }}
    </style>
</head>
<body>
    <div style="background:#FEF2F2;border:2px solid #DC2626;border-radius:6px;padding:8px 10px;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
        <div style="width:24px;height:24px;border:3px solid #DC2626;border-radius:50%;flex-shrink:0;"></div>
        <div style="font-size:11px;color:#1F2937;"><strong style="color:#B91C1C;">UPS Origin Gateways</strong><br><span style="font-size:10px;color:#6B7280;">CGN, VIE, BER, BCN</span></div>
    </div>
    <div style="font-weight:600;color:#1B4F72;font-size:12px;margin-bottom:6px;">📍 Manufacturing Sites by Serviceability</div>
    <div style="background:white;border:1px solid #E5E8EB;border-radius:6px;max-height:500px;overflow-y:auto;">
        {items_html}
    </div>
</body>
</html>'''
        
        components.html(legend_html, height=560, scrolling=False)
    
    # Data Tables
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<p class="section-hdr">⚛️ Isotope Serviceability by Site</p>', unsafe_allow_html=True)
        summary_df = create_isotope_summary(df_legend)
        st.dataframe(summary_df, use_container_width=True, hide_index=True, height=280)
    
    with c2:
        st.markdown('<p class="section-hdr">✈️ UPS Origin Gateways</p>', unsafe_allow_html=True)
        st.dataframe(df_gateways[['Code', 'City', 'Country', 'Status']], use_container_width=True, hide_index=True, height=150)
        
        st.markdown('<p class="section-hdr" style="margin-top:16px;">📊 Isotope Half-Life Reference</p>', unsafe_allow_html=True)
        isotope_ref = []
        for name, hours in sorted(ISOTOPE_HALFLIVES.items(), key=lambda x: x[1]):
            if hours < 1:
                display = f"{hours*60:.1f} min"
            elif hours < 24:
                display = f"{hours:.1f} h"
            else:
                display = f"{hours/24:.1f} d"
            can_serve = "✓ Yes" if hours >= SERVICE_THRESHOLD_HOURS else "✗ No"
            isotope_ref.append({'Isotope': name, 'Half-Life': display, 'Serviceable': can_serve})
        st.dataframe(pd.DataFrame(isotope_ref), use_container_width=True, hide_index=True, height=200)
    
    st.markdown('<div class="info-box"><b>Service Threshold:</b> Marken can serve isotopes with half-life ≥ 6 hours. Isotopes with shorter half-lives (e.g., F-18, Ga-68) require specialized local production and delivery.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-bar"><b>Nuclear Medicine EMEA Dashboard</b> • Marken UPS Healthcare Logistics • CONFIDENTIAL</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
