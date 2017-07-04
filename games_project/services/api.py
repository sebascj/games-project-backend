
from services.models import Product, Order
# from tastypie.authentication import BasicAuthentication
# from tastypie.authentication import ApiKeyAuthentication
from services.authentication import CustomApiKeyAuthentication
# Create User
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields

from .models import UserProfile
from .utils import MINIMUM_PASSWORD_LENGTH, validate_password
from .exceptions import CustomBadRequest
#
import time

"""
# version 1
class CreateUserResource(ModelResource):
    user = fields.ForeignKey('core.api.UserResource', 'user', full=True)
    class Meta:
        allowed_medhods = ['post']
        always_return_data = True
        authentication = CustomApiKeyAuthentication()
        authorization = Authorization()
        queryset = UserProfile.objects.all()
        resource_name = 'create_user'
        always_return_data = True

    def hydrate(self, bundle):
        REQUIRED_USER_PROFILE_FIELDS = ("birth_year", "gender", "user")
        for field in REQUIRED_USER_PROFILE_FIELDS:
            if field not in bundle.data:
                raise CustomBadRequest(
                    code="missing_key",
                    message="Must provide {missing_key} when creating a user.".format(missing_key=field))

        REQUIRED_USER_FIELDS = ("username", "email", "first_name", "last_name", "raw_password")
        for field in REQUIRED_USER_FIELDS:
            if field not in bundle.data["user"]:
                raise CustomBadRequest(
                    code="missing_key",
                    message="Must proide {missing_key} when creating a user.".format(missing_key=field))
        return bundle

        def obj_create(self, bundle, **kwargs):
            try:
                email = bundle.data["user"]["email"]
                username = bundle.data["user"]["username"]
                if User.objects.filter(email=email):
                    raise CustomBadRequest(
                    code="duplicate_exception",
                    message="that email is already used.")
                if User.objects.filter(username=username):
                    raise CustomBadRequest(
                    code="duplicate_exception",
                    message="That username is already used.")
            except User.DoesNotExist:
                pass

            self._meta.resource_name = UserProfileResource._meta.resource_name
            return super(CreateUserResource, self).obj_create(bundle, **kwargs)

class UserResource(ModelResource):
    raw_password = fields.CharField(attribute=None, readonly=True, null=True, blank=True)

    class Meta:
        # authentication = CustomApiKeyAuthentication()
        authorization = Authorization();
        allowed_medhods = ['get', 'patch', 'put']
        always_return_data = True
        queryset = User.objects.all().select_related("api_key")
        excludes = ['is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']

        def authorized_read_list(self, object_list, bundle):
            return object_list.filter(id=bundle.request.user.id).select_related()

        def hydrate(self, bundle):
            if "raw_password" in bundle.data:
                raw_password = bundle.data.pop["raw_password"]

                if not validate_password(raw_password):
                    if len(raw_password) < MINIMUM_PASSWORD_LENGTH:
                        raise CustomBadRequest(
                            code="invalid_password",
                            message=("Your password sould contain at least {length} characters.".format(length=MINIMUM_PASSWORD_LENGTH)))
                    raise CustomBadRequest(
                        code="invalid_password",
                        message=("Your password should contain at least one number, one uppercase letter, no special character, and no spaces"))

                bundle.data["password"] = make_password(raw_password)
            return bundle

        def dehydrate(self, bundle):
            bundle.data['key'] = bundle.obj.api_key.key

            try:
                del bundle.data["raw_password"]
            except KeyError:
                pass
            return bundle

class UserProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        authorization = Authorization()
        always_return_data = True
        allowed_medhods = ['get', 'patch']
        detail_allowed_methods = ['get', 'patch', 'put']
        queryset = UserProfile.objects.all()
        resource_name = 'user_profile'

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user).selec_related()

    def get_list(self, request, **kwargs):
        kwargs["pk"] = request.user.profile.pk
        return super(UserProfileResource, self).get_detail(request, **kwargs)

"""

class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        excludes = ['product_type', 'price']
        allowed_medhods = ['get']
        authentication = CustomApiKeyAuthentication()
        # authentication = ApiKeyAuthentication()
        # authentication = BasicAuthentication()

    def dehydrate_name(self, bundle):
        return bundle.data['name'].upper()

    def dehydrate(self, bundle):
        bundle.data['server_time'] = time.ctime()
        return bundle

class OrderResources(ModelResource):
    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order'
        allowed_medhods = ['get', 'post', 'put']
        authentication = CustomApiKeyAuthentication()


"""
version 2
"""
class UserResource(ModelResource):
    '''Get and update user profile.'''

    class Meta:
        # For authentication, allow both basic and api key so that the key
        # can be grabbed, if needed.
        # authentication = MultiAuthentication(BasicAuthentication(),
        #                                      ApiKeyAuthentication())
        # authorization = CustomAuthorization()
        always_return_data = True
        # authentication = Authentication()
        # authorization = ReadOnlyAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch', 'put']
        queryset = User.objects.all().select_related('api_key')
        fields = ['email', 'first_name', 'last_name']
        resource_name = 'user'

    def hydrate(self, bundle):
        try:
            raw_password = bundle.data.pop('password')
            if not validate_password(raw_password):
                raise CustomBadRequest(
                    code='invalid_password',
                    message='Your password is invalid.')

            bundle.obj.set_password(raw_password)
        except KeyError:
            pass

        return bundle

    def dehydrate(self, bundle):
        if bundle.obj.pk == bundle.request.user.pk:
            bundle.data['key'] = bundle.obj.api_key.key

        return bundle

    def authorized_read_list(self, object_list, bundle):
        # Return the profile of user making api reqeust.
        return object_list.filter(id=bundle.request.user.id).select_related()


class CreateUserResource(ModelResource):
    '''Endpoint to create a new account for a user.'''

    class Meta:
        queryset = User.objects.all()
        always_return_data = True
        # authentication = Authentication()
        # authorization = ReadOnlyAuthorization()
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        authorization = Authorization()
        resource_name = 'create_user'
        fields = ['email', 'first_name', 'last_name', 'username']

    def obj_create(self, bundle, **kwargs):
        REQUIRED_FIELDS = ('email', 'first_name', 'last_name', 'password', 'username')
        for field in REQUIRED_FIELDS:
            if field not in bundle.data:
                raise CustomBadRequest(
                    code='missing_key',
                    message=('Must provide {missing_key} when creating a'
                             ' user.').format(missing_key=field))

        email = bundle.data['email']
        try:
            if User.objects.filter(email=email):
                raise CustomBadRequest(
                    code='duplicate_exception',
                    message='That email is already associated with some user.')
        except User.DoesNotExist:
            pass

        raw_password = bundle.data.pop('password')
        if not validate_password(raw_password):
            raise CustomBadRequest(
                code='invalid_password',
                message='Your password is invalid.')

        ## Add password to kwargs
        kwargs["password"] = make_password(raw_password)

        return super(CreateUserResource, self).obj_create(bundle, **kwargs)
