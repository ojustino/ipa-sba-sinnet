### Notes on Tennis Abstract attributes + how to encode their values.
*these are put to use in `_validate_attrs` and its associated methods. still
a work in progress.*

_(note that you only need one `'&f='` per URL; concatenate categories if
 more than one takes that prefix)_

**first batch**:
- [X] Time Span
    - form in URL for a year: `'&f=YYYYqq'`
    - form in URL for a custom range: `'&f=AcxYYYYMMD1YYYYMMD2qq'`
    - form in URL for career: `'&f=ACareerqq'` (my default)
    - take either both of `'start_date'` and `'end_date'`  or none, perhaps as
    datetimes.
    - _note that dates are when the tournament began, not when the actual
    match was played_
- [X] Head-to-Head
    - in URL: `'&q=FirstLast'`
    - it's also possible to add multiple head-to-heads; just comma separate
    them in the URL: `'&q=FirstLast1,FirstLast2'`
    - should also make use of `NameCheck()` class, like in `generate_url()`
- [X] Exclude Opp
    - in URL: `'&x=FirstLast'`
    - it's also possible to exclude multiple head-to-heads; just comma
    separate them in the URL: `'&x=FirstLast1,FirstLast2'`
    - should also utilize `NameCheck()` class, like in `generate_url()`
- [X] Surface **(does not make a difference in initial URL for ATP
  players...?)**
    - _format: 'lowercase string' (URL code)_
    - 'hard' (`'&f=B0'`), 'clay' (`'&f=B1'`), 'grass' (`'&f=B2'`), 'carpet'
    (`'&f=B3'`)
    - to do multiple, separate numbers with i's: `'&f=B1i2'`
- [X] Level
    - for now, limiting to:
        - 'Grand Slams' (`'&f=C0'`),
        - 'Masters' [men]/'Premiers' [women] (`'&f=C1'`) -- make sure the
        player played in an era that gave tournaments these distinctions,
        - 'All ATP' [men]/'All Tours' [women] (`'&f=C2'`).
    - to do multiple, separate numbers with i's: `'&f=C1i2'`
- [X] Event
    - to convert the names to URLs, just replace spaces with underscores and
    add 'qq', to the end of each name, and separate with commas. **Start the
    string of names with 'D'**.
    - **see `event_labels.md` for more info on why some tournaments require
    multiple labels.**
    - i chose to focus on upper-level tournaments with a bias for joint events,
    though not all are included here. for now, limiting to:
        - `'Australian_Open'`
        - `'Roland_Garros'`
        - `'Wimbledon'`
        - `'US_Open'`
        - `'Tour_Finals'` (men) **OR** `'Shenzhen_Finals'` AND
        `'WTA_Championships'` AND `'WTA_Tour_Championships'` AND
        `'WTA_Finals'` AND `'Singapore'` AND `'Virginia_Slims_Championships'`
        (women)
            - NOTE: 2014-15 singapore finals are labeled `'WTA_Finals'`, but
            are inaccessible via URL...
            - NOTE: `'Avon_Championships'` (1979-82) and first iteration of
            virginia slims (1972-78) are either incomplete or missing
        - `'Olympics'`
        - `'Davis_Cup'` (men) **OR** `'Fed_Cup'` (women)
        - `'Indian_Wells_Masters'` (men) **OR** `'Indian_Wells'` (women)
        - `'Miami_Masters'` (men) **OR** `'Miami'` (women)
        - `'Madrid_Masters'` (men) **OR** `'Madrid'` (women)
        - `'Rome_Masters'` (men) **OR** `'Rome'` (women)
        - `'Washington'`
        - `'Canada_Masters'` (men) **OR** `'Montreal'` AND `'Toronto'` AND
        `'Toronto_'` (women)
        - `'Cincinnati_Masters'` (men) **OR** `'Cincinnati'` (women)
        - `'Beijing'`
- [ ] Other events...?
---
**second batch**
- [X] Round
    - Final (`'&f=E0`)
    - Semis (`'&f=E1'`)
    - Quarters (`'&f=E2'`)
    - R16 (`'&f=E3'`)
    - R32 (`'&f=E4'`)
    - R64 (`'&f=E5'`)
    - R128 (`'&f=E6'`)
    - First Round (`'&f=E7'`) **not available for WTA players.**
    - Second Round (`'&f=E8'`) **not available for WTA players.**
    - Third Round (`'&f=E9'`) **not available for WTA players.**
    - First Match (`'&f=E10'`) **not available for WTA players.**
    - Second Match (`'&f=E11'`) **not available for WTA players.**
    - Third Match (`'&f=E12'`) **not available for WTA players.**
    - to do multiple, separate numbers with i's: `'&f=E1i2'`. **i will only
    allow combinations of the first seven categories** (Final through R128).
