import csv
import codecs
from django.shortcuts import render,get_object_or_404
from django.http import Http404, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import cache
from django.core.exceptions import PermissionDenied

from company_profile.models import LkpState
from traditional_app.hr_payroll import T3agoodPayroll
from traditional_app.models import MONTH_CHOICES

class UserPermissionMixin(UserPassesTestMixin):
    user_groups = []

    def test_func(self):
        return self.request.user.groups.filter(name__in=self.user_groups).exists()

class PayrollT3agood(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = int(self.request.GET['month'])
        state = get_object_or_404(LkpState,pk=self.request.GET['state'])
        format = self.request.GET.get('format',None)
        data = []

        try:
            user_state = self.request.user.traditional_app_user.state
            # print(user_state ,state)
            if user_state != state:
                raise Exception
        except:
            raise Http404

        
        payroll = T3agoodPayroll(year,month)
        header = ['الرمز','الموظف','المرتب الاساسي','غلاء معيشة','بدل السكن','بدل ترحيل','طبيعة عمل','بدل لبن','بدل علاج','اجمالي المرتب','تأمين اجتماعي','ضريبة','دمغة','صافي الإستحقاق',]
        summary_list = []

        for (emp,badalat,khosomat,) in payroll.employees_payroll_from_db(state=state):
            badalat_list = [b[1] for b in badalat]
            khsomat_list = [k[1] for k in khosomat]
            l = [emp.employee.id,emp.employee.name,] + badalat_list + khsomat_list
            data.append(l)

            for idx,s in enumerate(badalat_list):
                try:
                    summary_list[idx] += badalat_list[idx]
                except IndexError:
                    summary_list.insert(idx,badalat_list[idx])

            for idx2,s in enumerate(khsomat_list):
                x = idx2+idx+1
                try:
                    summary_list[x] += khsomat_list[idx2]
                except IndexError:
                    summary_list.insert(x,khsomat_list[idx2])

        summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'payroll'
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{state.name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response, quoting=csv.QUOTE_ALL)
            writer.writerow(header)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            template_name = 'traditional_app/payroll.html'
            context = {
                'title':'كشف مرتبات',
                'state':state.name,
                'header':header,
                'data': data,
                'summary':summary_list,
                'month':MONTH_CHOICES[month],
                'year':year,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response
    