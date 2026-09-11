import React from "react";
import { DATA_STATE_CONFIG } from "@/lib/financialUi";

interface DataStateBadgeProps {
  state?: string | null;
  className?: string;
}

export function DataStateBadge({ state, className = "" }: DataStateBadgeProps) {
  const safeState = state && DATA_STATE_CONFIG[state] ? state : "UNAVAILABLE";
  const config = DATA_STATE_CONFIG[safeState];

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium uppercase ${config.colorClass} ${className}`}>
      {config.label}
    </span>
  );
}
