import React, { useState, useEffect } from 'react';
import { csrftoken, STATE_DRAFT, STATE_ACCEPTED, STATE_REJECTED, getStateBadge } from '../utils.js';
import BankAccountForm from './BankAccountForm.js';

export default function BankAccountList({ user, isManager, isEmployee }) {
    const [bankAccounts, setBankAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [stateFilter, setStateFilter] = useState(STATE_DRAFT);

    const loadData = () => {
        setLoading(true);
        fetch('/bot/api/bank-accounts/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                setBankAccounts(data.bank_accounts);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        loadData();
    }, []);

    const filteredBankAccounts = bankAccounts.filter(b => {
        const matchesSearch = searchTerm === '' ||
            b.employee.toLowerCase().includes(searchTerm.toLowerCase()) ||
            String(b.employee_code).includes(searchTerm) ||
            b.bank.includes(searchTerm) ||
            b.account_no.includes(searchTerm);
        const matchesState = stateFilter === '' || b.state === stateFilter;
        return matchesSearch && matchesState;
    });

    const accept = (id) => {
        if (!confirm('هل أنت متأكد من قبول هذا الطلب؟')) return;
        
        fetch(`/bot/api/bank-accounts/${id}/accept/`, { 
            method: 'POST', 
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(res => res.json())
        .then(() => {
            alert('تم قبول الطلب بنجاح');
            loadData();
        })
        .catch(() => alert('حدث خطأ'));
    };

    const reject = (id) => {
        if (!confirm('هل أنت متأكد من رفض هذا الطلب؟')) return;
        
        fetch(`/bot/api/bank-accounts/${id}/reject/`, { 
            method: 'POST', 
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(res => res.json())
        .then(() => {
            alert('تم رفض الطلب');
            loadData();
        })
        .catch(() => alert('حدث خطأ'));
    };

    if (loading) {
        return <div className="flex justify-center p-8"><span className="loading loading-spinner loading-lg"></span></div>;
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">الحسابات البنكية</h2>
                {isEmployee && (
                    <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                        {showForm ? 'إلغاء' : 'إضافة حساب جديد'}
                    </button>
                )}
            </div>

            <div className="mb-4 flex gap-4">
                <input type="text" placeholder="بحث..." className="input input-bordered" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                <select className="select select-bordered" value={stateFilter} onChange={(e) => setStateFilter(e.target.value === '' ? '' : parseInt(e.target.value))}>
                    <option value="">جميع الحالات</option>
                    <option value={STATE_DRAFT}>مسودة</option>
                    <option value={STATE_ACCEPTED}>مقبول</option>
                    <option value={STATE_REJECTED}>مرفوض</option>
                </select>
            </div>

            {showForm && isEmployee && (
                <BankAccountForm onSuccess={() => { setShowForm(false); loadData(); }} />
            )}
            
            <div className="overflow-x-auto mt-4">
                <table className="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th>كود الموظف</th>
                            <th>الموظف</th>
                            <th>البنك</th>
                            <th>رقم الحساب</th>
                            <th>نشط</th>
                            <th>الحالة</th>
                            {isManager && <th>الإجراءات</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {filteredBankAccounts.map(b => (
                            <tr key={b.id}>
                                <td>{b.employee_code}</td>
                                <td>{b.employee}</td>
                                <td>{b.bank}</td>
                                <td>{b.account_no}</td>
                                <td>{b.active ? <span className="badge badge-success">نعم</span> : <span className="badge badge-error">لا</span>}</td>
                                <td>{getStateBadge(b.state)}</td>
                                {isManager && (
                                    <td>
                                        {b.state === STATE_DRAFT && (
                                            <div className="flex gap-2">
                                                <button className="btn btn-success btn-sm" onClick={() => accept(b.id)}>قبول</button>
                                                <button className="btn btn-error btn-sm" onClick={() => reject(b.id)}>رفض</button>
                                            </div>
                                        )}
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filteredBankAccounts.length === 0 && (
                    <div className="text-center p-8 text-gray-500">لا توجد بيانات</div>
                )}
            </div>
        </div>
    );
}
