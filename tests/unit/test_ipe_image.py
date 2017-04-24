'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import IdahoImage
from auth_mock import get_mock_gbdx_session
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import rasterio
import dask.array as da
from gbdxtools.ipe.io import to_geotiff

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. Replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. Replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)


class IpeImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        #mock_gbdx_session = get_mock_gbdx_session(token='dymmytoken')
        #cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_default.yaml', filter_headers=['authorization'])
    def test_basic_ipe_image(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid)
        self.assertTrue(isinstance(img, IdahoImage))
        assert img._node_id == 'toa_reflectance'
        assert img.shape == (8, 10496, 14848)
        assert img._proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_aoi.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_aoi(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid, bbox=[-74.01626586914064,45.394592696926615,-73.91601562500001,45.43363548747066])
        assert img._node_id == 'toa_reflectance'
        assert img.shape == (8, 3169, 8135)
        assert img._proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_proj.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_proj(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid, bbox=[-74.01626586914064,45.394592696926615,-73.91601562500001,45.43363548747066], proj='EPSG:3857')
        assert img._node_id == 'toa_reflectance'
        assert img.shape == (8, 4514, 8135)
        assert img._proj == 'EPSG:3857' 

    #@my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_aoi.yaml', filter_headers=['authorization'])
    def test_ipe_image_aoi(self):
        #idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        idahoid = '42c9467f-9f01-4bb0-a7db-d25b614bb1a0'
        bbox=[-104.9450969696045,39.79534795320513,-104.93994712829591,39.79729335524221]
        img = self.gbdx.idaho_image(idahoid)
        #aoi = img.aoi(bbox=[-74.01626586914064,45.394592696926615,-73.91601562500001,45.43363548747066])
        aoi = img.aoi(bbox=bbox)
        assert aoi.shape == (1, 440, 1164)#(8, 3169, 8135)
        #rgb = aoi[[4,2,1], ...]
        #assert isinstance(rgb, da.Array)
        tif = to_geotiff(img, path='/tmp/output.tif')
        with rasterio.open(tif) as src:
            assert list(src.bounds) == bbox

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_vrt.yaml', filter_headers=['authorization'])
    def test_ipe_image_vrt(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid, bbox=[-74.01626586914064,45.394592696926615,-73.91601562500001,45.43363548747066], proj='EPSG:3857')
        assert img._node_id == 'toa_reflectance'
        assert img.shape == (8, 4514, 8135)
        assert img._proj == 'EPSG:3857'
        assert isinstance(img.vrt, str)
    
    #@my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_aoi.yaml', filter_headers=['authorization'])
    #def test_ipe_image_to_geotiff(self):
    #    gbdx = Interface()
    #    idahoid = '42c9467f-9f01-4bb0-a7db-d25b614bb1a0'
    #    bbox=[-104.9450969696045,39.79534795320513,-104.93994712829591,39.79729335524221]
    #    img = gbdx.idaho_image(idahoid, bbox=bbox)
    #    print img.shape
    #    tif = to_geotiff(img, path='/tmp/output.tif')
    #    with rasterio.open(tif) as src:
    #        assert list(src.bounds) == bbox
