from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

# Some systems have a broken/missing ``roman`` module; monkey patch one in

try:
    import roman
except ImportError:
    from plone.app.theming import _roman
    import sys
    sys.modules['roman'] = _roman
