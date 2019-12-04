import matplotlib.pyplot as plt



from network_motifs.utilities.constants import human_readable



plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



def VisualizeAccuracyCurves(dataset, request_type, accuracies, label):
    plt.figure()

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
        plt.plot(orders, accuracies[k], label='k = {}'.format(k))

    plt.legend()

    plt.tight_layout()

    min_k = min(accuracies.keys())
    max_k = max(accuracies.keys())

    output_filename = 'figures/{}-{}-markov-results-{}-{}.png'.format(dataset, request_type, min_k, max_k)
    plt.savefig(output_filename)

    plt.clf()
