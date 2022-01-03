## `tennis_abs_api` 🎾
<p>
  <a href="https://mybinder.org/v2/gh/ojustino/tennis-abs-api/30903c?filepath=walkthrough.ipynb" target="_blank">
    <img src="https://mybinder.org/badge_logo.svg"/>
  </a>
  <a href="https://travis-ci.com/github//ojustino/tennis-abs-api/" target="_blank">
    <img src="https://travis-ci.org/ojustino/tennis-abs-api.svg?branch=master"/>
  </a>
  <br />
  <i> ( ⬆️ click above to run in the cloud) </i>
</p>

A Python API for querying Jeff Sackmann's
<a href="http://www.tennisabstract.com/" target="_blank">Tennis Abstract</a>
website, fetching historical match data from its player data pages, and
formatting the results as `pandas` DataFrames for use in further analysis.

The package creates a thin, programmatic interface for finding quick answers to
questions like
<a href="http://www.tennisabstract.com/cgi-bin/player-classic.cgi?p=RogerFederer&f=ACareerqqC2Q9" target="_blank">
    how many times Roger Federer has been bageled as a pro
</a> or
<a href="http://www.tennisabstract.com/cgi-bin/wplayer-classic.cgi?p=SerenaWilliams&f=Acx1995103020150810qqC0E0i1" target="_blank">
    how dominant Serena Williams used to be at closing out Grand Slams
</a> and then learning more about the results.

**Skills used:**
<br>
_(bear with me; I'm job-hunting)_

Headless browsing in Python with `selenium` (and `PyQt5` in earlier commits),
HTML DOM manipulation, JavaScript event triggering, cross-browser (Chromium,
Firefox) and cross-OS (Mac, Ubuntu) support, Data(Frame) manipulation with
`pandas`, cloud-based Jupyter environment creation with Binder and Docker,
testing and continuous integration with `pytest` and Travis, object-oriented
programming, regular expressions, and a lot of persistence.

The site doesn't have a public API and is designed for front-end, click-based
interaction. Its backend system for querying match data has a number of
<a href="https://github.com/ojustino/tennis-abs-api/blob/master/attributes.md" target="_blank">
    gender and attribute-specific quirks
</a> that I sought to abstract away to create a simple, consistent experience
for Python users.

### Example usage:

Find out how I did by reading through
<a href="https://github.com/ojustino/tennis-abs-api/blob/master/walkthrough.ipynb" target="_blank">
    `walkthrough.ipynb`
</a> for a quick introduction. Or, click the badge atop this file for an
interactive walkthrough.

### Installation ***(coming soon)***:

```
git clone https://github.com/ojustino/tennis-abs-api
cd tennis-abs-api
pip install .
```
(Add `-e` before the period in the final line if you intend to make changes to the source code.)

### License:

This project uses a
<a href="https://github.com/ojustino/tennis-abs-api/blob/master/LICENSE.md" target="_blank">
    slightly modified version
<a/> of the PolyForm Noncommercial License 1.0.0. Basically, you're free to
view, run, download, and modify this package for any non-commercial purpose.

### Acknowledgments:

Of course, this package wouldn't exist without Jeff Sackmann's efforts in
maintaining Tennis Abstract.
