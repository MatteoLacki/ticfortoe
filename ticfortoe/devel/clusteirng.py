%load_ext autoreload
%autoreload 2
import matplotlib.pyplot as plt
import numpy as np

from ticfortoe.binning import (
    get_aggregates,
    BinnedData
)


# res_path = "/home/matteo/Projects/ticfortoe/ticfortoe_results/G210521_025_Slot1-29_1_1731"
res_path = "/home/matteo/Projects/ticfortoe/local_results/M201203_013_Slot1-1_1_708.d"





from skimage.feature import blob_dog, blob_log, blob_doh
from skimage import exposure, feature, segmentation, filters, measure, morphology



# img = exposure.equalize_hist(data_2D.data.astype(float))
img = data_2D.data.astype(int)

def p(img):
    plt.imshow(img); plt.show()
?filters.threshold_otsu
thresh = filters.threshold_otsu(np.sqrt(img))
bw = morphology.closing(np.sqrt(img) > thresh)
cleared = segmentation.clear_border(bw)

p(img.T)
p(bw.T)
p(cleared)

p(measure.label(cleared))

clust = feature.corner_fast(
    image=img
)
p(clust)

p(filters.roberts(img))


p(clust)
p(img)
p(data_2D.data)
plt.imshow(img)
contours = measure.find_contours(img, 500)
for contour in contours:
    plt.plot(contour[:,1], contour[:,0], linewidth=2)
plt.show()
