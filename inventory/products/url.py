from django.urls import path

from .views import ProductSearchView,GenerateDummyProductsView,ActiveProductsView,UserDataView,ProductUpdateView,WebhookReceiver

urlpatterns = [
    path('products/search', ProductSearchView.as_view(), name='ProductSearchView'),
    path('genaratedummyProducts', GenerateDummyProductsView.as_view(), name='GenerateDummyProductsView'),
    path('ActiveProductsView', ActiveProductsView.as_view(), name='ActiveProductsView'),
    path('UserDataView', UserDataView.as_view(), name='UserDataView'),
    path('ProductUpdateView', ProductUpdateView.as_view(), name='ProductUpdateView'),

     path('webhook', WebhookReceiver.as_view(), name='webhook-receiver'),


]