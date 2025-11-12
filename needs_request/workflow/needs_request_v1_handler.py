"""
Auto-generated workflow handler for: طلب احتياجات

GENERATED CODE - Customize the implementation of each method as needed.

Generated from BPMN process: needs_request_v1
Workflow key: needs_request_v3
Version: 1
"""

from django.db import transaction
from django.utils import timezone
from typing import Dict, Any
from bpmn_workflow.engine import BaseWorkflowHandler
from bpmn_workflow.models import ProcessInstance, TaskInstance


class NeedsRequestV1Handler(BaseWorkflowHandler):
    """
    Handler for طلب احتياجات
    
    This class contains methods that are called when tasks and gateways
    are executed in the workflow. Customize the implementation to add
    your business logic.
    """
    
    workflow_key = 'needs_request_v3'
    
    def __init__(self):
        super().__init__()
        # Add any initialization code here
    
    @transaction.atomic
    def handle_dga_approval_or_rejection(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: اعتماد/رفض م.ا.ع المعنية
        BPMN ID: Activity_dga_approval_or_rejection
        Authorized groups: any authorized user
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """

        # Access the business object
        business_object = task_instance.process_instance.content_object

        is_it_related = False
        approved = data.get('approved',False)

        if not approved:          
            # Update the business object with form data
            business_object.rejection_cause = data.get('dga_rejection_cause')
            business_object.save()
        else:
            for item in business_object.items.all():
                if item.requested_item.is_it_related:
                    is_it_related = True
                    break
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
            'is_it_related': is_it_related,
            'approved': approved,
        }

    @transaction.atomic
    def handle_sd_comment(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: تعليق قسم الامداد
        BPMN ID: Activity_sd_comment
        Authorized groups: sd_pub
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        # Access the business object
        business_object = task_instance.process_instance.content_object
        
        # Update the business object with form data
        business_object.sd_comment = data.get('comment')
        business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
        }

    @transaction.atomic
    def handle_doa_comment(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: تعليق مدير إدارة الشئون الإدارية
        BPMN ID: Activity_doa_comment
        Authorized groups: doa_pub
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        
        # Access the business object
        business_object = task_instance.process_instance.content_object
        
        # Update the business object with form data
        business_object.doa_comment = data.get('comment')
        business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
        }

    @transaction.atomic
    def handle_it_comment(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: تعليق م.ا.ع للتخطيط والجودة والمعلومات
        BPMN ID: Activity_it_comment
        Authorized groups: it_pub
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        # Access the business object
        business_object = task_instance.process_instance.content_object
        
        # Update the business object with form data
        business_object.it_comment = data.get('comment')
        business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
        }

    @transaction.atomic
    def handle_dgdhra_recommendation(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: توصية م.ا.ع للموارد البشرية والإدارية
        BPMN ID: Activity_dgdhra_recommendation
        Authorized groups: dgdhra_pub
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        # Access the business object
        business_object = task_instance.process_instance.content_object
        
        # Update the business object with form data
        business_object.dgdhra_recommendation = data.get('recommendation')
        business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
        }

    @transaction.atomic
    def handle_dgfa_recommendation(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: توصية م.ا.ع للشئون المالية
        BPMN ID: Activity_dgfa_recommendation
        Authorized groups: agmfa_pub
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        # Access the business object
        business_object = task_instance.process_instance.content_object
        
        # Update the business object with form data
        business_object.dgfa_recommendation = data.get('recommendation')
        business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
        }

    @transaction.atomic
    def handle_agmfa_approval_or_rejection(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: اعتماد/رفض مساعد المدير العام
        BPMN ID: Activity_agmfa_approval_or_rejection
        Authorized groups: agmfa_approval
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        approved = data.get('approved', False)

        if not approved:
            # Access the business object
            business_object = task_instance.process_instance.content_object
            
            # Update the business object with form data
            business_object.rejection_cause = data.get('rejection_cause')
            business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
            'approved': approved,
        }

    @transaction.atomic
    def handle_gm_approval_or_rejection(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: تصديق/رفض المدير العام
        BPMN ID: Activity_gm_approval_or_rejection
        Authorized groups: gm_pub
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }
        """
        approved = data.get('approved', False)

        if not approved:
            # Access the business object
            business_object = task_instance.process_instance.content_object
            
            # Update the business object with form data
            business_object.rejection_cause = data.get('rejection_cause')
            business_object.save()
        
        # Return variables to store in the process
        return {
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
            'approved': approved,
        }

    def evaluate_0hvbla2(self, process_instance: ProcessInstance) -> str:
        """
        Gateway: هل تم الإعتماد من مدير الإدارة العامة المعنية؟
        BPMN ID: Gateway_0hvbla2
        Type: exclusive_gateway
        
        Evaluate this gateway to determine which path to take.
        
        # Available outgoing flows:
        #   1. 'نعم' -> تعليق قسم الامداد (condition: default)
        #   2. 'لا' -> رفض م.ا.ع (condition: default)

        
        Returns:
            The BPMN ID of the sequence flow to take
            
        Example:
            approved = self.get_variable(process_instance, 'approved')
            if approved:
                return 'flow_to_approval'
            else:
                return 'flow_to_rejection'
        """
        # Get process variables
        approved = self.get_variable(process_instance, 'approved')
        
        # Example routing logic:
        if not approved:
            return 'Flow_1dywxj6'  # Route to: رفض م.ا.ع
        
        # Default flow
        return 'Flow_098pt9i'

    def evaluate_0muh5ax(self, process_instance: ProcessInstance) -> str:
        """
        Gateway: هل الطلب مرتبط بأجهزة او معدات او خدمات؟
        BPMN ID: Gateway_0muh5ax
        Type: exclusive_gateway
        
        Evaluate this gateway to determine which path to take.
        
        # Available outgoing flows:
        #   1. 'نعم' -> تعليق م.ا.ع للتخطيط والجودة والمعلومات (condition: default)
        #   2. 'لا' -> توصية م.ا.ع للموارد البشرية والإدارية (condition: default)

        
        Returns:
            The BPMN ID of the sequence flow to take
            
        Example:
            approved = self.get_variable(process_instance, 'approved')
            if approved:
                return 'flow_to_approval'
            else:
                return 'flow_to_rejection'
        """
        # Get process variables
        is_it_related = self.get_variable(process_instance, 'is_it_related')
        
        # Example routing logic:
        if not is_it_related:
            return 'Flow_06tx6q4'  # Route to: لا
        
        # Default flow
        return 'Flow_12dtcv4'

    def evaluate_0ihoepi(self, process_instance: ProcessInstance) -> str:
        """
        Gateway: اعتماد مساعد المدير العام المالي والإداري؟
        BPMN ID: Gateway_0ihoepi
        Type: exclusive_gateway
        
        Evaluate this gateway to determine which path to take.
        
        # Available outgoing flows:
        #   1. 'Flow 1' -> رفض مساعد المدير العام (condition: default)
        #   2. 'Flow 2' -> تصديق/رفض المدير العام (condition: default)

        
        Returns:
            The BPMN ID of the sequence flow to take
            
        Example:
            approved = self.get_variable(process_instance, 'approved')
            if approved:
                return 'flow_to_approval'
            else:
                return 'flow_to_rejection'
        """
        # Get process variables
        approved = self.get_variable(process_instance, 'approved')
        
        # Example routing logic:
        if not approved:
            return 'Flow_1va9uk3'  # Route to: رفض مساعد المدير العام
                
        # Default flow
        return 'Flow_1bgg2f7'

    def evaluate_1mgjqv0(self, process_instance: ProcessInstance) -> str:
        """
        Gateway: تصديق المدير العام؟
        BPMN ID: Gateway_1mgjqv0
        Type: exclusive_gateway
        
        Evaluate this gateway to determine which path to take.
        
        # Available outgoing flows:
        #   1. 'Flow 1' -> تم التصديق (condition: default)
        #   2. 'Flow 2' -> رفض المدير العام (condition: default)

        
        Returns:
            The BPMN ID of the sequence flow to take
            
        Example:
            approved = self.get_variable(process_instance, 'approved')
            if approved:
                return 'flow_to_approval'
            else:
                return 'flow_to_rejection'
        """
        # Get process variables
        approved = self.get_variable(process_instance, 'approved')
        
        # Example routing logic:
        if not approved:
            return 'Flow_0bio06b'  # Route to: رفض المدير العام
                
        # Default flow
        return 'Flow_085if4e' # Route to: تم التصديق
