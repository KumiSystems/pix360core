from django.urls import path

from .views import ConverterView, StartConversionView, ConversionStatusView, ConversionLogView, ConversionListView, ConversionDeleteView, ConversionResultView, ConversionRetryView, ConversionDownloadView

urlpatterns = [
    path('', ConverterView.as_view(), name='converter'),
    path('start', StartConversionView.as_view(), name='conversion_start'),
    path('status/<uuid:id>', ConversionStatusView.as_view(), name='conversion_status'),
    path('log/<uuid:id>', ConversionLogView.as_view(), name='conversion_log'),
    path('list', ConversionListView.as_view(), name='conversion_list'),
    path('delete/<uuid:id>', ConversionDeleteView.as_view(), name='conversion_delete'),
    path('result/<uuid:id>', ConversionResultView.as_view(), name='conversion_result'),
    path('retry/<uuid:id>', ConversionRetryView.as_view(), name='conversion_retry'),
    path('download/<uuid:id>', ConversionDownloadView.as_view(), name='conversion_download'),
]