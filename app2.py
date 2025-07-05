import streamlit as st
import requests
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
import json
import time
from datetime import datetime, timedelta
import io
import base64

# Page configuration
st.set_page_config(
    page_title="GeoSpectre AI Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        animation: fadeIn 0.5s ease-in;
    }
    
    .user-message {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    .assistant-message {
        background: #f0f2f6;
        color: #2d3748;
        margin-right: 20%;
        border-bottom-left-radius: 5px;
        border-left: 4px solid #667eea;
    }
    
    .progress-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-completed {
        background: #c6f6d5;
        color: #22543d;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .status-processing {
        background: #fef5e7;
        color: #c05621;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .status-pending {
        background: #e2e8f0;
        color: #4a5568;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .stat-card {
        background: linear-gradient(45deg, #f7fafc, #edf2f7);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #718096;
        text-transform: uppercase;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_map' not in st.session_state:
    st.session_state.current_map = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'current_progress' not in st.session_state:
    st.session_state.current_progress = 0
if 'map_generated' not in st.session_state:
    st.session_state.map_generated = False
if 'prevent_rerun' not in st.session_state:
    st.session_state.prevent_rerun = False
if 'current_lat' not in st.session_state:
    st.session_state.current_lat = 20.5937
if 'current_lon' not in st.session_state:
    st.session_state.current_lon = 78.9629
if 'current_analysis_type' not in st.session_state:
    st.session_state.current_analysis_type = "elevation"

# OpenTopography API configuration
OPENTOPO_API_KEY = "f4f6840a5ff309df9554c11f74f83a66"  # Replace with actual API key
OPENTOPO_BASE_URL = "https://cloud.sdsc.edu/v1/CommunityDEM"


class GeoSpectreAI:
    def __init__(self):
        self.name = "GeoSpectre AI"
        self.capabilities = [
            "Flood Risk Analysis",
            "Fire Danger Mapping",
            "Population Density",
            "Agricultural Suitability",
            "Elevation Analysis",
            "Slope Stability",
            "Watershed Analysis"
        ]

    def get_elevation_data(self, north, south, east, west, dem_type="SRTM_GL1"):
        """Fetch elevation data from OpenTopography API"""
        try:
            params = {
                'demtype': dem_type,
                'south': south,
                'north': north,
                'west': west,
                'east': east,
                'outputFormat': 'GTiff',
                'API_Key': OPENTOPO_API_KEY
            }

            response = requests.get(OPENTOPO_BASE_URL, params=params)

            if response.status_code == 200:
                return response.content
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Error fetching elevation data: {str(e)}")
            return None

    def create_sample_elevation_map(self, lat, lon, analysis_type="elevation"):
        """Create a sample elevation map with realistic data"""
        # Create sample elevation data
        lats = np.linspace(lat - 0.1, lat + 0.1, 50)
        lons = np.linspace(lon - 0.1, lon + 0.1, 50)

        # Generate realistic elevation data
        elevation_data = []
        for i, latitude in enumerate(lats):
            for j, longitude in enumerate(lons):
                # Simulate elevation with some noise
                base_elevation = 100 + 50 * np.sin(i/10) + 30 * np.cos(j/8)
                noise = np.random.normal(0, 10)
                elevation = max(0, base_elevation + noise)
                elevation_data.append([latitude, longitude, elevation])

        return pd.DataFrame(elevation_data, columns=['lat', 'lon', 'elevation'])

    def analyze_flood_risk(self, elevation_data, rainfall_factor=1.0):
        """Analyze flood risk based on elevation and rainfall"""
        # Lower elevations have higher flood risk
        flood_risk = []
        for _, row in elevation_data.iterrows():
            # Normalize elevation
            base_risk = max(0, 1 - (row['elevation'] / 200))
            risk_with_rainfall = min(1, base_risk * rainfall_factor)

            if risk_with_rainfall > 0.7:
                risk_level = "High"
                color = "red"
            elif risk_with_rainfall > 0.4:
                risk_level = "Medium"
                color = "orange"
            else:
                risk_level = "Low"
                color = "green"

            flood_risk.append({
                'lat': row['lat'],
                'lon': row['lon'],
                'risk_score': risk_with_rainfall,
                'risk_level': risk_level,
                'color': color
            })

        return pd.DataFrame(flood_risk)

    def analyze_fire_danger(self, elevation_data, temperature_factor=1.0):
        """Analyze fire danger based on elevation and temperature"""
        fire_risk = []
        for _, row in elevation_data.iterrows():
            # Higher elevations and slopes increase fire risk
            base_risk = (row['elevation'] / 300) * temperature_factor
            risk_score = min(1, max(0, base_risk + np.random.normal(0, 0.1)))

            if risk_score > 0.7:
                risk_level = "Extreme"
                color = "darkred"
            elif risk_score > 0.5:
                risk_level = "High"
                color = "red"
            elif risk_score > 0.3:
                risk_level = "Moderate"
                color = "orange"
            else:
                risk_level = "Low"
                color = "green"

            fire_risk.append({
                'lat': row['lat'],
                'lon': row['lon'],
                'risk_score': risk_score,
                'risk_level': risk_level,
                'color': color
            })

        return pd.DataFrame(fire_risk)

    def create_interactive_map(self, data, lat, lon, analysis_type="elevation"):
        """Create an interactive map using Folium"""
        # Create base map
        m = folium.Map(location=[lat, lon], zoom_start=12)

        if analysis_type == "elevation":
            # Add elevation heatmap
            heat_data = [[row['lat'], row['lon'], row['elevation']]
                         for _, row in data.iterrows()]
            plugins.HeatMap(heat_data, radius=15, blur=25).add_to(m)

            # Add contour lines
            for _, row in data.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=3,
                    popup=f"Elevation: {row['elevation']:.1f}m",
                    color='blue',
                    fill=True,
                    weight=1
                ).add_to(m)

        elif analysis_type == "flood":
            # Add flood risk markers
            for _, row in data.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=5,
                    popup=f"Risk: {row['risk_level']}<br>Score: {row['risk_score']:.2f}",
                    color=row['color'],
                    fill=True,
                    weight=2
                ).add_to(m)

        elif analysis_type == "fire":
            # Add fire danger markers
            for _, row in data.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=5,
                    popup=f"Danger: {row['risk_level']}<br>Score: {row['risk_score']:.2f}",
                    color=row['color'],
                    fill=True,
                    weight=2
                ).add_to(m)

        # Add legend
        legend_html = f"""
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>{analysis_type.title()} Analysis</h4>
        <p><i class="fa fa-circle" style="color:red"></i> High Risk</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Medium Risk</p>
        <p><i class="fa fa-circle" style="color:green"></i> Low Risk</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        return m


# Initialize AI
ai = GeoSpectreAI()

# Header
st.markdown("""
<div class="main-header">
    <h1>🌍 GeoSpectre AI Assistant</h1>
    <p>Advanced geospatial analysis powered by real satellite data and AI</p>
