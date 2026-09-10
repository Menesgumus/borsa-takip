"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { X, Search } from "lucide-react";
import { fetchApi } from "@/lib/api";

type ActionType = "DEPOSIT" | "WITHDRAW" | "BUY" | "SELL";
type BuyMode = "QUANTITY" | "BUDGET";

interface PortfolioActionModalProps {
  portfolioId: string;
  isOpen: boolean;
  onClose: () => void;
  summary: any;
}

export function PortfolioActionModal({ portfolioId, isOpen, onClose, summary }: PortfolioActionModalProps) {
  const queryClient = useQueryClient();
  const [actionType, setActionType] = useState<ActionType>("DEPOSIT");
  const [buyMode, setBuyMode] = useState<BuyMode>("QUANTITY");
  
  const [amount, setAmount] = useState("");
  const [symbolQuery, setSymbolQuery] = useState("");
  const [selectedInstrument, setSelectedInstrument] = useState<any>(null);
  
  const [quantity, setQuantity] = useState("");
  const [budgetAmount, setBudgetAmount] = useState("");

  const { data: searchResults } = useQuery({
    queryKey: ["instrument-search", symbolQuery],
    queryFn: async () => {
      if (symbolQuery.length < 2) return [];
      const data = await fetchApi(`/api/v1/instruments?query=${symbolQuery}`) as any;
      return data.items || [];
    },
    enabled: symbolQuery.length >= 2,
  });

  const { data: quote, isError: quoteError } = useQuery({
    queryKey: ["instrument-quote", selectedInstrument?.symbol],
    queryFn: async () => {
      if (!selectedInstrument) return null;
      return await fetchApi(`/api/v1/instruments/${selectedInstrument.symbol}/quote`) as any;
    },
    enabled: !!selectedInstrument,
    refetchInterval: 10000,
  });

  const transactionMutation = useMutation({
    mutationFn: async (payload: any) => {
      // Use different endpoint for TRADE vs DEPOSIT/WITHDRAW
      const endpoint = (payload.transaction_type === "DEPOSIT" || payload.transaction_type === "WITHDRAW")
        ? `/api/v1/portfolios/${portfolioId}/transactions`
        : `/api/v1/portfolios/${portfolioId}/trade`;
        
      const method = "POST";
      return await fetchApi(endpoint, { method, body: JSON.stringify(payload) });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio", portfolioId, "summary"] });
      queryClient.invalidateQueries({ queryKey: ["portfolio", portfolioId, "transactions"] });
      queryClient.invalidateQueries({ queryKey: ["portfolios"] });
      onClose();
      resetForm();
    }
  });

  const resetForm = () => {
    setAmount("");
    setSymbolQuery("");
    setSelectedInstrument(null);
    setQuantity("");
    setBudgetAmount("");
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
    
    if (actionType === "BUY") {
      transactionMutation.mutate({
        side: "BUY",
        instrument_id: selectedInstrument.id,
        quantity: buyMode === "QUANTITY" ? parseFloat(quantity) : null,
        budget_amount: buyMode === "BUDGET" ? parseFloat(budgetAmount) : null,
      });
    } else {
      transactionMutation.mutate({
        side: "SELL",
        instrument_id: selectedInstrument.id,
        quantity: parseFloat(quantity)
      });
    }
  };

  const cashBalance = Number(summary?.cash_balance || 0);
  
  const currentPrice = quote && quote.price && quote.price > 0 ? Number(quote.price) : 0;
  const quoteStatus = quote?.status || "";
  const isQuoteUnavailable = !currentPrice || ["UNAVAILABLE", "PROVIDER_ERROR", "TIMEOUT", "NOT_FOUND"].includes(quoteStatus);

  const maxPurchasable = currentPrice > 0 ? Math.floor(cashBalance / currentPrice) : 0;
  
  const existingPosition = summary?.positions?.find((p: any) => p.instrument_id === selectedInstrument?.id);
  const maxSellable = existingPosition ? Number(existingPosition.quantity) : 0;

  // Calculate budget preview
  let budgetQuantity = 0;
  let budgetCost = 0;
  let budgetRemainder = 0;
  if (buyMode === "BUDGET" && budgetAmount && currentPrice > 0) {
    budgetQuantity = Math.floor(parseFloat(budgetAmount) / currentPrice);
    budgetCost = budgetQuantity * currentPrice;
    budgetRemainder = parseFloat(budgetAmount) - budgetCost;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-xl flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-center p-4 border-b border-slate-100 bg-slate-50 rounded-t-2xl">
          <h2 className="font-bold text-navy-900">Yeni İşlem</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
        </div>

        <div className="p-5 overflow-y-auto">
          <div className="flex gap-2 mb-6 bg-slate-100 p-1 rounded-lg shrink-0">
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
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-200 shrink-0">
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
                  className="w-full border border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="10000"
                  min="0"
                  step="0.01"
                />
              </div>
              {actionType === "WITHDRAW" && (
                <div className="text-sm text-slate-500">
                  Kullanılabilir Nakit: {cashBalance.toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺
                </div>
              )}
              <button
                onClick={handleCashAction}
                disabled={!amount || parseFloat(amount) <= 0 || transactionMutation.isPending}
                className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 mt-4"
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
                    className="w-full border border-slate-200 rounded-lg pl-10 p-2.5 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Hisse Sembolü (örn. THYAO)"
                  />
                  {searchResults && searchResults.length > 0 && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-xl z-20 max-h-72 overflow-y-auto">
                      {searchResults.map((inst: any) => (
                        <button
                          key={inst.id}
                          onClick={() => { setSelectedInstrument(inst); setSymbolQuery(""); }}
                          className="w-full text-left px-4 py-3 hover:bg-slate-50 focus:bg-slate-50 flex flex-col border-b border-slate-100 last:border-0"
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

                  <div className={`p-3 rounded-lg text-sm flex justify-between ${isQuoteUnavailable ? 'bg-danger-50 text-danger-800' : 'bg-primary-50 text-primary-800'}`}>
                    <span>Piyasa Fiyatı:</span>
                    <span className="font-bold">
                      {isQuoteUnavailable ? "Fiyat alınamadı" : `${currentPrice.toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺`}
                      {quoteStatus === "DELAYED" && <span className="ml-2 text-xs font-normal opacity-80">(GECİKMELİ)</span>}
                    </span>
                  </div>

                  {actionType === "BUY" && (
                    <div className="flex gap-2 bg-slate-100 p-1 rounded-lg">
                      <button
                        onClick={() => setBuyMode("QUANTITY")}
                        className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${buyMode === "QUANTITY" ? 'bg-white shadow-sm text-navy-900' : 'text-slate-500'}`}
                      >
                        Adet ile Al
                      </button>
                      <button
                        onClick={() => setBuyMode("BUDGET")}
                        className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${buyMode === "BUDGET" ? 'bg-white shadow-sm text-navy-900' : 'text-slate-500'}`}
                      >
                        Tutar ile Al
                      </button>
                    </div>
                  )}

                  {actionType === "BUY" && buyMode === "QUANTITY" && (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Adet</label>
                        <input
                          type="number"
                          value={quantity}
                          onChange={(e) => setQuantity(e.target.value)}
                          className="w-full border border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                          min="1"
                          step="1"
                        />
                      </div>
                      <div className="text-sm text-slate-600 space-y-1">
                        <div className="flex justify-between">
                          <span>Tahmini işlem tutarı:</span>
                          <span className="font-medium">{(currentPrice * parseFloat(quantity || "0")).toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Kullanılabilir nakit:</span>
                          <span>{cashBalance.toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺</span>
                        </div>
                        <div className="flex justify-between border-t border-slate-100 pt-1">
                          <span>İşlem sonrası tahmini nakit:</span>
                          <span className="font-medium text-navy-900">{(cashBalance - (currentPrice * parseFloat(quantity || "0"))).toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺</span>
                        </div>
                        <div className="text-xs text-primary-600 mt-2">Maksimum alınabilir: {maxPurchasable} adet</div>
                      </div>
                    </div>
                  )}

                  {actionType === "BUY" && buyMode === "BUDGET" && (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Harcanacak Tutar (₺)</label>
                        <input
                          type="number"
                          value={budgetAmount}
                          onChange={(e) => setBudgetAmount(e.target.value)}
                          className="w-full border border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                          min="0"
                          step="0.01"
                        />
                      </div>
                      <div className="text-sm text-slate-600 space-y-1">
                        <div className="flex justify-between">
                          <span>Alınabilecek:</span>
                          <span className="font-medium text-navy-900">{budgetQuantity} adet</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Tahmini kullanılacak:</span>
                          <span>{budgetCost.toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺</span>
                        </div>
                        <div className="flex justify-between border-t border-slate-100 pt-1">
                          <span>Kalan bütçe (Nakit):</span>
                          <span>{budgetRemainder.toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺</span>
                        </div>
                        {budgetAmount && parseFloat(budgetAmount) > 0 && budgetQuantity < 1 && (
                          <div className="text-danger-600 text-xs mt-2">Bu tutarla en az 1 adet hisse alınamıyor.</div>
                        )}
                      </div>
                    </div>
                  )}

                  {actionType === "SELL" && (
                    <div className="space-y-3">
                      <div className="flex justify-between mb-2">
                         <span className="text-sm text-slate-500">Mevcut Pozisyon:</span>
                         <span className="text-sm font-medium text-navy-900">{maxSellable} adet</span>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Satılacak Adet</label>
                        <div className="flex gap-2">
                          <input
                            type="number"
                            value={quantity}
                            onChange={(e) => setQuantity(e.target.value)}
                            className="flex-1 border border-slate-200 rounded-lg p-2.5 focus:ring-primary-500 focus:border-primary-500"
                            min="1"
                            step="1"
                          />
                          <button
                            onClick={() => setQuantity(maxSellable.toString())}
                            className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium"
                          >
                            Tümünü Sat
                          </button>
                        </div>
                      </div>
                      <div className="text-sm text-slate-600 space-y-1">
                        <div className="flex justify-between">
                          <span>Tahmini işlem tutarı:</span>
                          <span className="font-medium">{(currentPrice * parseFloat(quantity || "0")).toLocaleString('tr-TR', {minimumFractionDigits:2, maximumFractionDigits:2})} ₺</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <button
                    onClick={handleTradeAction}
                    disabled={
                      isQuoteUnavailable || 
                      transactionMutation.isPending || 
                      (actionType === "BUY" && buyMode === "QUANTITY" && (!quantity || parseFloat(quantity) <= 0)) ||
                      (actionType === "BUY" && buyMode === "BUDGET" && (!budgetAmount || budgetQuantity < 1)) ||
                      (actionType === "SELL" && (!quantity || parseFloat(quantity) <= 0))
                    }
                    className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 mt-4"
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
