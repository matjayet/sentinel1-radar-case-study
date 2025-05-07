from esa_snappy import ProductIO, GPF, HashMap
from radar_cs.utils import reproject_geotiff, view_geotiff
import json
import os

def load_aoi_wkt(geojson_path: str) -> str:
    """
    Load an AOI polygon from a GeoJSON file and convert it to WKT format.

    Args:
        geojson_path (str): Path to the GeoJSON file containing the area of interest.

    Returns:
        str: WKT string representation of the polygon.
    """
    with open(geojson_path, 'r') as file:
        geojson_data = json.load(file)["features"][0]["geometry"]
    wkt_coords = ", ".join(f"{coord[0]} {coord[1]}" for coord in geojson_data["coordinates"][0])
    return f"POLYGON(({wkt_coords}))"

def preprocess_slc(file_path: str, output_file: str = 'outputs/preprocessed_slc', aoi_geojson: str = 'AOI_Rubicon_sent1.geojson') -> None:
    """
    Preprocess Sentinel-1 SLC data using SNAP operators:
    apply orbit file, thermal noise removal, calibration, debursting,
    speckle filtering, terrain correction, and AOI subset.

    Args:
        file_path (str): Path to the input Sentinel-1 SLC product (ZIP or SAFE).
        output_file (str): Base path (without extension) for output products.
        aoi_geojson (str): Path to GeoJSON defining the subset area.
    """
    # Load Sentinel-1 product
    product = ProductIO.readProduct(file_path)

    # Apply orbit file
    orbit_params = HashMap()
    orbit_params.put('orbitType', 'Sentinel Precise (Auto Download)')
    orbit_params.put('polyDegree', '3')
    orbit_params.put('continueOnFail', False)
    product = GPF.createProduct('Apply-Orbit-File', orbit_params, product)

    # Remove thermal noise
    noise_params = HashMap()
    noise_params.put('removeThermalNoise', True)
    product = GPF.createProduct('ThermalNoiseRemoval', noise_params, product)

    # Calibrate to Sigma0
    band_names = [b for b in product.getBandNames() if b.endswith('VV') or b.endswith('VH')]
    calib_params = HashMap()
    calib_params.put('outputSigmaBand', True)
    calib_params.put('selectedPolarisations', 'VV,VH')
    calib_params.put('sourceBands', ','.join(band_names))
    calib_params.put('outputImageScaleInDb', False)
    product = GPF.createProduct('Calibration', calib_params, product)

    # Deburst IW bursts
    product = GPF.createProduct('TOPSAR-Deburst', HashMap(), product)

    # Apply speckle filtering
    speckle_params = HashMap()
    speckle_params.put('filter', 'Refined Lee')
    speckle_params.put('filterSizeX', '3')
    speckle_params.put('filterSizeY', '3')
    speckle_params.put('dampingFactor', '2')
    speckle_params.put('estimateENL', True)
    speckle_params.put('enl', '1.0')
    product = GPF.createProduct('Speckle-Filter', speckle_params, product)

    # Terrain correction
    terrain_params = HashMap()
    terrain_params.put('demName', 'Copernicus 30m Global DEM')
    terrain_params.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    terrain_params.put('pixelSpacingInMeter', '10.0')
    terrain_params.put('mapProjection', 'AUTO:42001')
    terrain_params.put('nodataValueAtSea', False)
    terrain_params.put('saveSelectedSourceBand', True)
    terrain_params.put('selectedPolarisations', 'VV,VH')
    product = GPF.createProduct('Terrain-Correction', terrain_params, product)

    # Subset to AOI
    if not os.path.exists(aoi_geojson):
        raise FileNotFoundError(f"AOI file not found: {aoi_geojson}")
    aoi_wkt = load_aoi_wkt(aoi_geojson)

    subset_params = HashMap()
    subset_params.put('geoRegion', aoi_wkt)
    subset_product = GPF.createProduct('Subset', subset_params, product)

    # Write outputs: BEAM-DIMAP and GeoTIFF
    ProductIO.writeProduct(subset_product, output_file, 'BEAM-DIMAP')
    ProductIO.writeProduct(subset_product, output_file + '.tif', 'GeoTIFF')

if __name__ == "__main__":
    
    file_path = "data/S1A_IW_SLC__1SDV_20250503T173148_20250503T173215_059033_07527A_2B0C.SAFE.zip"
    output_file = "outputs/preprocessed_slc"
    crs = 'EPSG:3857'

    preprocess_slc(file_path=file_path, output_file=output_file)

    reproject_geotiff(
        input_file=output_file + '.tif',
        output_file=output_file + f'_{crs}.tif',
        target_crs=crs
    )

    view_geotiff(input_file=output_file + f'_{crs}.tif')
