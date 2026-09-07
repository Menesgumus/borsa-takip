# Phase 14: Alerts & Notifications

**Goal**: Implement a robust in-app alert system with cooldown and deduplication mechanics. No push notifications yet (reserved for Phase 18).

## Tasks
1. **T01 - Data Models & Enums**
   - Create AlertType enum (PRICE, RSI, KAP, NEWS, DECISION, CONCENTRATION, DAILY_LOSS).
   - Create AlertRule model.
   - Create UserNotification model.

2. **T02 - API Endpoints**
   - CRUD /api/v1/alerts/rules
   - GET /api/v1/alerts/notifications (with mark-as-read support)

3. **T03 - Evaluator Engine**
   - Create ackend/app/services/alerts.py.
   - Function evaluate_alert(rule, current_value, context_data) handling cooldown logic and duplicate suppression.

4. **T04 - Frontend**
   - /alerts UI for managing rules.
   - Notification history panel/indicator.

5. **T05 - Tests**
   - Test rule CRUD IDOR.
   - Test cooldown mechanics (preventing spam).
