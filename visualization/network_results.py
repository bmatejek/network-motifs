import matplotlib.pyplot as plt



from network_motifs.utilities.constants import human_readable



plt.style.use('seaborn-white')
plt.rc({'fontname', 'Ubuntu'})



def VisualizeNetworkDurations(output_filename_prefix, title, accuracies, duration_errors, occurrences):
    nbins = len(accuracies)
    assert (len(accuracies) == len(duration_errors))
    assert (len(accuracies) == len(occurrences))

    plt.figure()

    plt.title(title, fontsize=20)
    plt.xlabel('Percent Trace Completed', fontsize=16)
    plt.ylabel('QoS Violation Prediction Accuracy', fontsize=16)

    plt.ylim([0, 100])
    plt.xlim([0, 1])

    xs = []
    ys = []

    for bin in range(nbins):
        if not occurrences[bin]: continue

        xs.append(bin / nbins)
        ys.append(accuracies[bin])

    plt.plot(xs, ys, label='Accuracy')

    plt.legend()
    plt.tight_layout()
    plt.savefig('{}-accuracies.png'.format(output_filename_prefix))

    plt.clf()

    plt.figure()

    plt.title(title, fontsize=20)
    plt.xlabel('Percent Trace Completed', fontsize=16)



    max_error = max(duration_errors)
    if max_error > 10 ** 9:
        seconds = True
        max_error /= 10 ** 9
    else:
        seconds = False

    if seconds: plt.ylabel('Predicted Request Duration Errors (seconds)', fontsize=16)
    else:  plt.ylabel('Predicted Request Duration Errors', fontsize=16)

    plt.ylim([0, max_error])
    plt.xlim([0, 1])

    xs = []
    ys = []

    for bin in range(nbins):
        if not occurrences[bin]: continue

        xs.append(bin / nbins)
        if seconds: ys.append(duration_errors[bin] / 10 ** 9)
        else: ys.append(duration_errors[bin])

    plt.plot(xs, ys, label='Mean Absolute Error')

    plt.legend()
    plt.tight_layout()
    plt.savefig('{}-duration-errors.png'.format(output_filename_prefix))

    plt.clf()
