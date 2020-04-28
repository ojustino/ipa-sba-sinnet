import pytest

from construct_query import DownloadStats
from datetime import datetime
from validate_attrs import ValidateURLAttrs

# expect the entire test to take about 1 minute to run

val_obj = ValidateURLAttrs()

# remember that capitalization is typically not important in attribute values
validations = [
    # h2h and exclude (lists and strings)
    # these take longer because they use NameCheck to connect to the site
    {'tour': 'ATP', 'attrs': {'head-to-head': ['jo-wi tsong', 'gael mONf']},
     'expect': '&f=ACareerqq&q=JoWilfriedTsonga,GaelMonfils'},
    {'tour': 'ATP', 'attrs': {'exclude opp': ['jo-wi tsong', 'gael mONf']},
     'expect': '&f=ACareerqq&x=JoWilfriedTsonga,GaelMonfils'},
    {'tour': 'WTA', 'attrs': {'exclude opp': 'Sab Lisi'},
     'expect': '&f=ACareerqq&x=SabineLisicki'},
    {'tour': 'WTA', 'attrs': {'head-to-head': ['Venus', 'bia rees']},
     'expect': '&f=ACareerqq&q=VenusWilliams,BiancaAndreescu'},
    {'tour': 'ATP', 'attrs': {'head-to-head': ['juan potro']},
     'expect': '&f=ACareerqq&q=JuanMartinDelPotro'},
    {'tour': 'ATP', 'attrs': {'head-to-head': 'Art Ash'},
     'expect': '&f=ACareerqq&q=ArthurAshe'},

    # date-related attributes (datetimes, no tour needed)
    {'tour': None, 'attrs': {'start date': datetime(2003, 12, 11)},
     'error': ValueError,
     'error-msg': ("'start date' and 'end date' must both be present "
                   "or absent in your 'attrs' dict.")},
    {'tour': None, 'attrs': {'start date': datetime(2003, 12, 11),
                             'end date': datetime(2001, 12, 11)},
                             # misordered dates -- they'll be corrected
     'expect': '&f=Acx2001121120031211qq'},
    {'tour': None, 'attrs': {'start date': datetime(1991, 2, 11),
                             'end date': datetime(1993, 2, 11)},
     'expect': '&f=Acx1991021119930211qq'},

    # surface (lists and strings, no tour needed)
    {'tour': None, 'attrs': {'surface': 'dirt'},
     'error': ValueError,
     'error-msg': ("Invalid value for key 'surface'. Choose from 'hard', "
                   "'clay', 'grass', and 'carpet'.")},
    {'tour': None, 'attrs': {'surface': 'grass'},
     'expect': '&f=ACareerqqB2'},
    {'tour': None, 'attrs': {'surface': ['clay', 'carpet']},
     'expect': '&f=ACareerqqB1i3'},

    # event (lists and strings)
    {'tour': 'ATP', 'attrs': {'event': 'Olympics'},
     'expect': '&f=ACareerqqDOlympicsqq'},
    {'tour': 'WTA', 'attrs': {'event': 'Canada'},
     'expect': '&f=ACareerqqDMontrealqq,Torontoqq,Toronto_qq,Canadian_Open'},
    {'tour': 'WTA', 'attrs': {'event': ['Washington', 'Beijing']},
     'expect': '&f=ACareerqqDWashingtonqq,Beijingqq'},
    {'tour': 'ATP', 'attrs': {'event': ['Tour Finals', 'French Open']},
     'expect': '&f=ACareerqqDTour_Finalsqq,Masters,Roland_Garrosqq'},
    {'tour': 'ATP', 'attrs': {'event': 'Shanghai'},
     'error': ValueError,
     'error-msg': (
            "Invalid value for key 'event'. If your spelling is correct, "
            "it may be that this event is not yet supported.")},

    # level (lists and strings)
    {'tour': 'ATP', 'attrs': {'level': 'Backyard'},
     'error': ValueError,
     'error-msg': ("Invalid value for key 'level'.")},
    {'tour': 'ATP', 'attrs': {'level': 'All Tour'},
     'expect': '&f=ACareerqqC2'},
    {'tour': 'ATP', 'attrs': {'level': ['Premier', 'Grand Slams']},
     'error': ValueError,
     'error-msg': ("The 'Premier' level doesn't go with the 'ATP' tour. "
                   "For this level, 'ATP' goes with 'Masters' and 'WTA' "
                   "goes with 'Premier'.")},
    {'tour': 'WTA', 'attrs': {'level': ['Masters', 'Grand Slams']},
     'error': ValueError,
     'error-msg': ("The 'Masters' level doesn't go with the 'WTA' tour. "
                   "For this level, 'ATP' goes with 'Masters' and 'WTA' "
                   "goes with 'Premier'.")},
    {'tour': 'WTA', 'attrs': {'level': ['premier', 'grand slams']},
     'expect': '&f=ACareerqqC1i0'},

    # sets (lists and strings)
    {'tour': 'ATP', 'attrs': {'sets': 'straight sets'},
     'expect': '&f=ACareerqqP0'},
    {'tour': 'WTA', 'attrs': {'sets': '2 of 3 sets'}, # custom sol'n for WTA
     'expect': '&f=ACareerqqP0'},
    {'tour': 'ATP', 'attrs': {'sets': ['3/3 sets', '4/5 sets']},
     'expect': '&f=ACareerqqP8i4'},
    {'tour': 'WTA', 'attrs': {'sets': ['3/3 sets', '4/5 sets']},
     'error': ValueError,
     'error-msg': (
        "Sorry, this option is only available for ATP players. "
        "For WTA players, try 'straight sets' or 'deciding set'.")},
    {'tour': 'ATP', 'attrs': {'sets': ['deciding set', '5/5 sets']},
     'error': ValueError,
     'error-msg': (
        r"Valid 'sets' lists can include up to two categories that aren't "
        r"already covered by an existing category. For example, \['4 of 5 "
        r"sets', 'straight sets'\] is valid. However, \['3 of 3 sets', "
        r"'5 of 5 sets'\] is not, since this combination is just 'deciding "
        r"set'.")},
    {'tour': 'ATP', 'attrs': {'sets': ['decider', '2/3 sets', '4/5 sets']},
     'error': ValueError,
     'error-msg': (
        r"Valid 'sets' lists can include up to two categories that aren't "
        r"already covered by an existing category. For example, \['4 of 5 "
        r"sets', 'straight sets'\] is valid. However, \['3 of 3 sets', "
        r"'5 of 5 sets'\] is not, since this combination is just 'deciding "
        r"set'.")},

    # round (lists and strings)
    {'tour': 'WTA', 'attrs': {'round': 'R128'},
     'expect': '&f=ACareerqqE6'},
    {'tour': 'ATP', 'attrs': {'round': ['Final', 'SF', 'quarterfinals']},
     'expect': '&f=ACareerqqE0i1i2'},
    {'tour': 'ATP', 'attrs': {'round': ['first match']},
     'expect': '&f=ACareerqqE10'},
    {'tour': 'WTA', 'attrs': {'round': ['third match']},
     'error': ValueError,
     'error-msg': (
        r"Sorry, this option is only available for ATP players. Try names "
        r"for late rounds \('Quarterfinal' or later\) or that are based on "
        r"the remaining number of players \('Round of 16'/'R16' or "
        r"earlier\).")},
    {'tour': 'ATP', 'attrs': {'round': ['first match', '1R']},
     'error': ValueError,
     'error-msg': (
        r"Valid 'round' lists that combine categories may only include "
        r"round names for late rounds \('Quarterfinal' or later\) and "
        r"those based on the number of remaining players "
        r"\('Round of 16'/'R16' or earlier\).")},

    # score (strings only, no tour needed)
    {'tour': None, 'attrs': {'score': 'all 7-6'},
     'expect': '&f=ACareerqqQ0'},
    {'tour': None, 'attrs': {'score': 'lost 6-1'},
     'expect': '&f=ACareerqqQ12'},
    {'tour': None, 'attrs': {'score': 'won 6-3'},
     'error': ValueError,
     'error-msg': (
        r"Invalid value for key 'score'. Choose 'all', 'won', or 'lost' "
        r"for scores of '7-6', '7-5', '6-0', or '6-1' \(e.g., 'all 7-6', "
        r"'lost 6-0'\).")},

    # vs height (strings only)
    {'tour': 'ATP', 'attrs': {'vs height': "Over 6'4"},
     'expect': '&f=ACareerqqM5'},
    {'tour': 'WTA', 'attrs': {'vs height': 'shorter'},
     'expect': '&f=ACareerqqM0'},
    # {'tour': 'WTA', 'attrs': {'vs height': ['shorter', "under 5'6"]},
    #  'expect': '&f=ACareerqqM0'}, # hopefully soon
    {'tour': 'WTA', 'attrs': {'vs height': 'Equal'},
     'error': ValueError,
     'error-msg': (
        "Invalid value for key 'height'. For tour 'WTA', choose from "
        "'Shorter', 'Taller', 'Under 5'6', 'Under 5'8', 'Over 5'10', and "
        "'Over 6'0'.")},
    {'tour': 'ATP', 'attrs': {'vs height': 'Equal'},
     'error': ValueError,
     'error-msg': (
        "Invalid value for key 'height'. For tour 'ATP', choose from "
        "'Shorter', 'Taller', 'Under 5'10', 'Under 6'0', 'Over 6'2', and "
        "'Over 6'4'.")},

    # vs hand (strings only, no tour needed)
    {'tour': None, 'attrs': {'vs hand': 'right'},
     'expect': '&f=ACareerqqK0'},
    {'tour': None, 'attrs': {'vs hand': 'Left'},
     'expect': '&f=ACareerqqK1'},
    {'tour': None, 'attrs': {'vs hand': 'ambidextrous'},
     'error': ValueError,
     'error-msg': ("Invalid value for key 'hand'. Choose 'right' or 'left'.")},

    # vs entry (lists and strings, no tour needed)
    {'tour': None, 'attrs': {'vs entry': 'unseeded'},
     'expect': '&f=ACareerqqJ1'},
    {'tour': None, 'attrs': {'vs entry': ['wild card', 'seeded']},
     'expect': '&f=ACareerqqJ3i0'},
    {'tour': None, 'attrs': {'vs entry': 'none'},
     'error': ValueError,
     'error-msg': (
        "Invalid value for key 'vs entry'. Choose from 'seeded', "
        "'unseeded', 'qualifier', and 'wild card'.")},

    # as entry (lists and strings, no tour needed)
    {'tour': None, 'attrs': {'as entry': 'Seeded'},
     'expect': '&f=ACareerqqH0'},
    {'tour': None, 'attrs': {'as entry': ['Unseeded', 'Qualifier']},
     'expect': '&f=ACareerqqH1i2'},
    {'tour': None, 'attrs': {'as entry': 'none'},
     'error': ValueError,
     'error-msg': (
        "Invalid value for key 'as entry'. Choose from 'seeded', "
        "'unseeded', 'qualifier', and 'wild card'.")},

    # vs current rank (strings only)
    {'tour': 'ATP', 'attrs': {'vs current rank': 'Top 50'},
     'expect': '&f=ACareerqqR2'},
    {'tour': 'ATP', 'attrs': {'vs current rank': 'inactive'},
     'expect': '&f=ACareerqqR5'},
    {'tour': 'WTA', 'attrs': {'vs current rank': 'inactive'},
     'error': ValueError,
     'error-msg': ("Sorry, this attribute is only available for ATP players.")},

    # vs rank (string or tuple)
    {'tour': 'ATP', 'attrs': {'vs rank': 'Top 5'},
     'expect': '&f=ACareerqqITop_5qq'},
    {'tour': 'WTA', 'attrs': {'vs rank': 'Top 5'}, # custom sol'n for WTA
     'expect': '&f=ACareerqqIcx1000110005qq'},
    {'tour': 'ATP', 'attrs': {'vs rank': (14, 112)},
     'expect': '&f=ACareerqqIcx1001410112qq'},
    {'tour': 'ATP', 'attrs': {'vs rank': 'Number 2'},
     'error': ValueError,
     'error-msg': (
        r"Invalid value for key 'vs rank'. Choose from 'Top 5', 'Top 10', "
        r"'Top 20', 'Top 50', 'Top 100', or provide a a tuple with your "
        r"desired \(inclusive\) range.")},

    # as rank (strings only, no tour needed)
    {'tour': None, 'attrs': {'as rank': 'Top 5'},
     'expect': '&f=ACareerqqG1'},
    {'tour': None, 'attrs': {'as rank': 'Below 50'},
     'expect': '&f=ACareerqqG9'},
    {'tour': None, 'attrs': {'as rank': 'Number 2'},
     'error': ValueError,
     'error-msg': (
        "Invalid value for key 'as rank'. Choose from 'Number 1', 'Top 5', "
        "'Top 10', 'Top 20', 'Top 50', and 'Below 50'.")},
]

