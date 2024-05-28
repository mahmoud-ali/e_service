import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.mixins import LoginRequiredMixin

from hr.models import Drajat3lawat
from hr.payroll import Payroll

class Badalat(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        data = []
        
        payroll = Payroll(year,month)
        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','ابتدائي','غلاء معيشة','اساسي','طبيعة عمل','تمثيل','مهنة','معادن','مخاطر','عدوى','اجتماعية قسيمة','اجتماعية اطفال','مؤهل','شخصية','اجمالي المرتب']
        summary_list = []

        for (emp,badalat,khosomat) in payroll.all_employees_payroll_from_db():
            badalat_list = [round(b[1],2) for b in badalat]
            l = [emp.code,emp.name,Drajat3lawat.DRAJAT_CHOICES[emp.draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[emp.alawa_sanawia]] + badalat_list
            data.append(l)

            for idx,s in enumerate(badalat_list):
                try:
                    summary_list[idx] += badalat_list[idx]
                except IndexError:
                    summary_list.insert(idx,badalat_list[idx])

        summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'allowance'
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            writer = csv.writer(response)
            writer.writerow(header)

            data.append(['-','-','-',]+summary_list)
            for r in data:
                writer.writerow(r)

            return response

        else:
            template_name = 'hr/badalat.html'
            context = {
                'title':'كشف البدلات',
                'header':header,
                'data': data,
                'summary':summary_list,
            }
            return render(self.request,template_name,context)
    
class Khosomat(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        data = []
        
        payroll = Payroll(year,month)
        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','تأمين اجتماعي','معاش','الصندوق','الضريبة','دمغه','إجمالي الإستقطاعات الأساسية','صندوق كهربائيه','السلفيات','استقطاع القوات المسلحه','الزكاة','إجمالي الإستقطاعات السنوية','خصومات - جزاءات','إجمالي الإستقطاع الكلي','صافي الإستحقاق']
        summary_list = []

        for (emp,badalat,khosomat) in payroll.all_employees_payroll_from_db():
            khosomat_list = [round(k[1],2) for k in khosomat]
            l = [emp.code,emp.name,Drajat3lawat.DRAJAT_CHOICES[emp.draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[emp.alawa_sanawia]] + khosomat_list
            data.append(l)

            for idx,s in enumerate(khosomat_list):
                try:
                    summary_list[idx] += khosomat_list[idx]
                except IndexError:
                    summary_list.insert(idx,khosomat_list[idx])

        summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'deduction'
            print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            writer = csv.writer(response)
            writer.writerow(header)

            data.append(['-','-','-',]+summary_list)
            for r in data:
                writer.writerow(r)

            return response

        else:
            template_name = 'hr/khosomat.html'
            context = {
                'title':'كشف الخصومات',
                'header':header,
                'data': data,
                'summary':summary_list,
            }
            return render(self.request,template_name,context)