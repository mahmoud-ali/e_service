from django.shortcuts import render
from django.views.generic import View

from hr.models import Drajat3lawat
from hr.payroll import Payroll

class Badalat(View):
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        data = []
        
        payroll = Payroll(year,month)

        seq = 0
        summary_list = []
        for (emp,badalat,khosomat) in payroll.all_employees_payroll_from_db():
            seq +=1
            badalat_list = [round(b[1],2) for b in badalat]
            l = [seq,emp.name,Drajat3lawat.DRAJAT_CHOICES[emp.draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[emp.alawa_sanawia]] + badalat_list
            data.append(l)

            for idx,s in enumerate(badalat_list):
                try:
                    summary_list[idx] += badalat_list[idx]
                except IndexError:
                    summary_list.insert(idx,badalat_list[idx])

        template_name = 'hr/badalat.html'
        context = {
            'title':'كشف البدلات',
            'header':['م','الموظف','الدرجة الوظيفية','العلاوة','ابتدائي','غلاء معيشة','اساسي','طبيعة عمل','تمثيل','مهنة','معادن','مخاطر','عدوى','اجتماعية-قسيمة','اجتماعية اطفال','مؤهل','شخصية','اجمالي المرتب'],
            'data': data,
            'summary':[round(s,2) for s in summary_list],
        }
        return render(self.request,template_name,context)
    
class Khosomat(View):
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        data = []
        
        payroll = Payroll(year,month)

        seq = 0
        summary_list = []
        for (emp,badalat,khosomat) in payroll.all_employees_payroll_from_db():
            seq +=1
            khosomat_list = [round(k[1],2) for k in khosomat]
            l = [seq,emp.name,Drajat3lawat.DRAJAT_CHOICES[emp.draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[emp.alawa_sanawia]] + khosomat_list
            data.append(l)

            for idx,s in enumerate(khosomat_list):
                try:
                    summary_list[idx] += khosomat_list[idx]
                except IndexError:
                    summary_list.insert(idx,khosomat_list[idx])

        template_name = 'hr/khosomat.html'
        context = {
            'title':'كشف الخصومات',
            'header':['م','الموظف','الدرجة الوظيفية','العلاوة','تأمين اجتماعي','معاش','الصندوق','الضريبة','دمغه','إجمالي الإستقطاعات الأساسية','صندوق كهربائيه','السلفيات','استقطاع يوم اجمالي لصالح دعم القوات المسلحه','الزكاة','إجمالي الإستقطاعات السنوية','خصومات - جزاءات','إجمالي الإستقطاع الكلي','صافي الإستحقاق'],
            'data': data,
            'summary':[round(s,2) for s in summary_list],
        }
        return render(self.request,template_name,context)