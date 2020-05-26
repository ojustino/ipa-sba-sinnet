## `tennis_abs_api` 🎾
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ojustino/tennis-abs-api/master?filepath=query_examples.ipynb)
[![Build Status](https://travis-ci.org/ojustino/tennis-abs-api.svg?branch=master)](https://travis-ci.com/github/ojustino/tennis-abs-api/)

A Python API for querying Jeff Sackmann's
[Tennis Abstract](http://www.tennisabstract.com/) website, fetching historical
match data from its player data pages, and formatting the results as pandas
DataFrames for use in further analysis.

If you've ever wondered
[how many times Roger Federer has been bageled as a pro](
http://www.tennisabstract.com/cgi-bin/player-classic.cgi?p=RogerFederer&f=ACareerqqC2Q9)
or [how dominant Serena Williams used to be at closing out Grand Slams](
http://www.tennisabstract.com/cgi-bin/wplayer-classic.cgi?p=SerenaWilliams&f=Acx1995103020150810qqC0E0i1),
this package provides a programmatic interface for finding fast answers and
learning more about the results.

Skills used:
<br>
_(bear with me; I'm job-hunting)_

Headless browsing with `PyQt5`, HTML DOM manipulation, event triggering in
JavaScript, data(Frame) manipulation with `pandas`, testing with `pytest`,
object-oriented programming, multiple inheritance, regular expressions, and
more.

### Example usage:

Read through
[`query_examples.ipynb`](https://github.com/ojustino/tennis-abs-api/blob/master/query_examples.ipynb)
for a quick introduction.

### Installation ***(coming soon)***:

```
git clone https://github.com/ojustino/tennis-abs-api
cd tennis_abs_api
pip install .
```
(Add `-e` before the period in the final line if you intend to make changes to the source code.)

### License:

This project uses a slightly modified version of the PolyForm Noncommercial
License 1.0.0. Basically, you're free to view, run, download, and modify this
package for any non-commercial purpose. For more details, read the license in
full [here](https://github.com/ojustino/tennis-abs-api/blob/master/LICENSE.md).

### Acknowledgments:

Of course, this package wouldn't exist without Jeff Sackmann's efforts in
maintaining Tennis Abstract.
