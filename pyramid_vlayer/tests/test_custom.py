from pyramid.exceptions import ConfigurationError
from pyramid_vlayer.vlayer import ID_VLAYER

from base import BaseTestCase


class TestSettingsError(BaseTestCase):

    _settings = {'vlayer.custom': 'unknown'}
    _include = False

    def test_custom(self):
        self.assertRaises(
            ConfigurationError, self.config.include, 'pyramid_vlayer')


class TestSettingsCustom(BaseTestCase):

    _auto_include = False
    _settings = {'vlayer.custom': 'pyramid_vlayer:tests/bundle/'}

    def test_custom_dir(self):
        self.config.add_vlayer(
            'dir1', path='pyramid_vlayer:tests/dir1/')
        self.config.commit()

        storage = self.registry.get(ID_VLAYER)
        self.assertIn('dir1', storage)
        self.assertEqual(2, len(storage['dir1']))
        self.assertEqual('vlayer_custom', storage['dir1'][0]['name'])
        self.assertEqual('', storage['dir1'][1]['name'])
