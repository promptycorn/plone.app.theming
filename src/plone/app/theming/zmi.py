import logging

from App.special_dtml import DTMLFile
from zope.globalrequest import getRequest

LOGGER = logging.getLogger('plone.app.theming')


class NoThemeDTMLFile(DTMLFile):
    '''DTMLFile that automatically sets the X-Theme-Disabled header'''

    def _exec(self, bound_data, args, kw):
        request = getRequest()
        if request is not None:
            request.response.setHeader('X-Theme-Disabled', '1')
        return DTMLFile._exec(self, bound_data, args, kw)

# Most ZMI pages include 'manage_page_header'
NO_THEME_DTML = [
    'manage',
    'manage_page_header',
    'manage_top_frame',
]


def patch_zmi():
    from App.Management import Navigation
    for name in NO_THEME_DTML:
        dtml = getattr(Navigation, name, None)
        if dtml is None:
            LOGGER.debug(
                'Zope Management Interface DTML file %s is not available.',
                name)
            continue
        try:
            dtml.__class__ = NoThemeDTMLFile
        except TypeError:
            LOGGER.debug(
                'Could not patch Zope Management Interface DTML file %s.',
                name)
    LOGGER.debug('Patched Zope Management Interface to disable theming.')
