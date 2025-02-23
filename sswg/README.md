 # SSWG Django Application

 ## Introduction
 The SSWG (Sudanese Single Window Gateway) application is a Django-based system designed to manage and track the workflow of security-related forms and processes. It provides a structured approach to handling various stages of security approvals and documentation.

 ## Features
 1. Multi-stage workflow management with state transitions
 2. Role-based access control for different user groups
 3. Integrated file attachments for supporting documents
 4. Automatic data synchronization between related models 
 5. Comprehensive admin interface for managing records
 6. Audit logging with creation and update tracking

 ## Usage
 To use the SSWG application:
 1. Add app to setting.py
 2. Ensure all migrations are applied:
 ```bash
 python manage.py migrate
```

 3. Create user groups and assign permissions using the create_app_groups management command.
 4. Access the admin interface at /admin/sswg/ to manage records.
 5. Use the following user groups to control access:
     * sswg_manager
     * sswg_secretary
     * sswg_economic_security
     * sswg_ssmo
     * sswg_smrc
     * sswg_mm
     * sswg_mocs
     * sswg_military_intelligence 
     * sswg_cbs 
     * sswg_custom_force


 ### User Workflows

The application implements the following workflows through the admin interface:

  #### Basic Form Workflow  

  1. Secretary creates a new BasicForm 
  2. Economic Security reviews and confirms 
  3. SSMO adds measurements and certificate
  4. SMRC provides no-objection documentation
  5. Ministry of Minerals provides acceptance
  6. Military Intelligence reviews
  7. Ministry of Commerce and Supply processes  
  8. Central Bank of Sudan handles financial aspects 
  9. Custom Force completes final checks

  #### Key Admin Features

 1. State-based form locking and permissions 
 2. Automatic company details creation from related forms 
 3. File attachment handling for supporting documents
 4. Audit trail tracking for all changes
 5. Custom admin views for each user group 

### State Transitions

The system manages state transitions through the admin interface:

 1. Users can only move forms to the next state 
 2. Previous states are locked for editing 
 3. Required data must be present before state transition 
 4. Notifications and logging for state changes 

Security Features

 1. Role-based access control
 2. Data validation at each state 
 3. File upload restrictions 
 4. Audit logging of all changes
 5. State-based permission enforcement


