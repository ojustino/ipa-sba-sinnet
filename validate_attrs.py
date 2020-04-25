import functools as ft
import operator
import re

from execute_query import NameCheck

class ValidateURLAttrs:
    '''
    The parent of ConstructURL() that holds all of its attribute validation
    methods. There are many, and since they're not meant to be user-facing,
    they live in this class so ConstructURL() can look shorter and simpler.

    self._validate_attrs() is the hub and calls the rest of these methods if
    the user has provided a value for their corresponding attributes.

    '''
    def _validate_attrs(self, tour, **kwargs):
        '''
        Validates the keys and values provided by the user in
        self.generate_url()'s `attrs` argument.

        If no 'start date'/'end date' keys are specified, defaults to a URL that
        requests all career data from the player in question.

        Arguments
        ---------

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male.

        **kwargs : optional
            The unpacked `attrs` dictionary (i.e., **attrs) from
            self.generate_url().
        '''
        H2H_KEY = 'head-to-head' # 'versus'?
        EXCLUDE_KEY = 'exclude opp' # 'exclude'?
        TIME1_KEY = 'start date' # 'from'?
        TIME2_KEY = 'end date' # 'until'?
        TIME_DEFAULT_KEY = 'default date'
        SURF_KEY = 'surface'
        LEVEL_KEY = 'level'
        EVENT_KEY = 'event'
        ROUND_KEY = 'round'
        SETS_KEY = 'sets'
        SCORE_KEY = 'score'
        ASRANK_KEY = 'as rank'
        VSRANK_KEY = 'vs rank'
        VSCURR_KEY = 'vs current rank'
        ASENTRY_KEY = 'as entry'
        VSENTRY_KEY = 'vs entry'
        HAND_KEY = 'vs hand'
        HEIGHT_KEY = 'vs height'

        # attrs = {'H2H_KEY': 'head-to-head', 'EXCLUDE_KEY': 'exclude opp',
        #          'TIME1_KEY': 'start date', 'TIME2_KEY': 'end date',
        #          #'TIME3_KEY': 'year',
        #          'SURF_KEY': 'surface', 'LEVEL_KEY': 'level'}

        #VALID_ATTRS = ['head-to-head', 'exclude opp', 'time span', 'surface', 'level']
        #VALID_ATTRS = [var for var in attrs.keys() if var.endswith('_KEY')]

        attr_codes = {}
        final_code = ''

        # check that start/end dates are both either present or absent
        if (   (TIME1_KEY in kwargs.keys())
               + (TIME2_KEY in kwargs.keys()) == 1  ):
            raise ValueError(
                f"'{TIME1_KEY}' and '{TIME2_KEY}' must both be present "
                "or absent in your 'attrs' dict.")
        # if both are present, check that they're properly ordered
        elif (   (TIME1_KEY in kwargs.keys())
                 + (TIME2_KEY in kwargs.keys()) == 2  ):
            if kwargs[TIME1_KEY] >= kwargs[TIME2_KEY]:
                (kwargs[TIME1_KEY],
                 kwargs[TIME2_KEY]) = kwargs[TIME2_KEY], kwargs[TIME1_KEY]
        else: # if both are absent, get whole career
            attr_codes[TIME_DEFAULT_KEY] = '&f=ACareer'

        for key, val in kwargs.items():
            # TAKE LOWER CASE VERSION OF key AND MAYBE val???
            if (key == H2H_KEY) or (key == EXCLUDE_KEY):
                prefix = '&q=' if key == H2H_KEY else '&x='

                if type(val) == str:
                    name_str = NameCheck(val, tour).name_str
                elif type(val) == list:
                    names = [NameCheck(nm, tour).name_str for nm in val]
                    name_str = ','.join(names)
                else:
                    raise ValueError(
                        f"Invalid value type for key '{key}'. Try a string "
                        "name or a list of string names.")

                attr_codes[key] = prefix + name_str

            elif (key == TIME1_KEY) or (key == TIME2_KEY):
                date = val.strftime('%Y%m%d')
                attr_codes[key] = date

            elif key == SURF_KEY:
                prefix = 'B'

                if type(val) == str:
                    surf_code = self._validate_surfaces(val)
                elif type(val) == list:
                    surfaces = [self._validate_surfaces(sf) for sf in val]
                    surf_code = 'i'.join(surfaces)

                attr_codes[key] = prefix + surf_code

            elif key == LEVEL_KEY:
                prefix = 'C'

                if type(val) == str:
                    lvl_code = self._validate_levels(val, tour)
                elif type(val) == list:
                    levels = [self._validate_levels(lv, tour) for lv in val]
                    lvl_code = 'i'.join(levels)

                attr_codes[key] = prefix + lvl_code

            elif key == EVENT_KEY:
                prefix = 'D'

                if type(val) == str:
                    event_code = self._validate_events(val, tour)
                elif type(val) == list:
                    events = [self._validate_events(ev, tour) for ev in val]
                    event_code = ','.join(events)

                attr_codes[key] = prefix + event_code

            elif key == ROUND_KEY:
                prefix = 'E'

                if type(val) == str:
                    round_code = self._validate_round(val, tour)
                elif type(val) == list:
                    rounds = [self._validate_round(rd, tour) for rd in val]
                    self._validate_round_list(rounds)
                    round_code = 'i'.join(rounds)

                attr_codes[key] = prefix + round_code

            elif key == SETS_KEY:
                prefix = 'P'

                if type(val) == str:
                    set_code = self._validate_set(val, tour)
                elif type(val) == list:
                    sets = [self._validate_set(st, tour) for st in val]
                    self._validate_set_list(sets)
                    set_code = 'i'.join(sets)

                attr_codes[key] = prefix + set_code

            elif key == SCORE_KEY:
                # ALLOW CERTAIN COMBINATIONS, AS WITH SETS AND ROUND
                prefix = 'Q'

                score_code = self._validate_score(val)
                attr_codes[key] = prefix + score_code

            elif key == ASRANK_KEY:
                prefix = 'G'

                asrank_code = self._validate_asrank(val)
                attr_codes[key] = prefix + asrank_code

            elif key == VSRANK_KEY:
                prefix = 'I'

                vsrank_code = self._validate_vsrank(val, tour)
                attr_codes[key] = prefix + vsrank_code

            elif key == VSCURR_KEY:
                prefix = 'R'

                vscurr_code = self._validate_vscurrrank(val, tour)
                attr_codes[key] = prefix + vscurr_code

            elif (key == ASENTRY_KEY) or (key == VSENTRY_KEY):
                prefix = 'H' if key == ASENTRY_KEY else 'J'

                if type(val) == str:
                    entry_code = self._validate_entry(key, val)
                elif type(val) == list:
                    entries = [self._validate_entry(key, en) for en in val]
                    entry_code = 'i'.join(entries)

                attr_codes[key] = prefix + entry_code

            elif key == HAND_KEY:
                prefix = 'K'

                hand_code = self._validate_hand(val)
                attr_codes[key] = prefix + hand_code

            elif key == HEIGHT_KEY:
                prefix = 'M'

                #if type(val) == str:
                #    height_code = self._validate_height(val, tour)
                #elif type(val) == list:
                #    heights = [self._validate_height(h, tour) for h in val]
                #    #self._validate_height_list(heights) # wrong behavior on site
                #    height_code = 'i'.join(heights)

                height_code = self._validate_height(val, tour)
                attr_codes[key] = prefix + height_code

            else:
                raise KeyError(f"'{key}' is an invalid attribute.")

        # begin with dates, as is common with links on the site
        if TIME_DEFAULT_KEY in attr_codes:
            final_code += attr_codes[TIME_DEFAULT_KEY]
        else:
            final_code += ('&f=Acx'
                           + attr_codes[TIME1_KEY] + attr_codes[TIME2_KEY])
        final_code += 'qq' # needed after date in URL

        # next, add attributes that also fall under '&f=' in URL
        final_code += ''.join([cd for ky, cd in attr_codes.items()
                               if not cd.startswith('&')
                               and not ky.endswith('date')])

        # lastly, add attributes with other parameters (like h2h and exclude)
        final_code += ''.join([cd for ky, cd in attr_codes.items()
                               if cd.startswith('&')
                               and not ky.endswith('date')])

        return final_code

    def _validate_surfaces(self, value):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'surface' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        I'VE FOUND THAT INCLUDING A SURFACE CODE IN AN ATP PLAYER'S URL CURRENTLY DOESN'T MAKE A DIFFERENCE.
        YOU CAN ONLY USE THAT FILTER BY SELECTING ITEMS IN AN ALREADY-LOADED PAGE'S SURFACE MENU....

        Arguments
        ---------

        value : str, required
            The surface upon which a match was played.
        '''
        value = value.lower()

        code = ('0' if value == 'hard' else '1' if value == 'clay'
                else '2' if value == 'grass' else '3' if value == 'carpet'
                else None)

        if code is None:
            raise ValueError(
                "Invalid value for key 'surface'. Choose from 'hard', "
                "'clay', 'grass', and 'carpet'.")

        return code

    def _validate_levels(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'level' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            The level of the tournament in which a match was played.

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because the level of tournaments
            just below Grand Slams has a different name on each tour.
        '''
        value = value.title()

        if value == 'Grand Slams':
            code = '0'
        elif (value == 'Masters') or (value == 'Premier'):
            if (     ((value == 'Masters') and (tour == 'WTA'))
                  or ((value == 'Premier') and (tour == 'ATP'))  ):
                raise ValueError(
                    f"The '{value}' level doesn't go with the '{tour}' "
                    "tour. For this level, 'ATP' goes with 'Masters' "
                    "and 'WTA' goes with 'Premier'.")
            else:
                code = '1'
        elif value == 'All Tour':
            code = '2'
        else:
            raise ValueError(f"Invalid value for key 'level'.")

        return code

    def _simple_event_code(self, value, with_suffix=True):
        '''
        RENAME ME!

        Called from ... (FILL ME IN)

        Replace spaces with underscores in certain attribute codes. Can also
        add 'qq' (which is used as a separator for a few attributes) to the
        end of the code.

        Arguments
        ---------

        value : str, requried
            The string phrase to be translated into an attribute code.

        with_suffix : bool, optional
            Adds 'qq' to the end of the resulting code when True.
            [default: True]
        '''
        return value.replace(' ', '_') + ('qq' if with_suffix else '')

    def _validate_events(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'event' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            The event (tournament) at which a match was played.

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because Tennis Abstract's event
            labels for non-Grand Slams often vary depending on the tour.
        '''
        value = value.title()

        if value == 'Australian Open':
            code = _simple_event_code(value)

        elif (value == 'Roland Garros') or (value == 'French Open'):
            code = _simple_event_code('Roland Garros')

        elif value == 'Wimbledon':
            code = _simple_event_code(value)

        elif value == 'US Open':
            code = _simple_event_code(value)

        elif value == 'Tour Finals':
            if tour == 'ATP':
                # 70-89 is 'Masters'
                special_vals = ['Tour_Finals', 'Masters']
                code = 'qq,'.join(special_vals)
            else: #== 'WTA'
                # NEED TO RESEARCH SIGNIFICANCE OF COLGATE SERIES FINALS
                special_vals = ['WTA_Championships', 'Singapore'
                                'WTA_Tour_Championships', 'Shenzhen_Finals',
                                'Virginia_Slims_Championships']
                code = 'qq,'.join(special_vals)

        elif value == 'Olympics':
            code = _simple_event_code(value)

        elif value == 'Davis Cup':
            if tour == 'WTA':
                raise ValueError(
                    f"'{value}' and '{tour}' do not go together. Try 'Davis "
                    "Cup' with 'ATP' or 'Fed Cup' with 'WTA'.")
            code = _simple_event_code(value)

        elif value == 'Fed Cup':
            if tour == 'ATP':
                raise ValueError(
                    f"'{value}' and '{tour}' do not go together. Try 'Davis "
                    "Cup' with 'ATP' or 'Fed Cup' with 'WTA'.")
            code = _simple_event_code(value)

        elif value == 'Indian Wells':
            if tour == 'ATP':
                # 74-75 is 'Tucson'. 76-78 is 'Palm Springs'.
                # 79-80 is 'Rancho Mirage'. 81-86 is 'La Quinta'.
                # 87-89 is 'Indian Wells'. 90 onward is 'Indian Wells Masters'
                special_vals = ['Indian_Wells_Masters', 'Indian_Wells',
                                'La_Quinta', 'Rancho_Mirage',
                                'Palm_Springs', 'Tucson']
                code = 'qq,'.join(special_vals)
            else: #== 'WTA'
                # began in 89. same name every year except 91, which is
                # 'Palm Springs'. that overlaps with the 78 colgate series
                # championship in the data, so i will likely just leave 91 out
                code = _simple_event_code(value)

        elif value == 'Miami':
            if tour == 'ATP':
                # 85 is 'delray beach', but that overlaps more recent tourney,
                # so i'll likely leave it out. 86 is 'Boca West'.
                # 87-89 is 'Key Biscayne'
                special_vals = ['Miami_Masters', 'Key_Biscayne', 'Boca West']
                code = 'qq,'.join(special_vals)
            else: #== 'WTA'
                # 85-99 is 'Key Biscayne'
                special_vals = ['Miami', 'Key_Biscayne']
                code = 'qq,'.join(special_vals)

        elif value == 'Madrid':
            if tour == 'ATP':
                # newer tourney; no old names to worry about
                # (there was a separate, non-Masters Madrid Open from 72-94)
                code = (_simple_event_code(value, False)
                        + '_Masters' + 'qq')
            else: #== 'WTA'
                # newer tourney; no old names to worry about
                code = _simple_event_code(value)

        elif value == 'Rome':
            if tour == 'ATP':
                # old tourney, but same name throughout data (back to ~70s)
                code = (_simple_event_code(value, False)
                        + '_Masters' + 'qq')
            else: #== 'WTA'
                # old tourney, but same name throughout data (back to 79)
                code = _simple_event_code(value)

        elif value == 'Washington':
            # ATP: old tourney, but same name back to 70
            # WTA: newer tourney; no old names to worry about
            code = _simple_event_code(value)

        elif value == 'Canada':
            if tour == 'ATP':
                # aka 'Toronto' and 'Toronto / Montreal',
                # **THE LATTER CAN'T BE SEARCHED ON THE SITE -- IT'S PROBABLY THE '/'
                special_vals = ['Canada_Masters', 'Toronto'] #, 'Toronto_/_Montreal']
                code = 'qq,'.join(special_vals)
            else: #== 'WTA'
                # data begin in 80 as 'Canadian Open'
                special_vals = ['Montreal', 'Toronto',
                                'Toronto_', 'Canadian_Open']
                code = 'qq,'.join(special_vals)

        elif value == 'Cincinnati':
            if tour == 'ATP':
                # old tourney, but same name throughout data
                code = (_simple_event_code(value, False)
                        + '_Masters' + 'qq')
            else: #== 'WTA'
                # not held from 74-87 and 89-03. there was a separate avon
                # tourney from 80-82 also labeled on the site as 'Cincinnati';
                # there's no quick way to differentiate them. don't think it's
                # worth it to correct for 3 years in the 80s
                code = _simple_event_code(value)

        elif value == 'Beijing':
            # newer tourney; no old names to worry about
            code = _simple_event_code(value)

        return code

    def _validate_asrank(self, value):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'as rank' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        WOULD BE NICE TO BE ABLE TO ENTER CUSTOM RANKINGS FOR THIS FILTER AS YOU CAN WITH 'vs rank'.

        Arguments
        ---------

        value : str, required
            The player's ranking (or ranking range) at the time of the match.
        '''
        # need to come up with better entry names
        value = value.title()

        code = ('0' if value == 'Number 1' else '1' if value == 'Top 5'
                else '2' if value == 'Top 10' else '3' if value == 'Top 20'
                else '4' if value == 'Top 50' else '9' if value == 'Below 50'
                else None)

        if code is None:
            raise ValueError(
                "Invalid value for key 'as rank'. Choose from 'Number 1', "
                "'Top 5', 'Top 10', 'Top 20', 'Top 50', and 'Below 50'.")

        return code

    def _validate_vsrank(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'vs rank' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str or tuple, required
            The opponent's ranking (or ranking range) at the time of the match.

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because Tennis Abstract lacks a
            Top 5 'vs rank' label for WTA players.
        '''
        # maybe just make the tuple strategy the overall strategy???

        if type(value) == str:
            value = value.title()

            if value in {'Top 10', 'Top 20', 'Top 50', 'Top 100'}:
                code = _simple_event_code(value)
            elif value == 'Top 5':
                if tour == 'WTA':
                    return self._validate_vsrank((1, 5), tour)
                else:
                    code = _simple_event_code(value)
            else:
                raise ValueError(
                    "Invalid value for key 'vs rank'. Choose from 'Top 5', "
                    "'Top 10', 'Top 20', 'Top 50', 'Top 100', or provide a "
                    "a tuple with your desired (inclusive) range.")
        elif type(value) == tuple:
            # ensure that ranks five digits or less and are ints
            # (or is_integer=True for floats)
            prefix = 'cx'
            base_str = '10000'
            tuple_of_strs = (str(rk) for rk in value)

            formatted_rks = [base_str[:-len(rk)] + rk for rk in tuple_of_strs]
            code = prefix + ft.reduce(operator.add, formatted_rks) + 'qq'
        else:
            raise ValueError(
                "Invalid type for key 'vs rank'. Should either be a string "
                "or a tuple of ints.")

        return code

    def _validate_vscurrrank(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'vs current rank'
        attribute. If valid, encodes it in Tennis Abstract's URL style and
        returns the result.

        Arguments
        ---------

        value : str, required
            The opponent's *current* ranking (or ranking range) at the time of
            the query.

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because Tennis Abstract doesn't
            make this feature available for WTA players.
        '''
        # might be able to come up with a better attribute name?
        # should communicate that this covers current rank OR current status

        if tour == 'WTA':
            raise ValueError(
                "Sorry, this attribute is only available for ATP players.")

        value = value.title()
        code = ('0' if value == 'Top 10' else '1' if value == 'Top 20'
                else '2' if value == 'Top 50' else '3' if value == 'Top 100'
                else '4' if value == 'Active' else '5' if value == 'Inactive'
                else None)

        if code is None:
            raise ValueError(
                "Invalid value for key 'vs current rank'. Choose from 'Top "
                "10', 'Top 20', 'Top 50', 'Top 100', 'Active', and 'Inactive'.")

        return code

    def _validate_entry(self, key, value):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'as entry' or 'vs entry'
        attributes. If valid, encodes it in Tennis Abstract's URL style and
        returns the result.

        Arguments
        ---------

        key : str, required
            Will either be 'as entry' or 'vs entry'. Needed since this method
            can handle either but needs to know which is pertinent when called.

        value : str, required
            The player's (or opponent's) entry status in a given tournament.
        '''
        value = value.lower()
        code = ('0' if value == 'seeded' else '1' if value == 'unseeded'
                else '2' if value == 'qualifier'
                else '3' if value == 'wild card'
                else None)

        if code is None:
            raise ValueError(
                f"Invalid value for key '{key}'. Choose from 'seeded', "
                "'unseeded', 'qualifier', and 'wild card'.")

        return code

    def _validate_hand(self, value):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'vs hand' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            The opponent's dominant hand.
        '''
        value = value.lower()
        code = '0' if value == 'right' else '1' if value == 'left' else None

        if code is None:
            raise ValueError(
                "Invalid value for key 'hand'. Choose 'right' or 'left'.")

        return code

    def _validate_height(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'vs height' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            The opponent's height. Should begin with 'Under ' or 'Over ' and end
            with values in feet and inches separated by an apostrophe.
            ("Under 5'10" or "Over 6'0" are valid examples -- depending on
            the tour.)

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because Tennis Abstract's height
            cutoffs are different based on the tour.
        '''
        if tour == 'WTA':
            under0 = "Under 5'6"; under1 = "Under 5'8"
            over0 = "Over 5'10"; over1 = "Over 6'0"
        else: #tour == 'ATP'
            under0 = "Under 5'10"; under1 = "Under 6'0"
            over0 = "Over 6'2"; over1 = "Over 6'4"

        value = value.title()
        code = ('0' if value == 'Shorter' else '1' if value == 'Taller'
                else '2' if value == under0 else '3' if value == under1
                else '4' if value == over0 else '5' if value == over1
                else None)

        if code is None:
            raise ValueError(
                f"Invalid value for key 'height'. For tour '{tour}', choose "
                f"from 'Shorter', 'Taller', '{under0}', '{under1}', '{over0}', "
                f"and '{over1}'.")

        return code

    def _validate_height_list(self, heights):
        '''
        Called from self._validate_attrs().

        If the user provided a list of multiple strings for the 'height'
        attribute, ensure that they've chosen a valid combination.

        I'm the one imposing validity here; intra-attribute filters are joined
        using logical OR instead of AND, and I don't want to allow combinations
        that overlap or cause confusion.

        I think I could implement this better, but this is my solution for now.

        Arguments
        ---------

        heights : list, required
            The list of height strings.
        '''
        allowed_codes = set(
                ['02', '03', '04', '05', # any over/under with 'shorter'
                 '12', '13', '14', '15', # any over/under with 'taller'
                 '24', '25', '34', '35', # 1 over + 1 under
                 '024', '025', '034', '035', # shorter + 1 under + 1 over
                 '124', '125', '134', '135']) # taller + 1 under + 1 over

        proposed_code = ft.reduce(operator.add, sorted(heights))

        if len(proposed_code) > 1 and proposed_code not in allowed_codes:
            # length 1 codes already checked in self._validate_height
            raise ValueError(
                "Valid 'height' lists that combine categories can include up "
                "to one 'Under' category, up to one 'Over' category, and up to "
                "one of 'Shorter'/'Taller'.")

    def _validate_round(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'round' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            The opponent's dominant hand.

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because Tennis Abstract only
            makes certain filters available for WTA players.
        '''
        value = value.title() if len(value) != 2 else value.upper()

        if value in {'Final', 'Finals', 'F'}:
            code = '0'
        elif value in {'Semifinal', 'Semifinals', 'SF'}:
            code = '1'
        elif value in {'Quarterfinal', 'Quarterfinals', 'QF'}:
            code = '2'
        elif value in {'R16', 'Round Of 16'}:
            code = '3'
        elif value in {'R32', 'Round Of 32'}:
            code = '4'
        elif value in {'R64', 'Round Of 64'}:
            code = '5'
        elif value in {'R128', 'Round Of 128'}:
            code = '6'
        elif value in {'First Round', 'Second Round', 'Third Round',
                       '1R', '2R', '3R',
                       'First Match', 'Second Match', 'Third Match'}:
            if tour == 'WTA':
                raise ValueError(
                    "Sorry, this option is only available for ATP players. "
                    "Try names for late rounds ('Quarterfinal' or later) or "
                    "that are based on the remaining number of players "
                    "('Round of 16'/'R16' or earlier).")

            code = ('7' if value == 'First Round' or value == '1R'
                    else '8' if value == 'Second Round' or value == '2R'
                    else '9' if value == 'Third Round' or value == '3R'
                    else '10' if value == 'First Match'
                    else '11' if value == 'Second Match'
                    else '12' if value == 'Third Match'
                    else None)
        else:
            code = None

        if code is None:
            raise ValueError(
                "Invalid value for key 'round'. See the docstring for a "
                "guide to the many valid options.")

        return code

    def _validate_round_list(self, rounds):
        '''
        Called from self._validate_attrs().

        If the user provided a list of multiple strings for the 'round'
        attribute, ensure that they've chosen a valid combination.

        I'm the one imposing validity here; since filters like 'First Match'
        aren't available for WTA players, I don't allow them to be used in
        any combinations. I'm relying on the two tours being brought to feature
        parity instead of hacking together an ATP-only solution.

        Arguments
        ---------

        rounds : list, required
            The list of round strings.
        '''
        allowed_combo = all([int(cd) <= 6 for cd in rounds])

        if len(rounds) > 1 and not allowed_combo:
            raise ValueError(
                "Valid 'round' lists that combine categories may only include "
                "round names for late rounds ('Quarterfinal' or later) and "
                "those based on the number of remaining players "
                "('Round of 16'/'R16' or earlier).")

    def _validate_set(self, value, tour):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'sets' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            Either the maximum number of sets in the match (e.g., 'best of 3')
            or the match's result as a count ('2 of 3 sets', '3/5 sets') or a
            common descriptor ('straight sets', 'deciding set').

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male. Needed because Tennis Abstract only
            makes certain filters available for WTA players.
        '''
        value = value.lower()

        if (  (value == 'straight sets') or (value == 'straights')
             or (value in {'2 of 3 sets', '2/3 sets'} and tour == 'WTA')):
            code = '0'
        elif ( (value == 'deciding set') or (value == 'decider')
             or (value in {'3 of 3 sets', '3/3 sets'} and tour == 'WTA')):
            code = '1'
        elif value == 'best of 5 sets':
            if tour == 'WTA': # doesn't catch 1984-98's bof5 wta finals matches
                raise ValueError(
                    "Sorry, this option is only available for ATP players. For "
                    "WTA players, try 'straight sets' or 'deciding set'.")
            else: # == 'ATP'
                code = '2'
        elif value == 'best of 3 sets':
            if tour == 'WTA': # site lacks a WTA option, but we can customize
                code = '0i1'
            else: # == 'ATP'
                code = '6'
        elif re.match('\d of \d sets', value) or re.match('\d/\d', value):
            if tour == 'WTA': # 2/3 and 3/3 when tour=='WTA' was caught earlier
                raise ValueError(
                    "Sorry, this option is only available for ATP players. For "
                    "WTA players, try 'straight sets' or 'deciding set'.")
            code = ('3' if value == '3 of 5 sets'
                    else '4' if value == '4 of 5 sets' or value == '4/5 sets'
                    else '5' if value == '5 of 5 sets' or value == '5/5 sets'
                    else '7' if value == '2 of 3 sets' or value == '2/3 sets'
                    else '8' if value == '3 of 3 sets' or value == '3/3 sets'
                    else None)
        else:
            code = None

        if code is None:
            raise ValueError(
                "Invalid value for key 'sets'. Choose from 'straight sets', "
                "'deciding set', or, for ATP players, 'X of Y sets', where Y "
                "can be '3' or '5'.")

        return code

    def _validate_set_list(self, sets):
        '''
        Called from self._validate_attrs().

        If the user provided a list of multiple strings for the 'sets'
        attribute, ensure that they've chosen a valid combination.

        I'm the one imposing validity here; intra-attribute filters are joined
        using logical OR instead of AND, and I don't want to allow combinations
        that overlap or cause confusion.

        I think I could implement this better, but this is my solution for now.

        Arguments
        ---------

        sets : list, required
            The list of set strings.
        '''
        # puzzling out valid combnations and their combind codes...
        # straight: deciding (01), 4/5 (04), 5/5 (05), 3/3 (08)
        # deciding: 3/5 (13), 4/5 (14), 2/3 (17)
        # best of 5: 2/3 (27), 3/3 (28)
        # 3/5: 4/5 (34), 5/5 (35), bo3 (36), 3/3 (38)
        # 4/5: 5/5 (45), bo3 (46), 2/3 (47), 3/3 (48)
        # 5/5: bo3 (56), 2/3 (57)
        # 2/3 + 3/3 is just best of 3; 2/3 + 3/5 is just straight sets
        # 3/3 + 5/5 is just deciding set; 3/5 + 4/5 + 5/5 is just best of 5

        allowed_codes = set(['01', '04', '05', '08', '13', '14', '17',
                             '27', '28', '34', '35', '36', '38', '45',
                             '46', '47', '48', '56', '57'])
        proposed_code = ft.reduce(operator.add, sorted(sets))

        if len(proposed_code) > 1 and proposed_code not in allowed_codes:
            raise ValueError(
                "Valid 'sets' lists can include up to two categories that "
                "aren't already covered by an existing category. For example, "
                "['4 of 5 sets', 'straight sets'] is valid. However, "
                "['3 of 3 sets', '5 of 5 sets'] is not, since this combination "
                "is just 'deciding set'.")

    def _validate_score(self, value):
        '''
        Called from self._validate_attrs().

        Validates the value associated with a query's 'score' attribute. If
        valid, encodes it in Tennis Abstract's URL style and returns the result.

        Arguments
        ---------

        value : str, required
            A hyphen-separated set score with the winning score first (e.g.,
            '6-0', '7-6').
        '''
        value = value.lower()
        if ('tiebreak' in value) or ('7-6' in value):
            code = ('0' if 'all' in value
                    else '1' if 'won' in value or 'win' in value
                    else '2' if 'lost' in value or 'loss' in value
                    else '3' if 'deciding' in value or 'final' in value
                    else None)
        elif '7-5' in value:
            code = ('4' if 'all' in value
                    else '5' if 'won' in value or 'win' in value
                    else '6' if 'lost' in value or 'loss' in value
                    else None)
        elif '6-0' in value:
            code = ('7' if 'all' in value
                    else '8' if 'won' in value or 'win' in value
                    else '9' if 'lost' in value or 'loss' in value
                    else None)
        elif '6-1' in value:
            code = ('10' if 'all' in value
                    else '11' if 'won' in value or 'win' in value
                    else '12' if 'lost' in value or 'loss' in value
                    else None)
        else:
            code = None

        if code is None:
            raise ValueError("Invalid value for key 'score'. Choose 'all', "
                             "'won', or 'lost' for scores of '7-6', '7-5', "
                             "'6-0', or '6-1' (e.g., 'all 7-6', 'lost 6-0')")

        return code
