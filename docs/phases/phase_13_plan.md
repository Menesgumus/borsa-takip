# Phase 13: Opportunity Scanner

**Goal**: Provide a ranked list of instruments based on deterministic Market View (Raw Opportunity), filtered and adjusted by Personal Portfolio Fit (User Fit).

## Tasks
1. **T01 - Scanner Engine**
   - Implement scan_opportunities(portfolio_id=None) in ackend/app/services/scanner.py.
   - Iterate over active instruments, run the existing Phase 10 evaluate_decision logic for each.
   - Separate aw_score (overall_market_score) from user_fit_score (portfolio_fit_score).

2. **T02 - Rules & Suppression**
   - Explicitly suppress (filter out or mark as HOLD) instruments with STALE or MISSING data.
   - Implement deterministic sorting (by aw_score DESC, then symbol ASC to prevent tie-break randomness).

3. **T03 - API Endpoint**
   - GET /api/v1/opportunities?portfolio_id={id}
   - Returns a typed list of OpportunityResult.

4. **T04 - Frontend UI**
   - rontend/app/(protected)/opportunities/page.tsx
   - Show table/cards with Raw Score vs User Fit.

5. **T05 - Tests**
   - Test data-quality suppression, stable ranking, and differing user-fit scores for the same instrument across different portfolios.
