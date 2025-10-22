import React, { useState, useEffect } from 'react';
import { csrftoken, STATE_DRAFT, getStateBadge } from '../utils.js';

export default function RegistrationList({ user, isManager }) {
    const [registrations, setRegistrations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    const loadData = () => {
        setLoading(true);
        fetch('/bot/api/registrations/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                setRegistrations(data.registrations);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        loadData();
    }, []);

    const filteredRegistrations = registrations.filter(r =>
        searchTerm === '' ||
        r.employee.toLowerCase().includes(searchTerm.toLowerCase()) ||
        String(r.employee_code).includes(searchTerm) ||
        r.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.phone.includes(searchTerm)
    );

    const accept = (id) => {
        if (!confirm('هل أنت متأكد من قبول هذا الطلب؟')) return;
        
        fetch(`/bot/api/registrations/${id}/accept/`, { 
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
        
        fetch(`/bot/api/registrations/${id}/reject/`, { 
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

    const resetPassword = (id) => {
        if (!confirm('هل أنت متأكد من إعادة تعيين كلمة المرور؟')) return;
        
        fetch(`/bot/api/registrations/${id}/reset-password/`, { 
            method: 'POST', 
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
        .then(res => res.json())
        .then(() => {
            alert('تم إعادة تعيين كلمة المرور بنجاح');
        })
        .catch(() => alert('حدث خطأ'));
    };

    if (loading) {
        return <div className="flex justify-center p-8"><span className="loading loading-spinner loading-lg"></span></div>;
    }

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">طلبات التسجيل</h2>
            
            <div className="mb-4">
                <input type="text" placeholder="بحث..." className="input input-bordered" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
            </div>
            
            <div className="overflow-x-auto">
                <table className="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th>كود الموظف</th>
                            <th>الموظف</th>
                            <th>الاسم</th>
                            <th>الهاتف</th>
                            <th>تاريخ الإنشاء</th>
                            <th>الحالة</th>
                            {isManager && <th>الإجراءات</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {filteredRegistrations.map(r => (
                            <tr key={r.id}>
                                <td>{r.employee_code}</td>
                                <td>{r.employee}</td>
                                <td>{r.name}</td>
                                <td>{r.phone}</td>
                                <td>{r.created_at}</td>
                                <td>{getStateBadge(r.state)}</td>
                                {isManager && (
                                    <td>
                                        <div className="flex gap-2">
                                            {r.state === STATE_DRAFT && (
                                                <>
                                                    <button className="btn btn-success btn-sm" onClick={() => accept(r.id)}>قبول</button>
                                                    <button className="btn btn-error btn-sm" onClick={() => reject(r.id)}>رفض</button>
                                                </>
                                            )}
                                            <button className="btn btn-info btn-sm" onClick={() => resetPassword(r.id)}>إعادة تعيين</button>
                                        </div>
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filteredRegistrations.length === 0 && (
                    <div className="text-center p-8 text-gray-500">لا توجد طلبات</div>
                )}
            </div>
        </div>
    );
}
