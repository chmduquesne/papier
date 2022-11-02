"""
Support for papier predictors

We try to run the predictors so that they can benefit from each other's
results.

Predictors can specify tags that they would like to consume, along with
tags they provide.
"""
from collections import namedtuple



Predictor = namedtuple('Predictor', ['func', 'consumes', 'produces'])



_predictors = []



def register_predictor(func, produces=None, consumes=None):
    """Register a predictor, its preferred dependencies"""
    _predictors.append(Predictor(func, produces, consumes))




def unsatisfied(predictors):
    """total unsatisfied dependencies if the list is processed in order"""
    available = set()
    res = 0
    for p in predictors:
        for tag in p.consumes:
            if tag not in available:
                res += 1
        for tag in p.produces:
            available.add(tag)
    return res




def resolve(predictors):
    """sort the predictors to minimize the total unmet dependencies"""
    res = []
    for p in predictors:
        possibilities = []
        for i in range(len(curr) + 1):
            possibilities.append(res[:i] + [p] + res[i:])
        res = min(possibilities, key=unsatisfied)
    return res
