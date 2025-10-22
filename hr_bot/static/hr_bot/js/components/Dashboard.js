import React, { useState, useEffect } from 'react';
import { STATE_DRAFT } from '../utils.js';

export default function Dashboard({ user, setView, isManager, isEmployee }) {
    const [stats, setStats] = useState({
        registrations: 0,
        families: 0,
        moahil: 0,
        bank_accounts: 0
    });

    useEffect(() => {
        if (isManager) {
            fetch('/bot/api/registrations/', { credentials: 'same-origin' })
                .then(res => res.json())
                .then(data => setStats(prev => ({ ...prev, registrations: data.registrations.length })))
                .catch(() => {});
            
            fetch('/bot/api/families/', { credentials: 'same-origin' })
                .then(res => res.json())
                .then(data => setStats(prev => ({ ...prev, families: data.families.filter(f => f.state === STATE_DRAFT).length })))
                .catch(() => {});
            
            fetch('/bot/api/moahil/', { credentials: 'same-origin' })
                .then(res => res.json())
                .then(data => setStats(prev => ({ ...prev, moahil: data.moahil.filter(m => m.state === STATE_DRAFT).length })))
                .catch(() => {});
            
            fetch('/bot/api/bank-accounts/', { credentials: 'same-origin' })
                .then(res => res.json())
                .then(data => setStats(prev => ({ ...prev, bank_accounts: data.bank_accounts.filter(b => b.state === STATE_DRAFT).length })))
                .catch(() => {});
        }
    }, [isManager]);

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">لوحة التحكم</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {isManager && (
                    <>
                        <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer" onClick={() => setView('registrations')}>
                            <div className="card-body">
                                <h2 className="card-title">طلبات التسجيل</h2>
                                <p className="text-3xl font-bold text-primary">{stats.registrations}</p>
                                <p className="text-sm opacity-70">طلب قيد الانتظار</p>
                            </div>
                        </div>
                        
                        <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer" onClick={() => setView('families')}>
                            <div className="card-body">
                                <h2 className="card-title">بيانات العائلة</h2>
                                <p className="text-3xl font-bold text-primary">{stats.families}</p>
                                <p className="text-sm opacity-70">طلب قيد الانتظار</p>
                            </div>
                        </div>
                        
                        <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer" onClick={() => setView('moahil')}>
                            <div className="card-body">
                                <h2 className="card-title">المؤهلات العلمية</h2>
                                <p className="text-3xl font-bold text-primary">{stats.moahil}</p>
                                <p className="text-sm opacity-70">طلب قيد الانتظار</p>
                            </div>
                        </div>
                        
                        <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer" onClick={() => setView('bank_accounts')}>
                            <div className="card-body">
                                <h2 className="card-title">الحسابات البنكية</h2>
                                <p className="text-3xl font-bold text-primary">{stats.bank_accounts}</p>
                                <p className="text-sm opacity-70">طلب قيد الانتظار</p>
                            </div>
                        </div>
                    </>
                )}
                
                <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer" onClick={() => setView('employee_data')}>
                    <div className="card-body">
                        <h2 className="card-title">بياناتي الشخصية</h2>
                        <p className="text-sm opacity-70">عرض البيانات الشخصية</p>
                    </div>
                </div>
            </div>

            {isEmployee && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button className="btn btn-primary btn-lg" onClick={() => setView('families')}>
                        إضافة بيانات عائلة
                    </button>
                    <button className="btn btn-primary btn-lg" onClick={() => setView('moahil')}>
                        إضافة مؤهل علمي
                    </button>
                    <button className="btn btn-primary btn-lg" onClick={() => setView('bank_accounts')}>
                        إضافة حساب بنكي
                    </button>
                </div>
            )}
        </div>
    );
}
