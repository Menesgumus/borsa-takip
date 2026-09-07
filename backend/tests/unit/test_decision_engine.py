import pytest
from decimal import Decimal
from app.schemas.decision import (
    TechnicalInputs, FundamentalInputs, NewsInputs, PortfolioFitInputs, Horizon
)
from app.services.decision_engine import evaluate_decision
from app.db.models import DecisionAction

def test_strong_favorable_al():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("25"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    fund = FundamentalInputs(pe_ratio=Decimal("10"), pb_ratio=Decimal("1.5"))
    news = NewsInputs(sentiment_score=Decimal("90"))
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, news)
    # tech: 50 + 20 + 15 + 15 = 100. fund: 50 + 25 + 25 = 100. news: 90. 
    # score = 100*0.4 + 100*0.4 + 90*0.2 = 40 + 40 + 18 = 98 >= 80 -> STRONG_BUY
    assert res.market_view == DecisionAction.STRONG_BUY
    assert res.overall_market_score == Decimal("98")

def test_favorable_caution_kademeli_al():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("40"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    fund = FundamentalInputs(pe_ratio=Decimal("20"), pb_ratio=Decimal("3"))
    news = NewsInputs(sentiment_score=Decimal("60"))
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, news)
    # tech: 50 + 15 + 15 = 80. fund: 50. news: 60.
    # score = 80*0.4 + 50*0.4 + 60*0.2 = 32 + 20 + 12 = 64 >= 60 -> BUY
    assert res.market_view == DecisionAction.BUY

def test_mixed_bekle():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("50"), macd_line=Decimal("1"), macd_signal=Decimal("2"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    fund = FundamentalInputs(pe_ratio=Decimal("20"), pb_ratio=Decimal("3"))
    news = NewsInputs(sentiment_score=Decimal("50"))
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, news)
    # tech: 50 - 15 + 15 = 50. fund: 50. news: 50.
    # score = 50. -> HOLD
    assert res.market_view == DecisionAction.HOLD

def test_unfavorable_kademeli_sat():
    tech = TechnicalInputs(current_price=Decimal("110"), rsi_14=Decimal("60"), macd_line=Decimal("-1"), macd_signal=Decimal("0"), sma_50=Decimal("120"), sma_200=Decimal("100"))
    fund = FundamentalInputs(pe_ratio=Decimal("35"), pb_ratio=Decimal("3"))
    news = NewsInputs(sentiment_score=Decimal("40"))
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, news)
    # tech: 50 - 15 - 15 = 20. fund: 50 - 25 = 25. news: 40.
    # score: 20*0.4 + 25*0.4 + 40*0.2 = 8 + 10 + 8 = 26 < 40 -> SELL
    assert res.market_view == DecisionAction.SELL

def test_strong_unfavorable_sat():
    tech = TechnicalInputs(current_price=Decimal("90"), rsi_14=Decimal("80"), macd_line=Decimal("-2"), macd_signal=Decimal("-1"), sma_50=Decimal("100"), sma_200=Decimal("120"))
    fund = FundamentalInputs(pe_ratio=Decimal("35"), pb_ratio=Decimal("6"))
    news = NewsInputs(sentiment_score=Decimal("10"))
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, news)
    # tech: 50 - 20 - 15 - 15 = 0. fund: 50 - 25 - 25 = 0. news: 10.
    # score = 0 + 0 + 2 = 2 < 20 -> STRONG_SELL
    assert res.market_view == DecisionAction.STRONG_SELL

def test_missing_critical_data_bekle():
    tech = TechnicalInputs(current_price=None)
    res = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs())
    assert res.market_view == DecisionAction.HOLD
    assert res.data_quality_score < Decimal("50")
    assert "MISSING_CURRENT_PRICE" in res.warnings

def test_stale_critical_data_bekle():
    tech = TechnicalInputs(current_price=Decimal("10"), rsi_14=None, macd_line=None, sma_50=None, is_stale=True)
    res = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs())
    # missing techs (-30), stale (-20) -> dq = 50. Wait! dq = 100 - 30 - 20 = 50. Is 50 < 50? No. So it might not be HOLD.
    # Actually if RSI is missing, tech_score is 50.
    assert res.data_quality_score == Decimal("50")
    # Let's test if dq < 50 triggers hold
    tech2 = TechnicalInputs(current_price=Decimal("10"), rsi_14=None, macd_line=None, sma_50=None, is_stale=True)
    res2 = evaluate_decision(1, Horizon.SHORT, tech2, FundamentalInputs(), NewsInputs(is_mock=True))
    assert res2.data_quality_score == Decimal("40")
    assert res2.market_view == DecisionAction.HOLD

def test_positive_market_view_concentration_limit_personal_bekle():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("25"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    fund = FundamentalInputs(pe_ratio=Decimal("10"), pb_ratio=Decimal("1.5"))
    news = NewsInputs(sentiment_score=Decimal("90"))
    pf = PortfolioFitInputs(current_weight=Decimal("35"), max_weight_limit=Decimal("30"))
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, news, pf)
    
    assert res.market_view == DecisionAction.STRONG_BUY
    assert res.personal_action == DecisionAction.HOLD
    assert "PORTFOLIO_CONCENTRATION_LIMIT" in res.warnings
    assert "RISK_LIMIT_EXCEEDED" in res.reason_codes

def test_portfolio_fit_favorable():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("25"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    pf = PortfolioFitInputs(current_weight=Decimal("0"), max_weight_limit=Decimal("30"))
    res = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs(), pf)
    # Fit score = 100
    assert res.portfolio_fit_score == Decimal("100")
    assert res.personal_action == DecisionAction.STRONG_BUY

def test_news_unavailable_not_negative():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("25"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    res = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs(sentiment_score=None))
    assert "NEWS_UNAVAILABLE" in res.warnings
    assert res.news_score is None
    # Tech: 100, Fund: 50. Weights: Tech 0.5, Fund 0.5 -> score 75 -> BUY
    assert res.market_view == DecisionAction.BUY

def test_mock_news_source_data_quality():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("50"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    res = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs(sentiment_score=Decimal("90"), is_mock=True))
    assert res.data_quality_score == Decimal("90")
    assert "LOW_DATA_QUALITY_MOCK_NEWS" in res.warnings

def test_same_input_exact_same_output():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("25"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    res1 = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs())
    res2 = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs())
    assert res1.overall_market_score == res2.overall_market_score

def test_market_only_vs_personalized():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("25"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    res_market = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs())
    assert res_market.personal_action is None
    
    pf = PortfolioFitInputs()
    res_personal = evaluate_decision(1, Horizon.SHORT, tech, FundamentalInputs(), NewsInputs(), pf)
    assert res_personal.personal_action is not None

def test_asset_type_without_equity_fundamentals():
    tech = TechnicalInputs(current_price=Decimal("150"), rsi_14=Decimal("50"), macd_line=Decimal("2"), macd_signal=Decimal("1"), sma_50=Decimal("140"), sma_200=Decimal("120"))
    fund = FundamentalInputs(pe_ratio=Decimal("10"), instrument_type="CRYPTO")
    res = evaluate_decision(1, Horizon.SHORT, tech, fund, NewsInputs())
    assert res.fundamental_score is None
    assert "FUNDAMENTALS_NOT_APPLICABLE" in res.warnings
