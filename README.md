GeoSpectre AI Assistant
GeoSpectre is an AI-powered geospatial assistant that provides interactive maps and actionable insights for flood risk, fire danger, elevation analysis, and more — all using real satellite and terrain data.

<!-- Add this image in your repo root folder -->

Features
Real-Time Satellite Integration with OpenTopography API

Flood Risk Mapping using elevation and rainfall factors

Fire Danger Analysis based on terrain and temperature

Elevation Visualizations with heatmaps and contours

Farming Suitability Checks for specific regions

Population Density & Urban Planning Insights

Conversational AI Interface with natural language requests

Interactive Maps rendered with Folium and Streamlit

App UI Preview



Tech Stack
Frontend: Streamlit

Geospatial Processing: Folium, Plotly

Data Sources: OpenTopography API, Weather, Census, Land Use

Language: Python

Core Functionalities
Chat-Driven Analysis
bash
Copy
Edit
"Show me flood risk areas in Kerala with rainfall data"
"Create a fire danger map for California forests"
"Find best farming areas in Punjab"
Data Fetching
Fetch DEM (Digital Elevation Model) using OpenTopography API

Generate synthetic sample elevation where real DEM is not available

Risk Analysis
Flood Risk: Based on elevation and rainfall factor

Fire Danger: Based on elevation and temperature factor

Map Rendering
Folium-based heatmaps and circle markers

Risk-level color codes and legends

Supported Cities
Supports location-specific analysis for 40+ Indian and global cities including:

Copy
Edit
Mumbai, Delhi, Kerala, Bengaluru, Chennai, Hyderabad, Pune, Kolkata, Jaipur, Lucknow...
(Full list implemented via keyword-to-coordinates matching in the code.)

Export & Share
Download generated map

Share links (placeholder)

Edit map feature (planned)

Architecture
mermaid
Copy
Edit
flowchart TD
    A[User Chat Input] --> B[NLP-based Prompt Detection]
    B --> C[Location + Analysis Type Extraction]
    C --> D[Elevation Data Fetch (API or Simulated)]
    D --> E[Risk Analysis (Flood/Fire/etc)]
    E --> F[Map Visualization (Folium)]
    F --> G[Streamlit Display + UI]
About the AI
The GeoSpectreAI class encapsulates:

Elevation Data Fetching

Risk Analysis Models

Interactive Map Generator

Future Work
Integration with QGIS / GDAL

Improved Prompt Interpretation using LLMs

Rainfall + Terrain Overlays

Export to GeoTIFF / SHP

LangChain-based geospatial chains

