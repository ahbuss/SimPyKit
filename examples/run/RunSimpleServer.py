"""
This example executes the Simple Server component for one replication, estimating the expected average number in
queue and utilization of servers. Arrivals are using the ArrivalProcess component

Parameters Used:
    ArrivalProcess: Exponential(1.7) interarrival times
    SimpleServer: 2 servers, Gamma(1.7, 1.8) service times
    Run length: 100,000 time units
"""
from examples.arrivalprocess import ArrivalProcess
from examples.simpleserver import SimpleServer
from simkit.rand import RandomVariate
from simkit.simkit import EventList
from simkit.stats import SimpleStatsTimeVarying
from simkit.simutil import SimpleStateChangeDumper
from time import time

interarrival_time_generator = RandomVariate.instance('Exponential', mean=1.7)
arrival_process = ArrivalProcess(interarrival_time_generator)

number_servers = 2;
service_time_generator = RandomVariate.instance('Gamma', alpha=1.7, beta=1.8)
simple_server = SimpleServer(number_servers, service_time_generator)

arrival_process.add_sim_event_listener(simple_server)

number_in_queue_stat = SimpleStatsTimeVarying('number_in_queue')
number_available_servers_stat = SimpleStatsTimeVarying('number_available_servers')

simple_server.add_state_change_listener(number_in_queue_stat)
simple_server.add_state_change_listener(number_available_servers_stat)

print(arrival_process.describe())
print(simple_server.describe())
print()


stopTime = 100000;
EventList.stop_at_time(stopTime)

start = time()
EventList.reset()
EventList.start_simulation()
end = time()

elapsed = end - start
print('Simulation took {time:.3f} sec'.format(time=elapsed))
print('Simulation ended at simtime {time:,.0f}'.format(time=EventList.simtime))
utilization = 1.0 - number_available_servers_stat.mean / simple_server.total_number_servers
print('Avg # in queue = \t{avg:.4f}'.format(avg=number_in_queue_stat.mean))
print('Avg # utilization = {avg:.4f}'.format(avg=utilization))