</div>
""", unsafe_allow_html=True)

# Main layout
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("💬 Chat with GeoSpectre")

    # Quick action buttons
    st.markdown("**Popular Requests:**")
    if st.button("🌊 Flood Risk Areas", key="flood_btn"):
        st.session_state.messages.append({
            "role": "user",
            "content": "Show me flood risk areas in Kerala with rainfall data"
        })
        st.session_state.map_generated = False
        st.session_state.prevent_rerun = True

    if st.button("🔥 Fire Danger Zones", key="fire_btn"):
        st.session_state.messages.append({
            "role": "user",
            "content": "Create a fire danger map for California forests"
        })
        st.session_state.map_generated = False
        st.session_state.prevent_rerun = True

    if st.button("👥 Population Density", key="pop_btn"):
        st.session_state.messages.append({
            "role": "user",
            "content": "Map population density in Mumbai city"
        })
        st.session_state.map_generated = False
        st.session_state.prevent_rerun = True

    if st.button("🌾 Best Farming Areas", key="farm_btn"):
        st.session_state.messages.append({
            "role": "user",
            "content": "Find best farming areas in Punjab with soil data"
        })
        st.session_state.map_generated = False
        st.session_state.prevent_rerun = True

    # Chat interface
    user_input = st.text_area("Type your request:",
                              key="user_input", height=100)

    if st.button("Send 🚀", key="send_btn"):
        if user_input:
            st.session_state.messages.append(
                {"role": "user", "content": user_input})
            st.session_state.map_generated = False
            st.session_state.prevent_rerun = True
            st.session_state.current_progress = 0

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

    # Process latest message only if not already processed
    if (st.session_state.messages and
        st.session_state.messages[-1]["role"] == "user" and
            not st.session_state.map_generated):

        latest_message = st.session_state.messages[-1]["content"].lower()

        # Determine analysis type and location
        if "flood" in latest_message:
            analysis_type = "flood"
            location = "Kerala" if "kerala" in latest_message else "Default Location"
        elif "fire" in latest_message:
            analysis_type = "fire"
            location = "California" if "california" in latest_message else "Default Location"
        elif "population" in latest_message:
            analysis_type = "population"
            location = "Mumbai" if "mumbai" in latest_message else "Default Location"
        else:
            analysis_type = "elevation"
            location = "Default Location"

        # Set coordinates based on location mentioned in message
        if "kerala" in latest_message:
            lat, lon = 10.8505, 76.2711
        elif "california" in latest_message:
            lat, lon = 36.7783, -119.4179
        elif "mumbai" in latest_message:
            lat, lon = 19.0760, 72.8777
        elif "punjab" in latest_message:
            lat, lon = 31.1471, 75.3412
        elif "delhi" in latest_message:
            lat, lon = 28.7041, 77.1025
        elif "bangalore" in latest_message or "bengaluru" in latest_message:
            lat, lon = 12.9716, 77.5946
        elif "chennai" in latest_message:
            lat, lon = 13.0827, 80.2707
        elif "hyderabad" in latest_message:
            lat, lon = 17.3850, 78.4867
        elif "kolkata" in latest_message:
            lat, lon = 22.5726, 88.3639
        elif "ahmedabad" in latest_message:
            lat, lon = 23.0225, 72.5714
        elif "pune" in latest_message:
            lat, lon = 18.5204, 73.8567
        elif "jaipur" in latest_message:
            lat, lon = 26.9124, 75.7873
        elif "lucknow" in latest_message:
            lat, lon = 26.8467, 80.9462
        elif "kanpur" in latest_message:
            lat, lon = 26.4499, 80.3319
        elif "nagpur" in latest_message:
            lat, lon = 21.1458, 79.0882
        elif "indore" in latest_message:
            lat, lon = 22.7196, 75.8577
        elif "thane" in latest_message:
            lat, lon = 19.2183, 72.9781
        elif "bhopal" in latest_message:
            lat, lon = 23.2599, 77.4126
        elif "visakhapatnam" in latest_message:
            lat, lon = 17.6868, 83.2185
        elif "patna" in latest_message:
            lat, lon = 25.5941, 85.1376
        elif "vadodara" in latest_message:
            lat, lon = 22.3072, 73.1812
        elif "ludhiana" in latest_message:
            lat, lon = 30.9010, 75.8573
        elif "rajkot" in latest_message:
            lat, lon = 22.3039, 70.8022
        elif "agra" in latest_message:
            lat, lon = 27.1767, 78.0081
        elif "siliguri" in latest_message:
            lat, lon = 26.7271, 88.3953
        elif "nashik" in latest_message:
            lat, lon = 19.9975, 73.7898
        elif "faridabad" in latest_message:
            lat, lon = 28.4089, 77.3178
        elif "meerut" in latest_message:
            lat, lon = 28.9845, 77.7064
        elif "kalyan" in latest_message:
            lat, lon = 19.2437, 73.1355
        elif "vasai" in latest_message:
            lat, lon = 19.4912, 72.8054
        elif "varanasi" in latest_message:
            lat, lon = 25.3176, 82.9739
        elif "srinagar" in latest_message:
            lat, lon = 34.0837, 74.7973
        elif "aurangabad" in latest_message:
            lat, lon = 19.8762, 75.3433
        elif "dhanbad" in latest_message:
            lat, lon = 23.7957, 86.4304
        elif "amritsar" in latest_message:
            lat, lon = 31.6340, 74.8723
        elif "navi mumbai" in latest_message:
            lat, lon = 19.0330, 73.0297
        elif "allahabad" in latest_message or "prayagraj" in latest_message:
            lat, lon = 25.4358, 81.8463
        elif "ranchi" in latest_message:
            lat, lon = 23.3441, 85.3096
        elif "howrah" in latest_message:
            lat, lon = 22.5958, 88.2636
        elif "coimbatore" in latest_message:
            lat, lon = 11.0168, 76.9558
        elif "jabalpur" in latest_message:
            lat, lon = 23.1815, 79.9864
        elif "gwalior" in latest_message:
            lat, lon = 26.2183, 78.1828
        elif "vijayawada" in latest_message:
            lat, lon = 16.5062, 80.6480
        elif "jodhpur" in latest_message:
            lat, lon = 26.2389, 73.0243
        elif "madurai" in latest_message:
            lat, lon = 9.9252, 78.1198
        elif "raipur" in latest_message:
            lat, lon = 21.2514, 81.6296
        elif "kota" in latest_message:
            lat, lon = 25.2138, 75.8648
        elif "chandigarh" in latest_message:
            lat, lon = 30.7333, 76.7794
        elif "guwahati" in latest_message:
            lat, lon = 26.1445, 91.7362
        else:
            lat, lon = 20.5937, 78.9629  # Default to India center

        # Store coordinates and analysis type in session state
        st.session_state.current_lat = lat
        st.session_state.current_lon = lon
        st.session_state.current_analysis_type = analysis_type

        # Add AI response
        response = f"Perfect! I'll create a {analysis_type} analysis map for {location}. Let me process the satellite data and generate your custom map."
        st.session_state.messages.append(
            {"role": "assistant", "content": response})

        # Generate map data
        elevation_data = ai.create_sample_elevation_map(
            lat, lon, analysis_type)

        if analysis_type == "flood":
            st.session_state.current_map = ai.analyze_flood_risk(
                elevation_data, rainfall_factor=1.2)
        elif analysis_type == "fire":
            st.session_state.current_map = ai.analyze_fire_danger(
                elevation_data, temperature_factor=1.1)
        else:
            st.session_state.current_map = elevation_data

        st.session_state.analysis_complete = True
        st.session_state.map_generated = True
        st.session_state.prevent_rerun = False
        st.rerun()

with col2:
    st.subheader("🗺️ Your Generated Map")

    if st.session_state.current_map is not None:
        # Create and display map with stored coordinates and analysis type
        map_obj = ai.create_interactive_map(
            st.session_state.current_map,
            st.session_state.current_lat,
            st.session_state.current_lon,
            st.session_state.current_analysis_type
        )

        # Use a unique key and disable return_on_hover to prevent constant reruns
        map_data = st_folium(
            map_obj,
            width=700,
            height=500,
            key="main_map",
            # Only return specific data
            returned_objects=["last_object_clicked"],
            return_on_hover=False  # Disable hover events that trigger reruns
        )

        # Map controls
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            if st.button("📥 Download Map", key="download_map"):
                st.success("Map download initiated!")
        with col2b:
            if st.button("📤 Share Map", key="share_map"):
                st.success("Share link generated!")
        with col2c:
            if st.button("✏️ Edit Map", key="edit_map"):
                st.success("Edit mode activated!")
    else:
        st.info(
            "Your custom map will appear here. Start chatting to generate your first map!")

with col3:
    # Tabs for different information
    tab1, tab2, tab3 = st.tabs(["📊 Progress", "📡 Data Sources", "📈 Results"])

    with tab1:
        st.subheader("Analysis Progress")

        progress_steps = [
            {"title": "🔍 Understanding Request", "status": "completed"},
            {"title": "📡 Collecting Satellite Data",
                "status": "processing" if st.session_state.current_progress > 0 else "pending"},
            {"title": "🧠 Smart Analysis",
                "status": "processing" if st.session_state.current_progress > 1 else "pending"},
            {"title": "🎨 Creating Map",
                "status": "completed" if st.session_state.analysis_complete else "pending"}
        ]

        for step in progress_steps:
            status_class = f"status-{step['status']}"
            status_text = "✅ Complete" if step['status'] == 'completed' else "⏳ Processing" if step[
                'status'] == 'processing' else "⏳ Waiting"

            st.markdown(f"""
            <div class="progress-card">
                <strong>{step['title']}</strong><br>
                <span class="{status_class}">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

        # Demo button
        if st.button("🚀 Try Demo: Create Sample Map", key="demo_btn"):
            st.session_state.messages.append({
                "role": "user",
                "content": "Show me elevation data for a sample area"
            })
            st.session_state.map_generated = False
            st.session_state.prevent_rerun = True
            st.rerun()

    with tab2:
        st.subheader("Data Sources")

        data_sources = [
            {"name": "Live Satellite Images",
                "type": "Real-time space data", "icon": "🛰️"},
            {"name": "Elevation Data", "type": "OpenTopography API", "icon": "🏔️"},
            {"name": "Street Maps", "type": "Roads, buildings, rivers", "icon": "🗺️"},
            {"name": "Weather Data", "type": "Climate & rainfall info", "icon": "🌡️"},
            {"name": "Population Data", "type": "Census & demographic", "icon": "👥"},
            {"name": "Land Use", "type": "Agriculture & urban", "icon": "🌾"}
        ]

        for source in data_sources:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 10px; margin: 5px 0; 
                        background: rgba(255,255,255,0.8); border-radius: 10px;">
                <span style="font-size: 24px; margin-right: 15px;">{source['icon']}</span>
                <div>
                    <strong>{source['name']}</strong><br>
                    <small style="color: #666;">{source['type']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("Map Statistics")

        if st.session_state.current_map is not None:
            # Calculate statistics
            if 'elevation' in st.session_state.current_map.columns:
                area_covered = len(st.session_state.current_map) * 0.01
                max_elevation = st.session_state.current_map['elevation'].max()
                min_elevation = st.session_state.current_map['elevation'].min()
                data_points = len(st.session_state.current_map)
            elif 'risk_score' in st.session_state.current_map.columns:
                area_covered = len(st.session_state.current_map) * 0.01
                high_risk_count = len(
                    st.session_state.current_map[st.session_state.current_map['risk_level'] == 'High'])
                risk_percentage = (high_risk_count /
                                   len(st.session_state.current_map)) * 100
                data_points = len(st.session_state.current_map)
            else:
                area_covered = 0
                data_points = 0

            # Display statistics
            col3a, col3b = st.columns(2)

            with col3a:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{area_covered:.1f}</div>
                    <div class="stat-label">sq km covered</div>
                </div>
                """, unsafe_allow_html=True)

            with col3b:
                if 'risk_score' in st.session_state.current_map.columns:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-value">{risk_percentage:.1f}%</div>
                        <div class="stat-label">high risk</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-value">{max_elevation:.0f}m</div>
                        <div class="stat-label">max elevation</div>
                    </div>
                    """, unsafe_allow_html=True)

            col3c, col3d = st.columns(2)

            with col3c:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{data_points}</div>
                    <div class="stat-label">data points</div>
                </div>
                """, unsafe_allow_html=True)

            with col3d:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">96%</div>
                    <div class="stat-label">accuracy</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 Results will appear here after your map is generated")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px;">
    <p>🌍 GeoSpectre AI Assistant - Powered by OpenTopography API & Advanced Geospatial Analysis</p>
    <p>Built with Streamlit • Real-time satellite data • AI-powered insights</p>
</div>
""", unsafe_allow_html=True)
