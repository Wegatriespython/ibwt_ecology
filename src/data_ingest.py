#!/usr/bin/env python3
"""
Data ingestion module for freshwater fish occurrence dataset and drainage basins shapefile.
"""

import os
import pandas as pd
import geopandas as gpd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "data"))

def load_csv_tables(data_dir=DATA_DIR):
    """
    Load species occurrence, drainage basins, and references tables.
    """
    basins_fp = os.path.join(data_dir, "Drainage_Basins_Table.csv")
    occ_fp = os.path.join(data_dir, "Occurrence_Table.csv")
    refs_fp = os.path.join(data_dir, "References_Table.csv")
    basins = pd.read_csv(basins_fp, sep=";", encoding="latin-1")
    occ = pd.read_csv(occ_fp, sep=";", encoding="latin-1")
    refs = pd.read_csv(refs_fp, sep=";", encoding="latin-1")
    return basins, occ, refs

def load_shapefile(data_dir=DATA_DIR):
    """
    Load drainage basins shapefile as GeoDataFrame.
    """
    shp_fp = os.path.join(data_dir, "Basin042017_3119.shp")
    basins_gdf = gpd.read_file(shp_fp)
    return basins_gdf

def main():
    basins_df, occ_df, refs_df = load_csv_tables()
    print(f"Loaded drainage basins table: {basins_df.shape}")
    print(f"Loaded species occurrence table: {occ_df.shape}")
    print(f"Loaded references table: {refs_df.shape}")
    basins_gdf = load_shapefile()
    print(f"Loaded basins shapefile: {basins_gdf.shape}")

    print("\nBasins table sample:")
    print(basins_df.head())
    print("\nOccurrence table sample:")
    print(occ_df.head())
    print("\nBasins shapefile sample:")
    print(basins_gdf.head())

if __name__ == "__main__":
    main()