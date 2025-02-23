# Company Profile Django Application

## Introduction
The Company Profile application is a comprehensive Django-based system designed to manage and track company-related information, licenses, and various application workflows. It provides a structured approach to handling company data, production details, and application processes.

## Features
1. Company profile management with detailed information
2. License tracking and management system
3. Workflow management for various application types
4. Role-based access control for different user groups
5. Comprehensive admin interface for managing records
6. Audit logging with creation and update tracking
7. File attachment handling for supporting documents
8. State-based workflow transitions

## Usage
To use the Company Profile application:

1. Ensure all migrations are applied:
```bash
python manage.py migrate
```

2. Create user groups and assign permissions using the admin interface.

3. Access the admin interface at `/admin/company_profile/` to manage records.

4. Use the following main user groups to control access:
   - pro_company_application_accept
   - pro_company_application_approve
   - company_type_entaj
   - company_type_mokhalfat
   - company_type_emtiaz
   - company_type_sageer

## User Workflows
The application implements the following workflows through the admin interface:

### Company Management Workflow
1. Create new company profiles with detailed information
2. Manage company licenses and production details
3. Track factory information and capacities
4. Handle user roles and permissions

### Application Workflow
1. Submit various application types (e.g., foreigner movement, work plans, technical reports)
2. Process applications through state transitions:
   - SUBMITTED
   - ACCEPTED
   - APPROVED
   - REJECTED
3. Handle application-specific details and attachments
4. Manage notifications and email alerts

### Key Admin Features
1. State-based application locking and permissions
2. Automatic company details creation from related forms
3. File attachment handling for supporting documents
4. Audit trail tracking for all changes
5. Custom admin views for each user group
6. CSV export functionality for license data
7. Company type-based filtering

### State Transitions
The system manages state transitions through the admin interface:
1. Applications start in SUBMITTED state
2. Can be moved to ACCEPTED state
3. Can be approved to APPROVED state
4. Can be rejected to REJECTED state
5. Previous states are locked for editing
6. Required data must be present before state transition
7. Automatic email notifications for state changes

### Security Features
1. Role-based access control
2. Company type-based data isolation
3. File upload restrictions
4. Audit logging of all changes
5. State-based permission enforcement
6. Unique constraints on company codes and licenses
