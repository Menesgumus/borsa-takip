export interface OpportunityListResult {
  instrument_id: number;
  symbol: string;
  name: string;

  quote_price: number | null;
  quote_data_state: string | null;
  quote_as_of: string | null;

  market_score: number | null;
  personal_score: number | null;
  portfolio_fit_score: number | null;
  data_quality_score: number;

  technical_score: number | null;
  fundamental_score: number | null;
  news_score: number | null;
  risk_reward_score: number | null;

  market_view: string;
  personal_action: string | null;

  reason_codes: string[];
  warnings: string[];

  missing_data: boolean;
  decision_state: string;
  calculated_at: string;
  engine_version: string;

  selected_portfolio_id: number | null;
  
  current_position_quantity: number | null;
  current_position_market_value: number | null;
  current_position_weight_percentage: number | null;

  recommended_budget: number | null;
  recommended_quantity: number | null;
  recommended_target_weight: number | null;

  max_executable_budget: number | null;
  max_executable_quantity: number | null;
  theoretical_max_additional_budget: number | null;
  hard_max_weight: number | null;

  estimated_post_trade_weight: number | null;

  sizing_state: string | null;
  sizing_reason_codes: string[] | null;
}

// Ensure backward compatibility or same interface for detail
export type OpportunityDetailResult = OpportunityListResult;
