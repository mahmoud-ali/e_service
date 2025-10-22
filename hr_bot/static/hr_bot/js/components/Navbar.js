import React from 'react';

export default function Navbar({ user, logout, setView }) {
    return (
        <div className="navbar bg-primary text-primary-content shadow-lg">
            <div className="navbar-start">
                <button className="btn btn-ghost text-xl" onClick={() => setView('dashboard')}>
                    نظام إدارة الموارد البشرية
                </button>
            </div>
            <div className="navbar-end gap-2">
                <span className="text-sm">مرحباً، {user.user}</span>
                <button className="btn btn-ghost btn-sm" onClick={logout}>تسجيل الخروج</button>
            </div>
        </div>
    );
}
