import os
import unittest
import json

from bridgestyle import qgis

from qgis.core import QgsRasterLayer, QgsVectorLayer

class QgisToStylerTest(unittest.TestCase):
   pass
    
_layers = {}
def load_layer(file):    
    if file not in _layers:
        name = os.path.basename(file)
        layer = QgsRasterLayer(file, "testlayer", "gdal")
        if not layer.isValid():
            layer = QgsVectorLayer(file, "testlayer", "ogr")
        _layers[file] = layer
    return _layers[file]

def test_function(datafile, stylefile, expected):
    def test(self):
        layer = load_layer(datafile)
        layer.loadNamedStyle(stylefile)
        geostyler, icons, warnings = qgis.togeostyler.convert(layer)
        expected["name"] = "testlayer" #just in case the expected geostyler was created 
                                       # from a layer with a different name
        self.assertEqual(geostyler, expected)
    return test

def run_tests():
    '''
    This methods dinamically create tests based on the contents of the 'qgis'
    subfolder.
    The structure of files in the subfolder must be as follows:
    - For each dataset that you want to use, create a subfolder under 'qgis'
    - Add the layer file in that subfolder. It must be named 'testlayer.gpkg'
      or 'testlayer.tiff' depending of whether it is a vector or a raster layer
    - In the same subfolder, along with the layer file, you can add as many
      qml files as you want to test. The names of these files will be used
      to set the name of the corresponding test
    - For each qml file, a .geostyler file with the same name must exist in
      the subfolder. It must contain the expected geostyler representation
      of the style in the qml file.
    - The test will load the testlayer file, assign the qml to it, generate
      a geostyler representation from it, and then compare to the expected
      geostyler result.
    '''
    suite = unittest.TestSuite()
    main_folder = os.path.join(os.path.dirname(__file__), "data", "qgis")
    for subfolder in os.listdir(main_folder):
        datafile = os.path.join(main_folder, subfolder, "testlayer.gpkg")
        if not os.path.exists(datafile):
            datafile = os.path.join(main_folder, subfolder, "testlayer.tiff")
        subfolder_path = os.path.join(main_folder, subfolder)
        for style in os.listdir(subfolder_path):
            if style.lower().endswith("qml"):
                stylefile = os.path.join(subfolder_path, style)
                name = os.path.splitext(stylefile)[0]
                expectedfile = name + ".geostyler"
                with open(expectedfile) as f:
                    expected = json.load(f)                
                setattr(QgisToStylerTest, 'test_' + name, test_function(datafile, stylefile, expected))                
    
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QgisToStylerTest)
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    run_tests()
    