queries = [
    # Simona Halep matches against Caroline Wozniacki or Angelique Kerber at
    # Cincy, Canada, or Rome from 2013-07-26 to 2018-12-09.
    {'player': 'Sim halep', 'tour': 'WTA',
     'attrs': {'head-to-head': ['caro wozni', 'ang kerb'],
               'start date': datetime(2013, 7, 26),
               'end date': datetime(2018, 12, 9),
               'event': ['cincinnati', 'canada', 'rome']},
     'expect': (
        "Matches (2-1) > Opponent: Caroline Wozniacki; Opponent: Angelique "
        "Kerber; Time Span: 26-Jul-2013 to 09-Dec-2018 [custom]; Event: "
        "Cincinnati, Montreal, Rome, Toronto, Toronto")},

    # Serena Williams matches in the Round of 32 or Round of 16 of Premier
    # tournaments on clay or carpet between 7-8-1999 and 4-14-2010 where she
    # was ranked in the top 5 and faced a lefty.
    {'player': 'Sere Will', 'tour': 'WTA',
     'attrs': {'surface': ['carpet', 'clay'], 'level': 'premier',
               'start date': datetime(1999, 8, 7),
               'end date': datetime(2010, 4, 14), 'vs hand': 'left',
               'as rank': 'Top 5', 'round': ['R16', 'Round of 32']},
     'expect': (
        "Matches (3-1) > Time Span: 07-Aug-1999 to 14-Apr-2010 [custom]; "
        "Surface: Clay, Carpet; Level: Premiers; Round: R16, R32; as Rank: Top "
        "5; vs Hand: Left")},

    # Andy Murray matches where he was seeded -- and his opponent (who is not
    # Arnaud Clement or Guillermo Canas) was right-handed, shorter than him,
    # ranked between 14-112 at the time, was either seeded or given a wild card,
    # and is currently inactive -- that ended in 4 sets or straight sets and
    # featured at least 1 tiebreak.
    {'player': 'Andy Murr', 'tour': 'ATP',
     'attrs': {'vs height': 'Shorter', 'vs hand': 'right',
               'vs entry': ['wild card', 'seeded'],
               'as entry': 'seeded', 'vs current rank': 'inactive',
               'vs rank': (14, 112), 'sets': ['straights', '4 of 5 sets'],
               'score': 'all 7-6',
               'exclude opp': ['Arnaud Clement', 'Guillermo Canas']},
     'expect': (
        "Matches (1-3) > Exclude: Arnaud Clement; Exclude: Guillermo Canas; "
        "Time Span: Career; Sets: Straights, 4-Setters; Scores: All tiebreaks; "
        "as Entry: Seeded; vs Rank: 14 to 112 [custom]; vs Curr Rank: "
        "Inactive; vs Entry: Seeded, Wild Card; vs Hand: Right; "
        "vs Height: Shorter")},

    # Using only a URL, James Blake ATP-level matches that were his third in
    # a particular event, went to 3 of 3 sets, featured a 6-1 set, and were
    # against a opponent over 6'2 who was ranked in the top 50 at the time.
    {'url': ("http://www.tennisabstract.com/cgi-bin/player-classic.cgi?"
             "p=JamesBlake&f=ACareerqqC2E12P8Q10ITop_50qqM4"),
     # what the name/tour/attrs combination would have been
     # 'player': 'James Blake', 'tour': 'ATP',
     # 'attrs': {'level': 'All Tour', 'round': 'Third Match',
     #           'score': 'All 6-1', 'sets': '3/3 Sets',
     #           'vs rank': 'Top 50', 'vs height': "Over 6'2"}
     'expect': (
        "Matches (1-3) > Time Span: Career; Level: All ATP; Round: "
        "Third Match; Sets: 3 Sets (of 3); Scores: All 6-1; vs Rank: "
        "Top 50; vs Height: Over 6'2")},
]

def test_validation():
    for args in validations:
        if 'expect' in args:
            result = val_obj._validate_attrs(tour=args['tour'], **args['attrs'])
            assert result == args['expect'], 'validation mismatch!'

        elif all(key in args for key in ('error', 'error-msg')):
            with pytest.raises(args['error'], match=args['error-msg']):
                val_obj._validate_attrs(tour=args['tour'], **args['attrs'])

        else:
            raise ValueError('Invalid `validations` dict.')

def test_full_queries():
    for args in queries:
        if all(key in args for key in ('player', 'expect')):
            result = DownloadStats(name=args['player'], tour=args['tour'],
                                   attrs=args['attrs'])
        elif all(key in args for key in ('url', 'expect')):
            result = DownloadStats(url=args['url'])
        else:
            raise ValueError('Invalid `queries` dict.')
        assert result.title == args['expect'], 'query result mismatch!'
