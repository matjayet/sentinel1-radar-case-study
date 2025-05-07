import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from osgeo import gdal

def reproject_geotiff(input_file, output_file, target_crs):
    """
    Reproject a GeoTIFF file to a target coordinate reference system (CRS).
    """
    gdal.Warp(output_file, input_file, dstSRS=target_crs)

def rescale_to_01(array, lower_percentile=2, upper_percentile=92):
    """
    Rescale array values to 0–1 range based on given percentiles,
    to reduce the influence of extreme outliers.
    """
    min_val, max_val = np.percentile(array, [lower_percentile, upper_percentile])
    return np.clip((array - min_val) / (max_val - min_val + 1e-10), 0, 1)

def view_geotiff(input_file, output_dir='outputs/'):
    """
    Visualize VV, VH, and VV/VH ratio from a GeoTIFF file.
    Saves grayscale plots for VH, VV, and an RGB composite.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_name = os.path.splitext(os.path.basename(input_file))[0]

    # Read VV and VH bands from geotiff
    with rasterio.open(input_file) as dataset:
        vh = dataset.read(1).astype(np.float32)  # Band 1: sigma0_VH
        vv = dataset.read(2).astype(np.float32)  # Band 2: sigma0_VV

    # Rescale bands
    vh_rescaled = rescale_to_01(vh, 2, 92)
    vv_rescaled = rescale_to_01(vv, 2, 92)

    # Compute VV / VH ratio (with epsilon to avoid division by zero)
    epsilon = 1e-10
    vv_vh_ratio = vv / (vh + epsilon)
    vv_vh_rescaled = rescale_to_01(vv_vh_ratio, 2, 92)

    # Plot VH grayscale
    plt.imshow(vh_rescaled, cmap='gray')
    plt.title('Sigma0 VH (Rescaled)')
    plt.axis('off')
    plt.savefig(os.path.join(output_dir, f"{output_name}_vh.png"))
    plt.close()

    # Plot VV grayscale
    plt.imshow(vv_rescaled, cmap='gray')
    plt.title('Sigma0 VV (Rescaled)')
    plt.axis('off')
    plt.savefig(os.path.join(output_dir, f"{output_name}_vv.png"))
    plt.close()

    # Create RGB composite (R = VV, G = VH, B = VV/VH ratio)
    rgb = np.dstack((vv_rescaled, vh_rescaled, vv_vh_rescaled))

    plt.imshow(rgb)
    plt.title('RGB Composite (VV, VH, VV/VH)')
    plt.axis('off')
    plt.savefig(os.path.join(output_dir, f"{output_name}_rgb.png"))
    plt.close()

    print(f"Plots saved to {output_dir}")


