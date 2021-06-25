from rest_framework import permissions

class ExpiryLinksPermission(permissions.BasePermission):
    message = 'Expiry links are available only for higher tier accounts.'

    def has_permission(self, request, view):

         if request.method == "GET":
             return True
         else:
             return request.user.account_type.expiring_link_allow
