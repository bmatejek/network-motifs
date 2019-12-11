import os
import glob
import json



def PruneXTraceJSONFiles(request_types):
    """
    Prune a folder of xtrace files to remove garbace collection traces and a few
    others that do not correspond to the various request types
    @params request_types: the allowable request types for this set of traces.
    """
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
            os.remove(xtrace_filename)
        # otherwise make sure there is only one request
        else:
            # make sure that there is only one tag per requeset
            assert (len(tags) == 1)

            # turn the tag into a request_type
            request = list(tags)[0]
            request_type = request.split(' ')[0].strip('-')
            assert (request_type in request_types)

            traces_per_request_type[request_type] += 1

    print (traces_per_request_type)
