import io
import unittest
import zipfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from plone.app.theming.browser.mapper import ThemeMapper

from plone.app.theming.utils import extractThemeInfo, getTheme


class ThemeTextTests(unittest.TestCase):
    def test_preview_does_not_parse_the_published_query_twice(self):
        request = HTTPRequest(io.BytesIO(), {
            'SERVER_NAME': 'localhost', 'SERVER_PORT': '80',
            'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'path=%2F&theme=off',
        }, HTTPResponse())
        request.processInputs()
        portal = SimpleNamespace(absolute_url=lambda: 'http://localhost/plone')
        response = SimpleNamespace(getBody=lambda: b'binary',
                                   headers={'content-type': 'application/octet-stream'})
        with patch('plone.app.theming.browser.mapper.getPortal', return_value=portal), \
                patch('plone.app.theming.browser.mapper.subrequest', return_value=response) as subrequest:
            self.assertEqual(ThemeMapper(object(), request).getFrame(), b'binary')
        subrequest.assert_called_once_with('/', root=portal)

    def manifest(self, binary=False):
        rules = '/++theme++demo/gr\u00fc\u00dfe.xml'
        prefix = '/++theme++demo/gr\u00fc\u00dfe'
        if binary:
            rules, prefix = rules.encode('utf-8'), prefix.encode('utf-8')
        return dict(title='Gr\u00fc\u00dfe', description='Beschreibung', rules=rules,
                    prefix=prefix, parameters={}, doctype='', preview=None)

    def test_unicode_manifest_paths(self):
        theme = getTheme('demo', self.manifest())
        self.assertEqual(theme.rules, '/++theme++demo/gr\u00fc\u00dfe.xml')
        self.assertEqual(theme.absolutePrefix, '/++theme++demo/gr\u00fc\u00dfe')

    def test_utf8_manifest_paths(self):
        theme = getTheme('demo', self.manifest(binary=True))
        self.assertEqual(theme.rules, '/++theme++demo/gr\u00fc\u00dfe.xml')
        self.assertEqual(theme.absolutePrefix, '/++theme++demo/gr\u00fc\u00dfe')

    def test_import_description_is_preserved(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as archive:
            archive.writestr('demo/manifest.cfg', '[theme]\ntitle = Titel\ndescription = Gr\u00fc\u00dfe\n')
            archive.writestr('demo/rules.xml', '<rules/>')
        data.seek(0)
        with zipfile.ZipFile(data) as archive:
            theme = extractThemeInfo(archive)
        self.assertEqual(theme.title, 'Titel')
        self.assertEqual(theme.description, 'Gr\u00fc\u00dfe')
