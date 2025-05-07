from osgeo import gdal
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import cv2

def reproject_geotiff(input_file, output_file, target_crs):
    gdal.Warp(output_file, input_file, dstSRS=target_crs)

def view_geotiff(input_file, output_dir='outputs/'):

    output_name = input_file.split('/')[-1].split('.')[0]

    # Read VV and VH bands
    with rasterio.open(input_file) as dataset:
        vh = dataset.read(1)  # Band 1 (likely VV or VH)
        vv = dataset.read(2)  # Band 2 (likely the other polarization)
        # Calculate percentiles for histogram-based adjustment (ignoring extreme outliers)
    
    vh_min, vh_max = np.percentile(vh, [2, 92])  # 2nd and 98th percentiles
    vv_min, vv_max = np.percentile(vv, [2, 92])
    print(vv_max, vv_min, vh_max, vh_min)

    # Rescale VH and VV based on the histogram percentiles
    vh_rescaled = np.clip((vh - vh_min) / (vh_max - vh_min), 0, 1)
    vv_rescaled = np.clip((vv - vv_min) / (vv_max - vv_min), 0, 1)

    # vv_rescaled = np.zeros((height, width),np.float32)
    # cv2.normalize(vv, vv_rescaled, 0, 1.0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)


    plt.imshow(vh_rescaled, cmap='gray')
    plt.title('Sigma0 VH after processing')

    plt.savefig(output_dir + output_name + '_plot_vh.png')

    plt.imshow(vv_rescaled, cmap='gray')
    plt.title('Sigma0 VV after processing')
    plt.savefig(output_dir + output_name + '_plot_vv.png')

    # Compute VH - VV
    epsilon = 1e-10  # Small constant to avoid division by zero
    vvqvh = vv / (vh+epsilon)

    vvqvh_min, vvqvh_max = np.percentile(vvqvh, [2, 92])
    vvqvh_rescaled = np.clip((vvqvh - vvqvh_min) / (vvqvh_max - vvqvh_min), 0, 1) 

    # Stack into RGB image
    rgb = np.dstack((vv_rescaled, vh_rescaled, vvqvh_rescaled))

    plt.imshow(rgb) 
    plt.title('Image after processing')
    plt.savefig(output_dir + output_name + '_plot_rgb.png')
