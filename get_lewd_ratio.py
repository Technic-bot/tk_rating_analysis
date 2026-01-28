import pandas as pd
import numpy as np
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

years =mdates.YearLocator()
six_months = mdates.MonthLocator(interval=1)

def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', help = 'File To check')
  parser.add_argument('--prefix', help = 'Prefix name for graphs on disks')  
  parser.add_argument('--title', help = 'Prefix name for graphs on disks', default=None)  
  parser.add_argument('--freq', help = 'Group by frequency in months', default="QE")  
  parser.add_argument('--time-start', help = 'Only consider entries after this date')  
  parser.add_argument('--time-stop', help = 'Only consider entries after this date')  
  parser.add_argument('--high-def',help = "Get high definition counts", action='store_true')
  return parser.parse_args()

def process_file(filename,time_start=None, time_stop=None):
  """ Gets rating value s"""
  print(f'Reading {filename}')
  df = pd.read_csv(filename)
  print(f'Got {len(df)} entries')
  if time_start: 
    df = df[df['creation'] > time_start ]
  if time_stop: 
    df = df[df['creation'] < time_stop ]
  df['creation'] = pd.to_datetime(df['creation'], format='ISO8601')
  df['safe'] = 0
  df['questionable'] = 0
  df.loc[df['rating'] == 's','safe'] = 1
  df.loc[df['rating'] != 's','questionable'] = 1
  print("Pre-processing complete")
  print(f'Got {len(df)} entries after prunning!')
  return df

def group_df(df,frequency):
  print("Grouping each {} months".format(frequency))
  grouper = pd.Grouper(key='creation',freq=frequency, origin='epoch',dropna=False)
  grouped_df = df.groupby(grouper)
  count_df = grouped_df.sum().reset_index()
  
  # Easier than running another groupby 
  count_df['total'] = count_df['safe'] + count_df['questionable'] 
  count_df['ratio'] = count_df['questionable'] / count_df['safe']
  count_df['safe_ratio'] = count_df['safe']/count_df['total'] * 100
  count_df['quest_ratio']  = count_df['questionable']/count_df['total'] * 100
  #print(count_df)
  return count_df 

def group_high_def(df):
  print("Grouping each week")
  grouper = pd.Grouper(key='creation',freq='W', origin='epoch',dropna=False)
  grouped_df = df.groupby(grouper)
  count_df = grouped_df.sum().reset_index()
  
  # Easier than running another groupby 
  count_df['total'] = count_df['safe'] + count_df['questionable'] 
  count_df['ratio'] = count_df['questionable'] / count_df['safe']
  count_df['safe_ratio'] = count_df['safe']/count_df['total'] * 100
  count_df['quest_ratio']  = count_df['questionable']/count_df['total'] * 100
  #print(count_df)
  return count_df 

def graph_high_def(count_df,title=None):
  print("Graphing high definition")
  fig,ax = plt.subplots(figsize=(12,8))
  fig.autofmt_xdate()
  
  mon_l = mdates.MonthLocator(interval=1)
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_major_locator(mon_l)
  
  header = 'Number of Safe and Questionable sketches over time'
  if title:
    header += ':\n' + title  
  ax.set_title(header)

  ax.set_xlabel('Date')
  ax.set_ylabel('Sketches')

  ax.plot(count_df['creation'], count_df['safe'], label='Safe',color='#72CDFF')
  ax.plot(count_df['creation'], count_df['questionable'], label='Questionable',color='#F7941D')

  ax.legend()
  return fig


def graph_counts(count_df ,title=None):
  fig,ax = plt.subplots(figsize=(12,8))

  mon_l = mdates.MonthLocator(bymonth=[1,4,7,10])
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_major_locator(mon_l)
  
  # To get python native datetime: 
  # py_date = count['creation'].dt.to_pydatetime()
  x_num = mdates.date2num(count_df['creation'])

  n_series = 2
  spacing = np.min(np.diff(x_num))
  bar_w = spacing/(n_series)
  # Again bar uses a scalar for X axis, so can't use a simple offset
  
  # to plot multiple series
  # For the record: 
  # ax.bar(h_count['creation'],s_count['counts'],width=25)
  # works
  header = 'Number of Safe and Questionable sketches over time'
  if title:
    header += ':\n' + title  
  ax.set_title(header)

  ax.set_xlabel('Date')
  ax.set_ylabel('Sketches')
  alg='center'
  ax.bar(x_num - bar_w/2, count_df['safe'], width=bar_w,
         align=alg, label='Safe', color='#72CDFF')
  ax.bar(x_num + bar_w/2, count_df['questionable'], width=bar_w,
        align=alg, label='Questionable', color='#F7941D' )
  # automfmt _xdate does this too:
  ax.xaxis_date()
  plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
  ax.legend()
  ax.annotate("Graph by TecBot with ❤️  ", xy= (0.8,-0.125),
              xycoords='axes fraction', fontsize=10)
  return fig

def graph_ratio(count_df, title=None):
  fig, ax = plt.subplots(figsize=(12,8))
  fig.autofmt_xdate()

  mon_l = mdates.MonthLocator(bymonth=[1,4,7,10])
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_major_locator(mon_l)
  
  x_num = mdates.date2num(count_df['creation'])
  n_series = 1
  spacing = np.min(np.diff(x_num))
  bar_w = spacing/(n_series*1.2)

  header = 'Safe and Questionable sketches by percent over time'
  if title:
    header += ':\n' + title  
  ax.set_title(header)
  ax.set_xlabel('Year')
  ax.set_ylabel('Percentage [%]')
  safe_ratio = count_df['safe_ratio'] 
  quest_ratio = count_df['quest_ratio'] 
  align='edge'
  ax.bar(x_num, quest_ratio, width=bar_w, bottom=safe_ratio,
        align=align, label='Questionable', color='#F7941D' )
  ax.bar(x_num, safe_ratio, width=bar_w,
         align=align, label='Safe',color='#72CDFF')

  ax.annotate("Graph by TecBot with ❤️  ", xy= (0.8,-0.2),
              xycoords='axes fraction', fontsize=10)
  ax.legend()
  return fig

def graph_lewd(count_df,title=None):
  fig,ax = plt.subplots(figsize=(10,8))

  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
  ax.xaxis.set_major_locator(years)
  x_num = mdates.date2num(count_df['creation'])
  header = 'Lewd Ratio'
  if title:
    header += ':\n' + title  
  ax.set_title(header)
  ax.set_xlabel('Year')
  ax.set_ylabel('Ratio ')
  ax.plot(count_df['creation'],count_df['ratio'], 
        label='Lewd Ratio', color='#72CDEE' )

  ax.annotate("Graph by TecBot with ❤️  ", xy= (0.8,-0.2),
              xycoords='axes fraction', fontsize=10)
  ax.legend()
  return fig

if __name__ == '__main__':
  args = parse_arguments()
  plt.style.use('ggplot')
  df = process_file(args.file,args.time_start,args.time_stop)
  counts = group_df(df,args.freq)
  cnt_fig = graph_counts(counts, args.title)
  ratio_fig = graph_ratio(counts, args.title)
  if args.prefix:
    cnt_fig.savefig(args.prefix + 'sfw-nsfw-count.png')
    ratio_fig.savefig(args.prefix + 'sfw-nsfw-ratio.png')
  else:
    plt.show()
