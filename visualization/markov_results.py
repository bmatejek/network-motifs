import matplotlib.pyplot as plt



from network_motifs.utilities.constants import *



plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



def VisualizeAccuracyCurves(dataset,  accuracies):
    plt.figure()

    title = '{} Markov Chain Results'.format(human_readable[dataset])
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

    output_filename = 'figures/{}-markov-results.png'.format(dataset)
    plt.savefig(output_filename)

    plt.clf()
