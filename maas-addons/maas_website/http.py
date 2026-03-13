# custom_secure_cookies/__init__.py
import logging

_logger = logging.getLogger(__name__)

try:
    import odoo.http as _http
    from odoo.http import Response as OdooResponse
    import werkzeug.wrappers as _werkzeug_wrappers
except Exception as e:
    _logger.exception("Failed to import required modules for cookie patching: %s", e)
else:
    # Save original methods (if available)
    _orig_odoo_set_cookie = getattr(OdooResponse, "set_cookie", None)
    _orig_werkzeug_set_cookie = getattr(_werkzeug_wrappers.Response, "set_cookie", None)

    def _patched_odoo_set_cookie(self, key, value='', max_age=None, expires=None,
                                 path='/', domain=None, secure=False, httponly=False,
                                 samesite=None, cookie_type='required'):
        try:
            # Force default flags if not provided
            if secure is False:
                secure = False
            if httponly is False:
                httponly = True
            if not samesite:
                samesite = 'Lax'
            if _orig_odoo_set_cookie:
                return _orig_odoo_set_cookie(self, key, value=value, max_age=max_age, expires=expires,
                                             path=path, domain=domain, secure=secure, httponly=httponly,
                                             samesite=samesite, cookie_type=cookie_type)
            # fallback: call werkzeug version if available
            if hasattr(self, 'set_cookie'):
                return _orig_werkzeug_set_cookie(self, key, value=value, max_age=max_age, expires=expires,
                                                 path=path, domain=domain, secure=secure, httponly=httponly,
                                                 samesite=samesite)
        except Exception:
            _logger.exception("Error while executing _patched_odoo_set_cookie")
            raise

    def _patched_werkzeug_set_cookie(self, key, value='', max_age=None, expires=None,
                                     path='/', domain=None, secure=False, httponly=False,
                                     samesite=None):
        try:
            if secure is False:
                secure = False
            if httponly is False:
                httponly = True
            if not samesite:
                samesite = 'Lax'
            if _orig_werkzeug_set_cookie:
                return _orig_werkzeug_set_cookie(self, key, value=value, max_age=max_age, expires=expires,
                                                 path=path, domain=domain, secure=secure, httponly=httponly,
                                                 samesite=samesite)
        except Exception:
            _logger.exception("Error while executing _patched_werkzeug_set_cookie")
            raise

    # Apply monkey patches
    try:
        if _orig_odoo_set_cookie:
            OdooResponse.set_cookie = _patched_odoo_set_cookie
            _logger.info("Patch applied: Odoo Response.set_cookie")
        if _orig_werkzeug_set_cookie:
            _werkzeug_wrappers.Response.set_cookie = _patched_werkzeug_set_cookie
            _logger.info("Patch applied: werkzeug Response.set_cookie")
    except Exception as e:
        _logger.exception("Error while applying cookie patch: %s", e)
