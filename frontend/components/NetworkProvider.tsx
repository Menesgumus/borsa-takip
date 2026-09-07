"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { WifiOff, RefreshCw } from "lucide-react";

type NetworkContextType = {
  isOnline: boolean;
};

const NetworkContext = createContext<NetworkContextType>({ isOnline: true });

export const useNetwork = () => useContext(NetworkContext);

export function NetworkProvider({ children }: { children: React.ReactNode }) {
  const [isOnline, setIsOnline] = useState(true); // default to true, check on mount
  const [showReconnecting, setShowReconnecting] = useState(false);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => {
      setIsOnline(true);
      setShowReconnecting(true);
      setTimeout(() => setShowReconnecting(false), 3000);
    };
    
    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return (
    <NetworkContext.Provider value={{ isOnline }}>
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 bg-red-600 text-white text-xs font-bold text-center p-1 z-50 flex items-center justify-center gap-2 shadow-md">
          <WifiOff size={14} /> Çevrimdışı (Offline Mod)
        </div>
      )}
      {showReconnecting && (
        <div className="fixed top-0 left-0 right-0 bg-green-600 text-white text-xs font-bold text-center p-1 z-50 flex items-center justify-center gap-2 shadow-md">
          <RefreshCw size={14} className="animate-spin" /> Bağlantı kuruldu, yenileniyor...
        </div>
      )}
      <div className={!isOnline || showReconnecting ? "pt-6" : ""}>
        {children}
      </div>
    </NetworkContext.Provider>
  );
}
