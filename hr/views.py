import csv
import codecs
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from django.utils.translation import gettext_lazy as _
from django.utils import cache
from django.views.defaults import bad_request
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from hr.models import Drajat3lawat, EmployeeBankAccount, PayrollMaster
from hr.payroll import M2moriaSheet, MobasharaSheet, Payroll,Mokaf2Sheet

SHOW_CSV_TOTAL = False

def get_employee_accounts():
    data = {}
    for emp in EmployeeBankAccount.objects.filter(active=True).prefetch_related("employee"):
        id = emp.employee.id
        data[id] = (emp.account_no,emp.get_bank_display())
        # print(f'id: {id}, account_no: {data[id]}')

    return data

class UserPermissionMixin(UserPassesTestMixin):
    user_groups = []

    def test_func(self):
        return self.request.user.groups.filter(name__in=self.user_groups).exists()

class Badalat(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        data = []
        
        payroll = Payroll(year,month)
        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','ابتدائي','غلاء معيشة','اساسي','طبيعة عمل','تمثيل','مهنة','معادن','مخاطر','عدوى','اجتماعية قسيمة','اجتماعية اطفال','مؤهل','شخصية','اجمالي المرتب']
        summary_list = []

        for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
            badalat_list = [round(b[1],2) for b in badalat]
            l = [emp.code,emp.name,Drajat3lawat.DRAJAT_CHOICES[draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[alawa_sanawia]] + badalat_list
            data.append(l)

            for idx,s in enumerate(badalat_list):
                try:
                    summary_list[idx] += badalat_list[idx]
                except IndexError:
                    summary_list.insert(idx,badalat_list[idx])

        summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'allowances'
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            template_name = 'hr/badalat.html'
            context = {
                'title':'كشف البدلات',
                'header':header,
                'data': data,
                'summary':summary_list,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response
    
class Khosomat(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        payroll_master = None

        try:
            payroll_master = PayrollMaster.objects.get(year=year,month=month)
        except PayrollMaster.DoesNotExist as e:
            bad_request(self.request,e)
        
        payroll = Payroll(year,month)

        header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','تأمين اجتماعي','معاش','الصندوق','الضريبة','دمغه','إجمالي الإستقطاعات الأساسية',]

        if payroll_master.enable_sandog_kahraba:
            header += ['صندوق كهربائيه',]

        header += ['السلفيات',]

        if payroll_master.khasm_salafiat_elsandog_min_elomoratab:
            header += ['سلفيات الصندوق',]

        if payroll_master.enable_youm_algoat_almosalaha:
            header += ['استقطاع القوات المسلحه',]

        header += ['الزكاة','إجمالي الإستقطاعات السنوية','خصومات - جزاءات','إجمالي الإستقطاع الكلي','صافي الإستحقاق']

        summary_list = []

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                l = [emp.code,emp.name,bank,bnk_no,round(khosomat.safi_alisti7gag,2)]
                data.append(l)
        else:
            template_name = 'hr/khosomat.html'

            for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in payroll.all_employees_payroll_from_db():
                khosomat_list = [round(k[1],2) for k in khosomat]
                l = [emp.code,emp.name,Drajat3lawat.DRAJAT_CHOICES[draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[alawa_sanawia]] + khosomat_list
                data.append(l)

                for idx,s in enumerate(khosomat_list):
                    try:
                        summary_list[idx] += khosomat_list[idx]
                    except IndexError:
                        summary_list.insert(idx,khosomat_list[idx])

            summary_list = [round(s,2) for s in summary_list]

        if format == 'csv':
            sheet_name = 'net'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف الخصومات',
                'header':header,
                'data': data,
                'summary':summary_list,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

class Mobashara(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        
        mobashara = MobasharaSheet(year,month)

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for emp_mobashara in mobashara.all_employees_mobashara_from_db().prefetch_related("employee__mosama_wazifi"):
                emp = emp_mobashara.employee
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                total = (emp_mobashara.amount+emp_mobashara.amount_m2moria+emp_mobashara.amount_e3asha)
                l = [emp.code,emp.name,bank,bnk_no,round(total,2)]
                data.append(l)
        else:
            template_name = 'hr/mobashara.html'
            header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','المسمى الوظيفي','الاستحقاق اليومي','ايام الشهر','ايام المباشرة','ايام الاجازة','ايام التكليف','طوارئ','مأمورية','إعاشة','صافي الاستحقاق']

            summary_list = []

            for emp_mobashara in mobashara.all_employees_mobashara_from_db().prefetch_related("employee__mosama_wazifi"):
                emp = emp_mobashara.employee
                total = (emp_mobashara.amount+emp_mobashara.amount_m2moria+emp_mobashara.amount_e3asha)
                l = [emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),emp.mosama_wazifi.name,emp_mobashara.rate,emp_mobashara.no_days_month,emp_mobashara.no_days_mobashara,emp_mobashara.no_days_2jazaa,emp_mobashara.no_days_taklif,emp_mobashara.amount,emp_mobashara.amount_m2moria,emp_mobashara.amount_e3asha,total]
                data.append(l)

        if format == 'csv':
            sheet_name = 'mobashara'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف المباشرة',
                'header':header,
                'data': data,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

class Mokaf2(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []

        try:
            payroll_master = PayrollMaster.objects.get(year=year,month=month)
        except PayrollMaster.DoesNotExist as e:
            bad_request(self.request,e)

        mokaf2 = Mokaf2Sheet(year,month)

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for emp_mokaf2 in mokaf2.all_employees_mokaf2_from_db():
                emp = emp_mokaf2.employee
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                l = [emp.code,emp.name,bank,bnk_no,round(emp_mokaf2.safi_2l2sti7gag,2)]
                data.append(l)
        else:
            template_name = 'hr/mokaf2.html'
            header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','اجمالي المرتب','الضريبة','الدمغة',]

            if not payroll_master.khasm_salafiat_elsandog_min_elomoratab:
                header += ['سلفيات الصندوق',]

            header += ['صافي الاستحقاق',]

            summary_list = []

            for emp_mokaf2 in mokaf2.all_employees_mokaf2_from_db():
                mokaf2_list = [round(k[1],2) for k in emp_mokaf2]
                emp = emp_mokaf2.employee
                l = [emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),]+mokaf2_list #round(emp_mokaf2.ajmali_2lmoratab,2),round(emp_mokaf2.dariba,2),emp_mokaf2.damga,]
                #if not payroll_master.khasm_salafiat_elsandog_min_elomoratab:
                #    l += [round(emp_mokaf2.salafiat_sandog,2),]
                #l +=[round(emp_mokaf2.safi_2l2sti7gag,2),]

                data.append(l)

                for idx,s in enumerate(mokaf2_list):
                    try:
                        summary_list[idx] += mokaf2_list[idx]
                    except IndexError:
                        summary_list.insert(idx,mokaf2_list[idx])

            summary_list = [round(s,2) for s in summary_list]


        if format == 'csv':
            sheet_name = 'bonace'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            if SHOW_CSV_TOTAL:
                data.append(['-','-','-','-',]+summary_list)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف المكافأة',
                'header':header,
                'data': data,
                'summary':summary_list,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response

class M2moria(LoginRequiredMixin,UserPermissionMixin,View):
    user_groups = ['hr_manager','hr_payroll']
    def get(self,*args,**kwargs):
        year = self.request.GET['year']
        month = self.request.GET['month']
        format = self.request.GET.get('format',None)
        bank_sheet = self.request.GET.get('bank_sheet',False)
        data = []
        
        m2moria = M2moriaSheet(year,month)

        if bank_sheet:
            template_name = 'hr/bank.html'
            header = ['الرمز','الموظف','البنك','رقم الحساب','صافي الاستحقاق']
            emp_accounts = get_employee_accounts()

            for emp_m2moria in m2moria.all_employees_m2moria_from_db():
                emp = emp_m2moria.employee
                try:
                    bnk_no,bank = emp_accounts[emp.id] #employeeemp.employeebankaccount_set.get(active=True).account_no
                except KeyError:
                    bnk_no,bank = ('-','-')

                l = [emp.code,emp.name,bank,bnk_no,round(emp_m2moria.safi_2l2sti7gag,2)]
                data.append(l)
        else:
            template_name = 'hr/mokaf2.html'

            header = ['الرمز','الموظف','الدرجة الوظيفية','العلاوة','اجمالي المرتب','اجر اليوم','عدد الايام','الدمغة','صافي الاستحقاق']

            summary_list = []

            for emp_m2moria in m2moria.all_employees_m2moria_from_db():
                emp = emp_m2moria.employee
                l = [emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),emp_m2moria.ajmali_2lmoratab,emp_m2moria.ajmali_2lmoratab/30*1.5,emp_m2moria.no_days,emp_m2moria.damga,emp_m2moria.safi_2l2sti7gag]
                data.append(l)

        if format == 'csv':
            sheet_name = 'm2moria'
            # print(f'attachment; filename="{sheet_name}_{month}_{year}.csv"')
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{sheet_name}_{month}_{year}.csv"'},
            )

            # BOM
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(header)

            for r in data:
                writer.writerow(r)

            cache.patch_cache_control(response, max_age=0)
            return response

        else:
            context = {
                'title':'كشف المأمورية',
                'header':header,
                'data': data,
            }

            response = render(self.request,template_name,context)
            cache.patch_cache_control(response, max_age=0)
            return response
