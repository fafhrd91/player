import mock
import os, shutil
import sys
import tempfile

import pyramid
from pyramid.compat import NativeIO
from pyramid_vlayer import script as vlayer

from base import BaseTestCase


class TestPvlayerCommand(BaseTestCase):

    def setUp(self):
        super(TestPvlayerCommand, self).setUp()

        self.stdout = sys.stdout
        sys.stdout = self.out = NativeIO()

    def tearDown(self):
        sys.stdout = self.stdout
        super(TestPvlayerCommand, self).tearDown()

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_no_params(self, m_bs):
        m_bs.return_value = {'registry': self.registry}

        sys.argv[:] = ['pvlayer', 'pyramid_vlayer.ini']

        vlayer.main()

        val = self.out.getvalue()
        self.assertIn('[-h] [-l] [-lt] config [asset [asset ...]]', val)

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_list_categories_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}

        sys.argv[:] = ['pvlayer', '-l', 'pyramid_vlayer.ini']

        vlayer.main()

        val = self.out.getvalue()
        self.assertIn('No layers are found.', val)

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_list_categories(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_vlayer(
            'test1', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test2', path='pyramid_vlayer:tests/bundle/')

        sys.argv[:] = ['pvlayer', '-l', 'pyramid_vlayer.ini']

        vlayer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_list_categories_limit(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_vlayer(
            'test1', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test2', path='pyramid_vlayer:tests/bundle/')

        sys.argv[:] = ['pvlayer', '-l', 'pyramid_vlayer.ini', 'test2']

        vlayer.main()

        val = self.out.getvalue()
        self.assertNotIn('* Layer: test1', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_list_templates(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_vlayer(
            'test1', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test2', path='pyramid_vlayer:tests/bundle/')

        sys.argv[:] = ['pvlayer', '-lt', 'pyramid_vlayer.ini']

        vlayer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('pyramid_vlayer:tests/dir1/', val)
        self.assertIn('actions: .pt', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_list_templates_limit(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_vlayer(
            'test1', path='pyramid_vlayer:tests/dir1/')
        self.config.add_vlayer(
            'test2', path='pyramid_vlayer:tests/bundle/')

        sys.argv[:] = ['pvlayer', '-lt', 'pyramid_vlayer.ini', 'test1']

        vlayer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('pyramid_vlayer:tests/dir1/', val)
        self.assertIn('actions: .pt', val)
        self.assertNotIn('* Layer: test2', val)

    @mock.patch('pyramid_vlayer.script.bootstrap')
    def test_list_templates_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}

        sys.argv[:] = ['pvlayer', '-lt', 'pyramid_vlayer.ini']

        vlayer.main()

        val = self.out.getvalue()
        self.assertIn('No layers are found.', val)
