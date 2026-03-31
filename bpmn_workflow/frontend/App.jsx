import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Clock, 
  ListTodo, 
  Archive, 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Bell, 
  User, 
  LogOut, 
  MoreHorizontal,
  CheckCircle2,
  Circle,
  AlertCircle,
  ArrowRight
} from 'lucide-react';

// --- Mock API Helpers ---
const fetchDashboardStats = () => Promise.resolve({
  waitingTasks: 12,
  activeRequests: 5,
  completedTasks: 48
});

const fetchRecentTasks = () => Promise.resolve([
  { id: 'T-101', title: 'اعتماد طلب إجازة', type: 'إجازة سنوية', priority: 'urgent', date: '2024-02-11' },
  { id: 'T-102', title: 'مراجعة تقرير الصرف', type: 'مالية', priority: 'normal', date: '2024-02-10' },
]);

// --- Components ---

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button 
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
      active 
        ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' 
        : 'text-slate-600 hover:bg-blue-50 hover:text-blue-600'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </button>
);

const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-3xl shadow-xl shadow-slate-100 border border-slate-100 p-6 ${className}`}>
    {children}
  </div>
);

const StatCard = ({ label, value, icon: Icon, color }) => (
  <Card className="hover:scale-[1.02] transition-transform cursor-default">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-slate-500 text-sm mb-1">{label}</p>
        <h3 className="text-3xl font-bold text-slate-800">{value}</h3>
      </div>
      <div className={`p-3 rounded-2xl ${color}`}>
        <Icon size={24} />
      </div>
    </div>
  </Card>
);

const TimelineItem = ({ title, user, status, date, isLast }) => {
  const getStatusStyle = () => {
    switch(status) {
      case 'completed': return 'bg-emerald-500 text-white';
      case 'active': return 'bg-blue-600 text-white ring-4 ring-blue-100 animate-pulse';
      default: return 'bg-slate-200 text-slate-400';
    }
  };

  return (
    <div className="relative flex gap-4 pb-8">
      {!isLast && <div className="absolute top-8 right-2.5 w-0.5 h-full bg-slate-100" />}
      <div className={`mt-1 h-5 w-5 rounded-full flex items-center justify-center z-10 ${getStatusStyle()}`}>
        {status === 'completed' && <CheckCircle2 size={12} />}
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-start mb-1">
          <h4 className={`font-bold ${status === 'active' ? 'text-blue-600' : 'text-slate-800'}`}>{title}</h4>
          <span className="text-xs text-slate-400">{date}</span>
        </div>
        <p className="text-sm text-slate-500">{user}</p>
      </div>
    </div>
  );
};

// --- Main Views ---

const Dashboard = ({ onNavigate }) => {
  const [stats, setStats] = useState({ waitingTasks: 0, activeRequests: 0, completedTasks: 0 });
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetchDashboardStats().then(setStats);
    fetchRecentTasks().then(setTasks);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">مرحباً بك، محمد أحمد</h1>
        <p className="text-slate-500">لديك {stats.waitingTasks} مهام تتطلب انتباهك اليوم.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard label="مهام قيد الانتظار" value={stats.waitingTasks} icon={Clock} color="bg-orange-100 text-orange-600" />
        <StatCard label="طلبات نشطة" value={stats.activeRequests} icon={ListTodo} color="bg-blue-100 text-blue-600" />
        <StatCard label="طلبات مكتملة" value={stats.completedTasks} icon={CheckCircle2} color="bg-emerald-100 text-emerald-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-slate-800">أحدث المهام</h2>
              <button 
                onClick={() => onNavigate('waiting-tasks')}
                className="text-blue-600 text-sm font-medium hover:underline"
              >
                عرض الكل
              </button>
            </div>
            <div className="space-y-4">
              {tasks.map(task => (
                <div key={task.id} className="flex items-center justify-between p-4 rounded-2xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100 group">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-xl ${task.priority === 'urgent' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'}`}>
                      <AlertCircle size={20} />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800">{task.title}</h4>
                      <p className="text-xs text-slate-500">{task.type} • {task.id}</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => onNavigate('details')}
                    className="p-2 rounded-lg bg-white shadow-sm border border-slate-200 text-slate-400 group-hover:text-blue-600 group-hover:border-blue-200 transition-all"
                  >
                    <ChevronLeft size={18} />
                  </button>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <h2 className="text-lg font-bold text-slate-800 mb-6">روابط سريعة</h2>
            <div className="space-y-3">
              <button 
                onClick={() => onNavigate('new-request')}
                className="w-full flex items-center justify-between p-4 rounded-2xl bg-gradient-to-l from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-100 hover:scale-[1.02] transition-transform"
              >
                <div className="flex items-center gap-3">
                  <PlusCircle size={20} />
                  <span className="font-medium">إنشاء طلب جديد</span>
                </div>
                <ChevronLeft size={18} opacity={0.7} />
              </button>
              <button className="w-full flex items-center justify-between p-4 rounded-2xl bg-white border border-slate-100 text-slate-700 hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <Search size={20} className="text-slate-400" />
                  <span className="font-medium">البحث عن موظف</span>
                </div>
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

