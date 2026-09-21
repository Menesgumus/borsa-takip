export enum LifecycleHealthState {
  STABLE = "STABLE",
  WATCH = "WATCH",
  CONFIRMED_DETERIORATION = "CONFIRMED_DETERIORATION",
  RECOVERING = "RECOVERING",
  CLOSED = "CLOSED",
}

export enum LifecycleAction {
  HOLD = "HOLD",
  CONSIDER_ADD = "CONSIDER_ADD",
  CONSIDER_REDUCE = "CONSIDER_REDUCE",
  CONSIDER_EXIT = "CONSIDER_EXIT",
  NO_ACTION_DATA = "NO_ACTION_DATA",
}

export interface LifecycleEvidence {
  market_view?: string;
  reason_codes: string[];
}

export interface PositionLifecycleDTO {
  id: number;
  portfolio_id: number;
  instrument_id: number;
  episode_number: number;
  
  health_state: LifecycleHealthState;
  recommended_action: LifecycleAction;
  policy_version: string;
  
  negative_confirmation_count: number;
  strong_sell_confirmation_count: number;
  recovery_confirmation_count: number;
  add_confirmation_count: number;
  
  last_counted_market_observation_key?: string;
  last_evaluated_at?: string;
  last_transition_at?: string;
  
  episode_started_at: string;
  closed_at?: string;
  
  symbol?: string;
  asset_class?: string;
  native_currency?: string;
  
  is_evaluable?: boolean;
  data_state?: string;
  
  current_quantity?: number | string;
  average_cost_base?: number | string;
  current_market_value_base?: number | string;
  unrealized_pnl_base?: number | string;
  unrealized_pnl_pct?: number | string;
  current_weight?: number | string;
  
  market_score?: number | string;
  technical_score?: number | string;
  fundamental_score?: number | string;
  data_quality_score?: number | string;
  
  suggested_reduce_quantity?: number | string;
  suggested_remaining_quantity?: number | string;
  estimated_released_cash_base?: number | string;
  
  evidence?: LifecycleEvidence;
}

export interface LifecycleSnapshotDTO {
  id: number;
  episode_number: number;
  health_state_before?: LifecycleHealthState;
  health_state_after: LifecycleHealthState;
  recommended_action: LifecycleAction;
  evaluated_at: string;
  
  market_view?: string;
  reason_codes?: string;
}

export interface LifecycleSummaryDTO {
  open_positions_count: number;
  stable_count: number;
  watch_count: number;
  reduce_count: number;
  exit_count: number;
}
