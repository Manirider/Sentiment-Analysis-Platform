import { NavLink } from 'react-router-dom';

const navItems = [
    { path: '/', label: 'Overview', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { path: '/feed', label: 'Live Stream', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
    { path: '/analytics', label: 'Deep Dive', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
];

export default function Sidebar() {
    return (
        <aside className="fixed left-0 top-0 h-screen w-72 glass-sidebar flex flex-col z-50">
            <div className="p-8 pb-8">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00b4d8] to-[#7209b7] flex items-center justify-center shadow-lg shadow-purple-500/20">
                        <span className="text-white font-bold text-lg">S</span>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white tracking-tight">Sentiment</h1>
                        <p className="text-xs text-[#00b4d8] font-medium tracking-wide">AI PLATFORM</p>
                    </div>
                </div>
            </div>


            <nav className="flex-1 px-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `relative flex items-center gap-3 px-5 py-3.5 rounded-xl transition-all duration-300 group ${isActive
                                ? 'bg-white/10 text-white shadow-lg shadow-black/20'
                                : 'text-zinc-500 hover:text-white hover:bg-white/5'
                            }`
                        }
                    >
                        {({ isActive }) => (
                            <>
                                {isActive && (
                                    <div className="absolute left-0 w-1 h-8 bg-[#00f5d4] rounded-r-full shadow-[0_0_10px_#00f5d4]"></div>
                                )}
                                <svg className={`w-5 h-5 transition-colors duration-300 ${isActive ? 'text-[#00f5d4]' : 'text-zinc-500 group-hover:text-white'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                                </svg>
                                <span className="font-semibold tracking-wide text-sm">{item.label}</span>
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>


            <div className="p-6">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-[#7209b7]/20 to-[#f72585]/20 border border-white/10 backdrop-blur-md">
                    <p className="text-xs text-zinc-400 mb-1">Status</p>
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-[#00f5d4] animate-pulse shadow-[0_0_8px_#00f5d4]"></span>
                        <p className="text-sm font-semibold text-white">System Online</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
