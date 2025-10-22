import React, { useState, useEffect } from 'react';
import { csrftoken } from './utils.js';
import Navbar from './components/Navbar.js';
import Dashboard from './components/Dashboard.js';
import RegistrationList from './components/RegistrationList.js';
import FamilyList from './components/FamilyList.js';
import MoahilList from './components/MoahilList.js';
import BankAccountList from './components/BankAccountList.js';
import EmployeeData from './components/EmployeeData.js';

export default function App() {
    const [user, setUser] = useState(null);
    const [view, setView] = useState('dashboard');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/bot/api/login-status/', { credentials: 'same-origin' })
            .then(res => {
                if (!res.ok) throw new Error('Not authenticated');
                return res.json();
            })
            .then(data => {
                if (data.is_authenticated) {
                    setUser(data);
                } else {
                    window.location.href = '/admin/login/?next=/bot/';
                }
            })
            .catch(() => {
                window.location.href = '/admin/login/?next=/bot/';
            })
            .finally(() => setLoading(false));
    }, []);

    const logout = () => {
        fetch('/bot/api/logout/', { 
            method: 'POST', 
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(() => window.location.href = '/admin/login/');
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <span className="loading loading-spinner loading-lg"></span>
            </div>
        );
    }

    if (!user) return null;

    const isManager = user.groups.includes('hr_manager') || user.groups.includes('hr_manpower') || user.is_superuser;
    const isEmployee = user.groups.includes('hr_employee');

    return (
        <div className="min-h-screen">
            <Navbar user={user} logout={logout} setView={setView} />
            <div className="container mx-auto p-4">
                {view === 'dashboard' && <Dashboard user={user} setView={setView} isManager={isManager} isEmployee={isEmployee} />}
                {view === 'registrations' && <RegistrationList user={user} isManager={isManager} />}
                {view === 'families' && <FamilyList user={user} isManager={isManager} isEmployee={isEmployee} />}
                {view === 'moahil' && <MoahilList user={user} isManager={isManager} isEmployee={isEmployee} />}
                {view === 'bank_accounts' && <BankAccountList user={user} isManager={isManager} isEmployee={isEmployee} />}
                {view === 'employee_data' && <EmployeeData user={user} />}
            </div>
        </div>
    );
}
