# Gold Travel Django Application

## Introduction
The Gold Travel application is a Django-based system designed to manage and track the movement of gold and silver between states and for export purposes. It provides a structured approach to handling gold movement forms, certificates, and related documentation.

## Features
1. State-based gold movement tracking
2. Export and re-export form management
3. Silver export management
4. Role-based access control for state representatives
5. Comprehensive admin interface for managing records
6. Audit logging with creation and update tracking
7. File attachment handling for supporting documents
8. State-based workflow transitions
9. Automatic form numbering and state code generation
10. CSV export functionality for transaction data

## Usage
To use the Gold Travel application:

1. Ensure all migrations are applied:
```bash
python manage.py migrate
```

2. Create state representatives using the admin interface at `/admin/gold_travel/`

3. Use the following main user groups to control access:
   - gold_travel_manager
   - gold_travel_state
   - gold_travel_ssmo

4. Import historical data using the `import_history` management command:
```bash
python manage.py import_history
```

## User Workflows
The application implements the following workflows through the admin interface:

### Gold Movement Workflow
1. Create new gold movement forms with:
   - Owner details
   - Representative information
   - Gold weight and alloy details
   - Supporting documents
2. Process forms through state transitions:
   - DRAFT
   - SMRC
   - MINISTRY OF MINERALS
   - MINING POLICE
   - MILITARY INTELLIGENCE
   - SSMO
   - CANCELED
3. Generate movement certificates
4. Export data to CSV for reporting

### Key Admin Features
1. State-based form locking and permissions
2. Automatic form numbering with state codes
3. File attachment handling for supporting documents
4. Audit trail tracking for all changes
5. Custom admin views for each user group
6. Date-based filtering with custom date ranges
7. State-specific form filtering

### State Transitions
The system manages state transitions through the admin interface:
1. Forms start in DRAFT state
2. Can be moved through approval states
3. Can be canceled to CANCELED state
4. Previous states are locked for editing
5. Required data must be present before state transition
6. Notifications and logging for state changes

### Security Features
1. Role-based access control
2. State-specific data isolation
3. File upload restrictions
4. Audit logging of all changes
5. State-based permission enforcement
6. Unique constraints on state representatives
