import os

from helpers import *

stats = {}

files = []
for root, _, filenames in os.walk('logs'):
    for filename in filenames:
        files.append(os.path.join(root, filename))

for file in files:
    dic = {}

    types = ['cpu', 'cpu_temp', 'gpu', 'ram_tot', 'ram_pct']

    tm_data = read_columns(file, 'Aktivitetshanteraren')
    for idx, data in enumerate(tm_data[-1][1:]):
        dic[types[idx]] = json.loads(data)
        
    temp = TaskManager(data = dic)
    tm += temp

    events = read_columns(file, 'Event')
    file_events = []
    for event in events:
        event_object = Event(event[1], event[5])
        if event_object not in file_events:
            if event_object not in stats:
                stats[event_object] = {'unique_files' : 0, 'occurances' : 0}
            stats[event_object]['unique_files'] += 1
            file_events.append(event_object)
        stats[event_object]['occurances'] += 1

tm.sort_data()

for key, value in stats.items():
    overwrite = True if key == list(stats.keys())[0] else False
    write_to_table(
        'stats.sqlite',
        'stats',
        (key.process, key.id, value['unique_files'], value['occurances']),
        overwrite
    )

for category in categories:
    overwrite = True if category == 'means' else False
    data = list(data_point for data_point in getattr(tm, category).values())
    write_to_table('stats.sqlite', 'task_manager', data, overwrite)