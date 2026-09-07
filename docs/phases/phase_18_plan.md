# Phase 18: PWA, Mobile Polish, Offline / Degraded Experience

**Goal**: Transform the web application into a Progressive Web App (PWA) with a polished mobile-first responsive design, touch-friendly UI, and safe degraded network/offline behavior.

## Tasks
1. **T01 - PWA Manifest & Icons**
   - Create public/manifest.json.
   - Add necessary PWA meta tags in rontend/app/layout.tsx.
   - Generate placeholder icons (labeled as placeholders).

2. **T02 - Service Worker & Offline Caching**
   - Use 
ext-pwa or custom service worker to cache the App Shell (static assets).
   - Ensure dynamic financial data is NEVER aggressively cached without a clear STALE indicator.
   - Clear sensitive cache on logout.

3. **T03 - Network State & Offline Safety UX**
   - Global NetworkProvider indicating ONLINE/OFFLINE/RECONNECTING.
   - Block offline portfolio mutations (BUY/SELL) with explicit error.
   - Mark cached decisions/prices as "STALE / OFFLINE / LAST KNOWN".
   - Disable AI Mentor while offline.

4. **T04 - Mobile Polish & Responsive Design**
   - Ensure 390px width layout works perfectly (no horizontal overflow).
   - Convert data-heavy tables (Opportunities, Alerts, Outcomes) to Card-based layouts on mobile.
   - Ensure touch-friendly buttons (min 44px recommended).

5. **T05 - Web Push Notification (Optional Foundations)**
   - Minimal opt-in permission flow for Alerts.
