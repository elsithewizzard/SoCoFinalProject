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
Using the **Python Reddit API Wrapper (PRAW)** to scrape `r/gaming`:
* **Target:** "Top" posts where the game name is featured in the title.
* **Engagement Metric:** Sum of upvotes.
* **Valence Metric:** Upvote/downvote ratio of the top 50 posts.

## 4. Methods of Analysis
**Assigned to: Elias & Alina**

We will employ three primary statistical methods:

1. **Spearman Rank Correlation:** Chosen to handle outliers and right-skewed gaming data. We will test the correlation between upvotes and recommendations (H1) and upvotes and playtime (H2).
2. **OLS Regression:** To measure the independent influence of variables (upvotes, valence, price) on playtime and player count.
3. **Mann-Whitney U-test:** To compare distributions between groups (F2P vs. B2P) without assuming normal distribution (H3).