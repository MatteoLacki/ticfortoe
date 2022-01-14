import IsoSpecPy as iso

def P(data, xlabel="", ylabel="", title="", origin='lower', aspect='auto', show=True, **kwargs):
    import matplotlib.pyplot as plt
    kwargs["origin"] = origin
    kwargs["aspect"] = aspect
    plt.imshow(data,**kwargs)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if title:
        plt.title(title)
    if show:
        plt.show()


def ute_friendly_plot(
    rt_min,
    Bruker_TIC,
    intensities,
    percentages,
    labels=["++>= 200", "++ [150,200)", "++ [100,150)", "++ [50, 100)", "++ [0,50)", "Singly Charged Ions"],
    title="Comparison of TIC calculations.",
    show=True
):
    """
    Arguments:
        rt_min (np.array): The centers of bins of retention times, if they were the default ones. Shit..
    """
    import matplotlib.pyplot as plt
    plt.subplot(2, 1, 1)
    plt.scatter(rt_min, Bruker_TIC,
        label="FULL TIC according to BRUKER"
    )
    plt.stackplot(rt_min, *intensities, labels=labels)
    plt.legend()
    # if equation:
    #     title += f" Multiply charged region defined as {equation}."
    plt.suptitle(title)
    plt.title("TIC View")
    plt.xlabel("Retention Time [minutes]")
    plt.ylabel("TIC [per minute]")

    plt.subplot(2, 1, 2)
    plt.stackplot(rt_min, *percentages, labels=labels)
    plt.legend()
    # title = "Composition of TIC in %."
    # if equation:
    #     title += f" Multiply charged region defined as {equation}."
    plt.title("Percentage View")
    plt.xlabel("Retention Time [minutes]")
    plt.ylabel(r"% composition of TIC [per minute]")
    if show:
        plt.show()


def plot_calibrants(formulas, show=True):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(len(formulas))
    for ax, formula in zip(axs, formulas):
        w = iso.IsoTotalProb(formula=formula, prob_to_cover=.9999)
        ax.stem(w.np_masses(), w.np_probs())
        ax.set_title(formula)
    if show:
        plt.show()


def inv_ion_mobility_mz_QC_plot(TIC, extent, points, show=True, **kwargs):
    import matplotlib.pyplot as plt
    plt.imshow(TIC, aspect="auto", origin="lower",
        extent=extent, **kwargs)
    x,y = zip(*points)
    plt.plot(x, y, c='red', linewidth=8)
    plt.xlabel("m/z")
    plt.ylabel("1/k0")
    if show:
        plt.show()