const MyRequests = ({ onNavigate }) => (
  <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
    <header className="flex justify-between items-center">
      <h1 className="text-2xl font-bold text-slate-800">طلباتي</h1>
      <button 
        onClick={() => onNavigate('new-request')}
        className="px-4 py-2 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all flex items-center gap-2"
      >
        <PlusCircle size={18} />
        <span>طلب جديد</span>
      </button>
    </header>

    <Card className="overflow-hidden p-0">
      <table className="w-full text-right">
        <thead>
          <tr className="bg-slate-50 text-slate-500 text-sm">
            <th className="px-6 py-4 font-bold">المعرف</th>
            <th className="px-6 py-4 font-bold">نوع الطلب</th>
            <th className="px-6 py-4 font-bold">المرحلة الحالية</th>
            <th className="px-6 py-4 font-bold">التقدم</th>
            <th className="px-6 py-4 font-bold">آخر تحديث</th>
            <th className="px-6 py-4"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {[1,2,3].map(i => (
            <tr key={i} className="hover:bg-slate-50/50 transition-colors cursor-pointer group" onClick={() => onNavigate('details')}>
              <td className="px-6 py-4 text-sm font-medium text-slate-900">#REQ-2024-00{i}</td>
              <td className="px-6 py-4 text-sm text-slate-600">طلب إجازة دورية</td>
              <td className="px-6 py-4 text-sm text-slate-600">
                <span className="inline-flex items-center gap-1.5 py-1 px-3 rounded-full bg-blue-50 text-blue-600 text-xs font-bold">
                  اعتماد المدير المباشر
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="w-32 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: '60%' }} />
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-slate-400">منذ ساعتين</td>
              <td className="px-6 py-4 text-left">
                <ChevronLeft size={18} className="text-slate-300 group-hover:text-blue-500 group-hover:translate-x-1 transition-all inline" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  </div>
);

const DetailsView = ({ onBack }) => (
  <div className="space-y-6 animate-in zoom-in-95 duration-300">
    <header className="flex items-center gap-4">
      <button 
        onClick={onBack}
        className="p-2 rounded-xl hover:bg-slate-100 text-slate-500 transition-colors"
      >
        <ChevronRight size={24} />
      </button>
      <div>
        <h1 className="text-2xl font-bold text-slate-800">تفاصيل الطلب #REQ-2024-001</h1>
        <p className="text-slate-500 text-sm">طلب إجازة سنوية • تم الإنشاء في 05 فبراير 2024</p>
      </div>
    </header>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <h2 className="text-lg font-bold text-slate-800 mb-6 border-b pb-4">معلومات الطلب</h2>
          <div className="grid grid-cols-2 gap-y-6">
            <div>
              <p className="text-slate-400 text-xs mb-1">نوع الإجازة</p>
              <p className="font-medium text-slate-800">إجازة سنوية</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs mb-1">تاريخ البدء</p>
              <p className="font-medium text-slate-800">15 فبراير 2024</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs mb-1">تاريخ الانتهاء</p>
              <p className="font-medium text-slate-800">20 فبراير 2024</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs mb-1">المدة</p>
              <p className="font-medium text-slate-800">5 أيام عمل</p>
            </div>
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-bold text-slate-800 mb-6">التعليقات والملاحظات</h2>
          <div className="space-y-6">
             <div className="text-center py-8">
                <p className="text-slate-400 italic">لا توجد تعليقات بعد</p>
             </div>
             <div className="flex gap-4">
                <input 
                  type="text" 
                  placeholder="أضف تعليقاً..." 
                  className="flex-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-blue-100 focus:border-blue-300 outline-none transition-all"
                />
                <button className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">إرسال</button>
             </div>
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <h2 className="text-lg font-bold text-slate-800 mb-8 border-b pb-4">مسار الاعتمادات</h2>
          <div className="pr-2">
            <TimelineItem title="تقديم الطلب" user="محمد أحمد (موظف)" status="completed" date="05 فبراير" />
            <TimelineItem title="اعتماد المدير المباشر" user="سارة خالد (مدير القسم)" status="active" date="جاري العمل" />
            <TimelineItem title="اعتماد الموارد البشرية" user="قسم الموارد البشرية" status="pending" date="" />
            <TimelineItem title="الاعتماد النهائي" user="أتمتة النظام" status="pending" date="" isLast={true} />
          </div>
          
          <div className="mt-8 p-4 bg-blue-50 rounded-2xl border border-blue-100">
             <div className="flex gap-3 text-blue-800">
                <Clock size={18} className="shrink-0 mt-0.5" />
                <p className="text-sm">
                  الطلب حالياً في انتظار مراجعة <strong>سارة خالد</strong> منذ 3 أيام.
                </p>
             </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
);

// --- App Component ---

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [prevTab, setPrevTab] = useState('home');
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  const handleNavigate = (tab) => {
    setPrevTab(activeTab);
    setActiveTab(tab);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home': return <Dashboard onNavigate={handleNavigate} />;
      case 'my-requests': return <MyRequests onNavigate={handleNavigate} />;
      case 'details': return <DetailsView onBack={() => handleNavigate(prevTab)} />;
      case 'archive': return <div className="p-20 text-center text-slate-400">قريباً: الأرشيف</div>;
      case 'waiting-tasks': return <div className="p-20 text-center text-slate-400">قريباً: صندوق المهام</div>;
      case 'new-request': return <div className="p-20 text-center text-slate-400">قريباً: إنشاء طلب جديد</div>;
      default: return <Dashboard onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans" dir="rtl">
      {/* Sidebar */}
      <aside className={`fixed top-0 bottom-0 right-0 z-50 bg-white border-l border-slate-100 transition-all duration-300 shadow-2xl shadow-slate-200 ${isSidebarOpen ? 'w-72' : 'w-20'}`}>
        <div className="flex flex-col h-full p-4">
          <div className="flex items-center gap-3 mb-10 px-2 py-4 border-b border-slate-50">
            <div className="h-10 w-10 bg-blue-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-200">
              ش
            </div>
            {isSidebarOpen && <span className="text-xl font-black text-slate-800 tracking-tight">شامل</span>}
          </div>

          <nav className="flex-1 space-y-2">
            <SidebarItem icon={LayoutDashboard} label={isSidebarOpen ? "لوحة التحكم" : ""} active={activeTab === 'home'} onClick={() => handleNavigate('home')} />
            <SidebarItem icon={Clock} label={isSidebarOpen ? "صندوق المهام" : ""} active={activeTab === 'waiting-tasks'} onClick={() => handleNavigate('waiting-tasks')} />
            <SidebarItem icon={ListTodo} label={isSidebarOpen ? "طلباتي" : ""} active={activeTab === 'my-requests' || activeTab === 'details'} onClick={() => handleNavigate('my-requests')} />
            <SidebarItem icon={Archive} label={isSidebarOpen ? "الأرشيف" : ""} active={activeTab === 'archive'} onClick={() => handleNavigate('archive')} />
          </nav>

          <div className="pt-4 border-t border-slate-50">
             <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-500 hover:bg-red-50 transition-colors">
                <LogOut size={20} />
                {isSidebarOpen && <span className="font-medium">تسجيل الخروج</span>}
             </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`transition-all duration-300 min-h-screen ${isSidebarOpen ? 'pr-72' : 'pr-20'}`}>
        {/* Top Navbar */}
        <header className="h-20 bg-white/80 backdrop-blur-md sticky top-0 z-40 px-8 flex items-center justify-between border-b border-slate-100/50">
          <div className="flex items-center gap-4">
             <button 
               onClick={() => setSidebarOpen(!isSidebarOpen)} 
               className="p-2 rounded-lg hover:bg-slate-100 text-slate-500 transition-colors"
             >
                {isSidebarOpen ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
             </button>
             <div className="relative group hidden sm:block">
                <Search size={18} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <input 
                  type="text" 
                  placeholder="ابحث عن طلبات، مهام..." 
                  className="bg-slate-50 border-transparent border focus:border-blue-200 focus:bg-white rounded-2xl pr-10 pl-4 py-2 text-sm outline-none transition-all w-64"
                />
             </div>
          </div>

          <div className="flex items-center gap-4">
             <button className="relative p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                <Bell size={20} />
                <span className="absolute top-2 left-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
             </button>
             <div className="h-8 w-[1px] bg-slate-100 mx-2" />
             <div className="flex items-center gap-3">
                <div className="text-left hidden sm:block text-right">
                   <p className="text-sm font-bold text-slate-800 leading-none">محمد أحمد</p>
                   <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest font-semibold">محلل نظم أول</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 border border-slate-100 overflow-hidden">
                   <User size={24} />
                </div>
             </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-8 max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}
