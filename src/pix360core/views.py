from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from pix360core.models import Conversion, ConversionStatus


class ConverterView(LoginRequiredMixin, TemplateView):
    """View for the converter
    """
    template_name = 'pix360core/converter.html'

@method_decorator(csrf_exempt, name='dispatch')
class StartConversionView(LoginRequiredMixin, View):
    """View for starting a conversion
    """
    def post(self, request, *args, **kwargs):
        """Handle the POST request
        """
        url = request.POST.get('url')
        title = request.POST.get('title')
        if not url:
            return JsonResponse({
                'error': 'No URL provided'
            }, status=400)
        
        conversion = Conversion.objects.create(url=url, title=title, user=request.user)
        return JsonResponse({
            'id': conversion.id
        })

class ConversionStatusView(LoginRequiredMixin, View):
    """View for getting the status of a conversion
    """
    def get(self, request, *args, **kwargs):
        """Handle the GET request
        """
        conversion = Conversion.objects.filter(id=kwargs['id']).first()
        if not conversion or not (conversion.user == request.user):
            return JsonResponse({
                'error': 'Conversion not found'
            }, status=404)
        
        response = {}

        if conversion.status == ConversionStatus.DONE:
            response['status'] = "completed"
            response['result'] = conversion.result.file.path
            response['content_type'] = conversion.result.mime_type
        elif conversion.status == ConversionStatus.FAILED:
            response['status'] = "failed"
        elif conversion.status == ConversionStatus.DOWNLOADING:
            response['status'] = "downloading"
        elif conversion.status == ConversionStatus.STITCHING:
            response['status'] = "stitching"
        else:
            response['status'] = "processing"

        return JsonResponse(response)

class ConversionLogView(LoginRequiredMixin, View):
    """View for getting the log of a conversion
    """
    def get(self, request, *args, **kwargs):
        """Handle the GET request
        """
        conversion = Conversion.objects.filter(id=kwargs['id']).first()
        if not conversion or not (conversion.user == request.user):
            return JsonResponse({
                'error': 'Conversion not found'
            }, status=404)
        
        return JsonResponse({
            'log': conversion.log
        })

class ConversionResultView(LoginRequiredMixin, View):
    """View for getting the result of a conversion
    """
    def get(self, request, *args, **kwargs):
        """Handle the GET request
        """
        conversion = Conversion.objects.filter(id=kwargs['id']).first()
        if not conversion or not (conversion.user == request.user):
            return JsonResponse({
                'error': 'Conversion not found'
            }, status=404)
        
        file = conversion.result
        if not file:
            return JsonResponse({
                'error': 'Conversion not done'
            }, status=404)

        content = file.file.read()

        response = HttpResponse(content, content_type=file.mime_type)

class ConversionListView(LoginRequiredMixin, View):
    """View for getting the list of conversions
    """
    def get(self, request, *args, **kwargs):
        """Handle the GET request
        """
        conversions = Conversion.objects.filter(user=request.user)
        return JsonResponse({
            'conversions': [{
                'id': conversion.id,
                'url': conversion.url,
                'title': conversion.title,
                'status': conversion.status,
            } for conversion in conversions]
        })

@method_decorator(csrf_exempt, name='dispatch')
class ConversionDeleteView(LoginRequiredMixin, View):
    """View for deleting a conversion
    """
    def post(self, request, *args, **kwargs):
        """Handle the POST request
        """
        conversion = Conversion.objects.filter(id=kwargs['id']).first()
        if not conversion or not (conversion.user == request.user):
            return JsonResponse({
                'error': 'Conversion not found'
            }, status=404)
        
        conversion.user = None
        conversion.save()
        
        return JsonResponse({})