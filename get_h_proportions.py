import pandas as pd
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

years =mdates.YearLocator()
months = mdates.MonthLocator()

def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', help = 'File To check')
  parser.add_argument('--save', help = 'Save graphs on disk as imgs', action='store_true')  
  return parser.parse_args()

def process_file(filename):
  df = pd.read_json(filename)
  df['creation'] = pd.to_datetime(df['creation'])
  grouper = pd.Grouper(key='creation',freq='YS', origin='epoch')
  safe_df = df[df['rating'] == 's']
  h_df = df[df['rating'] != 's']
  # Can also use count() but this way only one col per 
  # year is returned
  safe_count = safe_df.groupby(grouper).size().reset_index(name='safe')
  h_count = h_df.groupby(grouper).size().reset_index(name='questionable')
  # Getting total
  # total_count = df.groupby(grouper).size().reset_index(name='total')

  #safe_count = safe_df.groupby(grouper).size()
  #h_count = h_df.groupby(grouper).size()
  count_df = pd.merge(safe_count,h_count,on='creation')
  # Easier than running another groupby 
  count_df['total'] = count_df['safe'] + count_df['questionable'] 
  print(count_df)
  return count_df 

def graph_counts(count_df, persist):
  fig,ax = plt.subplots(figsize=(10,8))
  fig.autofmt_xdate()
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
  ax.xaxis.set_major_locator(years)
  # ax.xaxis.set_minor_locator(months)
  # To get python native datetime: 
  # py_date = count['creation'].dt.to_pydatetime()
  x_num = mdates.date2num(count_df['creation'])
  # Again bar uses a scalar for X axis, so can't use a simple offset
  # to plot multiple series
  # For the record: 
  # ax.bar(h_count['creation'],s_count['counts'],width=25)
  # works
  spacing = 365 / 3 
  ax.set_title("Safe vs Questionable sketches")
  ax.set_xlabel('Year')
  ax.set_ylabel('Sketches')
  ax.bar(x_num - spacing/2 ,count_df['safe'],width=spacing,
         align='center',label='Safe',color='#72CDEE')
  ax.bar(x_num + spacing/2,count_df['questionable'],width=spacing,
        align='center',label='Questionable', color='#F7941D' )
  # automfmt _xdate does this too:
  #ax.xaxis_date()
  ax.legend()
  return fig

def graph_ratio(count_df,persist):
  fig,ax = plt.subplots(figsize=(10,8))

  ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
  ax.xaxis.set_major_locator(years)
  x_num = mdates.date2num(count_df['creation'])
  spacing = 365 / 3 
  ax.set_title("Safe vs Questionable ratio")
  ax.set_xlabel('Year')
  ax.set_ylabel('Percentage [%]')
  safe_ratio = count_df['safe']/count_df['total'] * 100
  quest_ratio = count_df['questionable']/count_df['total'] * 100
  ax.bar(x_num,quest_ratio,width=spacing, bottom=safe_ratio,
        align='center',label='Questionable', color='#F7941D' )
  ax.bar(x_num, safe_ratio, width=spacing,
         align='center',label='Safe',color='#72CDEE')

  ax.legend()
  return fig

if __name__ == '__main__':
  args = parse_arguments()
  plt.style.use('ggplot')
  counts = process_file(args.file)
  cnt_fig = graph_counts(counts,args.save)
  ratio_fig =  graph_ratio(counts,args.save)
  
  if args.save:
    cnt_fig.savefig('sfw-nsfw-count.png')
    ratio_fig.savefig('sfw-nsfw-ratio.png')
  else:
    plt.show()
