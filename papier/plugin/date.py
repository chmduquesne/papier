import papier
import datetime
import dateparser
import dateparser.search
from dateparser_data.settings import default_parsers
from typing import Any


@papier.extracts(consumes=['lang'], produces=['date'])
def extract_date(document: papier.Document, tags: dict[str, Any]
                 ) -> tuple[dict[str, Any], dict[str, Any]]:

    lang = tags['lang']
    ref = datetime.datetime.now()

    settings = {}
    settings['REQUIRE_PARTS'] = ['year', 'month']
    settings['PREFER_DAY_OF_MONTH'] = 'first'
    settings['PARSERS'] = [p for p in default_parsers if p != 'relative-time']

    languages = None
    if lang is not None:
        languages = [lang]

    try:
        candidates = [(text, date) for (text, date) in
                      dateparser.search.search_dates(
                          document.text,
                          languages=languages,
                          settings=settings) if
                      date <= ref]
    except TypeError:
        candidates = []

    res = 'XXXX-XX-XX'
    if len(candidates) > 0:
        res = candidates[0][1].strftime("%Y-%m-%d")

    return ({'date': res}, {})
