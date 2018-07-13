from simkit.simkit import SimEntityBase
from simkit.simkit import Priority
from simkit.simkit import Entity
from examples.arrivalprocess import ArrivalProcess
from math import nan
from heapq import heappush
from heapq import heappop

class Job(Entity):

    def __init__(self):
        Entity.__init__(self, 'Job')
        self.total_delay_in_queue = 0.0
        self.time_in_system = 0.0

    def updateDelayInQueue(self):
        self.total_delay_in_queue += self.elapsed_time()

class JobCreator(ArrivalProcess):
    def __init__(self, interarrival_time_generator):
        ArrivalProcess.__init__(self, interarrival_time_generator)

    def arrival(self):
        ArrivalProcess.arrival(self)
        self.schedule('job_arrival', 0.0, Job(), 0)

class TransferLine(SimEntityBase):
    def __init__(self, number_stations, number_machines, service_times):
        SimEntityBase.__init__(self)
        self.number_stations = number_stations
        self.service_times = service_times
        self.number_machines = number_machines
        self.queue = []
        self.number_available_machines = []
        self.validate()

    def validate(self):
        service_times_ok = len(self.service_times) == self.number_stations
        number_machines_ok = len(self.number_machines) == self.number_stations
        if not service_times_ok or not number_machines_ok:
            raise ValueError('{ns:d} stations specified but {st:d} service times and {nm:d} machines'. \
                             format(ns=self.number_stations, st=len(self.service_times), nm=len(self.number_machines)))

    def reset(self):
        self.queue.clear()
        self.number_available_machines.clear()

    def run(self):
        if self.number_stations > 0:
            self.schedule('init', 0.0, 0, priority=Priority.HIGHER)

    def init(self, station):
        self.queue.append([])
        self.notify_indexed_state_change(station, 'queue', self.queue[station])

        self.number_available_machines.append(self.number_machines[station])
        self.notify_indexed_state_change(station, 'number_available_machines', self.number_available_machines[station])

        if station < self.number_stations - 1:
            self.schedule('init', 0.0, station + 1, priority=Priority.HIGHER)

    def arrival(self, job, station):
        job.stamp_time()
        heappush(self.queue[station], job)
        self.notify_indexed_state_change(station, 'queue', self.queue[station])

        if self.number_available_machines[station] > 0:
            self.schedule('start_processing', 0.0, station, priority=Priority.HIGH)

    def start_processing(self, station):
        job = heappop(self.queue[station])
        self.notify_indexed_state_change(station, 'delayInQueue', job.elapsed_time())
        job.updateDelayInQueue()

        self.number_available_machines[station] -= 1
        self.notify_indexed_state_change(station, 'number_available_machines', self.number_available_machines[station])

        self.schedule('end_processing', self.service_times[station].generate(), job, station)

    def end_processing(self, job, station):
        self.number_available_machines[station] += 1
        self.notify_indexed_state_change(station, 'number_available_machines', self.number_available_machines[station])

        if len(self.queue[station]) > 0:
            self.schedule('start_processing', 0.0, station, priority=Priority.HIGH)

        if station < self.number_stations - 1:
            self.schedule('arrival', 0.0, job, station + 1)

        if (station == self.number_stations - 1):
            self.schedule('jobComplete', 0.0,  job)

    def jobComplete(self, job):
        self.notify_state_change('total_delay_in_queue', job.totalDelayInQueue)
        self.notify_state_change('time_in_system', job.age())