- [X] Sets
    - Straight Sets (`'&f=P0'`)
    - Deciding Set (`'&f=P1'`) **does not include best of 5 matches in 1984-98
    WTA Finals** _(try searching the Monica Seles/Gabriela Sabatini H2H with
    this option and you won't find their 1990 WTA Finals match)_
    - Best of 5 Sets (`'&f=P2'`) **not available for WTA players.**
    - 3 of 5 Sets (`'&f=P3'`) **not available for WTA players.**
    - 4 of 5 Sets (`'&f=P4'`) **not available for WTA players.**
    - 5 of 5 Sets (`'&f=P5'`) **not available for WTA players.**
    - Best of 3 Sets (`'&f=P6'`) *not available for WTA players. have to make
    custom case*
    - 2 of 3 Sets (`'&f=P7'`) *not available for WTA players. have to make
    custom case*
    - 3 of 3 Sets (`'&f=P8'`) *not available for WTA players. have to make
    custom case*
    - **i may not allow this**, but to do multiple, separate numbers with i's:
    `'&f=P1i2'`
- [X] Scores
    - All tiebreaks (`'&f=Q0'`)
    - TB won (`'&f=Q1'`)
    - TB lost (`'&f=Q2'`)
    - deciding TB (`'&f=Q3'`) _-- new category?_
    - All 7-5 (`'&f=Q4'`)
    - 7-5 won (`'&f=Q5'`)
    - 7-5 lost (`'&f=Q6'`)
    - All 6-0 (`'&f=Q7'`)
    - 6-0 won (`'&f=Q8'`)
    - 6-0 lost (`'&f=Q9'`)
    - All 6-1 (`'&f=Q10'`)
    - 6-1 won (`'&f=Q11'`)
    - 6-1 lost (`'&f=Q12'`)
    - **i may not allow this**, but to do multiple, separate numbers with i's:
    `'&f=Q1i2'`
____
**third batch**
- [X] as Rank
    - **i figured out that this category's codes change based on the specific
    player's career high, which means these codes only work for players who
    have been number 1. would be great if this attribute worked more like
    'vs Rank'**
    - for now, limiting to:
        - Number 1 (`'&f=G0'`)
        - Top 5 (`'&f=G1'`)
        - Top 10 (`'&f=G2'`)
        - Top 20 (`'&f=G3'`)
        - Top 50 (`'&f=G4'`)
    - **i may not allow this**, but to do multiple, separate numbers with i's:
    `'&f=G1i2'`
- [X] vs Rank
    - for now, limiting to:
        - Top 5 (`'&f=ITop_5'`) *not available for WTA players. have to make
        custom case*
        - Top 10 (`'&f=ITop_10'`)
        - Top 20 (`'&f=ITop_20'`)
        - Top 50 (`'&f=ITop_50'`)
        - Top 100 (`'&f=ITop_100'`)
        - Higher (`'&f=IHigher'`)
        - Lower (`'&f=ILower'`)
        - custom. (for example, all opponents between 14 & 112:
        `'&f=Icx1001410112'`)
    - **remember to add `'qq'` to the end of any of these!!**
    - **i may not allow this**, but to do multiple, separate strings with
    commas and **only print the 'I' once**: `'&f=IHigherqq,Lowerqq`
        - ~~or... maybe only allow combining numbers (e.g., 'Top 10') with
        comparisons (e.g., 'Higher')~~ this doesn't work as i'd like because
        the site uses logical OR (not AND) when combining subcategories
- [X] vs Curr Rank (**not available for WTA players**)
    - Top 10 (`'&f=R0'`)
    - Top 20 (`'&f=R1'`)
    - Top 50 (`'&f=R2'`)
    - Top 100 (`'&f=R3'`)
    - Active (`'&f=R4'`)
    - Inactive (`'&f=R5'`)
    - **i don't think i'll allow this**, to do multiple, separate numbers with
    i's: `'&f=R1i2'`
- [X] as Entry
    - Seeded (`'&f=H0'`)
    - Unseeded (`'&f=H1'`)
    - Qualifier (`'&f=H2'`)
    - Wild Card (`'&f=H3'`)
    - to do multiple, separate numbers with i's: `'&f=H1i2'`
- [X] vs Entry
    - Seeded (`'&f=J0'`)
    - Unseeded (`'&f='J1'`)
    - Qualifier (`'&f=J2'`)
    - Wild Card (`'&f=J3'`)
    - to do multiple, separate numbers with i's: `'&f=J1i2'`
- [X] vs Hand
    - Right (`'&f=K0'`)
    - Left (`'&f=K1'`)
    - **i don't think i'll allow this**, but to do multiple, separate numbers
    with i's: `'&f=K0i1'`
- [X] vs Height
    - Shorter (`'&f=M0'`)
    - Taller (`'&f=M1'`)
    - for women:
        - Under 5'6 (`'&f=M2'`)
        - Under 5'8 (`'&f=M3'`)
        - Over 5'10 (`'&f=M4'`)
        - Over 6'0 (`'&f=M5'`)
    - for men:
        - Under 5'10 (`'&f=M2'`)
        - Under 6'0 (`'&f=M3'`)
        - Over 6'2 (`'&f=M4'`)
        - Over 6'4 (`'&f=M5'`)
    - **i may not allow this**, but to do multiple, separate numbers with i's:
    `'&f=M1i2'`.
---
**still remaining**
- [ ] vs Backhand (*my own creation*; **not available for WTA players**)
    - **i separated this category from 'vs Hand' because I found the lack of a
    logical AND in choosing options confusing.**
      - for example, left hand + one handed backhand brings up Grigor Dimitrov
      (a righty) as a match instead of only limiting to players like
      'Deliciano' Lopez.
    - One-hand BH (`'&f=K2'`)
    - Two-hand BH (`'&f=K3'`)
    - **i may not allow this**, but to do multiple, separate numbers with i's:
    `'&f=K2i3'`.
- [ ] vs Age
    - **i haven't yet deciphered this category's system.** its attribute code
    is 'L' (for men, at least), but nothing shows up for women even though the
    menu is available.
- [ ] Results
    - would like to do this one, just need to figure out how to organize it...
- [ ] vs Country
    - too large of an undertaking for now, but the site uses three letter
    country codes
