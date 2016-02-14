# Demo of using OpenTripPlanner and opentripplanner-jython
# Public domain

from opentripplanner import RoutingRequest, Graph
from opentripplanner.batch import BatchProcessor, PointSet
import time

init_time = time.time()

# Set the parameters for our search
r = RoutingRequest()
r.dateTime = 1449496800 # Monday, Dec. 7th, 2014, 7:00 am EST (doesn't matter for a walking search)
r.setModes('WALK,TRANSIT')

print 'routing request set in %g seconds' % (time.time() - init_time)

# read the graph
g = Graph('/home/clayton/otp/graphs/nyc/', 'nyc')

print 'graph read at %g seconds (cumulative time)' % (time.time() - init_time)

# read the destinations
# do this before running the batch processor, so that if there is an error reading the destinations, we don't have to wait for
# the batch processor to finish
destinations = PointSet('zcta_wac.shp')
print 'destinations read at %g seconds (cumulative time)' % (time.time() - init_time)

# Link the destinations to the graph
# In theory this is done automatically, but the automatic linking happens after the searches have happened
# This shouldn't be a problem, but due to OTP bug #1577, it needs to happen before searches are run
destinations.link(g)
print 'destinations linked at %g seconds (cumulative time)' % (time.time() - init_time)

# Create a BatchProcessor
b = BatchProcessor(
    graph=g,
    # What are the origins for the analysis?
    origins='zcta_nyc.shp',
    # What are the parameters for the search?
    routingRequest=r,
    # This is for efficiency; we stop the algorithm running after it has found all blocks within a certain number of minutes of a grocery
    # every place in the City is surely within 60 minutes of a grocery store, I hope
    cutoffMinutes=60,
    # I have four cores but eight hyperthreading cores, and that seemed
    # to count with the old Java batch analyst
    # CH dropped to 4 for testing
    threads=4
)
print 'BatchProcessor set at %g seconds (cumulative time)' % (time.time() - init_time)
analysis_time = time.time()
# Run the batch processor: build an SPT from each origin
b.run()

# get the results
results = b.eval(destinations)

# save the results as a csv
out = open('times.csv', 'w')

# loop over the destinations and write out geoid and time to nearest high school
out.write('geoid,time_minutes\n')

for did in xrange(len(destinations)):
    # we reconstruct the GEOID10 as for some reason it isn't picked up in properties
    geoid = destinations[did].properties['zcta5']
    # '%02d%03d%06d%04d' %\
    #        (destinations[did].properties['STATEFP10'],
    #         destinations[did].properties['COUNTYFP10'],
    #         destinations[did].properties['TRACTCE10'],
    #         destinations[did].properties['BLOCKCE10'])

    # Results is of type opentripplanner.batch.Matrix
    time = min(results.getCol(did))

    # write a row
    out.write('%s,%s\n' % (geoid, time / 60.0))
    
print 'script done. analysis in %g and full script in %g seconds' %(time.time() - analysis_time, time.time() - init_time)
