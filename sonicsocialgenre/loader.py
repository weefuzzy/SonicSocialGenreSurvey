import re
from collections import defaultdict
import numpy as np
import pandas as pd
import bibtexparser


def load_bib(path):
    """Load a bibtex file return a data frame with the vitals"""
    library = bibtexparser.parse_file(path)

    t = {"article": "journal", "inproceedings": "conference"}

    p = defaultdict(
        (lambda: lambda x: None),
        {
            "article": (lambda x: x.fields_dict["journaltitle"].value),
            "inproceedings": (
                lambda x: (
                    x.fields_dict["eventtitle"].value
                    if "eventtitle" in x.fields_dict
                    else x.fields_dict["booktitle"].value
                )
            ),
        },
    )

    pubs = [
        (
            (
                t.get(v.entry_type, v.entry_type)
                if v.entry_type != "thesis"
                else v.fields_dict["type"].value
            ),
            p[v.entry_type](v),
            v.fields_dict["doi"].value if "doi" in v.fields_dict else None,
        )
        for k, v in library.entries_dict.items()
    ]

    pubs_df = pd.DataFrame.from_records(
        pubs,
        index=[k for k in library.entries_dict.keys()],
        columns=["type", "venue", "doi"],
    )
    pubs_df.fillna(pd.NA, inplace=True)

    # purge the publication venues of braces
    debrace_re = re.compile(r"[\{\}]")
    pubs_df.venue = pubs_df.venue.apply(
        lambda s: debrace_re.sub(lambda x: "", s) if not pd.isnull(s) else pd.NA
    )
    pubs_df.type.astype("category")
    return pubs_df


def load_mgr_survey(path, bibpath=None):
    """
    Load up the survey data from the spreadsheet
    Return a nice boolean dataframe with a multiindex
    """
    # load raw csv; header=[0,1] creates us a multiindex on columns, but it will need some tidying
    df = pd.read_csv(
        path, header=[0, 1], skip_blank_lines=True, index_col=0, skipinitialspace=True
    )
    # needs some tidying

    # original survey data missing label for contribution type category
    # df.columns['Unnamed: 2_level_0'] = 'FUNCTION'

    # nans => 0s
    df.fillna(0, inplace=True)
    # surplus columns:
    #  - any at level 1 of multiindex containing 'unnamed'
    #  - spreadsheet columns that were just doing summations

    surplus_columns = df.columns[
        df.columns.get_level_values(1).str.contains("Unnamed")
        | df.columns.get_level_values(1).str.contains("No. datasets")
        | df.columns.get_level_values(1).str.contains("Number public")
    ]
    df.drop(columns=surplus_columns, inplace=True)

    # surely a better way exists
    col_tup = list(df.columns.to_flat_index())
    loc_private = df.columns.get_level_values(1).get_loc("Private data")
    loc_music = df.columns.get_level_values(1).get_loc("Music audio")
    col_tup[loc_private] = ("Private", "data")
    col_tup[loc_music] = ("modality", "Music audio")
    df.columns = pd.MultiIndex.from_tuples(col_tup)
    # # now sort out the multiindex so that the top level is correct: replace all unnamed with the preceding label
    df.columns = pd.MultiIndex.from_frame(
        df.columns.to_frame()
        .apply(lambda x: np.where(x.str.contains("Unnamed"), np.nan, x))
        .ffill()
    )
    # make column labels lower snake case and free of punctuation
    punc = re.compile(r"[^A-Z,a-z,0-9,_]")
    space = re.compile(r"[\s,-]")
    formatter = lambda s: punc.sub("", space.sub("_", s)).lower()
    top_level = list(map(formatter, df.columns.get_level_values(0)))
    first_level = list(map(formatter, df.columns.get_level_values(1)))
    df.columns = pd.MultiIndex.from_arrays(
        [top_level, first_level], names=["category", "variable"]
    )

    # # get rid of unneeded rows
    df = df.iloc[0 : df.index.get_loc("TOTALS") - 1]
    df = df[df.index.notnull()]

    # make it bool
    df = df.astype("bool")

    # add a year column
    regex_year = re.compile(r".+([0-9]{4})[a-z]?")
    df["year"] = [int(regex_year.match(e).groups()[0]) for e in list(df.index)]

    return df if not bibpath else (df, load_bib(bibpath))
