import functools as ft
import re
import selenium.common.exceptions as selexcept
import sys
import unicodedata

from better_abc import ABC, abstractmethod#, abstract_attribute
#from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


HOME_URL = 'http://www.tennisabstract.com/'

class LoadAndInteract(ABC):
    '''
    A parent for NameCheck, QueryData, or any class that uses selenium's
    headless browsing framework to load a webpage (static or
    JavaScript-rendered), "interact" with it (typically by programmatically
    triggering JavaScript events), and save elements of interest from the page.

    This is an abstract base class defined such that any children must include a
    self.inetract() method that defines the actual interactions that will take
    place.

    Arguments
    ---------

    url : str, required
        The URL of the target webpage.

    browser : str, required
        The browser that selenium will drive headlessly to the relevant URL.
        For now, choose between 'chromium' and 'firefox'. [default: 'chromium']

    load_images : boolean, required [DEPRECATED?]
        When False, prevents images on the target webpage from loading, which
        *should* decrease wait times. Need to determine whether this is possible...

    verbose : boolean, optional
        Controls whether or not to print debugging information. [default: False]
    '''
    def __init__(self, url, browser, verbose=False):#, load_images):
        self._vb = verbose

        # create the WebDriver instance used to browse
        driver = self.choose_browser(browser)

        # how long (in seconds) to wait for actions on the page to execute
        bide = WebDriverWait(driver, 5)
        # PERHAPS WAIT TIME SHOULD BE A KWARG?

        # load and interact with the page; close connection on completion/error
        self._pr('LoadAndInteract')
        driver.get(url)
        try:
            self.interact(driver, bide)
        except Exception as e:
            driver.close()
            raise e
        else:
            driver.close()

    def _pr(self, *args, **kwargs):
        print(*args, **kwargs) if self._vb else None

    def choose_browser(self, browser):
        if browser == 'chromium':
            from selenium.webdriver.chrome.options import Options
            Driver = webdriver.Chrome
        elif browser == 'firefox':
            from selenium.webdriver.firefox.options import Options
            Driver = webdriver.Firefox
        else:
            raise ValueError('invalid browser. choose "chromium" or "firefox".')

        # set browser options, which are the same for both
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-extensions')

        # create the WebDriver instance used to browse
        driver = Driver(options=options)
        driver.set_window_size(1440, 810)
        return driver

    @abstractmethod
    def interact(self, driver, bide):
        '''
        Performs the actual interaction with the desired webpage. Make sure to
        include the arguments when re-writing this abstract method.

        Arguments
        ---------

        driver : selenium.webdriver.firefox.webdriver.WebDriver, required
            An object that begins a FireFox browsing session and can send
            commands to the queried webpage.

        bide : selenium.webdriver.support.wait.WebDriverWait, required
            A constructor that sets a timer ('bides time') on an expected
            webpage event and throws an error if it doesn't occur.
        '''
        pass

class AwaitJSCondition:
    '''
    Serves as an argument for bide.until() (bide is a selenium WebDriverWait
    instance) prevents the code following its initialization from running until
    the JavaScript code provided as an argument returns "True".

    Arguments
    ---------

    js : str, required
        The JavaScript code with the conditions to check on the webpage. Should
        return "false" if the desired condition has not been met and "true" if
        it has. If there are portions that need to be filled in dynamically,
        write them as 'arguments[i]', with i being the index of the matching
        `entry` argument (starting from 0).

    entry : str, required [SHOULD BE ABLE TO TAKE ANY NUMBER OF ARGUMENTS]
        An object to insert into `js` when it's time to execute the JavaScript
        code.
    '''
    def __init__(self, js, entry):
        self.js = js
        self.entry = entry

    def __call__(self, driver):
        return driver.execute_script(self.js, self.entry)

