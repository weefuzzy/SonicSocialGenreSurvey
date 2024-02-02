import pandas as pd
import itertools
from functools import partial


""" 
Dictionaries to map column ranges to data levels, so that we group (e.g.) datasets together with pd Multindex for easier querying 
keys are top-level category, values are column *ranges* given by start and end labels (inclusive)
it's absolutely up to us as frail humans to ensure that these make sense: minimal error checking at this point
"""
datamaps = {
    "old": {
        "type": ["Review", "Experimental"],
        "datasets": ["GTZAN", "Unique"],
        "aggregates": ["Number public", "No. datasets"],
        "data_types": ["Music audio", "Non-Western?"],
        "doe": ["Classify", "Generalize"],
        "fom": ["Accuracy", "confusion instances"],
    },
    "new": {
        "type": ["Review", "Experimental"],
        "datasets": ["GTZAN", "PMG-Data"],
        "aggregates": ["Number public", "No. datasets"],
        "data_types": ["Music audio", "Non-Western?"],
        "doe": ["Classify", "Generalize"],
        "fom": ["Accuracy", "confusion instances"],
        "curiosity": ["Cites Critical MIR", "Engages Genre-Theory"],
        "rationale": ["Information Overload", "Public Utility"],
        "ontology": ["Flat", "Graph"],
    },
}


def read_survey_csv(path):
    """
    Read in one of the CSV files, ignoring surplus rows; fill empty cells with 0 nor NaN; delete unamed cols; make sure data is numeric
    """
    SKIP = [0, 2, 3]
    # read in csv, skipping unneeded rows at top 
    df = pd.read_csv(path, skiprows=SKIP, index_col=0).fillna(value=0)
    # drop unamed cols
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    # end of usuable data range is marked by TOTALS row, find that point and snip
    index_end = df.index.get_loc('TOTALS')
    df = df[:index_end - 1]    
    # get rid of empty rows
    df = df[df.index.notnull()]
    # mop up any 'I am not a number' weirdness
    df = df.apply(partial(pd.to_numeric, errors="coerce"))
    return df


def getcolrange(df, start_label, end_label):
    """
    Return the list of column labels in df between start_label and end_label, inclusive
    """
    s = df.columns.get_loc(start_label)
    f = df.columns.get_loc(end_label)
    return list(df.columns[s : f + 1])


def nest(a, b):
    """
    For constructing a pd.Multiindex for the data,
    return a list of tuples from the cartesian product of a top level label and a list of sub-labels
    """
    return list(itertools.product(a, b))


def make_multiindex_from_map(df, map):
    """
    For constructing a pd.Multiindex for the data columns of df
    Given a dict, `map`, whose keys are top level labels and whose value are a 2 item list with start and end column labels
    construct a pd.MultiIndex that gathers up all the columns between the starts and ends and associates them with the appropriate label
    returns a two-level multiindex
    """
    return pd.MultiIndex.from_tuples(
        list(
            itertools.chain(
                *[nest([k], getcolrange(df, v[0], v[1])) for k, v in map.items()]
            )
        )
    )


def load_survey_data(path, map):
    """
    read in and tidy a csv file and make a nice multindex for columns
    at this point still requires user to supply N of records to read. Fix this later if it makes us sad
    """
    df = read_survey_csv(path)
    newidx = make_multiindex_from_map(df, map)
    df.columns = newidx
    return df


if __name__ == "__main__":
    read_survey_csv("../../../data/new_survey.csv")
