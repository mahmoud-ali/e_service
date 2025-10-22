import React, { useState, useEffect } from 'react';
import { csrftoken, STATE_DRAFT, STATE_ACCEPTED, STATE_REJECTED, getStateInfo } from '../utils.js';
import FamilyForm from './FamilyForm.js';

function StateBadge({ state }) {
    const info = getStateInfo(state);
    return <span className={`badge ${info.className}`}>{info.label}</span>;
}

export default function FamilyList({ user, isManager, isEmployee }) {
    const [families, setFamilies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [stateFilter, setStateFilter] = useState(STATE_DRAFT);

    const loadData = () => {
        setLoading(true);
        fetch('/bot/api/families/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                setFamilies(data.families);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        loadData();
    }, []);

    const filteredFamilies = families.filter(f => {
        const matchesSearch = searchTerm === '' ||
            f.employee.toLowerCase().includes(searchTerm.toLowerCase()) ||
            String(f.employee_code).includes(searchTerm) ||
            f.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            f.relation.includes(searchTerm);
        const matchesState = stateFilter === '' || f.state === stateFilter;
        return matchesSearch && matchesState;
    });

    const accept = (id) => {
        if (!confirm('هل أنت متأكد من قبول هذا الطلب؟')) return;
        
        fetch(`/bot/api/families/${id}/accept/`, { 
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
        
        fetch(`/bot/api/families/${id}/reject/`, { 
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
                <h2 className="text-2xl font-bold">بيانات العائلة</h2>
                {isEmployee && (
                    <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                        {showForm ? 'إلغاء' : 'إضافة فرد جديد'}
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
                <FamilyForm onSuccess={() => { setShowForm(false); loadData(); }} />
            )}
            
            <div className="overflow-x-auto mt-4">
                <table className="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th>كود الموظف</th>
                            <th>الموظف</th>
                            <th>الاسم</th>
                            <th>العلاقة</th>
                            <th>تاريخ الإضافة</th>
                            <th>المرفق</th>
                            <th>الحالة</th>
                            {isManager && <th>الإجراءات</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {filteredFamilies.map(f => (
                            <tr key={f.id}>
                                <td>{f.employee_code}</td>
                                <td>{f.employee}</td>
                                <td>{f.name}</td>
                                <td>{f.relation}</td>
                                <td>{f.tarikh_el2dafa}</td>
                                <td>
                                    {f.attachement_file && (
                                        <a href={f.attachement_file} target="_blank" className="btn btn-sm btn-ghost">عرض</a>
                                    )}
                                </td>
                                <td><StateBadge state={f.state} /></td>
                                {isManager && (
                                    <td>
                                        {f.state === STATE_DRAFT && (
                                            <div className="flex gap-2">
                                                <button className="btn btn-success btn-sm" onClick={() => accept(f.id)}>قبول</button>
                                                <button className="btn btn-error btn-sm" onClick={() => reject(f.id)}>رفض</button>
                                            </div>
                                        )}
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filteredFamilies.length === 0 && (
                    <div className="text-center p-8 text-gray-500">لا توجد بيانات</div>
                )}
            </div>
        </div>
    );
}
