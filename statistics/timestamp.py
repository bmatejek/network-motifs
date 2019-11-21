import matplotlib.pyplot as plt

# set the style for plots
plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



from network_motifs.data_structures import open_stack



def VisualizeDistribution(function, distribution, index):
    # make the function name human readable
    split_funciton_name = function.split(':')

    if len(split_funciton_name) == 2:
        function_title = function
    else:
        function_title = '{}:{}\n{}'.format(split_funciton_name[0], split_funciton_name[1], split_funciton_name[2])

    plt.figure()

    plt.title(function_title, pad=20)
    plt.ylabel('Time (nanoseconds)')

    # plot the distribution
    plt.boxplot(distribution)

    # remove the xaxis
    ax = plt.axes()
    xax = ax.axes.get_xaxis()
    xax.set_visible(False)

    plt.tight_layout()

    output_filename = 'openstack-distributions/{:04d}-{:04d}.png'.format(len(distribution), index)
    plt.savefig(output_filename)

    # clear and close this figure
    plt.clf()
    plt.close()



def Distribution(traces):
    trace_functions = open_stack.GetUniqueFunctions(traces)

    # begin to keep track of the distributions
    timestamp_distributions = {}
    for function in trace_functions:
        timestamp_distributions[function] = []

    for trace in traces:
        # keep track of function entries for this stack
        entries = {}

        # go through all of the nodes
        for node in trace.nodes:
            # skip annotations
            if node.variant == 'Entry':
                # make sure that the entry is not already in the dictionary
                assert (not node.trace_id in entries)
                # record the timestamp for entry
                entries[node.trace_id] = node.timestamp
            elif node.variant == 'Exit':
                # make sure that an entry exists for this exit
                assert (node.trace_id in entries)
                # determine the time from entry to exit in nanoseconds
                duration = round((node.timestamp - entries[node.trace_id]).total_seconds() * 10 ** 9)
                timestamp_distributions[node.tracepoint_id].append(duration)

                # remove this entry
                entries.pop(node.trace_id)

    # for each function plot the distribution
    # need to sort so that each function saves to the same filename
    for iv, function in enumerate(sorted(trace_functions)):
        distribution = timestamp_distributions[function]

        # skip over annotation only functions
        if not len(distribution): continue

        VisualizeDistribution(function, distribution, iv)
