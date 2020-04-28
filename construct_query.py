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
            # it'd be good to check if 'tennisabstract.com' and 'player-classic'
            # are present as well. could be a separate _validate_url() method

            if differentiate is None:
                raise ValueError('Unexpected URL.')
            elif differentiate[-1] == 'w':
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
        Convert a query's resulting match data table into a final pandas
        DataFrame that's ready to be handed off to the user.

        Since data is spread across multiple tables on Tennis Abstract's
        player data pages, they must be merged post-query. The method does so by
        converting them into a single DataFrame and applying some formatting
        (simplifying categories, typing, handling null values, etc.)

        Arguments
        ---------

        html_tables : list, required
            A list of HTML tables retrieved from the query.
        '''
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
        data = ft.reduce(pd.merge, table_dfs)
        data = data.iloc[:-1] # last row has an unneeded link

        # format NaNs consistently, including other null patterns
        data.fillna(np.nan)
        data = data.replace(['^-$', r'-.*\(\d*/\d*\)'], np.nan, regex=True)

        # give name to results column
        result_col_og = 'Unnamed: 6'
        assert result_col_og in set(data.columns), ('column names/order '
                                                    'might have changed')
        data = data.rename(columns={result_col_og: 'Result'})

        # add a column to note whether the match was a win or loss
        # (if 'd.' comes before the country code, it's a win)
        won = (lambda val: (1 if re.search(r'd\.', val).span()[0]
                            < re.search(r'\[.*\]', val).span()[0]
                            else 0))
        # what about special cases?
        #walkover = [st.span()[-1] for st in re.finditer('W/O', result)]
        #retired...
        # need to account for failed searches... think about how
        #raise ValueError("Unexpected 'Result' string; "...)

        data['Won'] = data['Result'].apply(won)

        # move it beside the 'Score' column
        all_cols = list(data.columns)
        score_at = all_cols.index('Score')
        all_cols.insert(score_at, all_cols.pop())

        data = data[all_cols]

        # change dtype of columns w/ percentages as strings
        for col in data.columns:
            valid_entries = data[col].dropna()
            examp = (valid_entries.iloc[0]
                     if valid_entries.size > 0 else None)

            if examp is None:
                # skip columns where this isn't the case
                continue
            elif isinstance(examp, str) and examp[-1] == '%':
                # convert values. throw out those below 0 or above 100
                # (slicing by [:-1] removes index with '%')
                data[col] = data[col].apply(lambda val: float(val[:-1])
                                            if pd.notnull(val)
                                            and 0 <= float(val[:-1]) <= 100
                                            else np.nan)

                # ensure that column dtype has changed
                data = data.astype({col: np.float64})

                # add pct sign to these columns' names if it isn't present
                if col[-1] != '%':
                    data = data.rename(columns={col: col + '%'})
            elif isinstance(examp, float):
                # if all floats in the col could be ints, make it an int column
                if all(en.is_integer() for en in valid_entries):
                    data = data.astype({col: pd.Int64Dtype()})

        # split each break point column into two:
        # BPCo(n)v & BPS(a)v(e)d into Brks/BPForced & Brkn/BPFaced
        bp_cols = (col for col in data.columns if col.startswith('BP'))

        for col, col_data in data[bp_cols].iteritems():
            # set names for new columns based on current, "old" BP column
            new_cols = (['Brkn', 'BPFaced'] if re.match('BPSa?ve?d', col)
                        else ['Brks', 'BPForced'] if re.match('BPCo?nv', col)
                        else [])

            if new_cols:
                # save split version of BP column to be updated later
                # (format is 'NN.N% (Y/Z)'; split to get Y and Z)
                bp_info = col_data.apply(lambda vals: vals.split()[-1]
                                         if pd.notnull(vals) else np.nan)

                # add new columns in same order as Y and Z, ensuring type
                for i, c in enumerate(new_cols):
                    data[c] = bp_info.apply(lambda val:
                                            int(re.findall(r'\d+', val)[i])
                                            if pd.notnull(val) else np.nan)
                    data = data.astype({c: pd.Int64Dtype()})

                # move new columns beside predecessor BP column; drop the latter
                all_cols = list(data.columns)
                old_col_at = all_cols.index(col)
                all_cols = (all_cols[:old_col_at] + new_cols
                            + all_cols[old_col_at+1 : -len(new_cols)])
                data = data[all_cols]
            else:
                # import warnings!
                warnings.warn(f"Unexpected break point column name '{col}'")

        # finish changing 'BPSaved' to 'Brkn' (i.e., 'BPLost')
        data['Brkn'] = data['BPFaced'] - data['Brkn']

        # change dtypes of as of yet untouched 'object' type columns
        oth_cols = (col for col in data.columns
                    if data[col].dtype == np.dtype('O'))
        oth_col_types = []

        for col in oth_cols:
            valid_entries = data[col].dropna()
            examp = (valid_entries.iloc[0]
                     if valid_entries.size > 0 else '')

            if examp:
                # if examp is a number, type it as a float or int
                try:
                    oth_type = (pd.Int64Dtype()
                                if all(en.is_integer() for en in valid_entries)
                                else np.float64)
                # if examp is not a number, type it as a str
                except AttributeError:
                    oth_type = pd.StringDtype()
            else:
                # if column is all NaNs, don't change its dtype
                oth_type = np.dtype('O')

            # add this column's adjusted type to the list
            oth_col_types.append(oth_type)

        # assign the new dtypes
        data = data.astype(dict(zip(oth_cols, oth_col_types)))

        # stretch: if most stat cols in a row are NaN make all stat entries in
        # that row NaN?

        return data
