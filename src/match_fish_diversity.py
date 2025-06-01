#!/usr/bin/env python3
"""
Match fish diversity data to IBT project sender-receiver basin pairs using coordinates.
"""

import os
import sys
import pandas as pd
import geopandas as gpd
import re
from shapely.geometry import Point

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_ingest import load_csv_tables, load_shapefile

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "data"))

def parse_ibt_coordinates(data_dir=DATA_DIR):
    """
    Parse the Top_20_IBT_Projects_with_Coordinates.csv file to extract
    sender and receiver coordinates for each transfer pair.
    """
    ibt_file = os.path.join(data_dir, "Top_20_IBT_Projects_with_Coordinates.csv")
    ibt_df = pd.read_csv(ibt_file)
    
    projects = []
    for _, row in ibt_df.iterrows():
        # Parse sender coordinates
        sender_coords = row['Sender Coordinates']
        receiver_coords = row['Receiver Coordinates']
        
        # Extract lat/lon from coordinate strings
        sender_lat, sender_lon = parse_coordinate_string(sender_coords)
        receiver_lat, receiver_lon = parse_coordinate_string(receiver_coords)
        
        projects.append({
            'rank': row['#'],
            'basin_pair': row['Basin Pair'],
            'project': row['Project (Country)'],
            'design_flow': row['Design Flow (km³/yr)'],
            'sender_lat': sender_lat,
            'sender_lon': sender_lon,
            'receiver_lat': receiver_lat,
            'receiver_lon': receiver_lon
        })
    
    return pd.DataFrame(projects)

def parse_coordinate_string(coord_str):
    """
    Parse coordinate string like "Varanasi 25.32 °N 83.01 °E" to extract lat, lon.
    """
    # Match latitude and longitude with direction
    lat_match = re.search(r'(\d+\.?\d*)\s*°([NS])', coord_str)
    lon_match = re.search(r'(\d+\.?\d*)\s*°([EW])', coord_str)
    
    if not lat_match or not lon_match:
        raise ValueError(f"Could not parse coordinates from: {coord_str}")
    
    lat = float(lat_match.group(1))
    if lat_match.group(2) == 'S':
        lat = -lat
    
    lon = float(lon_match.group(1))
    if lon_match.group(2) == 'W':
        lon = -lon
    
    return lat, lon

def find_basin_by_coordinates(lat, lon, basins_gdf):
    """
    Find the drainage basin that contains the given coordinates.
    Returns basin name if found, None otherwise.
    """
    point = Point(lon, lat)  # Note: Point takes (x, y) which is (lon, lat)
    
    # Find which basin polygon contains this point
    containing_basins = basins_gdf[basins_gdf.geometry.contains(point)]
    
    if len(containing_basins) > 0:
        # Return the first match (there should typically be only one)
        return containing_basins.iloc[0]['BasinName']
    else:
        # If no exact match, find the nearest basin
        distances = basins_gdf.geometry.distance(point)
        nearest_idx = distances.idxmin()
        nearest_basin = basins_gdf.iloc[nearest_idx]['BasinName']
        nearest_distance = distances.iloc[nearest_idx]
        print(f"Warning: No basin contains point ({lat}, {lon}). Nearest basin is {nearest_basin} at distance {nearest_distance:.4f} degrees")
        return nearest_basin

def get_basin_fish_diversity(basin_name, occ_df):
    """
    Calculate fish diversity metrics for a given basin.
    """
    basin_fish = occ_df[occ_df['1.Basin.Name'] == basin_name]
    
    if len(basin_fish) == 0:
        return {
            'species_count': 0,
            'native_species_count': 0,
            'exotic_species_count': 0,
            'species_list': []
        }
    
    # Count total species
    species_count = basin_fish['6.Fishbase.Valid.Species.Name'].nunique()
    
    # Count native vs exotic species
    native_fish = basin_fish[basin_fish['3.Native.Exotic.Status'] == 'native']
    exotic_fish = basin_fish[basin_fish['3.Native.Exotic.Status'] == 'exotic']
    
    native_species_count = native_fish['6.Fishbase.Valid.Species.Name'].nunique()
    exotic_species_count = exotic_fish['6.Fishbase.Valid.Species.Name'].nunique()
    
    # Get species list
    species_list = basin_fish['6.Fishbase.Valid.Species.Name'].unique().tolist()
    
    return {
        'species_count': species_count,
        'native_species_count': native_species_count,
        'exotic_species_count': exotic_species_count,
        'species_list': species_list
    }

