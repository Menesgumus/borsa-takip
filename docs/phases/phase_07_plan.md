# Phase 07: Fundamentals + KAP + Macro + News Pipeline

**Goal**: Implement the foundational data models, API endpoints, and mock/simple providers for non-technical contextual data (KAP disclosures, news, macro events, and fundamentals). Ensure strict security against prompt injections in text data.

## Tasks
1. **T01 - Data Models & Migrations**
   - Create SQLAlchemy models for KAPDisclosure, NewsArticle, MacroEvent, and FundamentalData.
   - Ensure fields for factual data and sentiment separation exist.
   - Run Alembic migration.

2. **T02 - Ingestion Providers Base**
   - Create base classes/interfaces for KAPProvider, NewsProvider, and EVDSProvider.
   - Implement simple Mock providers to simulate incoming contextual data (KAP, News).

3. **T03 - API Endpoints**
   - Create GET /api/v1/instruments/{symbol}/context to fetch aggregated KAP, news, and fundamentals.
   - Ensure explicit separation between Facts (the news body) and Interpretation/Sentiment.

4. **T04 - Security Hardening**
   - Implement rigorous sanitization for all ingested text (malicious HTML stripping, prompt injection safeguards).
   - Write targeted tests for these security fixtures.

5. **T05 - Frontend Integration**
   - Update InstrumentDetail view to show a "News & KAP" tab or section containing sanitized context.

## Boundaries
- No actual LLM prompt execution yet (AI Mentor is Phase 11). "Factual extraction" and "sentiment" here refer to structuring data or relying on provider-supplied sentiment.
- Keep EVDS and KAP adapters as minimal/mock until actual production API keys/terms are verified by the user.
