import numpy as np



from network_motifs.data_structures.graph import Node



def ConvertJSON2Graph(json_nodes, json_edges):
    # get a list of all functions 
    functions = set()
    for json_node in json_nodes:
        functions.add(json_node.function)

    # there is a single node per function
    functions_to_nodes = {}

    nodes = []
    edges = []

    for index, function in enumerate(functions):
        functions_to_nodes[function] = index
        nodes.append(Node(function, index))

    # keep track of the function stack
    function_stack = []
    # where in the graph are we currently
    current_node_index = -1
    # where are we in the JSON file
    json_node_index = 0
    njson_nodes = len(json_nodes)

    # we collapse all exits to create loops
    collapsing_exits = False

    while json_node_index < njson_nodes:
        json_node = json_nodes[json_node_index]

        # skip all annotations
        if json_node.variance == 'Annotation':
            json_node_index += 1
            continue


        # start of a new function loop
        if current_node_index == -1:
            # make sure this node is an entry
            assert (json_node.variance == 'Entry')

            # update the current node that we are at
            current_node_index = functions_to_nodes[json_node.function]
            
            # add this function to the stack
            function_stack.append(json_node.function)

            # increment the json node index
            json_node_index += 1
        # if you are entering a new function the current node called this one
        elif json_node.variance == 'Entry':
            # what is the new node index 
            next_node_index = functions_to_nodes[json_node.function]

            # there is an edge from the previous node to this one
            edges.append((current_node_index, next_node_index))
            if current_node_index == next_node_index:
                print ('Entrance {}'.format(json_node_index))

            # update the current node index
            current_node_index = next_node_index

            # add this function to the stack
            function_stack.append(json_node.function)

            # increment the json node index 
            json_node_index += 1
        # otherwise we are returning to the previous function on the stack
        else:
            # pop the last element from the stack
            assert (function_stack.pop() == json_node.function)

            # have left this complete function call
            if not len(function_stack):
                current_node_index = -1

                # increment the json node index
                json_node_index += 1

                # start anew
                continue

            # the new next node is the last thing on the stack
            next_node_index = functions_to_nodes[function_stack[-1]]

            # there is an edge from the previous node to this one
            edges.append((current_node_index, next_node_index))
            if current_node_index == next_node_index:
                print ('Exit {}'.format(json_node_index))


            # update the current node index
            current_node_index = next_node_index

            # increment the json node index
            json_node_index += 1

    # create the list of weighted edges
    aggregated_edges = {}

    for edge in edges:
        if not edge in aggregated_edges:
            aggregated_edges[edge] = 1
        else:
            aggregated_edges[edge] += 1

    return nodes, aggregated_edges