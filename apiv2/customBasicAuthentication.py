import base64
import binascii

from rest_framework import authentication, HTTP_HEADER_ENCODING, exceptions
from django.utils.translation import gettext_lazy as _

from loginSystem.models import Administrator
from plogical import hashPassword


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class CustomBasicAuthentication(authentication.BaseAuthentication):
    """
    Custom HTTP Basic authentication against username/password.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return None

        if len(auth) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = _('Invalid basic header. Credentials not correctly base64 encoded.')
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self.authenticate_credentials(userid, password, request)

    def authenticate_credentials(self, userid, password, request=None):
        """
        Authenticate the userid and password against username and password
        with optional request for context.
        """
        try:
            user = Administrator.objects.get(userName=userid)
        except Administrator.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))

        user.username = user.userName

        if hashPassword.check_password(user.password, password):
            if user.api == 0:
                raise exceptions.AuthenticationFailed(_('API Access Disabled.'))
            else:
                request.session['userID'] = user.pk
        else:
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))

        return (user, None)

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm
