#!/usr/bin/env python3
# Steam Charts Scraper - Combined CSV Output
#
# Reads:
#   games_master_2021.csv
#
# Required columns:
#   app_id
#
# Outputs:
#   games_master_player_counts.csv
#
# Output columns:
#   app_id
#   game_name
#   Month
#   Avg. Players
#   Gain
#   % Gain
#   Peak Players

import csv
import sys
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# -----------------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------------

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, 10)

input_csv = "games_master_2021.csv"
output_csv = "games_master_player_counts.csv"

# -----------------------------------------------------------------------------------
# VERIFY INPUT FILE
# -----------------------------------------------------------------------------------

if not Path(input_csv).exists():
    print(f"Error: {input_csv} not found")
    driver.quit()
    sys.exit(1)

print(f"\n{'=' * 70}")
print("STEAM CHARTS SCRAPER - COMBINED CSV")
print(f"{'=' * 70}")
print(f"Input:  {input_csv}")
print(f"Output: {output_csv}")
print()

# -----------------------------------------------------------------------------------
# LOAD INPUT CSV
# -----------------------------------------------------------------------------------

with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    if not reader.fieldnames or "app_id" not in reader.fieldnames:
        print("Error: CSV must contain 'app_id' column")
        print(f"Available columns: {reader.fieldnames}")

        driver.quit()
        sys.exit(1)

    games_data = list(reader)

if not games_data:
    print("Error: No rows found in CSV")

    driver.quit()
    sys.exit(1)

print(f"Loaded {len(games_data)} games\n")

# -----------------------------------------------------------------------------------
# RESULTS STORAGE
# -----------------------------------------------------------------------------------

all_rows = []

successful = 0
failed = 0
failed_games = []

first_load = True

# -----------------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------------

for idx, game_row in enumerate(games_data, start=1):

    app_id = game_row["app_id"].strip()

    if not app_id:
        print(f"[{idx}] Missing app_id, skipping")
        failed += 1
        continue

    print(f"\n{'=' * 70}")
    print(f"[{idx}/{len(games_data)}] Processing app_id: {app_id}")
    print(f"{'=' * 70}")

    try:

        url = f"https://steamcharts.com/app/{app_id}"

        print(f"URL: {url}")

        driver.get(url)

        # --------------------------------------------------------------------------
        # COOKIE POPUP (FIRST LOAD ONLY)
        # --------------------------------------------------------------------------

        if first_load:

            try:
                cookies = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[1]/div[2]')
                    )
                )

                cookies.click()

                print("Cookie popup accepted")

            except TimeoutException:
                print("No cookie popup found")

            first_load = False

        # --------------------------------------------------------------------------
        # WAIT FOR TABLE
        # --------------------------------------------------------------------------

        try:
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//table/tbody/tr")
                )
            )

        except TimeoutException:

            print("⚠ Could not load player data table")

            failed += 1
            failed_games.append(app_id)

            continue

        # --------------------------------------------------------------------------
        # GET GAME NAME
        # --------------------------------------------------------------------------

        try:
            game_name = driver.find_element(By.TAG_NAME, "h1").text.strip()

        except Exception:
            game_name = f"app_{app_id}"

        print(f"Game: {game_name}")

        # --------------------------------------------------------------------------
        # EXTRACT TABLE DATA
        # --------------------------------------------------------------------------

        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

        game_row_count = 0

        for row in rows:

            try:
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) >= 5:

                    month = cells[0].text
                    avg_players = cells[1].text
                    gain = cells[2].text
                    percent_gain = cells[3].text
                    peak_players = cells[4].text

                    all_rows.append([
                        app_id,
                        game_name,
                        month,
                        avg_players,
                        gain,
                        percent_gain,
                        peak_players
                    ])

                    game_row_count += 1

            except Exception as e:
                print(f"Warning: Failed to parse row: {e}")

        if game_row_count == 0:

            print("⚠ No usable data rows found")

            failed += 1
            failed_games.append(app_id)

            continue

        print(f"✓ Collected {game_row_count} monthly records")

        successful += 1

    except Exception as e:

        print(f"✗ Error processing app_id {app_id}: {e}")

        failed += 1
        failed_games.append(app_id)

# -----------------------------------------------------------------------------------
# WRITE COMBINED CSV
# -----------------------------------------------------------------------------------

print(f"\n{'=' * 70}")
print("WRITING COMBINED CSV")
print(f"{'=' * 70}")

with open(output_csv, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "app_id",
        "game_name",
        "Month",
        "Avg. Players",
        "Gain",
        "% Gain",
        "Peak Players"
    ])

    writer.writerows(all_rows)

print(f"✓ Wrote {len(all_rows)} total rows to {output_csv}")

# -----------------------------------------------------------------------------------
# FINAL SUMMARY
# -----------------------------------------------------------------------------------

print(f"\n{'=' * 70}")
print("SCRAPING COMPLETE")
print(f"{'=' * 70}")

print(f"Successful games: {successful}/{len(games_data)}")
print(f"Failed games:     {failed}/{len(games_data)}")
print(f"Total data rows:  {len(all_rows)}")

if failed_games:

    print("\nFailed app_ids:")

    for game in failed_games[:10]:
        print(f"  • {game}")

    if len(failed_games) > 10:
        print(f"  ... and {len(failed_games) - 10} more")

print(f"{'=' * 70}\n")

driver.quit()
