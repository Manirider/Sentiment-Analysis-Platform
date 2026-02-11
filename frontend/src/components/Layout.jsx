import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
    return (
        <div className="min-h-screen bg-[var(--bg-primary)] text-white font-sans selection:bg-[#00f5d4] selection:text-black">
            <Sidebar />
            <main className="ml-72 min-h-screen relative z-10 flex flex-col">
                <div className="p-8 max-w-[1600px] mx-auto animate-slide-in flex-1">
                    <Outlet />
                </div>
                <footer className="p-4 text-center text-zinc-500 text-sm border-t border-white/5">
                    Author: <span className="text-[#00f5d4] font-medium">suryasai</span>
                </footer>
            </main>
        </div>
    );
}
