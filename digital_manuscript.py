import os
import re
import pandas as pd
from typing import List, Union, Optional
from recipe import Recipe
from manuscript_helpers import generate_complete_manuscript

properties = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name', 'profession', 'sensory', 'tool', 'time', 'weapon']

class BnF():

  def __init__(self, entry_list: List[str] = [], apply_corrections: bool = True) -> None:
    """
    Initialize entire manuscript as a dictionary of Recipe objected keyed by div ID.
    If a list of IDs is given, return a dict with these entries only.
    
    Inputs:
      entry_list: A list of div IDs
      apply_corrections: A bool deciding whether or not to apply the changes detailed in teh thesaurus.
                         For more information, checkout thesaurus.py.
    
    Outputs:
      None
    """
    complete_manuscript = generate_complete_manuscript(apply_corrections=apply_corrections)
    if entry_list: # choose specified entries
      self.entries = {i:e for i, e in complete_manuscript.items() if e.identity in entry_list}
    else: # otherwise, return all entries
      self.entries = complete_manuscript

  def entry(self, identity: str = ''):
    """ Return entry with the given identity. """
    return self.entries.get(identity)

  search_type = Optional[Union[List[str], bool]]
  def search(self, animal: search_type = None, body_part: search_type = None, currency: search_type = None,
             definition: search_type = None, environment: search_type = None, material: bool = None,
             medical: search_type = None, measurement: search_type = None, music: search_type = None,
             plant: search_type = None, place: search_type = None, personal_name: search_type = None,
             profession: search_type = None, sensory: search_type = None, tool: search_type = None,
             time: search_type = None, weapon: search_type = None) -> List[str]:
    """
    Search through each entry and return the identities that satisfy the criterion. Arguments are each of the element
    types for a manuscript entry, which can be a string, bool, or None. If the argument is a string, then results must have
    an element that matches that string. If the argument is a bool, then the results must have at least one of those element
    types. If the argument is None, it does not effect the search.
    """
    # TODO: fix this, its important

    args = {'animal': animal, 'body_part': body_part, 'currency': currency, 'definition': definition,
            'environment': environment, 'material': material, 'medical': medical, 'measurement': measurement,
            'music': music, 'plant': plant, 'place': place, 'personal_name': personal_name, 'profession': profession,
            'sensory': sensory, 'tool': tool, 'time': time, 'weapon': weapon}

    versions = ['tc', 'tcn', 'tl']
    results = self.entries # initialize results
    search_bools = [k for k, v in args.items() if isinstance(v, bool)] # select bool element categories
    search_strings = [k for k, v in args.items() if isinstance(v, list)] # select string element categories

    # print(search_bools)
    # print(search_strings)

    for s in search_bools: # filter by each bool
      results_temp = {}
      for i, r in results.items():
        for v in versions:
          if r.get_prop(s, v):
            results_temp[i] = r
      results = results_temp
      # results = {i: r for i, r in results.items() if any(r.get_prop(s, v) for v in versions)}

    for s in search_strings: # filter by each string
      results_temp = {}
      for i, r in results.items():
        for v in versions:
          prop_set = set(r.get_prop(s, v))
          search_set = set(args[s])
          if len(prop_set.intersection(search_set)) > 0:
            results_temp[i] = r
      # results = {i: r for i, r in results if any(args[s] in r.get_prop(s, v) for v in versions)}
      results = results_temp
    return([i for i, r in results.items()]) # return identities

  def search_margins(self, version: str, term: str, placement: str) -> List[str]:
    return [i for i, entry in self.entries.items()
            if any(margin[0] == placement and term in margin[1] for margin in entry.margins[version])]

  def tablefy(self):
    # id, head, no. words, category, amount of each tag, margins
    # include figure margins?
    df = pd.DataFrame(columns=['entry'], data=self.entries.values())
    df['folio'] = df.entry.apply(lambda x: x.folio)
    df['folio_display'] = df.entry.apply(lambda x: x.folio.lstrip('0'))
    df['div_id'] = df.entry.apply(lambda x: x.identity)
    df['categories'] = df.entry.apply(lambda x: (';'.join(x.categories)))
    df['heading_tc'] = df.entry.apply(lambda x: x.title['tc'])
    df['heading_tcn'] = df.entry.apply(lambda x: x.title['tcn'])
    df['heading_tl'] = df.entry.apply(lambda x: x.title['tl'])
    df['margins'] = df.entry.apply(lambda x: len(x.margins))
    df['del_tags'] = df.entry.apply(lambda x: '; '.join(x.del_tags))
    df['figures'] = df.entry.apply(lambda x: 'unknown')
    for prop in properties:
      df[prop] = df.entry.apply(lambda x: '; '.join(x.get_prop(prop=prop, version='tc')))
    return df

manuscript = BnF(apply_corrections=True)
# print(manuscript.entry('004v_1').title['tl'])