def main():
    # Load data
    print("Loading fish occurrence and basin data...")
    basins_df, occ_df, refs_df = load_csv_tables()
    basins_gdf = load_shapefile()
    
    # Parse IBT project coordinates
    print("Parsing IBT project coordinates...")
    ibt_projects = parse_ibt_coordinates()
    
    # Match coordinates to basins and calculate diversity
    results = []
    
    for _, project in ibt_projects.iterrows():
        print(f"\nProcessing project {project['rank']}: {project['basin_pair']}")
        
        # Find sender basin
        sender_basin = find_basin_by_coordinates(
            project['sender_lat'], project['sender_lon'], basins_gdf
        )
        
        # Find receiver basin
        receiver_basin = find_basin_by_coordinates(
            project['receiver_lat'], project['receiver_lon'], basins_gdf
        )
        
        # Get fish diversity for each basin
        sender_diversity = get_basin_fish_diversity(sender_basin, occ_df)
        receiver_diversity = get_basin_fish_diversity(receiver_basin, occ_df)
        
        # Calculate beta diversity (Jaccard dissimilarity)
        sender_species = set(sender_diversity['species_list'])
        receiver_species = set(receiver_diversity['species_list'])
        
        if len(sender_species) == 0 and len(receiver_species) == 0:
            jaccard_similarity = 0
            jaccard_dissimilarity = 0
        else:
            intersection = len(sender_species.intersection(receiver_species))
            union = len(sender_species.union(receiver_species))
            jaccard_similarity = intersection / union if union > 0 else 0
            jaccard_dissimilarity = 1 - jaccard_similarity
        
        result = {
            'rank': project['rank'],
            'basin_pair': project['basin_pair'],
            'project': project['project'],
            'design_flow': project['design_flow'],
            'sender_basin': sender_basin,
            'receiver_basin': receiver_basin,
            'sender_species_count': sender_diversity['species_count'],
            'sender_native_count': sender_diversity['native_species_count'],
            'sender_exotic_count': sender_diversity['exotic_species_count'],
            'receiver_species_count': receiver_diversity['species_count'],
            'receiver_native_count': receiver_diversity['native_species_count'],
            'receiver_exotic_count': receiver_diversity['exotic_species_count'],
            'jaccard_similarity': jaccard_similarity,
            'jaccard_dissimilarity': jaccard_dissimilarity,
            'shared_species_count': len(sender_species.intersection(receiver_species)),
            'total_unique_species': len(sender_species.union(receiver_species))
        }
        
        results.append(result)
        
        print(f"  Sender basin: {sender_basin} ({sender_diversity['species_count']} species)")
        print(f"  Receiver basin: {receiver_basin} ({receiver_diversity['species_count']} species)")
        print(f"  Jaccard dissimilarity: {jaccard_dissimilarity:.3f}")
    
    # Convert to DataFrame and save
    results_df = pd.DataFrame(results)
    output_file = os.path.join(DATA_DIR, "IBT_Fish_Diversity_Results.csv")
    results_df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    # Print summary
    print("\nSummary of IBT Projects with Fish Diversity:")
    print("=" * 60)
    for _, row in results_df.iterrows():
        print(f"{row['rank']:2d}. {row['basin_pair']}")
        print(f"    Sender: {row['sender_species_count']} species, Receiver: {row['receiver_species_count']} species")
        print(f"    Dissimilarity: {row['jaccard_dissimilarity']:.3f}")
        print()

if __name__ == "__main__":
    main()