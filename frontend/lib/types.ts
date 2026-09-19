export interface QuoteDTO {
  symbol: string;
  price: number;
  change_pct: number;
  data_state?: string;
  timestamp?: string;
  provider?: string;
  is_delayed?: boolean;
}

export interface PositionDTO {
  instrument_id: number;
  symbol: string;
  name: string;
  quantity: number;
  average_cost: number;
  realized_pnl: number;
  current_price: number | null;
  market_value: number | null;
  unrealized_pnl: number | null;
  unrealized_pnl_percent: number | null;
  asset_class?: string | null;
  native_currency?: string | null;
  average_cost_native?: number | null;
  current_native_price?: number | null;
  current_fx_rate_to_base?: number | null;
}

export interface PortfolioOverviewDTO {
  id: number;
  user_id: number;
  name: string;
  portfolio_type: string;
  currency: string;
  created_at: string;
  updated_at: string;
  cash_balance: number;
  total_realized_pnl: number;
  total_unrealized_pnl: number | null;
  total_market_value: number | null;
  data_freshness: string;
  valuation_complete: boolean;
}

export interface PortfolioSummaryDTO {
  portfolio_id: number;
  cash_balance: number;
  total_deposits: number;
  total_withdrawals: number;
  total_realized_pnl: number;
  total_unrealized_pnl: number | null;
  total_market_value: number | null;
  market_data_freshness: string;
  valuation_complete: boolean;
  positions: PositionDTO[];
}

export interface TransactionRead {
  id: number;
  portfolio_id: number;
  transaction_type: string;
  instrument_id: number | null;
  instrument_symbol: string | null;
  quantity: number;
  price: number;
  fee: number;
  executed_at: string;
  created_at: string;
  notes: string | null;
  strategy: string | null;
}

export interface SleeveAllocationDTO {
  asset_class: string;
  current_value: number;
  current_weight: number;
  target_weight: number;
  target_value: number;
  deficit_value: number;
  proposed_allocation: number;
  unallocated_reason: string | null;
}

export interface BasketItemDTO {
  instrument_id: number;
  symbol: string;
  name: string;
  asset_class: string;
  native_currency: string;
  market_view: string;
  personal_action: string;
  market_score: number;
  data_quality_score: number;
  analysis_native_price: number;
  fx_rate_to_base: number;
  analysis_base_price: number;
  proposed_quantity: number;
  proposed_native_budget: number;
  proposed_base_budget: number;
  projected_weight: number;
  recommended_target_weight: number;
  hard_max_weight: number;
  sizing_state: string;
  reason_codes: string[];
}

export interface BasketPreviewResponse {
  portfolio_id: number;
  base_currency: string;
  risk_tolerance: string;
  allocation_policy_version: string;
  portfolio_total_value: number;
  available_cash: number;
  requested_deploy_amount: number;
  allocated_amount: number;
  unallocated_amount: number;
  target_cash_reserve: number;
  constraint_unallocated: number;
  valuation_complete: boolean;
  data_state: string;
  sleeves: SleeveAllocationDTO[];
  items: BasketItemDTO[];
}
