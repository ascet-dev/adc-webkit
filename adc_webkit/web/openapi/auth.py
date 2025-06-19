from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adc_webkit.web.auth import HTTPAuth


def build_security_definition(auth: 'HTTPAuth'):
    return auth.__class__.__name__.lower(), {
        'type': 'http',
        'description': auth.description,
        'scheme': auth.scheme,
        'name': auth.header_name,
    }
