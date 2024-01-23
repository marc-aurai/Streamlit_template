import unittest
from Home import load_images
from PIL import Image

class TestLoadImage(unittest.TestCase):
    def test_load_images(self):
        self.assertIsInstance(
            load_images('./assets/image/aurai_logo.png'), 
            Image.Image
            )

if __name__ == '__main__':
    unittest.main()