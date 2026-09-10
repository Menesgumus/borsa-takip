"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { X, Search } from "lucide-react";

type ActionType = "DEPOSIT" | "WITHDRAW" | "BUY" | "SELL";

interface PortfolioActionModalProps {
  portfolioId: string;
  isOpen: boolean;
  onClose: () => void;
  summary: any;
}

export function PortfolioActionModal({ portfolioId, isOpen, onClose, summary }: PortfolioActionModalProps) {
  const queryClient = useQueryClient();
  const [actionType, setActionType] = useState<ActionType>("DEPOSIT");
  const [amount, setAmount] = useState("");
  const [symbolQuery, setSymbolQuery] = useState("");
  const [selectedInstrument, setSelectedInstrument] = useState<any>(null);
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");

  const { data: searchResults } = useQuery({
    queryKey: ["instrument-search", symbolQuery],
    queryFn: async () => {
      if (symbolQuery.length < 2) return [];
      const res = await fetch(`/api/v1/instruments?query=${symbolQuery}`);
      if (!res.ok) return [];
      const data = await res.json();
      return data.items || [];
    },
    enabled: symbolQuery.length >= 2,
  });

  const { data: quote } = useQuery({
    queryKey: ["instrument-quote", selectedInstrument?.symbol],
    queryFn: async () => {
      const res = await fetch(`/api/v1/instruments/quotes?symbols=${selectedInstrument.symbol}`);
      if (!res.ok) return null;
      const data = await res.json();
      return data[0];
    },
    enabled: !!selectedInstrument,
    refetchInterval: 10000,
  });

  const transactionMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await fetch(`/api/v1/portfolios/${portfolioId}/transactions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "İşlem başarısız");
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio", portfolioId, "summary"] });
      onClose();
      resetForm();
    }
  });

  const resetForm = () => {
    setAmount("");
    setSymbolQuery("");
    setSelectedInstrument(null);
    setQuantity("");
    setPrice("");
  };

  if (!isOpen) return null;

  const handleCashAction = () => {
    transactionMutation.mutate({
      transaction_type: actionType,
      quantity: parseFloat(amount),
      price: 1.0,
      fee: 0,
    });
  };

  const handleTradeAction = () => {
    if (!selectedInstrument) return;
    transactionMutation.mutate({
      transaction_type: actionType,
      instrument_id: selectedInstrument.id,
      quantity: parseFloat(quantity),
      price: parseFloat(price),
      fee: 0,
    });
  };

  const cashBalance = Number(summary?.cash_balance || 0);

  // Auto-set price if quote arrives and price is empty
  if (quote && quote.price && !price && (actionType === "BUY" || actionType === "SELL")) {
    setPrice(quote.price.toString());
  }

  const maxPurchasable = (price && parseFloat(price) > 0) ? Math.floor(cashBalance / parseFloat(price)) : 0;
  
  // Find current position quantity for SELL max
  const existingPosition = summary?.positions?.find((p: any) => p.instrument_id === selectedInstrument?.id);
  const maxSellable = existingPosition ? existingPosition.quantity : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-center p-4 border-b border-slate-100 bg-slate-50">
          <h2 className="font-bold text-navy-900">Yeni İşlem</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
        </div>

        <div className="p-5">
          <div className="flex gap-2 mb-6 bg-slate-100 p-1 rounded-lg">
            {(["DEPOSIT", "WITHDRAW", "BUY", "SELL"] as ActionType[]).map((type) => (
              <button
                key={type}
                onClick={() => { setActionType(type); resetForm(); }}
                className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  actionType === type ? 'bg-white shadow-sm text-navy-900' : 'text-slate-500 hover:text-navy-700'
                }`}
              >
                {type === "DEPOSIT" ? "Para Yatır" : type === "WITHDRAW" ? "Para Çek" : type === "BUY" ? "Al" : "Sat"}
              </button>
            ))}
          </div>

          {transactionMutation.isError && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-200">
              {transactionMutation.error?.message}
            </div>
          )}

          {(actionType === "DEPOSIT" || actionType === "WITHDRAW") ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Miktar (₺)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="10000"
                  min="0"
                  step="0.01"
                />
              </div>
              {actionType === "WITHDRAW" && (
                <div className="text-sm text-slate-500">
                  Kullanılabilir Nakit: {cashBalance.toLocaleString('tr-TR')} ₺
                </div>
              )}
              <button
                onClick={handleCashAction}
                disabled={!amount || parseFloat(amount) <= 0 || transactionMutation.isPending}
                className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {transactionMutation.isPending ? "İşleniyor..." : "Onayla"}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {!selectedInstrument ? (
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 text-slate-400 w-5 h-5" />
                  <input
                    type="text"
                    value={symbolQuery}
                    onChange={(e) => setSymbolQuery(e.target.value)}
                    className="w-full border-slate-200 rounded-lg pl-10 p-2.5 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Hisse Sembolü (örn. THYAO)"
                  />
                  {searchResults && searchResults.length > 0 && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                      {searchResults.map((inst: any) => (
                        <button
                          key={inst.id}
                          onClick={() => { setSelectedInstrument(inst); setSymbolQuery(""); }}
                          className="w-full text-left px-4 py-2 hover:bg-slate-50 flex justify-between items-center"
                        >
                          <span className="font-bold text-navy-900">{inst.symbol}</span>
                          <span className="text-xs text-slate-500">{inst.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <div>
                      <div className="font-bold text-navy-900">{selectedInstrument.symbol}</div>
                      <div className="text-xs text-slate-500">{selectedInstrument.name}</div>
                    </div>
                    <button onClick={() => setSelectedInstrument(null)} className="text-sm text-primary-600 font-medium">Değiştir</button>
                  </div>

                  {quote && (
                    <div className="text-sm flex justify-between bg-primary-50 p-2 rounded text-primary-800">
                      <span>Anlık Fiyat:</span>
                      <span className="font-bold">{quote.price} ₺</span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Fiyat (₺)</label>
                      <input
                        type="number"
                        value={price}
                        onChange={(e) => setPrice(e.target.value)}
                        className="w-full border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Adet</label>
                      <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        className="w-full border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                        min="1"
                        step="1"
                      />
                    </div>
                  </div>

                  <div className="text-xs flex justify-between px-1">
                    <span className="text-slate-500">
                      {actionType === "BUY" ? `Maks. Alınabilir: ${maxPurchasable} adet` : `Maks. Satılabilir: ${maxSellable} adet`}
                    </span>
                    <span className="font-bold text-navy-900">
                      Tutar: {(parseFloat(price||"0") * parseFloat(quantity||"0")).toLocaleString('tr-TR')} ₺
                    </span>
                  </div>

                  <button
                    onClick={handleTradeAction}
                    disabled={!quantity || !price || parseFloat(quantity) <= 0 || parseFloat(price) <= 0 || transactionMutation.isPending}
                    className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    {transactionMutation.isPending ? "İşleniyor..." : "İşlemi Onayla"}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
