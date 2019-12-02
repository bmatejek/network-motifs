import matplotlib.pyplot as plt



from network_motifs.utilities.constants import human_readable



plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



def VisualizeAccuracyCurves(dataset,  request_type, accuracies):
    plt.figure()

    if request_type == None:
        title = '{} Markov Chain Results'.format(human_readable[dataset])
    else:
        title = '{} {} Markov Chain Results'.format(human_readable[dataset], request_type)
    plt.title(title, fontsize=16)
    plt.xlabel('Order of Markov Chain', fontsize=14)
    plt.ylabel('Accuracy', fontsize=14)

    # create the axis for orders
    orders = [iv + 1 for iv in range(len(accuracies[1]))]

    # set axis information
    ax = plt.axes()
    ax.set_xlim(1, orders[-1])
    ax.set_ylim(0, 100)

    for k in accuracies:
        plt.plot(orders, accuracies[k], label='k = {}'.format(k), marker='x')

    plt.legend()

    plt.tight_layout()

    if request_type == None:
        output_filename = 'figures/{}-markov-results.png'.format(dataset)
    else:
        output_filename = 'figures/{}-{}-markov-results.png'.format(dataset, request_type)
    plt.savefig(output_filename)

    plt.clf()
