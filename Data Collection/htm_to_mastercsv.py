#!/usr/bin/env python3
"""
Most Played Games 2021 Consolidator
Consolidates game data from multiple HTML files into a single master CSV
Extracts: game_name, app_id, tag, 2021_peak_players
"""

import re
import csv
import sys
import os
from pathlib import Path
from html import unescape
import glob


def extract_tag_from_title(html_content):
    """
    Extract the tag/genre from the HTML page title
    
    Examples:
        "Most played Massively Multiplayer Games Steam Charts in 2021" -> "Massively Multiplayer"
        "Most played Action Games Steam Charts in 2021" -> "Action"
    
    Args:
        html_content: The HTML content as string
        
    Returns:
        str: The tag name, or None if not found
    """
    title_match = re.search(r'<title>Most played (.+?) Games Steam Charts in 2021', html_content)
    if title_match:
        return title_match.group(1)
    return None


def parse_html_file(html_file_path):
    """
    Parse HTML file and extract game data
    
    Args:
        html_file_path: Path to the HTML file
        
    Returns:
        Tuple of (list of game dicts, tag name, was_successful bool)
    """
    # Read the HTML file
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return None, None, False
    
    # Extract tag from title
    tag = extract_tag_from_title(content)
    if not tag:
        print(f"  ✗ Could not extract tag from page title")
        return None, None, False
    
    # Find tbody
    tbody_match = re.search(r'<tbody>(.+?)</tbody>', content, re.DOTALL)
    if not tbody_match:
        print(f"  ✗ Could not find tbody in HTML")
        return None, None, False
    
    tbody_content = tbody_match.group(1)
    
    # Find all game rows
    rows = re.findall(
        r'<tr class="app" data-appid="(\d+)"[^>]*>(.+?)</tr>',
        tbody_content,
        re.DOTALL
    )
    
    if not rows:
        print(f"  ✗ No game rows found")
        return None, None, False
    
    print(f"  ✓ Found {len(rows)} games with tag: {tag}")
    
    # Limit to top 500 games per file
    rows = rows[:500]
    
    games = []
    
    for appid, row_content in rows:
        # Extract game name
        name_match = re.search(
            r'<td><a class="b" href="/app/\d+/charts/">([^<]+)</a></td>',
            row_content
        )
        game_name = unescape(name_match.group(1)) if name_match else ""
        
        # Extract peak players (the second numeric td with data-sort)
        # Pattern: <td data-sort="XXX">YYY,ZZZ</td>
        data_sort_matches = re.findall(
            r'<td data-sort="(\d+)">[\d,]+</td>',
            row_content
        )
        
        # The peak players is typically the second numeric value
        peak_players = data_sort_matches[1] if len(data_sort_matches) > 1 else ""
        
        games.append({
            'game_name': game_name,
            'app_id': appid,
            'tag': tag,
            '2021_peak_players': peak_players
        })
    
    return games, tag, True


def process_batch(input_folder, output_file):
    """
    Process all HTML files in a folder and create master CSV
    
    Args:
        input_folder: Folder containing HTML files
        output_file: Path to output master CSV file
    """
    
    print(f"\n{'='*80}")
    print(f"MOST PLAYED GAMES 2021 CONSOLIDATOR")
    print(f"{'='*80}")
    print(f"Input folder:  {input_folder}")
    print(f"Output file:   {output_file}\n")
    
    # Find all HTML files
    html_files = sorted(glob.glob(os.path.join(input_folder, '*.htm')))
    html_files += sorted(glob.glob(os.path.join(input_folder, '*.html')))
    
    if not html_files:
        print(f"✗ No HTML files found in {input_folder}")
        return
    
    print(f"Total files found: {len(html_files)}\n")
    
    results = {
        'successful': 0,
        'failed': 0,
        'total_games': 0,
        'files': []
    }
    
    all_games = []
    
    for html_file in html_files:
        filename = os.path.basename(html_file)
        print(f"Processing: {filename}")
        
        # Parse HTML
        games, tag, success = parse_html_file(html_file)
        
        if not success or games is None:
            results['failed'] += 1
            continue
        
        results['successful'] += 1
        results['total_games'] += len(games)
        results['files'].append({
            'filename': filename,
            'tag': tag,
            'games': len(games)
        })
        
        all_games.extend(games)
        print()
    
    # Write master CSV
    if all_games:
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['game_name', 'app_id', 'tag', '2021_peak_players']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(all_games)
            
            print(f"{'='*80}")
            print(f"CONSOLIDATION SUMMARY")
            print(f"{'='*80}")
            print(f"Files processed:     {results['successful']}")
            print(f"Files failed:        {results['failed']}")
            print(f"Total games:         {results['total_games']:,}")
            print(f"\n{'='*80}\n")
            
            if results['files']:
                print("Files consolidated:\n")
                print(f"{'Filename':<60} {'Tag':<25} {'Games':<8}")
                print(f"{'-'*80}")
                
                for file_info in results['files']:
                    print(f"{file_info['filename']:<60} {file_info['tag']:<25} {file_info['games']:<8}")
            
            print(f"\n{'='*80}")
            print(f"Master CSV created: {output_file}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"✗ Error writing master CSV: {e}")
    else:
        print(f"✗ No games found to consolidate")


def main():
    """Main function"""
    
    # Configuration
    input_folder = "Most Played Games 2021"
    output_file = "games_master_2021.csv"
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Verify input folder exists
    if not Path(input_folder).exists():
        print(f"Error: Input folder not found: {input_folder}")
        print(f"\nUsage:")
        print(f"  python consolidate_games.py [input_folder] [output_file]")
        print(f"\nExamples:")
        print(f"  python consolidate_games.py")
        print(f"  python consolidate_games.py 'Most Played Games 2021' 'games_master_2021.csv'")
        print(f"  python consolidate_games.py './html_files' './output/master.csv'")
        sys.exit(1)
    
    # Process batch
    process_batch(input_folder, output_file)


if __name__ == "__main__":
    main()
