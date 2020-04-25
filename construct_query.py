import functools as ft
import numpy as np
import re
import pandas as pd

from execute_query import NameCheck, QueryData
from validate_attrs import ValidateURLAttrs

class ConstructURL(ValidateURLAttrs):
    '''
    Takes a player's name and (optionally) a dictionary of attributes to filter
    results, then translates them into a URL that leads to results for the
    matching query on Tennis Abstract's website.

    The result is stored in the self.URL attribute. Users may also find the
    self.name attribute helpful -- it's the player's name formatted as it
    appears on the site.

    Inherits attribute validation infrastructure from ValidateURLAttrs.

    Arguments
    ---------

    name : str, required
        The chosen player's name. Make sure there are non-letter characters
        between each unit of the name (e.g., 'Serena Williams' and
        'Jo-Wilfried Tsonga' are fine, but 'SerenaWilliams' and
        'JoWilfried Tsonga' are not.)

    tour : str, required
        The chosen player's tour. Should be 'WTA' if the player is female or
        'ATP' if the player is male.

    attrs : dict, optional
        A dictionary of the attributes that will be used to filter the match
        data once the actual query takes place. Only specific keys and values
        are allowed; **future documentation** will give a full accounting.

    '''
    def __init__(self, name, tour, attrs={}):
        # check name first
        name_obj = NameCheck(name, tour)
        name_str = name_obj.name_str

        self.name = self.spaced_name_str(name_str)
        self.URL = self.generate_url(name_str, tour, attrs)

    @staticmethod
    def spaced_name_str(name_str):
        '''
        Insert spaces before capital letters (other than the first one) in the
        `name_str` attribute of a successfully initialized NameCheck() class
        instance.

        The returned result is how the player's name is printed on their match
        data webpage (instead of how it appears in the URL), which should be
        more readable.

        (Marked as a static method so DownloadStats() can call it without fully
        instantiating ConstructURL() when it just needs a spaced name string.)

        Arguments
        ---------

        name_str : str, required
            The `name_str` attribute from a NameCheck() instance. It's a
            name without spaces that leads to a matching match data page on
            Tennis Abstract's website.
        '''
        # find capital letters
        capital_inds = re.finditer('[A-Z]', name_str)

        # find indices where spaces should be added
        space_inds = [ind.span()[0] + i
                      for i, ind in enumerate(capital_inds, -1)
                      if i != -1]

        for ind in space_inds:
            name_str = name_str[:ind] + ' ' + name_str[ind:]

        return name_str

    def generate_url(self, name_str, tour, attrs={}):
        '''
        Create the matching URL for a specific query to a player's match data
        page on Tennis Abstract by translating the user's chosen name and
        attributes to the format recognized by the website.

        Arguments
        ---------

        name_str : str, required
            The name identifier used in the URL of the player's match data page.
            If it comes directly from a NameCheck() instance's `name_str`
            attribute, it should be ready to include in a URL as-is.

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male.

        attrs : dict, optional
            A dictionary of the attributes that will be used to filter the match
            data once the actual query takes place. Only specific keys and
            values are allowed; **future documentation** will give more detail.
        '''
        query_url = 'http://www.tennisabstract.com/cgi-bin/'

        # account for female players' slightly different URL format
        tour = tour.upper()
        if tour == 'ATP':
            gender = ''
        elif tour == 'WTA':
            gender = 'w' if tour == 'WTA' else ''
        else:
            raise ValueError('Unsupported tour.')

        # add more required verbiage to URL
        query_url += gender
        query_url += 'player-classic.cgi?p='

        # add name_str, which is already properly formatted
        query_url += name_str

        # then, add query (or ask for whole career data if attrs is empty)
        query_url += self._validate_attrs(tour, **attrs)

        return query_url

