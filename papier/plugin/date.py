import datetime
import dateparser
from dateparser_data.settings import default_parsers


def predict_date(doc: str, lang: str = None,
                 ref: datetime.datetime = None) -> str:
    import warnings
    warnings.filterwarnings("ignore", module="dateparser")

    if ref is None:
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
                          doc,
                          languages=languages,
                          settings=settings) if
                      date <= ref]
    except TypeError:
        candidates = []

    if len(candidates) > 0:
        return candidates[0][1].strftime("%Y-%m-%d")
    else:
        return "XXXX-XX-XX"
