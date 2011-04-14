import inspect

from core import Locust, SubLocust

def print_task_ratio(locusts, total=False, level=0, parent_ratio=1.0):
	ratio = {}
	for locust in locusts:
		ratio.setdefault(locust, 0)
		ratio[locust] += 1
	
	# get percentage
	ratio_percent = dict(map(lambda x: (x[0], float(x[1])/len(locusts) * parent_ratio), ratio.iteritems()))
	
	for locust, ratio in ratio_percent.iteritems():
		#print " %-10.2f %-50s" % (ratio*100, "  "*level + locust.__name__)
		print " %-10s %-50s" % ("  "*level + "%-6.1f" % (ratio*100), "  "*level + locust.__name__)
		if inspect.isclass(locust) and issubclass(locust, Locust):
			if total:
				print_task_ratio(locust.tasks, total, level+1, ratio)
			else:
				print_task_ratio(locust.tasks, total, level+1)

def print_task_ratio_confluence(locusts, total=False, level=0, parent_ratio=1.0):
	ratio = {}
	for locust in locusts:
		ratio.setdefault(locust, 0)
		ratio[locust] += 1
	
	# get percentage
	ratio_percent = dict(map(lambda x: (x[0], float(x[1])/len(locusts) * parent_ratio), ratio.iteritems()))
	
	for locust, ratio in ratio_percent.iteritems():
		print "*" + "*"*level + " %.1f" % (ratio*100) + " "+ locust.__name__
		if inspect.isclass(locust) and issubclass(locust, Locust):
			if total:
				print_task_ratio_confluence(locust.tasks, total, level+1, ratio)
			else:
				print_task_ratio_confluence(locust.tasks, total, level+1)
