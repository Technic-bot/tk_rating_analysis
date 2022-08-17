import json
import pandas as pd
import numpy as np
import argparse

def parser_opts():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', help='in json file')
  parser.add_argument('outfile', help='output csv file')
  return parser.parse_args()

def preprocess_df(df):
  print("Got {} entries ".format(len(df)))
  df['creation'] = pd.to_datetime(df['creation'])
  df['update'] = pd.to_datetime(df['update'])
  # do not care about characters in this case
  df.drop('characters', axis=1, inplace=True)
  df.set_index('id',inplace=True)
  return df

def clean_df(df):
  twk_df = preprocess_df(df)
  twk_df = remove_comic_pages(twk_df)
  return twk_df
  #twk_df = remove_non_color(twk_df)

def remove_comic_pages(df):
  """
  Remove any entry inside a pool, that is a comic.
  """
  df = df[~df["pools"].astype(bool)]
  # We removed every entry with a pool, remove the column
  df.drop('pools', axis=1, inplace=True)
  print("Trimmmed down to  {} entries ".format(len(df)))

  return df

def main():
  args=parser_opts()
  df = pd.read_json(args.file)

  df_proc=clean_df(df)
  if args.outfile:
    df_proc.to_csv(args.outfile)
  

if __name__=="__main__":
  main()
  
