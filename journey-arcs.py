import csv
import json
import os
from collections import defaultdict

def read_csv_data(csv_file):
    """Read the CSV file and organize data by airtag number."""
    airtags_data = defaultdict(list)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            airtag_num = row['Airtags']
            step_num = int(row['step number'])
            lon = float(row['lon'])
            lat = float(row['lat'])
            
            airtags_data[airtag_num].append({
                'step': step_num,
                'lon': lon,
                'lat': lat,
                'name': row['name of location']
            })
    
    # Sort each airtag's locations by step number
    for airtag in airtags_data:
        airtags_data[airtag].sort(key=lambda x: x['step'])
    
    return airtags_data

def create_arc_geojson(start_point, end_point):
    """Create a GeoJSON structure for an arc between two points."""
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [
                        [start_point['lon'], start_point['lat']],
                        [end_point['lon'], end_point['lat']]
                    ],
                    "type": "LineString"
                }
            }
        ]
    }
    return geojson

def generate_arc_files(airtags_data, output_dir='.'):
    """Generate GeoJSON arc files for each airtag journey."""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    generated_files = []
    
    for airtag_num, locations in airtags_data.items():
        # Generate arcs for consecutive steps
        for i in range(len(locations) - 1):
            start_point = locations[i]
            end_point = locations[i + 1]
            
            # Arc number corresponds to the starting step number
            arc_num = start_point['step']
            
            # Create filename
            filename = f"{airtag_num}-arc-{arc_num}.geojson"
            filepath = os.path.join(output_dir, filename)
            
            # Create GeoJSON
            geojson = create_arc_geojson(start_point, end_point)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=None, separators=(',', ':'))
            
            generated_files.append(filename)
            print(f"Created: {filename}")
            print(f"  From: {start_point['name']}")
            print(f"  To: {end_point['name']}")
            print()
    
    return generated_files

def main():
    # Input CSV file
    csv_file = '/mnt/project/Airtag_clothes_project_-_Map_locations__2_.csv'
    
    # Output directory
    output_dir = '/mnt/user-data/outputs'
    
    print("Reading CSV data...")
    airtags_data = read_csv_data(csv_file)
    
    print(f"\nFound {len(airtags_data)} AirTags with tracking data\n")
    print("=" * 60)
    
    print("\nGenerating arc GeoJSON files...\n")
    generated_files = generate_arc_files(airtags_data, output_dir)
    
    print("=" * 60)
    print(f"\nSuccessfully generated {len(generated_files)} arc files!")
    print(f"Files saved to: {output_dir}")
    
    # Summary by airtag
    print("\n" + "=" * 60)
    print("SUMMARY BY AIRTAG:")
    print("=" * 60)
    for airtag_num, locations in sorted(airtags_data.items(), key=lambda x: int(x[0])):
        num_arcs = len(locations) - 1
        print(f"AirTag #{airtag_num}: {len(locations)} locations, {num_arcs} arcs")

if __name__ == "__main__":
    main()