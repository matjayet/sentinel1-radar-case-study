from esa_snappy import ProductIO, GPF, HashMap
from radar_cs.utils import reproject_geotiff, view_geotiff
import json

def preprocess_slc(file_path, ouput_file='outputs/preprocessed_slc'):
    # Load product
    p = ProductIO.readProduct(file_path)

    # Apply orbit file
    parameters = HashMap()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', False)
    p = GPF.createProduct('Apply-Orbit-File', parameters, p)

    # Thermal noise removal
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    parameters.put('outputNoise', False)
    parameters.put('reintroduceThermalNoise', False)
    p = GPF.createProduct('ThermalNoiseRemoval', parameters, p)

    # Calibration
    band_names = [band for band in p.getBandNames() if band.endswith('VV') or band.endswith('VH')]
    source_bands_str = ','.join(band_names)

    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    parameters.put('selectedPolarisations', 'VV,VH')
    parameters.put('sourceBands', source_bands_str)
    parameters.put('outputImageScaleInDb', False)
    parameters.put('outputImageInComplex', False)
    parameters.put('createGammaBand', False)
    parameters.put('createBetaBand', False)
    parameters.put('outputBetaBand', False)
    parameters.put('outputGammaBand', False)
    p = GPF.createProduct('Calibration', parameters, p)

    # Deburst
    parameters = HashMap()
    p = GPF.createProduct('TOPSAR-Deburst', parameters, p)

    # Speckle filter
    parameters = HashMap()
    parameters.put('filter', 'Refined Lee')
    parameters.put('filterSizeX', '3')
    parameters.put('filterSizeY', '3')
    parameters.put('dampingFactor', '2')
    parameters.put('estimateENL', True)
    parameters.put('enl', '1.0')
    parameters.put('numLooksStr', '1')
    parameters.put('targetWindowSizeStr', '3x3')
    parameters.put('sigmaStr', '0.9')
    parameters.put('anSize', '50')
    p = GPF.createProduct('Speckle-Filter', parameters, p)

    # Terrain correction
    parameters = HashMap()
    parameters.put('demName', 'Copernicus 30m Global DEM')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', '10.0')
    parameters.put('mapProjection', 'AUTO:42001')
    parameters.put('nodataValueAtSea', False)
    parameters.put('saveSelectedSourceBand', True)
    parameters.put('selectedPolarisations', 'VV,VH')
    p = GPF.createProduct('Terrain-Correction', parameters, p)

    # Subset
    parameters = HashMap()

    with open('AOI_Rubicon_sent1.geojson', 'r') as file:
        geojson_data = json.load(file)["features"][0]["geometry"]

    subset_params = HashMap()
    subset_params.put('geoRegion', f'POLYGON(({", ".join([f"{coord[0]} {coord[1]}" for coord in geojson_data["coordinates"][0]])}))')
    subset = GPF.createProduct('Subset', subset_params, p)

    write_format = 'BEAM-DIMAP' # in this case write as BEAM-DIMAP
    ProductIO.writeProduct(subset , output_file, write_format)
    ProductIO.writeProduct(subset, output_file+'.tif', 'GeoTIFF')



if __name__ == "__main__":

    file_path = "data/S1A_IW_SLC__1SDV_20250503T173148_20250503T173215_059033_07527A_2B0C.SAFE.zip"
    output_file = "outputs/preprocessed_slc"
    crs = 'EPSG:3857'

    preprocess_slc(file_path=file_path, ouput_file=output_file)
    reproject_geotiff(output_file + '.tif', output_file=output_file+'_'+crs+'.tif', target_crs=crs)
    view_geotiff(input_file=output_file+'_'+crs+'.tif')
