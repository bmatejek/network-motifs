import matplotlib.pyplot as plt



plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



def VisualizeAccuracyCurves(trace_source,  accuracies):
    plt.figure()

    title = '{} Markov Chain Results'.format(trace_source)
    plt.title(title, fontsize=16)
    plt.xlabel('Order of Markov Chain', fontsize=14)
    plt.ylabel('Accuracy', fontsize=14)

    # create the axis for orders
    orders = [iv + 1 for iv in range(len(accuracies))]

    # set axis information
    ax = plt.axes()
    ax.set_xlim(1, orders[-1])
    ax.set_ylim(0, 100)

    plt.plot(orders, accuracies, label='Testing Data', marker='x')

    plt.legend()

    plt.tight_layout()

    output_filename = 'figures/{}-markov-results.png'.format(trace_source)
    plt.savefig(output_filename)

    plt.clf()
