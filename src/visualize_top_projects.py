#!/usr/bin/env python3
"""
Create attractive visualizations for top 5 IBT projects by flow volume.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set style
plt.style.use('default')
sns.set_palette("husl")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "data"))

def parse_flow_value(flow_str):
    """Extract numeric flow value from string like '≈ 200' or '44.8'"""
    # Remove non-numeric characters except decimal points
    numeric_str = re.sub(r'[^\d.]', '', str(flow_str))
    if numeric_str:
        return float(numeric_str)
    return 0

def create_flow_visualization(flow_value, ax, title="Design Flow"):
    """Create a flow volume bar chart"""
    ax.bar([0], [flow_value], color='steelblue', alpha=0.7, width=0.6)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0, max(flow_value * 1.1, 1))
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylabel('Flow (km³/yr)', fontsize=10)
    ax.set_xticks([])
    
    # Add value annotation
    ax.text(0, flow_value/2, f'{flow_value:.1f}\nkm³/yr', 
            ha='center', va='center', fontweight='bold', fontsize=11, color='white')

def create_species_bar_chart(native_count, exotic_count, ax, title, basin_name):
    """Create stacked bar chart for native vs exotic species"""
    total = native_count + exotic_count
    
    # Create stacked bars
    ax.bar([0], [native_count], color='forestgreen', alpha=0.8, label='Native', width=0.6)
    ax.bar([0], [exotic_count], bottom=[native_count], color='orangered', alpha=0.8, label='Exotic', width=0.6)
    
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0, max(total * 1.1, 1))
    ax.set_title(f'{title}\n({basin_name})', fontsize=12, fontweight='bold')
    ax.set_ylabel('Species Count', fontsize=10)
    ax.set_xticks([])
    
    # Add count annotations
    if native_count > 0:
        ax.text(0, native_count/2, str(native_count), ha='center', va='center', 
                fontweight='bold', color='white', fontsize=11)
    if exotic_count > 0:
        ax.text(0, native_count + exotic_count/2, str(exotic_count), ha='center', va='center', 
                fontweight='bold', color='white', fontsize=10)
    
    # Total count annotation
    ax.text(0, total + total*0.05, f'Total: {total}', ha='center', va='bottom', 
            fontweight='bold', fontsize=11)
    
    # Legend only on first subplot
    if title == "Sender Basin":
        ax.legend(loc='upper right', fontsize=9)

def create_dissimilarity_gauge(dissimilarity, ax, title="Jaccard Dissimilarity"):
    """Create a gauge-style visualization for dissimilarity score"""
    # Create semicircle gauge
    theta = np.linspace(0, np.pi, 100)
    radius = 1
    
    # Background arc (gray)
    ax.plot(radius * np.cos(theta), radius * np.sin(theta), 'lightgray', linewidth=20, alpha=0.3)
    
    # Colored arc based on dissimilarity level
    if dissimilarity < 0.3:
        color = 'green'
        level = 'Low'
    elif dissimilarity < 0.7:
        color = 'orange'
        level = 'Medium'
    else:
        color = 'red'
        level = 'High'
    
    # Draw arc up to dissimilarity value
    theta_fill = np.linspace(0, np.pi * dissimilarity, 50)
    ax.plot(radius * np.cos(theta_fill), radius * np.sin(theta_fill), color, linewidth=20)
    
    # Add needle
    needle_angle = np.pi * (1 - dissimilarity)  # Reverse for gauge
    needle_x = 0.8 * np.cos(needle_angle)
    needle_y = 0.8 * np.sin(needle_angle)
    ax.arrow(0, 0, needle_x, needle_y, head_width=0.05, head_length=0.05, 
             fc='black', ec='black', linewidth=2)
    
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    # Add value and level text
    ax.text(0, -0.1, f'{dissimilarity:.3f}\n({level} Risk)', ha='center', va='top', 
            fontsize=12, fontweight='bold')
    
    # Add scale labels
    ax.text(-1, 0, '0.0', ha='center', va='center', fontsize=9)
    ax.text(1, 0, '1.0', ha='center', va='center', fontsize=9)
    ax.text(0, 1, '0.5', ha='center', va='center', fontsize=9)

def create_project_visualization(project_data, output_dir):
    """Create 2x2 subplot visualization for a single project"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"Rank #{project_data['rank']}: {project_data['basin_pair']}\n{project_data['project']}", 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Parse flow value
    flow_value = parse_flow_value(project_data['design_flow'])
    
    # Top left: Flow volume
    create_flow_visualization(flow_value, axes[0, 0], "Design Flow Volume")
    
    # Top right: Sender basin species
    create_species_bar_chart(
        project_data['sender_native_count'], 
        project_data['sender_exotic_count'],
        axes[0, 1], 
        "Sender Basin", 
        project_data['sender_basin']
    )
    
    # Bottom left: Receiver basin species
    create_species_bar_chart(
        project_data['receiver_native_count'], 
        project_data['receiver_exotic_count'],
        axes[1, 0], 
        "Receiver Basin", 
        project_data['receiver_basin']
    )
    
    # Bottom right: Dissimilarity gauge
    create_dissimilarity_gauge(project_data['jaccard_dissimilarity'], axes[1, 1])
    
    plt.tight_layout()
    
    # Save figure
    filename = f"rank_{project_data['rank']:02d}_{project_data['basin_pair'].replace(' → ', '_to_').replace('/', '_').replace(' ', '_')}.png"
    filename = re.sub(r'[^\w\-_.]', '', filename)  # Remove special characters
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filepath

