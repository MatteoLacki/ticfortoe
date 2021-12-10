

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
    equation="",
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
    title = "Comparison of TIC calculations."
    if equation:
        title += f" Multiply charged region defined as {equation}."
    plt.title(title)
    plt.xlabel("Retention Time [minutes]")
    plt.ylabel("% of TIC [per minute]")

    plt.subplot(2, 1, 2)
    plt.stackplot(rt_min, *percentages, labels=labels)
    plt.legend()
    title = "Composition of TIC in %."
    if equation:
        title += f" Multiply charged region defined as {equation}."
    plt.title(title)
    plt.xlabel("Retention Time [minutes]")
    plt.ylabel("% of TIC [per minute]")
    if show:
        plt.show()

