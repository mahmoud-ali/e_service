const { useState, useEffect } = React;

function App() {
    const [user, setUser] = useState(null);
    const [view, setView] = useState('dashboard');

    useEffect(() => {
        fetch('/hr_bot/api/login-status/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => {
                if (data.is_authenticated) {
                    setUser(data);
                } else {
                    window.location.href = '/admin/login/';
                }
            });
    }, []);

    const logout = () => {
        fetch('/hr_bot/api/logout/', { method: 'POST', credentials: 'same-origin' })
            .then(() => window.location.href = '/admin/login/');
    };

    if (!user) return <div>Loading...</div>;

    return (
        <div className="container mx-auto p-4">
            <nav className="navbar bg-base-100">
                <div className="navbar-start">
                    <h1 className="text-xl font-bold">HR Bot</h1>
                </div>
                <div className="navbar-end">
                    <span>Welcome, {user.user}</span>
                    <button className="btn btn-ghost" onClick={logout}>Logout</button>
                </div>
            </nav>
            <div className="mt-4">
                {view === 'dashboard' && <Dashboard user={user} setView={setView} />}
                {view === 'registrations' && <RegistrationList user={user} />}
                {/* Add more views as needed */}
            </div>
        </div>
    );
}

function Dashboard({ user, setView }) {
    return (
        <div>
            <h2 className="text-2xl mb-4">Dashboard</h2>
            {user.groups.includes('hr_manager') && (
                <button className="btn btn-primary" onClick={() => setView('registrations')}>Manage Registrations</button>
            )}
            {/* Add buttons for other sections based on permissions */}
        </div>
    );
}

function RegistrationList({ user }) {
    const [registrations, setRegistrations] = useState([]);

    useEffect(() => {
        fetch('/hr_bot/api/registrations/', { credentials: 'same-origin' })
            .then(res => res.json())
            .then(data => setRegistrations(data.registrations));
    }, []);

    const accept = (id) => {
        fetch(`/hr_bot/api/registrations/${id}/accept/`, { method: 'POST', credentials: 'same-origin' })
            .then(() => alert('Accepted'));
    };

    return (
        <div>
            <h2 className="text-2xl mb-4">Registrations</h2>
            <ul className="list-disc">
                {registrations.map(r => (
                    <li key={r.id} className="mb-2">
                        {r.employee} - {r.state}
                        {user.groups.includes('hr_manager') && r.state === 1 && (
                            <button className="btn btn-sm btn-success ml-2" onClick={() => accept(r.id)}>Accept</button>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