def main():
    # Load results
    results_file = os.path.join(DATA_DIR, "IBT_Fish_Diversity_Results.csv")
    df = pd.read_csv(results_file)
    
    # Parse flow values and get top 5
    df['flow_numeric'] = df['design_flow'].apply(parse_flow_value)
    top_5 = df.nlargest(5, 'flow_numeric')
    
    # Create output directory
    output_dir = os.path.join(DATA_DIR, "visualizations")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating visualizations for top 5 IBT projects by flow volume:")
    print("=" * 70)
    
    created_files = []
    
    for idx, (_, project) in enumerate(top_5.iterrows(), 1):
        print(f"{idx}. Rank #{project['rank']}: {project['basin_pair']}")
        print(f"   Flow: {project['design_flow']} km³/yr")
        print(f"   Dissimilarity: {project['jaccard_dissimilarity']:.3f}")
        
        filepath = create_project_visualization(project, output_dir)
        created_files.append(filepath)
        print(f"   Saved: {os.path.basename(filepath)}")
        print()
    
    # Create summary visualization
    create_summary_comparison(top_5, output_dir)
    
    print(f"All visualizations saved to: {output_dir}")
    return created_files

def create_summary_comparison(top_5_df, output_dir):
    """Create a summary comparison chart of all top 5 projects"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Top 5 IBT Projects Comparison by Flow Volume', fontsize=18, fontweight='bold')
    
    # Prepare data
    projects = [f"#{row['rank']}: {row['basin_pair'].split(' → ')[0][:15]}..." for _, row in top_5_df.iterrows()]
    flows = [parse_flow_value(row['design_flow']) for _, row in top_5_df.iterrows()]
    sender_totals = [row['sender_species_count'] for _, row in top_5_df.iterrows()]
    receiver_totals = [row['receiver_species_count'] for _, row in top_5_df.iterrows()]
    dissimilarities = [row['jaccard_dissimilarity'] for _, row in top_5_df.iterrows()]
    
    # Colors for each project
    colors = sns.color_palette("husl", len(top_5_df))
    
    # Flow volumes
    axes[0, 0].bar(range(len(flows)), flows, color=colors, alpha=0.8)
    axes[0, 0].set_title('Design Flow Volume', fontsize=14, fontweight='bold')
    axes[0, 0].set_ylabel('Flow (km³/yr)', fontsize=12)
    axes[0, 0].set_xticks(range(len(projects)))
    axes[0, 0].set_xticklabels(projects, rotation=45, ha='right')
    
    # Species counts comparison
    x = np.arange(len(projects))
    width = 0.35
    axes[0, 1].bar(x - width/2, sender_totals, width, label='Sender Basin', alpha=0.8)
    axes[0, 1].bar(x + width/2, receiver_totals, width, label='Receiver Basin', alpha=0.8)
    axes[0, 1].set_title('Species Count Comparison', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylabel('Species Count', fontsize=12)
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(projects, rotation=45, ha='right')
    axes[0, 1].legend()
    
    # Dissimilarity scores
    bars = axes[1, 0].bar(range(len(dissimilarities)), dissimilarities, color=colors, alpha=0.8)
    axes[1, 0].set_title('Jaccard Dissimilarity Scores', fontsize=14, fontweight='bold')
    axes[1, 0].set_ylabel('Dissimilarity (0-1)', fontsize=12)
    axes[1, 0].set_xticks(range(len(projects)))
    axes[1, 0].set_xticklabels(projects, rotation=45, ha='right')
    axes[1, 0].set_ylim(0, 1)
    
    # Add risk level colors to dissimilarity bars
    for bar, dissim in zip(bars, dissimilarities):
        if dissim < 0.3:
            bar.set_color('green')
        elif dissim < 0.7:
            bar.set_color('orange')
        else:
            bar.set_color('red')
    
    # Flow vs Dissimilarity scatter
    axes[1, 1].scatter(flows, dissimilarities, c=colors, s=100, alpha=0.8)
    axes[1, 1].set_title('Flow Volume vs Ecological Risk', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Design Flow (km³/yr)', fontsize=12)
    axes[1, 1].set_ylabel('Jaccard Dissimilarity', fontsize=12)
    
    # Add project labels to scatter plot
    for i, (flow, dissim) in enumerate(zip(flows, dissimilarities)):
        axes[1, 1].annotate(f"#{top_5_df.iloc[i]['rank']}", 
                           (flow, dissim), 
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # Save summary
    summary_path = os.path.join(output_dir, "top_5_projects_summary.png")
    plt.savefig(summary_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Summary comparison saved: {os.path.basename(summary_path)}")

if __name__ == "__main__":
    main()