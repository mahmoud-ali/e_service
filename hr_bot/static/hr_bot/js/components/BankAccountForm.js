import React, { useState } from 'react';
import { csrftoken } from '../utils.js';

export default function BankAccountForm({ onSuccess }) {
    const [formData, setFormData] = useState({
        bank: '',
        account_no: '',
        active: true
    });
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmitting(true);
        
        const data = new FormData();
        data.append('bank', formData.bank);
        data.append('account_no', formData.account_no);
        data.append('active', formData.active);

        fetch('/bot/api/bank-accounts/create/', {
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
                <h3 className="card-title">إضافة حساب بنكي جديد</h3>
                <form onSubmit={handleSubmit}>
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">البنك</span>
                        </label>
                        <select 
                            className="select select-bordered" 
                            value={formData.bank}
                            onChange={(e) => setFormData({...formData, bank: e.target.value})}
                            required
                        >
                            <option value="">اختر البنك</option>
                            <option value="الوحدة">الوحدة</option>
                            <option value="الجمهورية">الجمهورية</option>
                            <option value="التجاري">التجاري</option>
                            <option value="الصحاري">الصحاري</option>
                        </select>
                    </div>
                    
                    <div className="form-control">
                        <label className="label">
                            <span className="label-text">رقم الحساب</span>
                        </label>
                        <input 
                            type="text" 
                            className="input input-bordered" 
                            value={formData.account_no}
                            onChange={(e) => setFormData({...formData, account_no: e.target.value})}
                            required
                        />
                    </div>
                    
                    <div className="form-control">
                        <label className="label cursor-pointer">
                            <span className="label-text">نشط</span>
                            <input 
                                type="checkbox" 
                                className="checkbox" 
                                checked={formData.active}
                                onChange={(e) => setFormData({...formData, active: e.target.checked})}
                            />
                        </label>
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
