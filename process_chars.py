import json
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt

def parser_opts():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', help='in json file')
  parser.add_argument('outfile', help='output csv file')
  return parser.parse_args()

def graph_numerics(names,counts):
  fig, ax = plt.subplots(figsize=(7,7))
  ax.bar(names,counts)
  for tick in ax.get_xticklabels():
    tick.set_rotation(75)
  

def get_numerics(df,thr=35):
  char_df = df['characters'].value_counts()
  char_df = char_df[char_df > thr]
  chars = char_df.index.to_list()
  chars_grph = [ c.rsplit('_',1)[0] for c in chars]
#  chars = [ c.replace('_(twokinds)','') for c in chars]
  cnts = char_df.values
  graph_numerics(chars_grph,cnts)
  msg = "Characters with more than {} sketches"
  print(msg.format(thr))
  for c in chars:
    print(c)
  return chars
  

def preprocess_df(df):
  print("Got {} entries ".format(len(df)))
  df['creation'] = pd.to_datetime(df['creation'])
  df['update'] = pd.to_datetime(df['update'])
  df = df[~df["pools"].astype(bool)]
  print("Trimmmed down to  {} entries ".format(len(df)))
  df_explo = df.explode('characters')
  msk = (df_explo['characters'] != 'webcomic_character')
  df_explo = df_explo[msk]
  
  return df_explo

def plot_timeseries(ax,timeseries,ch=None):
  dates=timeseries.index
  vals=timeseries.values
  ax.plot(dates,vals,label=ch)
  ax.legend()
  
  return

def get_timeseries(df,chars):
  """ Convert df to a timeseries with number of sketches per character per mont"""
  time_df = df.groupby([pd.Grouper(key='creation',freq='M'),'characters'])['rating'].count()

  # Out DF:
  # creation_date,character,Numberofsketches
  #print(time_df.loc[slice(None),'kathrin_vaughan'])
  #print(time_df.reset_index('characters'))
  
  #    char_tms = time_df.loc[slice(None),c]
   # plot_timeseries(ax,char_tms,c)
  

#  for c in chars:
#    char_df = df[df['character']==c]
#    char_tms = char_df.groupby(pd.Grouper(key='creation',freq='M')).count()
#    plot(cnt)
  return time_df
  

def main():
  args=parser_opts()
  df = pd.read_json(args.file)

  df_explo=preprocess_df(df)
  chars=get_numerics(df_explo)
  tms = get_timeseries(df_explo,chars)
  if args.outfile:
    tms.to_csv(args.outfile)
  
  plt.show()

if __name__=="__main__":
  main()
  
