import functools as ft
import re
import sys
import unicodedata

from better_abc import ABC, abstractmethod#, abstract_attribute
from bs4 import BeautifulSoup
#from collections import Counter
from PyQt5.QtCore import pyqtSignal, QEventLoop, QTimer, QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEnginePage#, QWebEngineView


_app = QApplication(sys.argv) # must be defined before instantiating a QObject
HOME_URL = 'http://www.tennisabstract.com/'

class _LoadAndInteractMeta(type(QWebEnginePage), type(ABC)):
    '''
    Handles metaclasses for LoadAndInteract's multiple inheritance scheme.
    See https://stackoverflow.com/a/28727066 for more.
    '''
    pass

class LoadAndInteract(QWebEnginePage, ABC, metaclass=_LoadAndInteractMeta):
    '''
    A parent for NameCheck, QueryData, or any class that uses PyQt5's headless
    browsing framework to load a webpage (static or JavaScript-rendered),
    "interact" with it (typically by programmatically triggering one or more
    JavaScript events), and save elements of interest from the page.

    This is an abstract base class defined such that any children must include a
    self.on_load_finish() method that ends with a call to
    self.kill_qt_event_loop() in order to properly terminate PyQt's connection
    to the page once the interaction is over.

    Arguments
    ---------

    url : str, required
        The URL of the target webpage.

    load_images : boolean, required
        When False, prevents images on the target webpage from loading, which
        *should* decrease wait times. I hope to test whether this is the case.
    '''
    def __init__(self, url, load_images):
        # assign QApplication instance before connecting to webpage
        self.app = _app

        # initialize QWebEnginePage
        super().__init__()
        #QWebEnginePage.__init__(self)
        #print('init')

        # set whether images are allowed to load
        settings = self.settings()
        settings.setAttribute(settings.AutoLoadImages, load_images)

        # allow for Ctrl+C process interruption?
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

        # load URL
        self.interact(url)

    def interact(self, url):
        self.loadFinished.connect(self.on_load_finish)
        #print('connect')
        self.load(QUrl(url))
        #print('load url')
        self.app.exec_()
        #print('app exec')

    def kill_qt_event_loop(self):
        # quit Qt's event loop after finishing interaction
        # or before throwing an error. without this step, the interpeter/
        # notebook will hang and need to have its whole process killed
        self.app.quit()

    @abstractmethod
    def on_load_finish(self, result):
        '''
        Make sure to keep 'result' argument and, most importantly,
        **end the method with self.kill_qt_event_loop()**.
        '''
        pass

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

    load_images : boolean, optional
        When False, prevents images on the target webpage from loading, which
        *should* decrease wait times. I hope to test whether this is the case.
        [default: False]

    Tips
    ----

    awaiting runJavaScript's async output: https://stackoverflow.com/a/55621469
    awaiting toHtml's async output: https://stackoverflow.com/a/47067553
    triggering a JS change event: https://stackoverflow.com/q/5963056/
    '''
    # should max_att be an argument?
    toHtmlFinished = pyqtSignal()

    def __init__(self, name, tour, url=HOME_URL, load_images=False):
        self.names = self.ready_names(name)
        self.gender = self.ready_gender(tour)
        self.suggestions = []

        # load URL, retrieve matching names
        super().__init__(url, load_images)
        self.name_str = self.validate_name()

    def ready_names(self, name):
        # remove non-letter characters and split (first, last, etc.)
        split_names = re.sub('[^a-zA-Z]', ' ', name).split()
        return split_names

    def ready_gender(self, tour):
        tour = tour.upper()
        if tour == 'ATP':
            gender = 'M'
        elif tour == 'WTA':
            gender = 'W'
        else:
            raise ValueError('Ineligible tour. Should be ATP or WTA.')

        return gender

    def wait_for_runJavaScript(self, name):
        #print('wait')
        def wait_for_test(result, att=0, max_att=10):
            print('wait_for_test', att)
            if result == True or (att > max_att):
                loop.quit()
            else:
                # control max wait time here instead of in JS
                att += 1
                inner_wrapper = ft.partial(wait_for_test, att=att)
                wrapper = ft.partial(self.runJavaScript,
                                     js, inner_wrapper)
                QTimer.singleShot(500, wrapper)

        # begin loop
        loop = QEventLoop()

        # has the input value changed to what was entered?
        # if so, has the list of suggestions appeared/changed?
        # [TIP: return instead of console.log() to view output. works for
        #  bool, int, float, lists (as js Arrays), and dict (as js Lists)]
        js = """
            function task(){{
                var input = document.getElementById('tags');
                if (input.value !== '{0}') {{ return false; }}

                var entered = '{0}'.toLowerCase();
                nodes = document.querySelectorAll('a.ui-corner-all');
                var suggests = Array.from(nodes).slice(0, 5);
                suggests = suggests.map(s => s.text.toLowerCase());

                if (suggests[0]) {{
                    var matched = suggests.filter(s => s.includes(entered));
                    if (matched.length === suggests.length) {{ return true; }}
                }}
            }}
            task();""".format(name)
        # for testing with input_test.html
        # js = """
        #   function task(){{
        #       var input = document.getElementById('tags');
        #       if (input.value == '{0}') {{ return true; }}
        #       else {{ return false; }}
        #   }}
        #   task();""".format(name)

        #print(js)
        self.runJavaScript(js, wait_for_test)
        loop.exec_()

    def on_load_finish(self, result):
        #print('on_load_finish')

        # change value in player search box, then write a keydown event
        # and trigger it to reveal autocomplete suggestions
        js = """
            var input = document.getElementById('tags');
            var action = new Event('keydown',
                                   {{'key': 'ArrowDown', 'code': 'ArrowDown',
                                    'keyCode': 40 }});
            input.onchange = function(){{
                input.dispatchEvent(action);
            }}

            input.value = '{}';
            input.onchange();"""

        # find an <input> with id 'tags' or class 'ui-autocomplete-input'
        # and, one at a time, enter names in self.names to get suggestions
        for nm in self.names:
            # run js asynchronously; wait for it to finish
            self.runJavaScript(js.format(nm))
            self.wait_for_runJavaScript(nm)

            # search suggestions asynchronously; wait for them to appear
            self.toHtml(self.search_html)
            loop = QEventLoop()
            self.toHtmlFinished.connect(loop.quit)
            loop.exec_()

        # remember to quit the Qt process
        self.kill_qt_event_loop()

    def search_html(self, html_str):
        #print('search_html')
        soup = BeautifulSoup(html_str, features='lxml')

        # all <a> with class 'ui-corner-all'
        suggested_links = soup.find_all('a', attrs={'class': 'ui-corner-all'})
        #suggested_links = soup.find_all('a')
        #print([a.text for a in suggested_links][:10])

        # name text is "(M)" or "(W)" followed by name, so restrict to
        # names with a matching gender
        suggested_names = {lk.text[4:] for lk in suggested_links
                           if lk.text[1] == self.gender}

        self.suggestions.append(suggested_names)
        self.toHtmlFinished.emit()

    def validate_name(self):
        # is there a name that appears in every list?

        # if any, gather suggestion(s) that matched each name
        #suggest_sets = [set(sug) for sug in self.suggestions]
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

    load_images : boolean, optional
        When False, prevents images on the target webpage from loading, which
        *should* decrease wait times. I hope to test whether this is the case.
        [default: False]

    Tips
    ----
    awaiting runJavaScript's async output: https://stackoverflow.com/a/55621469
    awaiting toHtml's async output: https://stackoverflow.com/a/47067553
    triggering a JS change event: https://stackoverflow.com/q/5963056/
    '''
    # should max_att be an argument?
    toHtmlFinished = pyqtSignal()

    def __init__(self, url, tour, load_images=False):
        self.tour = self.ready_tour(tour)

        self.html_tables = []
        self.title = None

        # load URL
        super().__init__(url, load_images)

    def ready_tour(self, tour):
        tour = tour.upper()
        if tour not in {'ATP', 'WTA'}:
            raise ValueError('Ineligible tour. Should be ATP or WTA.')

        return tour

    def wait_for_runJavaScript(self, id_, exp_text):
        #print('wait')
        def wait_for_test(result, att=0, max_att=10):
            print('wait_for_test', att)
            if result or (att > max_att):
                loop.quit()
            else:
                # control max wait time here instead of in JS
                att += 1
                inner_wrapper = ft.partial(wait_for_test, att=att)
                wrapper = ft.partial(self.runJavaScript,
                                     js, inner_wrapper)
                QTimer.singleShot(500, wrapper)

        # begin loop
        loop = QEventLoop()

        # write JS code to test if the table has been toggled
        if self.tour == 'WTA':
            # check that the <span>'s text matches check_text
            js = """
                function task(){{
                    var span = document.querySelector('span.{0}');
                    if (span.innerText === '{1}') {{ return true; }}
                    else {{ return false; }}
                }}
                task();""".format(id_, exp_text)
        else: # == 'ATP'
            # check that the <span> is no longer of class check_text
            js = """
                function task(){{
                    var span = document.querySelector('span.{0}');
                    var classes = Array.from(span.classList);

                    if (classes.indexOf('{1}') == -1) {{ return true; }}
                    else {{ return false; }}
                }}
                task();""".format(id_, exp_text)

            # for eventually reversing loss scores
            # js = """
            #   function task(){{
            #       var span = document.querySelector('span.{0}');
            #       var classes = Array.from(span.classList);

            #       if (classes.indexOf('{1}') == -1) {{ return true; }}
            #       else {{ return false; }}
            #    }}
            #    task();""".format('revscore', 'likelink') # pass as args?

        #print(js)
        self.runJavaScript(js, wait_for_test)
        loop.exec_()

    def on_load_finish(self, result):
        #print('on_load_finish')
        # fetch original stats table on page, toggle its stats by simulating
        # clicks on one or more pseudo-links, then save the new table(s)

        # fetch original stats table asynchronously; wait for completion
        self.toHtml(self.search_table)

        loop = QEventLoop()
        self.toHtmlFinished.connect(loop.quit)
        loop.exec_()

        # get id(s) of <span>(s) on which to simulate clicks and
        # their expected text content after the click takes place
        if self.tour == 'WTA':
            ids = ['srclick']
            exp_text = 'Show Serve Stats'
        # (tour value was already validated in self.ready_tour())
        else: # == 'ATP'
            ids = ['statsr', 'statsw'] # 'statso' selected by default
            exp_text = 'likelink'

        # write JS code that simulates the click
        script = """
            span = document.querySelector('span.{}');

            action = new Event('click');
            span.onchange = function(){{ span.dispatchEvent(action); }}
            span.onchange();"""

        # simulate a click on each element in ids
        # (also asynchronous, so wait for completion)
        for id_ in ids:
            # format script to include current id_
            self.runJavaScript(script.format(id_))
            self.wait_for_runJavaScript(id_, exp_text)

            # fetch the resulting stats table; wait for completion
            self.toHtml(self.search_table)

            loop = QEventLoop()
            self.toHtmlFinished.connect(loop.quit)
            loop.exec_()

        # remember to quit the Qt process
        self.kill_qt_event_loop()

    def search_table(self, html_str):
        # found ids by manually searching a representative page's html
        #print('search_table')
        soup = BeautifulSoup(html_str, features='lxml')

        # find and save the table (always has the same id)
        table = soup.find(attrs={'id': 'matches'})
        self.html_tables.append(table)

        # save table title if this is the first time through
        if self.title is None:
            title = soup.find('td', attrs={'id': "tablelabel"}).contents[0]
            # if it doesn't exist, find out after the Qt process closes
            if hasattr(title, 'text'):
                self.title = unicodedata.normalize('NFKD', title.text)
            else:
                self.title = ''

        self.toHtmlFinished.emit()
