import React, { useState } from 'react';
import { csrftoken } from '../utils.js';

export default function MoahilForm({ onSuccess }) {
    const [formData, setFormData] = useState({
        moahil: '',
        university: '',
        takhasos: '',
        graduate_dt: ''
    });
    const [file, setFile] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmitting(true);
        
        const data = new FormData();
        data.append('moahil', formData.moahil);
        data.append('university', formData.university);
        data.append('takhasos', formData.takhasos);
        data.append('graduate_dt', formData.graduate_dt);
        if (file) data.append('attachement_file', file);

        fetch('/bot/api/moahil/create/', {
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
                <h3 className="card-title">إضافة مؤهل جديد</h3>
                <form onSubmit={handleSubmit}>
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">المؤهل</span>
                        </label>
                        <select 
                            className="select select-bordered" 
                            value={formData.moahil}
                            onChange={(e) => setFormData({...formData, moahil: e.target.value})}
                            required
                        >
                            <option value="">اختر المؤهل</option>
                            <option value="بكالوريوس">بكالوريوس</option>
                            <option value="ماجستير">ماجستير</option>
                            <option value="دكتوراه">دكتوراه</option>
                            <option value="دبلوم">دبلوم</option>
                        </select>
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">الجامعة</span>
                        </label>
                        <input 
                            type="text" 
                            className="input input-bordered" 
                            value={formData.university}
                            onChange={(e) => setFormData({...formData, university: e.target.value})}
                            required
                        />
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">التخصص</span>
                        </label>
                        <input 
                            type="text" 
                            className="input input-bordered" 
                            value={formData.takhasos}
                            onChange={(e) => setFormData({...formData, takhasos: e.target.value})}
                            required
                        />
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">تاريخ التخرج</span>
                        </label>
                        <input 
                            type="date" 
                            className="input input-bordered" 
                            value={formData.graduate_dt}
                            onChange={(e) => setFormData({...formData, graduate_dt: e.target.value})}
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
