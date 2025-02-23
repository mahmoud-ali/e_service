 # Dabtiaat Altaedin Django Application    
  
 ## Introduction                      
 The Dabtiaat Altaedin application is a Django-based system designed to manage and track gold-related transactions and state-level financial records. It provides a structured approach to handling gold weight, pricing, and distribution calculations across different states. 
  
 ## Features                          
1. State-based transaction management
2. Automatic calculation of financial distributions
3. Role-based access control for state representatives
4. Comprehensive admin interface for managing records
5. Audit logging with creation and update tracking
6. CSV export functionality for transaction data
7. State-specific permissions and workflows
  
 ## Usage                             
 To use the Dabtiaat Altaedin application: 
  
 1. Ensure all migrations are applied:
 ```bash                              
 python manage.py migrate             
```

 2. Create state representatives using the admin interface at /admin/dabtiaat_altaedin/             
 3. Use the following user groups to control access:                            
    • dabtiaat_altaedin_manager       
    • dabtiaat_altaedin_state         
 4. Import historical data using the import_history management command:         

  
 ```bash                              
 python manage.py shell             
```
then:
 ```python                              
from dabtiaat_altaedin.data import load_data
load_data.import_history()
```
## User Workflows  
The application implements the following workflows through the admin interface:

### Transaction Management Workflow
 1. State representatives create new gold transactions                          
 2. System automatically calculates:   
    • Koli amount (22% of total value)
    • Al3wayid Aljalila amount (10%)  
    • Alhafiz amount (10%)            
    • Alniyaba amount (2%)            
    • SMRC amount (10% of Alhafiz)    
    • State amount (10% of Alhafiz)   
    • Police amount (10% of Alhafiz)  
    • Amn amount (10% of Alhafiz)     
    • Riasat Alquat Aldaabita amount (10% of Alhafiz)                          
    • Alquat Aldaabita amount (50% of Alhafiz)                                 
 3. Managers can confirm transactions and change states                         
 4. All transactions are locked after confirmation                              
 5. Data can be exported to CSV for reporting 

### Key Admin Features

1. State-based transaction locking and permissions                             
2. Automatic financial calculations   
3. File attachment handling for supporting documents                           
4. Audit trail tracking for all changes    
5. Custom admin views for each user group  
6. Date-based filtering with custom date ranges                                
7. State-specific transaction filtering    

### State Transitions

The system manages state transitions through the admin interface:              

1. Transactions start in DRAFT state  
2. Can be moved to SMRC state for confirmation                                 
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
