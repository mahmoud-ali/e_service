import React, { useState, useEffect } from 'react';
import { csrftoken, STATE_DRAFT, STATE_ACCEPTED, STATE_REJECTED, getStateBadge } from '../utils.js';
import MoahilForm from './MoahilForm.js';

export default function MoahilList({ user, isManager, isEmployee }) {
    const [moahil, setMoahil] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [stateFilter, setStateFilter] = useState(STATE_DRAFT);

    const loadData = () => {
        setLoading(true);
        fetch('/bot/api/moahil/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                setMoahil(data.moahil);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        loadData();
    }, []);

    const filteredMoahil = moahil.filter(m => {
        const matchesSearch = searchTerm === '' ||
            m.employee.toLowerCase().includes(searchTerm.toLowerCase()) ||
            String(m.employee_code).includes(searchTerm) ||
            m.moahil.includes(searchTerm) ||
            m.university.toLowerCase().includes(searchTerm.toLowerCase()) ||
            m.takhasos.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesState = stateFilter === '' || m.state === stateFilter;
        return matchesSearch && matchesState;
    });

    const accept = (id) => {
        if (!confirm('هل أنت متأكد من قبول هذا الطلب؟')) return;
        
        fetch(`/bot/api/moahil/${id}/accept/`, { 
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
        
        fetch(`/bot/api/moahil/${id}/reject/`, { 
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
                <h2 className="text-2xl font-bold">المؤهلات العلمية</h2>
                {isEmployee && (
                    <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                        {showForm ? 'إلغاء' : 'إضافة مؤهل جديد'}
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
                <MoahilForm onSuccess={() => { setShowForm(false); loadData(); }} />
            )}
            
            <div className="overflow-x-auto mt-4">
                <table className="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th>كود الموظف</th>
                            <th>الموظف</th>
                            <th>المؤهل</th>
                            <th>الجامعة</th>
                            <th>التخصص</th>
                            <th>تاريخ التخرج</th>
                            <th>المرفق</th>
                            <th>الحالة</th>
                            {isManager && <th>الإجراءات</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {filteredMoahil.map(m => (
                            <tr key={m.id}>
                                <td>{m.employee_code}</td>
                                <td>{m.employee}</td>
                                <td>{m.moahil}</td>
                                <td>{m.university}</td>
                                <td>{m.takhasos}</td>
                                <td>{m.graduate_dt}</td>
                                <td>
                                    {m.attachement_file && (
                                        <a href={m.attachement_file} target="_blank" className="btn btn-sm btn-ghost">عرض</a>
                                    )}
                                </td>
                                <td>{getStateBadge(m.state)}</td>
                                {isManager && (
                                    <td>
                                        {m.state === STATE_DRAFT && (
                                            <div className="flex gap-2">
                                                <button className="btn btn-success btn-sm" onClick={() => accept(m.id)}>قبول</button>
                                                <button className="btn btn-error btn-sm" onClick={() => reject(m.id)}>رفض</button>
                                            </div>
                                        )}
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filteredMoahil.length === 0 && (
                    <div className="text-center p-8 text-gray-500">لا توجد بيانات</div>
                )}
            </div>
        </div>
    );
}
