import wmi
import json

categories = ['means', 'medians', 'maximi', 'minimi', 'total']
types = ['cpu', 'cpu_temp', 'gpu', 'ram_tot', 'ram_pct']

class TaskManager():
    def __init__(
            self, 
            points : int = 30, 
            data : dict = dict((type, []) for type in types)
        ):
        self.points = points
        self.data = data

    def get_system_data(self):
        data_points = dict((key, []) for key in types)

        for _ in range(self.points):
            w = wmi.WMI(namespace = 'root\\OpenHardwareMonitor')
            sensors = w.Sensor()

            for sensor in sensors:
                if 'CPU Total' == sensor.name:
                    cpu = sensor.Value

                if 'CPU Package' == sensor.name and 'Temperature' in sensor.SensorType:
                    cpu_temp = sensor.Value

                if 'GPU Core' == sensor.name and 'Load' == sensor.SensorType:
                    gpu = sensor.Value

                if 'Available Memory' == sensor.name:
                    ram_tot = sensor.Value
                    ram_pct = sensor.Value / 0.24
            
            for data in data_points.keys():
                data_points[data].append(locals()[data])

        for lists in data_points.values():
            lists.sort()

        self.data = data_points

    def sort_data(self):
        maximi = {'maximi' : 'Maximi'}
        means = {'means' : 'Medelvärde'}
        medians = {'medians' : 'Median'}
        minimi = {'minimi' : 'Minimi'}
        total = {'total' : 'Total data'}
        
        for key, values in self.data.items():
            if self.points % 2 == 1:
                medians[key] = values[int((self.points - 1) / 2)]
            else:
                medians[key] = (values[int(self.points / 2)] + values[int(self.points / 2 + 1)]) / 2
            means[key] = sum(value for value in values) / len(self.data['cpu'])
            maximi[key] = max(values)
            minimi[key] = min(values)
            total[key] = json.dumps(values)

            if key in ['cpu_temp', 'gpu']:
                means[key] = round(10 * means[key]) / 10

        for category in categories:
            self.__setattr__(category, locals()[category])

    def __add__(self, other):
        dic = dict((type, self.data[type] + other.data[type]) for type in types)

        return TaskManager(data = dic)
    
tm = TaskManager()