

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
