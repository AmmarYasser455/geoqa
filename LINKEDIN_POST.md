# LinkedIn Post — GeoQA Launch

---

## Post Text

I'm excited to share **GeoQA** — an open-source Python package I built for **geospatial data quality assessment and interactive profiling**.

As a GIS developer, I kept running into the same frustrating question: *"Is this geodata good enough to use?"* — and there was no quick, automated way to answer it.

So I built GeoQA.

**What it does:**

- Profiles any vector dataset (Shapefile, GeoJSON, GeoPackage) with a single function call
- Computes an overall **quality score (0–100)** based on geometry validity, attribute completeness, and CRS
- Detects **invalid, empty, and duplicate geometries** automatically
- Generates **interactive web maps** with quality-issue highlighting
- Produces **self-contained HTML quality reports** with charts, tables, and spatial statistics

**What makes it unique:**

GeoQA is like **ydata-profiling** — but purpose-built for geodata. It understands geometry types, coordinate systems, spatial topology, and the real-world data problems that GIS professionals deal with daily.

**It also powers the pre-check module in OVC (Overlap Violation Checker)** — my other open-source tool for detecting overlapping buildings, road conflicts, and topological errors. Before OVC runs its spatial QC pipeline, GeoQA profiles every input dataset to catch fundamental issues early — missing CRS, invalid geometries, empty features — saving compute time and giving clear diagnostics upfront.

Together, GeoQA + OVC form a **complete geospatial quality control workflow**: GeoQA assesses data readiness, and OVC performs deep spatial validation.

**Who is this for?**

- GIS Analysts validating shapefiles before analysis
- Urban Planners checking building and road datasets
- Survey Engineers ensuring geometry integrity
- Data Engineers building geospatial ETL pipelines
- Government agencies auditing cadastral and infrastructure data
- Academic researchers profiling geodata for publications
- Anyone working with vector geospatial data who wants automated quality checks

Both tools are **free, open-source, and MIT-licensed**.

**Try it:**
- GeoQA on PyPI: https://pypi.org/project/geoqa/
- GeoQA on GitHub: https://github.com/AmmarYasser455/geoqa
- OVC on GitHub: https://github.com/AmmarYasser455/ovc

I'd love to hear your feedback — try it on your own datasets and let me know what you think!

---

## Recommended Media (attach to post)

1. **Screenshot of `profile.summary()`** — the rich-formatted terminal output showing dataset overview, quality score, and geometry checks
2. **Screenshot of the interactive Folium web map** — showing quality-highlighted features (valid in blue, issues in red)
3. **Screenshot of the HTML quality report** — the gradient header with quality score badge, overview cards, and charts
4. **Screenshot of OVC + GeoQA working together** — the pre-check output showing data readiness assessment before QC
5. **A short GIF or video** (60–90 seconds) showing the full workflow: profile → map → report in Jupyter

> Tip: LinkedIn favors **carousel posts (PDF)** and **native video**. Consider combining 3–4 screenshots into a carousel PDF for higher engagement.

---

## Hashtags

#GIS #Geospatial #Python #OpenSource #DataQuality #GeoQA #OVC
#GeoPandas #Mapping #SpatialData #GISDev #UrbanPlanning
#OpenData #DataScience #QualityAssurance #QualityControl
#SurveyEngineering #DataEngineering #WebMapping #Cartography
#RemoteSensing #SpatialAnalysis #BuildingData #RoadNetwork
#GISProfessionals #PythonDev #FOSS4G #Leaflet #Folium

---
