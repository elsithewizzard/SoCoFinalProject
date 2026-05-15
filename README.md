# SoCoFinalProject Steam Game Stats & Reddit Hype Correlation
**Social Computing - 2026**

### Group Members:
* **Data Collection:** Antonio & Jacob
* **Data Analysis:** Elias & Alina

**Reference:** Presentation: "Steam Game Stats & Reddit Hype" 
```⮕  The markdown was originally generated with Gemini based on our Research Proposal Presentation Slides: "Steam Game Stats & Reddit Hype"```

## 1. Motivation
Understanding social media dynamics is valuable for game studios, publishers, and developers to:
* Determine if a game's success is due to **long-term retention** or **short-term hype**.
* Evaluate if "hype-focused" launch strategies or general marketing are worth the investment compared to traditional development.
* Link public social signals to behavioral outcomes (e.g., playtime and sales).

## 2. Research Framework
### Research Questions
* **RQ1:** Are the number of user recommendations higher when engagement on Reddit is high?
* **RQ2:** Does Reddit engagement correlate with actual time spent on the game?

### Hypotheses
* **H1:** There are more user recommendations when engagement on Reddit is high.
* **H2:** For Buy-to-Play (B2P) games, median playtime is lower when Reddit engagement is high.
* **H3:** Among high-engagement games, Free-to-Play (F2P) titles have lower median playtime than B2P titles.

## 3. Data Collection Methodology
**Assigned to: Antonio & Jacob**

### Steam Data (Kaggle Dataset)
We are extracting the following features:
* `name`: Game title
* `recommendations`: User recommendation count
* `average_playtime_forever` & `median_playtime_forever`
* `price`: To distinguish between F2P (0.0) and B2P games
* `peak_ccu`: Peak concurrent users

### Reddit Engagement Data (PRAW)
Because Reddit's Data API now requires approval we were not able to aquire it thus we used Reddit's **public JSON endpoints** (`/r/<sub>/search.json`) instead of PRAW. The endpoint returns the same post fields PRAW would expose (`title`, `score`, `upvote_ratio`, `num_comments`, `created_utc`, `permalink`). We send a unique `User-Agent` on every request and sleep 1.1 s between calls, staying under Reddit's 60 req/min unauthenticated limit.

* **Notebook:** `SoCoFinalProject/Reddit_Ewom.ipynb`
* **Subreddit:** `r/gaming` only (`restrict_sr=1`).
* **Sort & cap:** `sort=top, t=all, limit=100` — top 100 posts of all time per search.
* **Date window:** posts whose `created_utc` falls between **2021-01-01** and **2025-12-31** are kept; everything else is discarded.
* **Game name source:** `games_with_aliases.csv` (one row per unique game from `games_master_player_counts.csv`, deduplicated by `app_id` / `game_name`).

#### Per-game search strategy

For every game we issue **one Reddit search per name variant** and merge the results (deduplicated by post `id`):

* The dataset name itself (after normalisation — `™ ® ©` stripped, curly quotes unified, `(2007)`-style parentheticals dropped, whitespace collapsed).
* All aliases from the `aliases` column of `games_with_aliases.csv` (pipe-separated). The aliases column contains:
  * **Rule-based alternates** — publisher prefixes stripped (`STAR WARS`, `Tom Clancy's`, `Marvel's`, `Disney's`, `LEGO`) and edition suffixes stripped (`Definitive Edition`, `Anniversary Edition`, `Game of the Year Edition`, etc.).
  * **Hand-curated abbreviations** for ~100 well-known games (e.g. `KOTOR`, `R6`, `RDR2`, `FFXIV`, `BG3`, `CK3`, `MWO`, `OSRS`, `PvZ Battle for Neighborville`).

A returned post is **kept** if its title contains any of the variant strings as a case-insensitive substring (after the same normalisation) AND if it falls inside the 2021-2025 window. We deliberately use substring matching rather than word-boundary regex to maximise recall on titles like `'Pacify' is terrifying` or `KOTOR remake update`.

#### Metrics computed per game

* **`engagement`** — sum of `score` (net upvotes) across all kept posts.
* **`valence`** — mean `upvote_ratio` of the top 50 kept posts by `score`. Reflects how positively the game is received (1.0 = unanimous upvote, 0.5 = controversial).
* **`n_posts`** — count of kept posts (sanity / coverage column).

#### Output files

Two CSVs land next to the notebook, both saved every 25 games and supporting resume:

1. **`games_reddit.csv` — one row per game** 
   * `app_id`, `game_name`, `peak_players` 
   * `num_aliases`, `aliases` 
   * `engagement`, `valence`, `n_posts`

2. **`reddit_posts.csv` — one row per matched post** 
   * `app_id`, `game_name` 
   * `title`, `score`, `upvote_ratio`, `num_comments`
   * `created_utc` 
   * `permalink` 

## 4. Methods of Analysis
**Assigned to: Elias & Alina**

We will employ three primary statistical methods:

1. **Spearman Rank Correlation:** Chosen to handle outliers and right-skewed gaming data. We will test the correlation between upvotes and recommendations (H1) and upvotes and playtime (H2).
2. **OLS Regression:** To measure the independent influence of variables (upvotes, valence, price) on playtime and player count.
3. **Mann-Whitney U-test:** To compare distributions between groups (F2P vs. B2P) without assuming normal distribution (H3).
