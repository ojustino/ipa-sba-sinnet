# Valid `attrs` dictionaries

Both **`DownloadStats`** and **`ConstructURL`** can take a **dictionary-typed keyword argument** named `attrs` to help **filter the match data returned by a query**. This dictionary's documentation merits its own page because Tennis Abstract doesn't have a public API and its structure is liable to change at any moment, 

## `attrs` may contain any or all of the following keys and values:

### `'start date'` : *pandas.Timestamp or datetime.datetime*
- Limit query to matches on or after the given date. **If you use this key, you must also use `'end_date'`**.

### `'end date'` : *pandas.Timestamp or datetime.datetime*
- Limit query to matches on or before the given date. **If you use this key, you must also use `'start_date'`**.

### `'head-to-head'` : *str, or list of str*
- Name(s) of opposing player(s) in eligible matches. Should be from the same tour as the originally queried player.
- *Note: As with the original player, make sure there are non-letter characters between each unit of the name (e.g., 'Serena Williams' and 'Jo-Wilfried Tsonga' are fine, but 'SerenaWilliams' and 'JoWilfried Tsonga' are not.)*

### `'exclude opp'` : *str, or list of str*
- Name(s) of opposing player(s) to be excluded from eligible matches. Besides that, follows similar rules as key `'head-to-head'`.

### `'surface'` : *str, or list of str*
- The surface(s) upon which eligible matches were played. Value(s) can be **'hard'**, **'clay'**, **'grass'**, and/or **'carpet'**.

### `'level'` : *str, or list of str*
- The tier(s) of tournaments at which eligible matches were played. Value(s) can be **'Grand Slam'**, **'Masters'** (for ATP/male players), **'Premier'** (for WTA/female players), or **'All Tour'** (excluding matches in minor leagues).

### `'event'` : *str, or list of str*
- The name(s) of eligible tournaments. Mostly features classic/major tournaments and joint ATP/WTA events. Value(s) can be:
    - **'Australian Open'**
    - **'Roland Garros'** or **'French Open'**
    - **'Wimbledon'**
    - **'US Open'**
    - **'Tour Finals'**
        - *Note: May not return matching results for the 2014 and 2015 WTA Finals. The WTA's Avon (1979-82) and Virginia Slims (1972-78) tour finals may be missing or incomplete.*
    - **'Olympics'**
    - **'Davis Cup'** (ATP) or **'Fed Cup'** (WTA)
    - **'Indian Wells'**
    - **'Miami'**
    - **'Madrid'**
    - **'Rome'**
    - **'Washington'**
    - **'Canada'**
        - *Note: May not return matching results for the ATP's pre-1990 iterations of this event.*
    - **'Cincinnati'**
    - **'Beijing'**
    
### `'round'` : *str, or list of str*
- The round(s) in which eligible matches took place. Value(s) can be:
    - **'Final'**, **'Finals'**, or **'F'**
    - **'Semifinal'**, **'Semifinals'**, or **'SF'**
    - **'Quarterfinal'**, **'Quarterfinals'**, or **'QF'**
    - **'R16'** or **'Round Of 16'**
    - **'R32'** or **'Round Of 32'**
    - **'R64'** or **'Round Of 64'**
    - **'R128'** or **'Round Of 128'**
- The following values are also eligible, but only for ATP players:
    - **'First Round'** or **'1R'**
    - **'Second Round'** or **'2R'**
    - **'Third Round'** or **'3R'**
    - **'First Match'**
    - **'Second Match'**
    - **'Third Match'**
    
### `'sets'` : *str, or list of str*
- The number of sets it took to complete eligible matches. Value(s) can be:
    - **'straight sets'** or **'straights'**
    - **'deciding set'** or **'decider'**
    - **'best of 3 sets'**
- The following values are also eligible, but only for ATP players:
    - **'2 of 3 sets'** or **'2/3 sets'**
    - **'3 of 3 sets'** or **'3/3 sets'**
    - **'4 of 5 sets'** or **'4/5 sets'**
    - **'5 of 5 sets'** or **'5/5 sets'**
    
### `'score'` : *str, or list of str*
- Eligible matches must include at least one set with that matches a score condition. Build conditions with:
    1. **'won'** or **'lost'** or **'all'** (includes both sets won and lost by a certain score)
    2. a score from **'6-0'**, **'6-1'**, **'7-5'**, or **'7-6'**/**'tiebreak'**,
- *(examples would be 'all 7-6' for all matches featuring at least one tiebreak; ['lost 6-0', 'lost 6-1'] for all matches where the player lost at least one set 6-0 or 6-1; etc.)*

### `'as rank'` : *str*
- The player's tour ranking at the time of eligible matches. The value can be:
    - **'Number 1'**
    - **'Top 5'**
    - **'Top 10'**
    - **'Top 20'**
    - **'Top 50'**
    - **'Below 50'**
    
### `'vs rank'` : *str or tuple*
- The opponent's tour ranking at the time of eligible matches. The value can be:
    - **'Top 5'**
    - **'Top 10'**
    - **'Top 20'**
    - **'Top 50'**
    - **'Top 100'**
    - **a tuple** with your desired, inclusive range, like (9, 16)
    
### `'vs current rank'` : *str*
- The opponent's ranking or career status *at the time of the query* in eligible matches. **Not available for WTA players**. The value can be:
    - **'Top 10',**
    - **'Top 20'**
    - **'Top 50'**
    - **'Top 100'**
    - **'Active'**
    - **'Inactive'**
    
### `'as entry'` : *str, or list of str*
- The player's entry status in eligible tournaments. Value(s) can be:
    - **'Seeded'**
    - **'Unseeded'**
    - **'Qualifier'** _(includes lucky loser)_
    - **'Wild Card'**
    
### `'vs entry'` : *str, or list of str*
- The opponent's entry status in eligible tournaments. Takes same values as key `'as-entry'`.

### `'vs hand'` : *str*
- The opponent's dominant hand in eligible matches. The value can be **'right'** or **'left'**.

### `'vs height'` : *str*
- The opponent's height (in feet and inches) in eligible matches. For ATP players, the value can be:
    - **"Under 5'10"**
    - **"Under 6'0"**
    - **"Over 6'2"**
    - **"Over 6'4"**
- For WTA players, the value can be:
    - **"Under 5'6"**
    - **"Under 5'8"**
    - **"Over 5'10"**
    - **"Over 6'0"**
