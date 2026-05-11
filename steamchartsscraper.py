# Steam Charts Scraper
#
#Use "steamgames.csv" for the list of games. Make sure there are headers in the file cause the script skips that first row. We can change if needed.
#
#The script takes player data from https://steamcharts.com and stores each games data in its own csv. Example "Stardew Valley_playercount.csv".

#We are extracting the following features from steamcharts.com:
#* `Month`: Period of the data collected. 
#* `Avg. Players`: Average players during that month.
#* 'Gain': Number of players gained/lost during that month.
#* `% Gain`: Percent of players gained/lost in players during that month.
#* `Peak Players`: Peak concurrent users during that month.

###-----------------------------------------------------------------------------------------------------------------------------------------------------


import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import quote

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

csv_file = "steamgames.csv"

with open(csv_file, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    all_rows = list(reader)

games = []
for row in all_rows:
    if row and row[0].strip():
        games.append(row[0].strip())

# Skip header row if present
if games and games[0].lower() in ['game', 'name', 'title', 'game name']:
    games = games[1:]

# Check for cookies on first page load only
first_load = True

# Loop through each game
for game in games:
    print(f"\n{'=' * 60}")
    print(f"Processing: {game}")
    print(f"{'=' * 60}")

    try:
        url = f"https://steamcharts.com/search/?q={quote(game)}"
        print(url)

        driver.get(url)

        # Only check for cookies on first load
        if first_load:
            try:
                cookies = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div/div[3]/div[1]/div[2]'))
                )
                cookies.click()
                print("Cookie popup accepted")
            except TimeoutException:
                print("No cookie popup found, continuing...")
            first_load = False

        # Wait for the game link to be clickable
        click_game = wait.until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/table/tbody/tr[1]/td[2]/a'))
        )
        click_game.click()

        # Wait for table to be visible
        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//table/tbody/tr"))
        )

        # Extract table data
        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
        table_data = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            month = cells[0].text
            avg_players = cells[1].text
            gain = cells[2].text
            percent_gain = cells[3].text
            peak_players = cells[4].text

            table_data.append([month, avg_players, gain, percent_gain, peak_players])

        # Export to CSV
        filename = f"{game}_playercount.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Month', 'Avg. Players', 'Gain', '% Gain', 'Peak Players'])
            writer.writerows(table_data)

        print(f"{game} player data exported to {filename}")

    except Exception as e:
        print(f"Error processing {game}: {str(e)}")
        continue

print(f"\n{'=' * 60}")
print("All games processed!")
print(f"{'=' * 60}")

driver.quit()
