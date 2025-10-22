import React, { useState } from 'react';
import { csrftoken } from '../utils.js';

export default function FamilyForm({ onSuccess }) {
    const [formData, setFormData] = useState({
        relation: '',
        name: '',
        tarikh_el2dafa: ''
    });
    const [file, setFile] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmitting(true);
        
        const data = new FormData();
        data.append('relation', formData.relation);
        data.append('name', formData.name);
        data.append('tarikh_el2dafa', formData.tarikh_el2dafa);
        if (file) data.append('attachement_file', file);

        fetch('/bot/api/families/create/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: data
        })
        .then(res => res.json())
        .then(() => {
            alert('تم إضافة البيانات بنجاح');
            onSuccess();
        })
        .catch(() => alert('حدث خطأ'))
        .finally(() => setSubmitting(false));
    };

    return (
        <div className="card bg-base-100 shadow-xl mb-4">
            <div className="card-body">
                <h3 className="card-title">إضافة فرد جديد</h3>
                <form onSubmit={handleSubmit}>
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">العلاقة</span>
                        </label>
                        <select 
                            className="select select-bordered" 
                            value={formData.relation}
                            onChange={(e) => setFormData({...formData, relation: e.target.value})}
                            required
                        >
                            <option value="">اختر العلاقة</option>
                            <option value="زوجة">زوجة</option>
                            <option value="ابن">ابن</option>
                            <option value="ابنة">ابنة</option>
                        </select>
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">الاسم</span>
                        </label>
                        <input 
                            type="text" 
                            className="input input-bordered" 
                            value={formData.name}
                            onChange={(e) => setFormData({...formData, name: e.target.value})}
                            required
                        />
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">تاريخ الإضافة</span>
                        </label>
                        <input 
                            type="date" 
                            className="input input-bordered" 
                            value={formData.tarikh_el2dafa}
                            onChange={(e) => setFormData({...formData, tarikh_el2dafa: e.target.value})}
                            required
                        />
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">المرفق</span>
                        </label>
                        <input 
                            type="file" 
                            className="file-input file-input-bordered" 
                            onChange={(e) => setFile(e.target.files[0])}
                        />
                    </div>
                    
                    <div className="form-control mt-6">
                        <button type="submit" className="btn btn-primary" disabled={submitting}>
                            {submitting ? 'جاري الحفظ...' : 'حفظ'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
