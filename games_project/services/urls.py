from django.conf.urls import url, include
from tastypie.api import Api
from services.api import ProductResource, OrderResources, CreateUserResource, UserResource

v1_api = Api(api_name='v1')
v1_api.register(ProductResource())
v1_api.register(OrderResources())
v1_api.register(CreateUserResource())
v1_api.register(UserResource())

urlpatterns = [url(r'^api/', include(v1_api.urls))]