class NameCheck(LoadAndInteract):
    '''
    Checks whether a provided name string has a matching player page on Tennis
    Abstract's website. If there's a match, saves the name string (formatted for
    use in query URLs) in the `name_str` class attribute.

    Inherits from LoadAndInteract to handle initial loading of the webpage and
    set itself up for interaction, then enters each name in the string (e.g.,
    first, middle, last, etc.) in the search bar on Tennis Abstract's homepage.
    The class saves the suggestions for each name and will only initialize
    successfully if there's one entry that appears in each suggestion list.

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

    url : str, optional
        The URL of the target webpage.
        [default: 'http://www.tennisabstract.com/']
        PERHAPS SHOULDN'T BE AN ARGUMENT AND **HOME_URL** SHOULD BE A CLASS ATTR OR DEFINED IN __init__()?

    browser : str, required
        The browser that selenium will drive headlessly to the relevant URL.
        For now, choose between 'chromium' and 'firefox'. [default: 'chromium']

    load_images : boolean, optional [DEPCREATED?]
        When False, prevents images on the target webpage from loading, which
        *should* decrease wait times. I hope to test whether this is the case.
        [default: False]
    '''
    # should max_wait (seconds) be an argument?
    def __init__(self, name, tour, url=HOME_URL, browser='chromium'):#, load_images=False):
        self.names = self.ready_names(name)
        self.gender = self.ready_gender(tour)
        self.suggestions = []

        # load URL, retrieve matching names
        super().__init__(url, browser)#, load_images)
        self.name_str = self.validate_name()

    def ready_names(self, name):
        # remove non-letter characters and split (first, last, etc.)
        split_names = re.sub('[^a-zA-Z]', ' ', name).split()

        # ensure each string to be searched only appears once
        final_names = list(set(split_names))
        return final_names

    def ready_gender(self, tour):
        tour = tour.upper()
        if tour == 'ATP':
            gender = 'M'
        elif tour == 'WTA':
            gender = 'W'
        else:
            raise ValueError('Ineligible tour. Should be ATP or WTA.')

        return gender

    def interact(self, driver, bide):
        self._pr('interact')
        # changes value in player search box, then create and trigger a keydown
        # event to reveal autocomplete suggestions
        input_js = """
            var input = document.getElementById('tags');
            var action = new Event('keydown',
                                   {'key': 'ArrowDown', 'code': 'ArrowDown',
                                    'keyCode': 40 });
            input.onchange = function(){
                input.dispatchEvent(action);
            }

            input.value = arguments[0];
            input.onchange();"""

        # if the input value has changed to the new entry *and* the list of
        # suggestions has changed from its previous state, saves new suggestions
        # [TIP: return instead of console.log() to view output. works for
        #  bool, int, float, lists (as js Arrays), and dict (as js Lists)]
        suggests_js = """
            var input = document.getElementById('tags');
            if (input.value !== arguments[0]) { return false; }

            var entered = arguments[0].toLowerCase();
            nodes = document.querySelectorAll('a.ui-corner-all');
            var suggests = Array.from(nodes);
            suggests = suggests.slice(0, 5).map(s => s.text.toLowerCase());

            if (suggests[0]) {
                var matched = suggests.filter(s => s.includes(entered));
                if (matched.length === suggests.length) { return true; }
            }"""

        for nm in self.names:
            self._pr('search name')
            # enter the current name in the search bar
            driver.execute_script(input_js, nm)

            # wait for input value to change on page
            bide.until(EC.text_to_be_present_in_element_value((By.ID, 'tags'),
                                                              nm))

            # wait for dropdown of suggestions to appear
            bide.until(AwaitJSCondition(suggests_js, nm))

            # save set of those suggestions
            lk_matches = driver.find_elements_by_css_selector('a.ui-corner-all')
            nm_matches = {lk.text[4:] for lk in lk_matches
                          if lk.text[1] == self.gender}
            self.suggestions.append(nm_matches)

    def validate_name(self):
        '''
        Find the name that appears in every set in `self.suggestions` after
        webpage interaction is complete. Throws an error if there's no match
        or more than one.
        '''
        self._pr('validate_name')
        # gather suggestion(s) that matched each name
        name_set = ft.reduce(set.intersection, self.suggestions)

        # if there's only one match, treat it as the selected player
        if len(name_set) == 1:
            # remove spaces for use in URL
            name_str = name_set.pop().replace(' ','')
            return name_str

        elif len(name_set) == 0:
            raise ValueError(
                'There were no direct matches. Did you provide a '
                'valid name? Did you provide the proper tour?')

        else:
            # (could use counter instead and report most common matches?)
            # print out some example names
            name_strs = [nm for nm in name_set][:10]
            newl = '\n'
            raise ValueError(
                'Your name pulled up multiple matches, including:'
                f"""{newl}'{"', '".join(name_strs)}'.{newl}"""
                'If you see a match, copy it and re-run. '
                'Otherwise, be more specific if possible, providing '
                'full first *and* last names.')

