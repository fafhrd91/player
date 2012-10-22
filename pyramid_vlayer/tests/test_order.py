from pyramid.exceptions import ConfigurationError
from pyramid_vlayer.vlayer import ID_VLAYER

from base import BaseTestCase


class TestOrder(BaseTestCase):

    _auto_include = False
    _settings = {'vlayer.order:test': 'l1 l2 l3'}

    def test_custom_dir(self):
        self.config.add_vlayer(
            'test', 'l1', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test', 'l2', path='pyramid_vlayer:tests/bundle/dir1/')
        self.config.commit()

        storage = self.registry.get(ID_VLAYER)
        self.assertIn('test', storage)
        self.assertEqual(2, len(storage['test']))
        self.assertEqual('l1', storage['test'][0]['name'])
        self.assertEqual('l2', storage['test'][1]['name'])


class TestOrderUnknown(BaseTestCase):

    _auto_include = False
    _settings = {'vlayer.order:test2': 'l1 l2 l3'}

    def test_custom_dir(self):
        self.config.add_vlayer(
            'test', 'l1', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test', 'l2', path='pyramid_vlayer:tests/bundle/dir1/')
        self.config.commit()

        storage = self.registry.get(ID_VLAYER)
        self.assertIn('test', storage)
        self.assertNotIn('test2', storage)
