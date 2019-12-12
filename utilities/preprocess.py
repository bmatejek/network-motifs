import os
import glob
import json
import time



def PruneXTraceJSONFiles(request_types):
    """
    Prune a folder of xtrace files to remove garbace collection traces and a few
    others that do not correspond to the various request types
    @params request_types: the allowable request types for this set of traces.
    """
    # start statistics
    start_time = time.time()

    # make pruned directory if it does not exist
    if not os.path.exists('jsons/xtrace/pruned-traces'):
        os.mkdir('jsons/xtrace/pruned-traces')

    # expect the xtrace files to be in this directory
    xtrace_filenames = sorted(glob.glob('jsons/xtrace/*.json'))

    # initialize the number of traces per request type to 0
    traces_per_request_type = {}
    for request_type in request_types:
        traces_per_request_type[request_type] = 0

    for xtrace_filename in xtrace_filenames:
        #print (xtrace_filename)
        # read this xtrace json file
        with open(xtrace_filename, 'r') as fd:
            data = json.load(fd)

        # get the base id for this file
        base_id = data['id']

        # consider all of the nodes in the list of reports
        reports = data['reports']
        nnodes = len(reports)
        tags = set()

        # determine if the trace should be removed by looking at tags
        remove_trace = False
        for report in reports:
            # skip the initial Tag of 'FsShell'
            if 'Tag' in report and not report['Tag'][0] == 'FsShell':
                # 'GarbageCollection', 'NameNode', and 'DataNode' have two components
                if not len(report['Tag']) == 1: remove_trace = True
                else: tags.add(report['Tag'][0])

        # if we should remove the trace, make sure there are no tags
        if remove_trace:
            assert (not len(tags))
            pruned_filename = 'jsons/xtrace/pruned-traces/{}.json'.format(base_id)
            os.rename(xtrace_filename, pruned_filename)
        # otherwise make sure there is only one request
        else:
            # make sure that there is only one tag per requeset
            assert (len(tags) == 1)

            # turn the tag into a request_type
            request = list(tags)[0]
            request_type = request.split(' ')[0].strip('-')
            assert (request_type in request_types)

            traces_per_request_type[request_type] += 1

    print ('Pruned XTrace files in {:0.2f} seconds.'.format(time.time() - start_time))

    for request_type in traces_per_request_type:
        print (' {}: {}'.format(request_type, traces_per_request_type[request_type]))