class QueryData(LoadAndInteract):
    '''
    Performs the actual connection-based query work for DownloadStats() by
    scraping all available match data from the tables on a Tennis Abstract
    webpage associated with the provided URL.

    Inherits from LoadAndInteract to handle initial loading of the webpage and
    set itself up for interaction, then saves the intial match data table.
    More information is usually accessible upon clicking a link or two, so it
    simulates an appropriate number of click events and saves the resulting
    table after each step.

    Arguments
    ---------

    url : str, optional
        The URL of the target webpage.

    tour : str, required
        The chosen player's tour. Should be 'WTA' if the player is female or
        'ATP' if the player is male.

    browser : str, required
        The browser that selenium will drive headlessly to the relevant URL.
        For now, choose between 'chromium' and 'firefox'. [default: 'chromium']

    load_images : boolean, optional [DEPRECATED?]
        When False, prevents images on the target webpage from loading, which
        *should* decrease wait times. I hope to test whether this is the case.
        [default: False]
    '''
    # should max_wait (seconds) be an argument?
    def __init__(self, url, tour, browser='chromium'):#load_images=False):
        self.tour = self.ready_tour(tour)

        self.html_tables = []
        self.title = None

        # load URL
        super().__init__(url, browser)#, load_images)

    def ready_tour(self, tour):
        tour = tour.upper()
        if tour not in {'ATP', 'WTA'}:
            raise ValueError('Ineligible tour. Should be ATP or WTA.')

        return tour

    def interact(self, driver, bide):
        # fetch original stats table on page, toggle its stats by simulating
        # clicks on one or more pseudo-links, then save the new table(s)
        self._pr('interact')

        # reverse loss scores in table; wait for change to reflect
        self._pr('reverse losses')
        rev_elem = 'span.revscore.likelink'
        bide.until(EC.element_to_be_clickable((By.CSS_SELECTOR, rev_elem)))
        driver.find_element_by_css_selector(rev_elem).click()
        bide.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, rev_elem),
                                                    'Standard Scores'))

        # find and save the initial table visible on the page
        bide.until(EC.visibility_of_element_located((By.ID, 'matches')))
        self.html_tables.append(self.search_table(driver))

        # get id(s) of <span>(s) on which to simulate clicks and
        # their expected text content after the click takes place
        if self.tour == 'WTA':
            classes = ['srclick']
            expected = 'Show Serve Stats'
        # (tour value was already validated in self.ready_tour())
        else: # == 'ATP'
            classes = ['statsr', 'statsw'] # 'statso' selected by default
            expected = '.likelink'

        # save table title, if it exists
        title = driver.find_element_by_id('tablelabel').text
        if title:
            self.title = unicodedata.normalize('NFKD', title)
        else:
            # if not, wait until after page interaction to deal with it
            self.title = ''

        # GIVE EC METHODS AN ERROR MESSAGE FOR WHEN CONDITION IS NOT MET ON TIME
        # ...
        for cl in classes:
            self._pr('click span')
            # simulate a click on the current element
            curr_elem = 'span.' + cl# + '.likelink'
            driver.find_element_by_css_selector(curr_elem).click()

            # wait for clicked span to lose its 'likelink' class
            # (will also pass if the span just doesn't exist)
            if self.tour == 'WTA':
                # until rev_elem's text changes
                bide.until(EC.text_to_be_present_in_element(( By.CSS_SELECTOR,
                                                              curr_elem ),
                                                            expected))
            else:
                # until clicked span loses its 'likelink' class
                bide.until(EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                               curr_elem
                                                               + expected)))

            # save the current version of the data table (always has same id)
            self.html_tables.append(self.search_table(driver))

    def search_table(self, driver):
        #self._pr('search_table')
        try:
            table = driver.find_element_by_id('matches')
            return table.get_attribute('outerHTML')
        except selexcept.NoSuchElementException:
            # if no matching element, inform user after interaction terminates
            return ''
        # should it be BeautifulSoup(table, features='lxml') so I can keep
        # same error messages in DownloadStats??

        # if not, soup = BeautifulSoup(test) at start of merge_and_edit_tables
        # if soup.contents == [], error #1 (no is None condition)
        # if soup.find('p'), error #2
        # if not soup.find('table'), error #3
        # then, work with NON-soup content for rest of method
