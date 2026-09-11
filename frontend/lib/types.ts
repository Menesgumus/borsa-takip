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
