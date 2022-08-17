import pandas as pd
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

years =mdates.YearLocator()
six_months = mdates.MonthLocator(interval=1)

def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', help = 'File To check')
  parser.add_argument('--save', help = 'Save graphs on disk as imgs', action='store_true')  
  parser.add_argument('--prefix', help = 'Prefix name for graphs on disks')  
  parser.add_argument('--title', help = 'Prefix name for graphs on disks', default=None)  
  parser.add_argument('--freq', help = 'Group by frequency in months', default=6,type=int)  
  parser.add_argument('--time', help = 'Only consider entries after this date')  
  return parser.parse_args()

def process_file(filename,frequency=6,time_slice=None):
  df = pd.read_csv(filename)
  if time_slice: 
    df = df[df['creation'] > time_slice ]
  df['creation'] = pd.to_datetime(df['creation'])
  df['safe'] = 0
  df['questionable'] = 0
  df.loc[df['rating'] == 's','safe'] = 1
  df.loc[df['rating'] != 's','questionable'] = 1
  
  f_str = "{}MS".format(frequency)
  print("Grouping each {} months".format(frequency))
  grouper = pd.Grouper(key='creation',freq=f_str, origin='epoch',dropna=False)
  grouped_df = df.groupby(grouper)
  count_df = grouped_df.sum().reset_index()
  
  # Easier than running another groupby 
  count_df['total'] = count_df['safe'] + count_df['questionable'] 
  count_df['ratio'] = count_df['questionable'] / count_df['safe']
  count_df['safe_ratio'] = count_df['safe']/count_df['total'] * 100
  count_df['quest_ratio']  = count_df['questionable']/count_df['total'] * 100
  #print(count_df)
  return count_df 

def graph_counts(count_df ,title=None,months=6):
  fig,ax = plt.subplots(figsize=(12,8))
  fig.autofmt_xdate()

  n_mon = 12 / months
  spacing = 365 / n_mon / 2 
  if months < 2 :
    months = 2 
  mon_l = mdates.MonthLocator(interval=months)
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_major_locator(mon_l)
  # To get python native datetime: 
  # py_date = count['creation'].dt.to_pydatetime()
  x_num = mdates.date2num(count_df['creation'])
  # Again bar uses a scalar for X axis, so can't use a simple offset
  # to plot multiple series
  # For the record: 
  # ax.bar(h_count['creation'],s_count['counts'],width=25)
  # works
  header = 'Number of Safe and Questionable sketches over time'
  if title:
    header += ':\n' + title  
  ax.set_title(header)

  ax.set_xlabel('Year')
  ax.set_ylabel('Sketches')
  alg='center'
  ax.bar(x_num   ,count_df['safe'],width=spacing,
         align=alg,label='Safe',color='#72CDFF')
  ax.bar(x_num + spacing,count_df['questionable'],width=spacing,
        align=alg,label='Questionable', color='#F7941D' )
  # automfmt _xdate does this too:
  #ax.xaxis_date()
  ax.legend()
  return fig

def graph_ratio(count_df,title=None,months=6):
  fig,ax = plt.subplots(figsize=(12,8))
  fig.autofmt_xdate()

  n_mon = 12 / months
  spacing = 365 / n_mon / 2 
  if months < 2 :
    months = 2 
  mon_l = mdates.MonthLocator(interval=months)
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
  ax.xaxis.set_major_locator(mon_l)
  
  x_num = mdates.date2num(count_df['creation'])
  header = 'Safe and Questionable sketches by percent over time'
  if title:
    header += ':\n' + title  
  ax.set_title(header)
  ax.set_xlabel('Year')
  ax.set_ylabel('Percentage [%]')
  safe_ratio = count_df['safe_ratio'] 
  quest_ratio = count_df['quest_ratio'] 
  ax.bar(x_num,quest_ratio,width=spacing, bottom=safe_ratio,
        align='center',label='Questionable', color='#F7941D' )
  ax.bar(x_num, safe_ratio, width=spacing,
         align='center',label='Safe',color='#72CDFF')

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

  ax.legend()
  return fig

if __name__ == '__main__':
  args = parse_arguments()
  plt.style.use('ggplot')
  counts = process_file(args.file,args.freq,args.time)
  cnt_fig = graph_counts(counts,args.title,months=args.freq)
  ratio_fig =  graph_ratio(counts,args.title,months=args.freq)
  lewd_fig =  graph_lewd(counts,args.title)
  
  if args.prefix:
    cnt_fig.savefig(args.prefix + 'sfw-nsfw-count.png')
    ratio_fig.savefig(args.prefix + 'sfw-nsfw-ratio.png')
    lewd_fig.savefig(args.prefix + 'lewd-ratio.png')
  else:
    plt.show()
