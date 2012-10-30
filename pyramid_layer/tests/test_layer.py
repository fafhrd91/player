from pyramid.exceptions import ConfigurationConflictError

from base import BaseTestCase


class TestLayerDirective(BaseTestCase):

    _include = False

    def test_layer_directive(self):
        self.assertFalse(hasattr(self.config, 'add_layer'))
        self.assertFalse(hasattr(self.config, 'add_layera'))
        self.config.include('pyramid_layer')

        self.assertTrue(hasattr(self.config, 'add_layer'))
        self.assertTrue(hasattr(self.config, 'add_layers'))


class TestLayer(BaseTestCase):

    _auto_include = False

    def test_layer_registration(self):
        from pyramid_layer.layer import ID_LAYER

        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')
        self.config.commit()

        data = self.registry.get(ID_LAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 1)
        self.assertEqual(data['test'][0]['name'], '')
        self.assertTrue(data['test'][0]['path'].endswith(
            'pyramid_layer/tests/dir1/'))

    def test_multple_layer_registration(self):
        from pyramid_layer.layer import ID_LAYER

        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')
        self.config.commit()

        self.config.add_layer(
            'test', 'custom', path='pyramid_layer:tests/bundle/dir1/')
        self.config.commit()

        data = self.registry.get(ID_LAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 2)
        self.assertEqual(data['test'][0]['name'], 'custom')
        self.assertTrue(data['test'][0]['path'].endswith(
            'pyramid_layer/tests/bundle/dir1/'))
        self.assertEqual(data['test'][1]['name'], '')
        self.assertTrue(data['test'][1]['path'].endswith(
            'pyramid_layer/tests/dir1/'))

    def test_register_layers(self):
        from pyramid_layer.layer import ID_LAYER

        self.config.add_layers(
            'custom', path='pyramid_layer:tests/bundle/')
        self.config.commit()

        data = self.registry.get(ID_LAYER)
        self.assertIn('dir1', data)
        self.assertEqual(len(data['dir1']), 1)
        self.assertEqual(data['dir1'][0]['name'], 'custom')
        self.assertTrue(data['dir1'][0]['path'].endswith(
            'pyramid_layer/tests/bundle/dir1'))

    def test_reg_conflict(self):
        self.config.commit()

        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')
        self.config.add_layer(
            'test', path='pyramid_layer:tests/bundle/dir1/')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)
