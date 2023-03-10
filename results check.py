import csv
import pandas as pd


f = open(r'ra_precise.csv', mode='r')
csv_reader = csv.DictReader(f)
dicts = []
for row in csv_reader:
    dicts.append(dict(row))

df = pd.DataFrame(dicts)

df[df.columns[3:]] = df[df.columns[3:]].astype(str).astype(float)

dtypes = [
    'use_rih',
    'use_ra',
    'use_2way',
    # 'step',
    # 'battery_capacity',
    # 'rtr_interval_s',
    # 'ra_data_limit',
    # 'ra_data_interval',
    # 'data_overhead',
    # 'velocity_cmps',
    'vein_diameter_mm',
    'nodes_num'
    # 'sim_time_s',
    # 'stats_collection_time'
]

group = df.groupby(dtypes)

series = group['received_data_bits:'].std().rename('stdev_rx_bits')

df2 = pd.merge(group.mean(), series, left_index=True, right_index=True)

df2['count'] = group['received_data_bits:'].count()

df2['stdev_rec%'] = df2['stdev_rx_bits'] / df2['received_data_bits:']*100

print(df2[['count','received_data_bits:', 'stdev_rx_bits','stdev_rec%']])
# print(df2)