class DownloadStats:
    '''
    Takes either a link to a player data page on Tennis Abstract or a player's
    name, tour, and (optionally) a dictionary of attributes to filter results,
    which are translated into a URL. Then, executes the matching query on Tennis
    Abstract's website.

    Saves the result in the self.match_data attribute, a pandas DataFrame. Also
    saves the table title (self.title), the player's name as it appears on the
    site (self.name), and the query's URL (self.URL).

    Does not inherit, but does create instances of ConstructURL() and
    QueryData() to handle parts of the process indicated in those class' names.

    This class' functionality was originally joined with QueryData's, but they
    are separated now so that the user-facing class (this one) doesn't carry
    all of PyQt5's QWebEnginePage-related attributes and methods. They're not
    needed after we've retrieved the data tables from Tennis Abstract.

    Arguments
    ---------

    name : str, optional
        The chosen player's name. Make sure there are non-letter characters
        between each unit of the name (e.g., 'Serena Williams' and
        'Jo-Wilfried Tsonga' are fine, but 'SerenaWilliams' and
        'JoWilfried Tsonga' are not.)

    tour : str, optional
        The chosen player's tour. Should be 'WTA' if the player is female or
        'ATP' if the player is male. *Required if you use the `name` argument.*

    attrs : dict, optional
        A dictionary of the attributes that will be used to filter the match
        data once the actual query takes place. Only specific keys and values
        are allowed; **future documentation** will give a full accounting.

    url : str, optional
        The URL to a Tennis Abstract player match data page. *This argument
        makes the class disregard the `name` and `attrs` arguments.*
    '''
    def __init__(self, name=None, tour='', attrs={}, url=None):
        # either make sure a proper tour was provided or infer tour from URL
        self.tour = self._validate_tour(tour, url)

        if url is None:
            # generate the query's URL; save player's name as shown on the site
            url_obj = ConstructURL(name, self.tour, attrs)
            self.URL = url_obj.URL
            self.name = url_obj.name
        else:
            self.URL = url

            # get formatted player name from URL; save it as it appears on site
            # (looks for 'p=' and saves all chars until it reaches a non-letter)
            formatted_name = re.search('p=[a-zA-Z]+', self.URL).group()[2:]
            self.name = ConstructURL.spaced_name_str(formatted_name)

        # make the query. then, format the results and save the table title
        query = QueryData(self.URL, self.tour)
        self.title = query.title
        self.match_data = self.merge_and_edit_tables(query.html_tables)


    def _validate_tour(self, tour, url):
        '''
        If the user provided a `name` in self.__init__(), ensure that they also
        provided a valid tour. If they provided a `url` instead, infer the tour
        from the URL string.

        Arguments
        ---------

        tour : str, required
            The chosen player's tour. Should be 'WTA' if the player is female or
            'ATP' if the player is male.

        url : str or None, required
            Is either the `url` the user provided in self.__init__() or None if
            the user provided a `name` there instead.
        '''
        if url is not None: # user provided `url` in __init__
            # the character after 'cgi-bin/' in the URL differs with the tour
            differentiate = re.search('cgi-bin/.', url).group()

            if differentiate[-1] == 'w':
                tour = 'WTA'
            elif differentiate[-1] == 'p':
                tour = 'ATP'
            else:
                raise ValueError('Unexpected URL.')

        else: # user provided `name` in __init__
            tour = tour.upper()
            if tour not in {'ATP', 'WTA'}:
                raise ValueError('Ineligible tour. Should be ATP or WTA.')

        return tour

    def merge_and_edit_tables(self, html_tables):
        '''
        (...) Since data is spread across multiple tables on Tennis Abstract's
        player data pages, they must be merged after the query completes. The
        method does so by converting them into one pandas DataFrame and
        applying some formatting (typing, handling NaNs, etc.)

        Arguments
        ---------

        html_tables : list, required
            A list of HTML tables retrieved from the query.
        '''
        #print('merge_and_edit')

        # ensure that we received tables -- if not, report what happened
        test = html_tables[0]
        if (test is None) or (test.contents == []):
            raise ValueError(
                'Your query returned a blank page. The package likely '
                'produced an invalid URL. Try another search and open an '
                'issue about these filters in the repository, if you may.')
        elif test.name == 'p':
            raise ValueError('Your filters produced no matches. '
                             'Try making them less stringent?')
        elif test.name != 'table':
            raise ValueError(
                'Unexpected result on website. Something likely failed '
                'inside this package. Try a different query and open an '
                'issue about these filters in the repository, if you may.')

        # convert the table html strings into (at least two) DataFrames
        table_strs = [tab.decode() for tab in html_tables]
        table_dfs = [pd.read_html(tab).pop() for tab in table_strs]

        # merge the DataFrames. pd.merge only takes two, so if there are
        # more, use ft.reduce use it in a chain
        stats_df = ft.reduce(pd.merge, table_dfs)
        stats_df = stats_df.iloc[:-1] # last row has an unneeded link

        # fill NaNs in as -1
        #stats_df = stats_df.fillna(-1)

        # give name to results column
        result_col_og = 'Unnamed: 6'
        assert result_col_og in set(stats_df.columns), ('column names/order '
                                                        'might have changed')
        stats_df.rename(columns={result_col_og: 'Result'}, inplace=True)

        # add a column to note whether the match was a win or loss
        stats_df['Won'] = np.zeros(stats_df.shape[0])

        # move it beside the 'Score' column
        new_cols = list(stats_df.columns)
        score_at = new_cols.index('Score')
        new_cols.insert(score_at, new_cols.pop())

        stats_df = stats_df[new_cols]

        # fill it out based on 'Result' column
        for ind, row in stats_df.iterrows():
            rslt = row['Result']

            # where is the 'd.'?
            # (As in 'Player1 d. Player2'; there should only be one)
            defeat = [st.span()[0] for st in re.finditer('d\.', rslt)]
            if len(defeat) == 1:
                defeat = defeat.pop()
            else:
                raise ValueError("Unexpected 'Result' string; "
                                 "losing player is unclear.")

            # where is the opponent's name? it's usually followed by
            # their country of origin, like '[USA]'. (again, only expect 1)
            opp = [st.span()[0] for st in re.finditer('\[.*\]', rslt)]
            if len(opp) == 1:
                opp = opp.pop()
            else:
                raise ValueError("Unexpected 'Result' string; "
                                 "opponent country is unclear.")

            # what about special cases?
            #walkover = [st.span()[-1] for st in re.finditer('W/O', result)]
            #retired

            # if the 'd.' came before the opponent, the result is a win
            stats_df.loc[ind, 'Won'] = 1 if defeat < opp else 0

        # # assign dtypes to each column
        # for col in stats_df.columns:
        #   valid_entries = stats_df[col].dropna()
        #   example = valid_entries.iloc[0]

        #   if valid_entries.size == 0:
        #       continue
        #   elif isinstance(example, str):
        #       # with str, pd.read_html uses 'nan' instead of np.NaN,
        #       # so fix that and re-drop NaNs
        #       valid_str_entries = valid_entries.apply(lambda n:
        #                                               np.nan if n == 'nan'
        #                                               else n).dropna()
        #       example = (valid_str_entries.iloc[0]
        #                  if valid_str_entries.size > 0 else '')

        #       if example[-1] == '%':
        #           # remove percent sign and convert the number to a float
        #           #stats_df[col] = [float(pct[:-1]) for pct in stats_df[col]]
        #           pct_to_float = lambda pct: np.float64(pct[:-1])
        #           stats_df[col][] = stats_df[col].apply(pct_to_float)
        #       elif '%' in example:
        #           # typically for BPSaved/BPConv columns
        #           #BPConv/BPCnv, BPSaved/BpSavd to:
        #           #BPForced/Breaks, BPFaced/OppBreaks

        #       else:
        #           continue
        #       stats_df[col] = stats_df[col].astype(str)
        #       #stats_df[col] = stats_df[col].astype(pd.StringDtype())
        #       #switch to commented line after testing 0.25.0 and finally 1.0.0
        #       #https://pandas.pydata.org/pandas-docs/stable/user_guide/text.html
        #   elif isinstance(example, float):
        #       n_ints = sum([n.is_integer() for n in valid_entries])
        #       # change column dtype to int if it fits
        #       if n_ints == len(valid_entries):
        #           stats_df[col] = stats_df[col].astype(pd.Int64Dtype())
        #       # otherwise, explicitly set the column's dtype as float
        #       else:
        #           stats_df[col] = stats_df[col].astype(float)
        #   elif isinstance(example, (int, np.integer)):
        #       stats_df[col] = stats_df[col].astype(pd.Int64Dtype())
        #   else:
        #       print(col)
        #       continue

        # change dtype of columns with numbers that could all be ints
        flt_cols = [col for col in stats_df.columns
                    if stats_df[col].dtype == float]

        for col in flt_cols:
            valid_entries = stats_df[col].dropna()
            n_ints = sum([n.is_integer() for n in valid_entries])

            if n_ints == len(valid_entries):
                stats_df[col] = stats_df[col].astype(pd.Int64Dtype())

        return stats_df
