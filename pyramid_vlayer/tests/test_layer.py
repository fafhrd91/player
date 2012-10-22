from pyramid.exceptions import ConfigurationConflictError

from base import BaseTestCase


class TestLayerDirective(BaseTestCase):

    _include = False

    def test_layer_directive(self):
        self.assertFalse(hasattr(self.config, 'add_vlayer'))
        self.config.include('pyramid_vlayer')

        self.assertTrue(hasattr(self.config, 'add_vlayer'))


class TestLayer(BaseTestCase):

    _auto_include = False

    def test_layer_registration(self):
        from pyramid_vlayer.vlayer import ID_VLAYER

        self.config.add_vlayer(
            'test', path='pyramid_vlayer:tests/dir1/')
        self.config.commit()

        data = self.registry.get(ID_VLAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 1)
        self.assertEqual(data['test'][0]['name'], '')
        self.assertTrue(data['test'][0]['path'].endswith(
            'pyramid_vlayer/tests/dir1/'))

    def test_multple_layer_registration(self):
        from pyramid_vlayer.vlayer import ID_VLAYER

        self.config.add_vlayer(
            'test', path='pyramid_vlayer:tests/dir1/')
        self.config.commit()

        self.config.add_vlayer(
            'test', 'custom', path='pyramid_vlayer:tests/bundle/dir1/')
        self.config.commit()

        data = self.registry.get(ID_VLAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 2)
        self.assertEqual(data['test'][0]['name'], 'custom')
        self.assertTrue(data['test'][0]['path'].endswith(
            'pyramid_vlayer/tests/bundle/dir1/'))
        self.assertEqual(data['test'][1]['name'], '')
        self.assertTrue(data['test'][1]['path'].endswith(
            'pyramid_vlayer/tests/dir1/'))

    def test_register_layers(self):
        from pyramid_vlayer.vlayer import ID_VLAYER

        self.config.add_vlayers(
            'custom', path='pyramid_vlayer:tests/bundle/')
        self.config.commit()

        data = self.registry.get(ID_VLAYER)
        self.assertIn('dir1', data)
        self.assertEqual(len(data['dir1']), 1)
        self.assertEqual(data['dir1'][0]['name'], 'custom')
        self.assertTrue(data['dir1'][0]['path'].endswith(
            'pyramid_vlayer/tests/bundle/dir1'))

    def test_reg_conflict(self):
        self.config.commit()

        self.config.add_vlayer(
            'test', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test', path='pyramid_vlayer:tests/bundle/dir1/')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)
