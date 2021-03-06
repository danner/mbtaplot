""" process lines that look like
s 1 <stop tag="64" title="Dudley Station - Harvard Side" lat="42.3294799" lon="-71.08391" stopId="00064"/>
d 1 <stop tag="64" />

and make a proper python importable table of tags, lats, and lons out of the s ones.

The d ones reference the s ones, and if a reference fails, we need to tell the mbta
""" 

import sys
import re
from collections import defaultdict

def interpret_stop_def_string(s):
  tag = re.match('.* tag="([^"]*)".*',s).groups(0)[0]
  lat =  re.match('.* lat="([^"]*)".*',s).groups(0)[0]
  lon = re.match('.* lon="([^"]*)".*',s).groups(0)[0]
  return tag, lat, lon

def interpret_stop_ref_string(s):
  tag = re.match('.* tag="([^"]*)".*',s).groups(0)[0]
  return tag

def start(fname_bus, fname_subway):
  print "# this file is autogenerated by update_stop_table.sh"
  print "table = ["

  route_stops = defaultdict(dict)

  for line in open(fname_bus):
    stop_type, route, stop_string = line.strip().split(" ", 2)

    try:
      if stop_type == 's':
        tag, lat, lon = interpret_stop_def_string(stop_string)
        print "('%s', '%s', %s, %s)," % (route, tag, lat, lon)
        assert tag not in route_stops[route]
        route_stops[route][tag]=0
      elif stop_type == 'd':
        tag = interpret_stop_ref_string(stop_string)
        assert tag in route_stops[route]
        route_stops[route][tag] += 1
    except AttributeError:
      raise Exception("Can't understand: %s" % line)

  for line in open(fname_subway):
    route, tag, lat, lon = line.strip().split()
    print "('%s', '%s', %s, %s)," % (route, tag, lat, lon)

  print "]"

  for route in sorted(route_stops):
    for tag in sorted(route_stops[route]):
      c = route_stops[route][tag]
      if c == 0:
        sys.stderr.write("Unreferenced stop %s for route %s\n" % (tag, route))

if __name__ == "__main__":
  start(*sys.argv[1:])
