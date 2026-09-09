'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  LineChart, 
  Briefcase, 
  ShieldAlert, 
  Target, 
  BookOpen, 
  Bell, 
  Settings, 
  Menu, 
  X,
  LogOut
} from 'lucide-react';

export const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Piyasalar', href: '/markets', icon: LineChart },
  { name: 'Portföyüm', href: '/portfolios', icon: Briefcase },
  { name: 'Risk Yönetimi', href: '/risk', icon: ShieldAlert },
  { name: 'Fırsatlar', href: '/opportunities', icon: Target },
  { name: 'Alarmlar', href: '/alerts', icon: Bell },
  { name: 'Eğitim', href: '/education', icon: BookOpen },
  { name: 'Mentor', href: '/mentor', icon: BookOpen }, // Could use a different icon
  { name: 'Ayarlar', href: '/settings', icon: Settings },
];

export default function Sidebar({ userEmail, onLogout }: { userEmail: string; onLogout: () => void }) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navContent = (
    <div className="flex flex-col h-full bg-navy-900 text-slate-300">
      <div className="flex items-center justify-between h-16 px-4 bg-navy-900 border-b border-navy-800 shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-lg text-white">
          <div className="w-8 h-8 rounded bg-primary-600 flex items-center justify-center text-white">BT</div>
          Borsa Takip
        </Link>
        <button className="lg:hidden text-slate-300" onClick={() => setMobileMenuOpen(false)}>
          <X className="w-6 h-6" />
        </button>
      </div>

      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                isActive 
                  ? 'bg-primary-600 text-white' 
                  : 'hover:bg-navy-800 hover:text-white'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <Icon className={`mr-3 shrink-0 h-5 w-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-navy-800 bg-navy-900 shrink-0">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-navy-700 flex items-center justify-center text-sm font-medium text-white shrink-0">
            {userEmail.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{userEmail}</p>
          </div>
          <button onClick={onLogout} className="p-1.5 text-slate-400 hover:text-white hover:bg-navy-800 rounded-md transition-colors">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden sticky top-0 z-40 flex items-center h-16 shrink-0 px-4 bg-navy-900 border-b border-navy-800">
        <button
          type="button"
          className="text-slate-300 focus:outline-none"
          onClick={() => setMobileMenuOpen(true)}
        >
          <Menu className="h-6 w-6" />
        </button>
        <Link href="/dashboard" className="ml-4 font-bold text-lg text-white">
          Borsa Takip
        </Link>
      </div>

      {/* Mobile Sidebar overlay */}
      {mobileMenuOpen && (
        <div className="relative z-50 lg:hidden">
          <div className="fixed inset-0 bg-navy-900/80 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-64 flex flex-col bg-navy-900">
            {navContent}
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 lg:border-r lg:border-navy-800 lg:bg-navy-900 z-50">
        {navContent}
      </div>
    </>
  );
}
