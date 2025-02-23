from django.test import RequestFactory, TestCase, Client                                                                                                                                            
from django.urls import reverse                                                                                                                                                     
from django.contrib.auth import get_user_model                                                                                                                                      
from django.contrib.auth.models import Group, Permission                                                                                                                            
from sswg.models import BasicForm, TransferRelocationFormData, CompanyDetails, SSMOData, SmrcNoObjectionData, MmAceptanceData, MOCSData, CBSData                                    
from sswg.admin import BasicFormAdmin                                                                                                                                               
                                                                                                                                                                                    
User = get_user_model()                                                                                                                                                             
                                                                                                                                                                                    
class SSWGAdminTests(TestCase):                                                                                                                                                     
    def setUp(self):                                                                                                                                                                
        self.client = Client()                                                                                                                                                      
        self.admin_user = User.objects.create_superuser(                                                                                                                            
            username='admin',                                                                                                                                                       
            password='adminpass',                                                                                                                                                   
            email='admin@example.com'                                                                                                                                               
        )                                                                                                                                                                           
        self.client.login(username='admin', password='adminpass')                                                                                                                   
                                                                                                                                                                                    
        self.basic_form = BasicForm.objects.create(                                                                                                                                 
            date='2025-01-01',                                                                                                                                                      
            sn_no='SSWG-ADMIN',                                                                                                                                                     
            created_by=self.admin_user,                                                                                                                                             
            updated_by=self.admin_user                                                                                                                                              
        )
        
        self.factory = RequestFactory()
                                                                                                                                                                                    
    def test_basic_form_admin_list_view(self):                                                                                                                                      
        url = reverse('admin:sswg_basicform_changelist')                                                                                                                            
        response = self.client.get(url)                                                                                                                                             
        self.assertEqual(response.status_code, 200)                                                                                                                                 
        self.assertContains(response, self.basic_form.sn_no)                                                                                                                        
                                                                                                                                                                                    
    def test_basic_form_admin_add_view(self):                                                                                                                                       
        url = reverse('admin:sswg_basicform_add')                                                                                                                                   
        response = self.client.get(url)                                                                                                                                             
        self.assertEqual(response.status_code, 200)                                                                                                                                 
                                                                                                                                                                                    
    def test_basic_form_admin_change_view(self):                                                                                                                                    
        url = reverse('admin:sswg_basicform_change', args=[self.basic_form.id])                                                                                                     
        response = self.client.get(url)                                                                                                                                             
        self.assertEqual(response.status_code, 200)                                                                                                                                 
        self.assertContains(response, self.basic_form.sn_no)                                                                                                                        
                                                                                                                                                                                    
    def test_basic_form_admin_delete_view(self):                                                                                                                                    
        url = reverse('admin:sswg_basicform_delete', args=[self.basic_form.id])                                                                                                     
        response = self.client.get(url)                                                                                                                                             
        self.assertEqual(response.status_code, 200)                                                                                                                                 
                                                                                                                                                                                    
    def test_basic_form_admin_save_model(self):                                                                                                                                     
        admin = BasicFormAdmin(model=BasicForm, admin_site=None)                                                                                                                    
        form = BasicForm(                                                                                                                                                           
            date='2025-01-01',                                                                                                                                                      
            sn_no='SSWG-SAVE',                                                                                                                                                      
            created_by=self.admin_user,                                                                                                                                             
            updated_by=self.admin_user                                                                                                                                              
        )
        
        request = self.factory.get('/app/managers/sswg/basicform')
        request.user = self.admin_user
        admin.save_model(request=request, obj=form, form=None, change=False)                                                                                                           
        self.assertEqual(BasicForm.objects.filter(sn_no='SSWG-SAVE').count(), 1)                                                                                                    
                                                                                                                                                                                    
    def test_basic_form_admin_get_queryset(self):                                                                                                                                   
        # Create test groups and users                                                                                                                                              
        manager_group = Group.objects.create(name='sswg_manager')                                                                                                                   
        secretary_group = Group.objects.create(name='sswg_secretary')                                                                                                               
                                                                                                                                                                                    
        manager_user = User.objects.create_user(                                                                                                                                    
            username='manager',                                                                                                                                                     
            password='managerpass'                                                                                                                                                  
        )                                                                                                                                                                           
        manager_user.groups.add(manager_group)                                                                                                                                      
                                                                                                                                                                                    
        secretary_user = User.objects.create_user(                                                                                                                                  
            username='secretary',                                                                                                                                                   
            password='secretarypass'                                                                                                                                                
        )                                                                                                                                                                           
        secretary_user.groups.add(secretary_group)                                                                                                                                  
                                                                                                                                                                                    
        # Test manager access                                                                                                                                                       
        admin = BasicFormAdmin(model=BasicForm, admin_site=None)                                                                                                                    
        request = self.client.get('/').wsgi_request                                                                                                                                 
        request.user = manager_user                                                                                                                                                 
        qs = admin.get_queryset(request)                                                                                                                                            
        self.assertEqual(qs.count(), 1)  # Manager should see all forms                                      
                                                                                                