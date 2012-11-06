# -*- coding: utf-8 -*-
""" Unit tests for L{pyramid_layer.message} """
from pyramid.compat import text_

from base import BaseTestCase
from pyramid_layer.message import add_message
from pyramid_layer.message import render_messages


class TestStatusMessages(BaseTestCase):

    def test_messages_addmessage(self):
        add_message(self.request, 'message')

        res = render_messages(self.request)

        self.assertEqual(
            res,
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>\n','utf-8'))

    def test_messages_warning_msg(self):
        add_message(self.request, 'warning', 'warning')

        self.assertEqual(
            render_messages(self.request),
            text_('<div class="alert alert-warning">\n  <a class="close" data-dismiss="alert">×</a>\n  warning\n</div>\n','utf-8'))

    def test_messages_error_msg(self):
        add_message(self.request, 'error', 'error')

        self.assertEqual(
            render_messages(self.request),
            text_('<div class="alert alert-error">\n  <a class="close" data-dismiss="alert">×</a>\n  error\n</div>\n','utf-8'))

        add_message(self.request, ValueError('Error'), 'error')
        self.assertEqual(
            render_messages(self.request),
            text_('<div class="alert alert-error">\n  <a class="close" data-dismiss="alert">×</a>\n  ValueError: Error\n</div>\n','utf-8'))

    def test_messages_custom_msg(self):
        self.config.add_layer(
            'message', 'test', path='pyramid_layer:tests/message/')

        add_message(self.request, 'message', 'custom')
        self.assertEqual(
            render_messages(self.request).strip(),
            '<div class="customMsg">message</div>')

    def test_messages_custom_msg_different_type(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/message/')

        add_message(self.request, 'message', 'test:custom')
        self.assertEqual(
            render_messages(self.request).strip(),
            '<div class="customMsg">message</div>')

    def test_messages_render_message_with_error(self):
        self.config.add_layer(
            'message', 'test', path='ptah:tests/messages/')

        def customMessage(context, request):
            raise ValueError()

        self.config.add_tmpl_filter('message:custom', customMessage)

        self.assertRaises(
            ValueError, add_message, self.request, 'message', 'custom')

    def test_messages_render(self):
        add_message(self.request, 'message')

        self.assertEqual(
            render_messages(self.request),
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>\n','utf-8'))

        msg = render_messages(self.request)
        self.assertEqual(msg, '')

    def test_messages_unknown_type(self):
        from pyramid_layer import RendererNotFound

        self.assertRaises(
            RendererNotFound,
            add_message, self.request, 'message', 'unknown')

    def test_messages_request_attr(self):
        from pyramid.request import Request
        from pyramid.testing import DummySession
        from pyramid.interfaces import IRequestExtensions

        req = Request(environ=self._environ)
        req.registry = self.registry
        req.session = DummySession()

        extensions = self.registry.getUtility(IRequestExtensions)
        req._set_extensions(extensions)

        # add_message
        req.add_message('message')

        res = req.render_messages()

        self.assertEqual(
            res,
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>\n','utf-8'))
        