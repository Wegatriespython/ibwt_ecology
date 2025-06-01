# Inter-Basin Water Transfer Ecological Impact Assessment

A Python-based tool for assessing ecological impacts of Inter-Basin Water Transfer (IBWT) projects using freshwater fish biodiversity data and the Inter-Basin Ecological Impact Index (IBEII).

## Overview

This project implements the biogeographic dissimilarity component (B) of the IBEII framework to evaluate ecological risks of major global water transfer projects. Using coordinate-based spatial matching, it connects IBT project locations with drainage basin fish diversity data to quantify potential biotic homogenization impacts.

## Key Features

- **Spatial Basin Matching**: Coordinate-based algorithm to match IBT project locations with drainage basins
- **Fish Diversity Analysis**: Species richness and native/exotic composition analysis for 3,119 global basins
- **Jaccard Dissimilarity Calculation**: Biogeographic dissimilarity measures between sender-receiver basin pairs
- **Comprehensive Visualizations**: Professional charts for top IBT projects showing flow volume, species diversity, and ecological risk
- **Global Coverage**: Analysis of top 20 IBT projects worldwide by design flow volume

## Results Summary

### Top 5 IBT Projects by Flow Volume

1. **Ganga/Brahmaputra ’ Peninsular rivers** (India): 200 km³/yr, 0.828 dissimilarity
2. **Yangtze ’ Yellow & Hai** (China): 44.8 km³/yr, 0.832 dissimilarity  
3. **Colorado ’ Imperial & Coachella** (USA): 23 km³/yr, 0.826 dissimilarity
4. **Sutlej-Beas ’ Thar Desert** (India): 16.5 km³/yr, 0.926 dissimilarity
5. **Narmada ’ Gujarat & Rajasthan** (India): 11.7 km³/yr, 1.000 dissimilarity

### Key Findings

- **High ecological risk**: Most projects show Jaccard dissimilarity of 0.6-1.0
- **Species diversity range**: From 1 species (arid basins) to 502 species (Mississippi)
- **Cross-basin transfers**: Generally higher dissimilarity than within-basin transfers
- **Desert/arid transfers**: Often show maximum dissimilarity (1.0)

## Data Sources

- **Global Freshwater Fish Database** (Tedesco et al., 2017): 14,953 species across 3,119 basins
- **IBT Projects Coordinates**: Curated dataset with sender-receiver coordinates for top 20 projects
- **Drainage Basins Shapefile**: Global basin polygons for spatial matching

## Installation

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv install

# Or add specific packages
uv add geopandas pandas matplotlib seaborn
```

## Usage

### Run Fish Diversity Analysis

```bash
uv run src/match_fish_diversity.py
```

### Generate Visualizations

```bash
uv run src/visualize_top_projects.py
```

### Load and Explore Data

```bash
uv run src/data_ingest.py
```

Here’s the cleaned and properly formatted Markdown. All garbled characters (e.g. `¿`, ``, `=`) have been removed or fixed, and indentation has been corrected:

```markdown
## Project Structure
```

```text
ibwt_ecology/
├── data/                         # Datasets and results
│   ├── Basin042017_3119.*       # Drainage basins shapefile
│   ├── *_Table.csv              # Fish occurrence data
│   ├── Top_20_IBT_Projects_with_Coordinates.csv
│   └── IBT_Fish_Diversity_Results.csv
│
├── visualizations/              # Generated charts and plots
├── src/                         # Analysis scripts
│   ├── data_ingest.py           # Data loading utilities
│   ├── match_fish_diversity.py  # Main analysis pipeline
│   └── visualize_top_projects.py# Visualization generation
│
├── pyproject.toml               # Project configuration
└── requirements.txt             # Dependencies
````

## Output Files

* **`IBT_Fish_Diversity_Results.csv`**: Complete analysis results with species counts and dissimilarity metrics
* **`visualizations/`**: Individual project charts (2x2 layout) and summary comparison plots

## IBEII Framework Implementation

This project implements the **B (Biogeographic Dissimilarity)** component of the IBEII formula:

**IBEII = F × B × E**

* **B**: Jaccard dissimilarity between basin fish assemblages (**implemented**)
* **F**: Relative flow volume (design flow / mean annual flow)
* **E**: Environmental/mitigation factor scoring

## References

* Tedesco, P.A. et al. (2017). A global database on freshwater fish species occurrence in drainage basins. *Scientific Data*, 4, 170141.
* IBEII framework based on proposed ecological impact indicator methodology for inter-basin water transfers.

## License

This project is for research and educational purposes. Data sources maintain their original licensing terms.

---

*Generated using fish biodiversity data and spatial analysis techniques for ecological impact assessment of major global water transfer projects.*

