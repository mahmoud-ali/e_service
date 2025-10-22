import React, { useState, useEffect } from 'react';

export default function EmployeeData({ user }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/bot/api/employee-data/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="flex justify-center p-8"><span className="loading loading-spinner loading-lg"></span></div>;
    }

    if (!data) {
        return <div className="text-center p-8 text-gray-500">لا توجد بيانات</div>;
    }

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">بياناتي الشخصية</h2>
            
            <div className="card bg-base-100 shadow-xl mb-4">
                <div className="card-body">
                    <h3 className="card-title">البيانات الأساسية</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <span className="font-bold">الكود:</span> {data.employee.code}
                        </div>
                        <div>
                            <span className="font-bold">الاسم:</span> {data.employee.name}
                        </div>
                        <div>
                            <span className="font-bold">الدرجة الوظيفية:</span> {data.employee.draja_wazifia}
                        </div>
                        <div>
                            <span className="font-bold">العلاوة السنوية:</span> {data.employee.alawa_sanawia}
                        </div>
                        <div>
                            <span className="font-bold">الهيكل الوظيفي:</span> {data.employee.hikal_wazifi}
                        </div>
                        <div>
                            <span className="font-bold">المسمى الوظيفي:</span> {data.employee.mosama_wazifi}
                        </div>
                        <div>
                            <span className="font-bold">الجنس:</span> {data.employee.sex}
                        </div>
                        <div>
                            <span className="font-bold">تاريخ الميلاد:</span> {data.employee.tarikh_milad}
                        </div>
                        <div>
                            <span className="font-bold">تاريخ التعيين:</span> {data.employee.tarikh_ta3in}
                        </div>
                        <div>
                            <span className="font-bold">تاريخ آخر ترقية:</span> {data.employee.tarikh_akhir_targia}
                        </div>
                        <div>
                            <span className="font-bold">القسيمة:</span> {data.employee.gasima}
                        </div>
                        <div>
                            <span className="font-bold">الأطفال:</span> {data.employee.atfal}
                        </div>
                        <div>
                            <span className="font-bold">المؤهل:</span> {data.employee.moahil}
                        </div>
                        <div>
                            <span className="font-bold">الهاتف:</span> {data.employee.phone}
                        </div>
                        <div>
                            <span className="font-bold">البريد الإلكتروني:</span> {data.employee.email}
                        </div>
                        <div>
                            <span className="font-bold">نوع الارتباط:</span> {data.employee.no3_2lertibat}
                        </div>
                        <div>
                            <span className="font-bold">سنوات الخبرة:</span> {data.employee.sanoat_2lkhibra}
                        </div>
                        <div>
                            <span className="font-bold">العضوية:</span> {data.employee.aadoa}
                        </div>
                        <div>
                            <span className="font-bold">المعاش:</span> {data.employee.m3ash}
                        </div>
                        <div>
                            <span className="font-bold">الحالة:</span> {data.employee.status}
                        </div>
                    </div>
                </div>
            </div>

            <div className="card bg-base-100 shadow-xl mb-4">
                <div className="card-body">
                    <h3 className="card-title">بيانات العائلة</h3>
                    {data.families.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="table table-zebra w-full">
                                <thead>
                                    <tr>
                                        <th>العلاقة</th>
                                        <th>الاسم</th>
                                        <th>تاريخ الإضافة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.families.map((f, idx) => (
                                        <tr key={idx}>
                                            <td>{f.relation}</td>
                                            <td>{f.name}</td>
                                            <td>{f.tarikh_el2dafa}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p className="text-gray-500">لا توجد بيانات عائلة</p>
                    )}
                </div>
            </div>

            <div className="card bg-base-100 shadow-xl mb-4">
                <div className="card-body">
                    <h3 className="card-title">المؤهلات العلمية</h3>
                    {data.moahil.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="table table-zebra w-full">
                                <thead>
                                    <tr>
                                        <th>المؤهل</th>
                                        <th>الجامعة</th>
                                        <th>التخصص</th>
                                        <th>تاريخ التخرج</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.moahil.map((m, idx) => (
                                        <tr key={idx}>
                                            <td>{m.moahil}</td>
                                            <td>{m.university}</td>
                                            <td>{m.takhasos}</td>
                                            <td>{m.graduate_dt}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p className="text-gray-500">لا توجد مؤهلات علمية</p>
                    )}
                </div>
            </div>

            <div className="card bg-base-100 shadow-xl mb-4">
                <div className="card-body">
                    <h3 className="card-title">الحسابات البنكية</h3>
                    {data.bank_accounts.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="table table-zebra w-full">
                                <thead>
                                    <tr>
                                        <th>البنك</th>
                                        <th>رقم الحساب</th>
                                        <th>نشط</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.bank_accounts.map((b, idx) => (
                                        <tr key={idx}>
                                            <td>{b.bank}</td>
                                            <td>{b.account_no}</td>
                                            <td>{b.active ? <span className="badge badge-success">نعم</span> : <span className="badge badge-error">لا</span>}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p className="text-gray-500">لا توجد حسابات بنكية</p>
                    )}
                </div>
            </div>
        </div>
    );
}
