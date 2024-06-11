import base64
from django.shortcuts import render
from django.views import View
from django.core.files.base import ContentFile
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin

from help_request.forms import HelpForm

class HelpView(LoginRequiredMixin,View):
    def post(self,request):
        updated_request = request.POST.copy()

        img = updated_request.get('issue_img')
        format, imgstr = img.split(';base64,') 
        ext = format.split('/')[-1] 
        img = ContentFile(base64.b64decode(imgstr), name=f'{self.request.user.id}.' + ext)
        updated_request.update({'issue_img': img})

        form = HelpForm(updated_request)
        
        if form.is_valid():
            self.object = form.save(commit=False)            
            self.object.created_by = self.request.user
            self.object.save()

            return JsonResponse({"message":"record added."})
        
        return JsonResponse({"errors":form.errors.as_json(escape_html=True)})
