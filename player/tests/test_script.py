import mock
import sys
from pyramid.compat import NativeIO
from player import script as layer
from player.layer import ID_LAYER

from base import BaseTestCase


class TestPlayerCommand(BaseTestCase):

    def setUp(self):
        super(TestPlayerCommand, self).setUp()

        self.stdout = sys.stdout
        sys.stdout = self.out = NativeIO()

    def tearDown(self):
        sys.stdout = self.stdout
        super(TestPlayerCommand, self).tearDown()

    @mock.patch('player.script.bootstrap')
    def test_no_params(self, m_bs):
        m_bs.return_value = {'registry': self.registry}

        sys.argv[:] = ['player', 'player.ini']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('[-h] [-l] [-lt] config [asset [asset ...]]', val)

    @mock.patch('player.script.bootstrap')
    def test_list_categories_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.registry[ID_LAYER] = {}

        sys.argv[:] = ['player', '-l', 'player.ini']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('No layers are found.', val)

    @mock.patch('player.script.bootstrap')
    def test_list_categories(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='player:tests/dir1/')
        self.config.add_layer(
            'test2', path='player:tests/bundle/')

        sys.argv[:] = ['player', '-l', 'player.ini']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('player.script.bootstrap')
    def test_list_categories_limit(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='player:tests/dir1/')
        self.config.add_layer(
            'test2', path='player:tests/bundle/')

        sys.argv[:] = ['player', '-l', 'player.ini', 'test2']

        layer.main()

        val = self.out.getvalue()
        self.assertNotIn('* Layer: test1', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('player.script.bootstrap')
    def test_list_templates(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='player:tests/dir1/')
        self.config.add_layer(
            'test2', path='player:tests/bundle/')

        def test(): pass

        self.config.add_tmpl_filter(
            'test1:actions', test)

        sys.argv[:] = ['player', '-lt', 'player.ini']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('player:tests/dir1/', val)
        self.assertIn('actions: .pt (test_script.py: test)', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('player.script.bootstrap')
    def test_list_templates_limit(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='player:tests/dir1/')
        self.config.add_layer(
            'test2', path='player:tests/bundle/')

        sys.argv[:] = ['player', '-lt', 'player.ini', 'test1']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('player:tests/dir1/', val)
        self.assertIn('actions: .pt', val)
        self.assertNotIn('* Layer: test2', val)

    @mock.patch('player.script.bootstrap')
    def test_list_templates_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.registry[ID_LAYER] = {}

        sys.argv[:] = ['player', '-lt', 'player.ini']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('No layers are found.', val)
