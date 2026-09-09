"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query"; import { useState } from "react"; import { useRouter } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { ArrowRight, AlertCircle, Plus } from "lucide-react";

export default function PortfolioOverviewPage() {
  const { data: portfolios, isLoading } = useQuery({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios/"),
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newPortName, setNewPortName] = useState('');
  const [newPortType, setNewPortType] = useState('REAL');
  const [isCreating, setIsCreating] = useState(false);
  const router = useRouter();
  const queryClient = useQueryClient();

  const handleCreate = async () => {
    if (!newPortName.trim()) return;
    setIsCreating(true);
    try {
      const data = await fetchApi("/api/v1/portfolios/", {
        method: "POST",
        body: JSON.stringify({
          name: newPortName,
          portfolio_type: newPortType,
          description: ""
        })
      });
      await queryClient.invalidateQueries({ queryKey: ["portfolios"] });
      setIsModalOpen(false);
      setNewPortName('');
      if ((data as any)?.id) {
        router.push(`/portfolios/${(data as any).id}`);
      }
    } catch (e) {
      console.error(e);
      alert("Hata oluştu.");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto relative">
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-navy-900/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-100">
            <h2 className="text-xl font-bold text-navy-900 mb-4">Yeni Portföy Ekle</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Portföy Adı</label>
                <input 
                  type="text" 
                  value={newPortName}
                  onChange={(e) => setNewPortName(e.target.value)}
                  placeholder="Örn: Uzun Vade Emeklilik" 
                  className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Portföy Tipi</label>
                <select 
                  value={newPortType}
                  onChange={(e) => setNewPortType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                >
                  <option value="REAL">Gerçek</option>
                  <option value="SIMULATION">Simülasyon (Sanal)</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex gap-3 justify-end">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-navy-700 hover:bg-slate-100 rounded-md text-sm font-medium transition-colors"
                disabled={isCreating}
              >
                İptal
              </button>
              <button 
                onClick={handleCreate}
                disabled={isCreating || !newPortName.trim()}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              >
                {isCreating ? "Oluşturuluyor..." : "Oluştur"}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Portföylerim</h1>
          <p className="text-navy-700 mt-1">Yatırımlarınızın güncel durumunu takip edin.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center gap-2"
        >
          <Plus size={16} /> Yeni Ekle
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-500">Yükleniyor...</div>
      ) : portfolios && (portfolios as any).length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
          {(portfolios as any).map((p: any) => (
            <Link key={p.id} href={`/portfolios/${p.id}`} className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm hover:shadow-md transition-shadow group">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-lg font-bold text-navy-900 group-hover:text-primary-600 transition-colors">{p.name}</h3>
                  <span className="inline-block mt-1 px-2 py-0.5 bg-slate-100 text-slate-600 text-xs font-semibold rounded">
                    {p.portfolio_type === 'REAL' ? 'GERÇEK' : 'SİMÜLASYON'}
                  </span>
                </div>
                <ArrowRight className="text-slate-300 group-hover:text-primary-600 transition-colors" />
              </div>
              
              <div className="space-y-1">
                <span className="text-xs text-navy-700/60 font-medium">Toplam Değer</span>
                <div className="text-2xl font-bold text-navy-900">
                  {p.total_market_value ? `${Number(p.total_market_value).toLocaleString('tr-TR')} ₺` : '0,00 ₺'}
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-slate-100 flex justify-between items-center text-sm">
                <span className="text-navy-700">Gerçekleşen K/Z</span>
                <span className={`font-semibold ${Number(p.total_realized_pnl) >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                  {Number(p.total_realized_pnl) > 0 ? '+' : ''}{Number(p.total_realized_pnl).toLocaleString('tr-TR')} ₺
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-surface rounded-xl p-12 border border-navy-800/10 shadow-sm text-center max-w-2xl mx-auto">
          <BriefcaseIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-navy-900 mb-2">Henüz Portföyünüz Yok</h2>
          <p className="text-navy-700 mb-6">Yatırımlarınızı takip etmek için ilk portföyünüzü oluşturun. İsterseniz gerçek hesap, isterseniz risk almadan simülasyon hesabı açabilirsiniz.</p>
          <button onClick={() => setIsModalOpen(true)} className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors shadow-sm">
            İlk Portföyü Oluştur
          </button>
        </div>
      )}
    </div>
  );
}

function BriefcaseIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="20" height="14" x="2" y="7" rx="2" ry="2"/>
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
    </svg>
  );
}
