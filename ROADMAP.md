# Borsa Takip Ã¢â‚¬â€ GeliÃ…Å¸tirme Roadmap'i

Tarih: 2026-09-05. **Planlama tamamlandÃ„Â±; implementation baÃ…Å¸lamadÃ„Â±.**

Tek nihai kaynak [BORSA_TAKIP_MASTER_SPEC.md](BORSA_TAKIP_MASTER_SPEC.md)'dir. Bu roadmap master'Ã„Â±n yerini almaz, gereksinimleri yeniden tanÃ„Â±mlamaz. Kaynak hash'i ve gerÃƒÂ§ek repository kanÃ„Â±tlarÃ„Â± [GAP_ANALYSIS.md](GAP_ANALYSIS.md)'dedir. YalnÃ„Â±z Phase 0'Ã„Â±n ayrÃ„Â±ntÃ„Â±lÃ„Â± gÃƒÂ¶rev planÃ„Â± [phase_00_plan.md](phase_00_plan.md)'dedir.

KullanÃ„Â±cÃ„Â±nÃ„Â±n bu ÃƒÂ§alÃ„Â±Ã…Å¸tÃ„Â±rmaya ÃƒÂ¶zel talebi nedeniyle bu dosya ve Phase 0 planÃ„Â± kÃƒÂ¶ktedir; master Ã‚Â§76'daki ilk ÃƒÂ§alÃ„Â±Ã…Å¸tÃ„Â±rmada implementation adÃ„Â±mÃ„Â± uygulanmamÃ„Â±Ã…Å¸tÃ„Â±r. Faz baÃ…Å¸lÃ„Â±klarÃ„Â± **0Ã¢â‚¬â€œ20 dahil 21 fazdÃ„Â±r**. TamamlanmÃ„Â±Ã…Å¸ faz yoktur.

## 1. Faz sÃ„Â±rasÃ„Â± ve baÃ…Å¸langÃ„Â±ÃƒÂ§ durumu

Zorunlu sÃ„Â±ra:

# Borsa Takip â€” GeliÅŸtirme Roadmap'i

Tarih: 2026-09-05. **Planlama tamamlandÄ±; implementation baÅŸlamadÄ±.**

Tek nihai kaynak [BORSA_TAKIP_MASTER_SPEC.md](BORSA_TAKIP_MASTER_SPEC.md)'dir. Bu roadmap master'Ä±n yerini almaz, gereksinimleri yeniden tanÄ±mlamaz. Kaynak hash'i ve gerÃ§ek repository kanÄ±tlarÄ± [GAP_ANALYSIS.md](GAP_ANALYSIS.md)'dedir. YalnÄ±z Phase 0'Ä±n ayrÄ±ntÄ±lÄ± gÃ¶rev planÄ± [phase_00_plan.md](phase_00_plan.md)'dedir.

KullanÄ±cÄ±nÄ±n bu Ã§alÄ±ÅŸtÄ±rmaya Ã¶zel talebi nedeniyle bu dosya ve Phase 0 planÄ± kÃ¶ktedir; master Â§76'daki ilk Ã§alÄ±ÅŸtÄ±rmada implementation adÄ±mÄ± uygulanmamÄ±ÅŸtÄ±r. Faz baÅŸlÄ±klarÄ± **0â€“20 dahil 21 fazdÄ±r**. TamamlanmÄ±ÅŸ faz yoktur.

## 1. Faz sÄ±rasÄ± ve baÅŸlangÄ±Ã§ durumu

Zorunlu sÄ±ra:

`00 â†’ 01 â†’ 02 â†’ 03 â†’ 04 â†’ 05 â†’ 06 â†’ 07 â†’ 08 â†’ 09 â†’ 10 â†’ 11 â†’ 12 â†’ 13 â†’ 14 â†’ 15 â†’ 16 â†’ 17 â†’ 18 â†’ 19 â†’ 20`

Her fazÄ±n giriÅŸ koÅŸulu Ã¶nceki fazÄ±n gerÃ§ek completion kanÄ±tÄ±yla kapanmasÄ±dÄ±r. AÅŸaÄŸÄ±da ek veri/domain baÄŸÄ±mlÄ±lÄ±klarÄ± ayrÄ±ca gÃ¶sterilir. Bir Ã¶nceki faz baÅŸarÄ±sÄ±zsa sonraki faz uygulanmaz. Alt gÃ¶revler bÃ¶lÃ¼nebilir; kapsam veya exit gate sessizce gevÅŸetilemez.

| Faz | KÄ±sa ad | Implementation durumu | Plan / kabul durumu |
|---|---|---|---|
| 00 | Governance, scaffold, quality baseline | `COMPLETED` | Phase 00 READY, CI ve QA tamam |
| 01 | Auth, user profile, security | `COMPLETED` | Phase 01 READY â€” commit 4b65b2c |
| 08 | Real/paper portfolio, journal | `NOT_IMPLEMENTED` | 07 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 09 | Risk, pre-trade what-if | `NOT_IMPLEMENTED` | 08 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 10 | Deterministic decisions | `NOT_IMPLEMENTED` | 09 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 11 | AI Mentor | `NOT_IMPLEMENTED` | 10 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 12 | Bilgi Merkezi | `NOT_IMPLEMENTED` | 11 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler; minimum MVP sÃ„Â±nÃ„Â±rÃ„Â± |
| 13 | Opportunity scanner | `NOT_IMPLEMENTED` | 12 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 14 | Alerts, notifications | `NOT_IMPLEMENTED` | 13 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 15 | Backtest | `NOT_IMPLEMENTED` | 14 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 16 | Outcomes, champion/challenger | `NOT_IMPLEMENTED` | 15 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 17 | Personal behavior analytics | `NOT_IMPLEMENTED` | 16 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 18 | PWA, offline, mobile polish | `NOT_IMPLEMENTED` | 17 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 19 | Performance hardening | `NOT_IMPLEMENTED` | 18 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |
| 20 | Security hardening, final release audit | `NOT_IMPLEMENTED` | 19 ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸Ã„Â±nÃ„Â± bekler |

## 2. Her faza uygulanan ortak kapÃ„Â±lar

Master Ã‚Â§0.4, Ã‚Â§33Ã¢â‚¬â€œ40, Ã‚Â§53, Ã‚Â§71 tÃƒÂ¼m fazlarÃ„Â±n kabul ÃƒÂ§erÃƒÂ§evesidir. Her faz planÃ„Â± kapsam/kapsam dÃ„Â±Ã…Å¸Ã„Â±, data model/migration, API/UI, test komutlarÃ„Â±, gÃƒÂ¼venlik, performans, mobil, veri doÃ„Å¸ruluÃ„Å¸u ve rollback'i aÃƒÂ§Ã„Â±kÃƒÂ§a tanÃ„Â±mlar. Ã„Â°lgisiz kontrol ancak gerekÃƒÂ§esiyle uygulanamaz olarak iÃ…Å¸aretlenebilir; ÃƒÂ§alÃ„Â±Ã…Å¸tÃ„Â±rÃ„Â±lmayan kontrol baÃ…Å¸arÃ„Â±lÃ„Â± sayÃ„Â±lamaz.

- **DoÃ„Å¸rulama:** Ã„Â°lgili unit, integration, migration, API contract, component, E2E, lint, typecheck, build; security static scan, secret ve dependency/image audit. Hatalar gizlenmez, kontroller kapatÃ„Â±lmaz.
- **GÃƒÂ¼venlik:** User scope/IDOR ilk user endpointinden; CSRF cookie mutations'ta; parameterized SQL/input limits; XSS/SSRF ve untrusted iÃƒÂ§erik ilgili entegrasyondan itibaren; secret redaction, rate limits, audit ve privacy. Phase 20 ilk gÃƒÂ¼venlik uygulamasÃ„Â± deÃ„Å¸ildir.
- **Veri:** UTC internal / Europe-Istanbul varsayÃ„Â±lan gÃƒÂ¶sterim; backend Decimal/NUMERIC para muhasebesi; missing Ã¢â€°Â  0; source/source_timestamp/ingested_at/freshness; immutable decision ve correction ledger. LLM ve frontend authoritative finansal hesap kaynaÃ„Å¸Ã„Â± deÃ„Å¸ildir.
- **DayanÃ„Â±klÃ„Â±lÃ„Â±k:** Bounded timeout/retry, idempotency, cache yaÃ…Å¸Ã„Â±nÃ„Â±n gÃƒÂ¶rÃƒÂ¼nÃƒÂ¼rlÃƒÂ¼Ã„Å¸ÃƒÂ¼, semantik/lisans uyumlu fallback, worker backpressure. Kritik eksik/stale veri gÃƒÂ¼ÃƒÂ§lÃƒÂ¼ aksiyon ÃƒÂ¼retemez; BEKLE ve reason code gerekir.
- **Mobil/eriÃ…Å¸ilebilirlik:** UI olan her fazda 360/390/430 telefon, tablet portrait ve landscape, 1280+ ve geniÃ…Å¸ desktop; overflow/nav/touch (~44 CSS px)/dialog/chart/table/safe area. Otomatik viewport + gerekli gerÃƒÂ§ek gÃƒÂ¶rsel/touch/keyboard incelemesi. Phase 18'e ertelenmez.
- **KapanÃ„Â±Ã…Å¸:** GerÃƒÂ§ek ÃƒÂ§Ã„Â±ktÃ„Â±larla completion; kritik baÃ…Å¸arÃ„Â±sÃ„Â±zlÃ„Â±k varsa `NOT READY`. Scaffold veya UI mock, domain feature tamamlandÃ„Â± anlamÃ„Â±na gelmez.

### Sabit performans bÃƒÂ¼tÃƒÂ§eleri ve kanÃ„Â±t ayrÃ„Â±mÃ„Â±

| Alan | Master hedefi | Ãƒâ€“lÃƒÂ§ÃƒÂ¼m/gate |
|---|---|---|
| Web | Production p75 LCP Ã¢â€°Â¤2.5s, INP Ã¢â€°Â¤200ms, CLS Ã¢â€°Â¤0.1 | Ã„Â°lk UI'dan production build lab kontrolÃƒÂ¼ ve bundle baseline; gerÃƒÂ§ek field p75 yalnÃ„Â±z yeterli gerÃƒÂ§ek ÃƒÂ¶lÃƒÂ§ÃƒÂ¼m varsa. Lighthouse skoru INP/p75 kanÃ„Â±tÃ„Â±nÃ„Â±n yerine geÃƒÂ§mez. |
| Latest quote | Cache hit p95 <150ms | Phase 3/4'ten itibaren belirtilmiÃ…Å¸ dataset, altyapÃ„Â±, concurrency ve cache durumuyla |
| Dashboard | Cache hit p95 <400ms | Phase 4'ten aggregated/paralel fetch, request count ve N+1 kontrolÃƒÂ¼ |
| Candles | YaygÃ„Â±n instrument 1Y daily p95 <500ms | Phase 3'ten indeks/EXPLAIN, bounded range ve cold/warm karÃ…Å¸Ã„Â±laÃ…Å¸tÃ„Â±rmasÃ„Â± |
| Chart | 2K ve 10K nokta benchmark; her tick full series reset yok | Phase 4'ten load/render/update/network/memory ve mobil touch kayÃ„Â±tlarÃ„Â± |
| Scanner | 100/500/1000 instrument benchmark | Phase 13 worker throughput; request-time tarama yok |
| Phase 0 | Empty app bundle ve health latency baseline | SayÃ„Â±sal saÃ„Å¸lÃ„Â±k endpoint SLA'sÃ„Â± master'da yok; ÃƒÂ¶lÃƒÂ§ÃƒÂ¼mÃƒÂ¼n kendisi zorunlu, finans endpoint hedefi uydurulmaz |

AynÃ„Â± provider verisinin tekrar ÃƒÂ§ekilmesi, unbounded history, gereksiz polling/rerender, synchronous aÃ„Å¸Ã„Â±r AI/hesap, N+1 ve cache invalidation her ilgili fazda incelenir. Phase 19 mevcut bÃƒÂ¼tÃƒÂ§elerdeki regresyonlarÃ„Â± ÃƒÂ¶lÃƒÂ§ÃƒÂ¼mle giderir.

## 3. Faz hedefleri, giriÃ…Å¸leri ve ÃƒÂ§Ã„Â±kÃ„Â±Ã…Å¸larÃ„Â±

### Phase 0 Ã¢â‚¬â€ PROJECT GOVERNANCE, SCAFFOLD, QUALITY BASELINE

- **Hedef/kapsam:** Monorepo, minimal Next.js/FastAPI app, PostgreSQL/Redis Compose, env/lockfiles, ADR, baseline Alembic, health/error/correlation, CI kalite zinciri. Finans ÃƒÂ¶zelliÃ„Å¸i yok.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Tam master okumasÃ„Â± ve repo denetimi tamam; kaynak deÃ„Å¸iÃ…Å¸ikliklerini yeniden kontrol et. Docker daemon E12 ile eriÃ…Å¸ilebilir; gerÃƒÂ§ek Compose, package install ve remote CI halen doÃ„Å¸rulanacak.
- **Test:** Clean clone startup, DB/Redis integration, clean migration, frontend build, backend/component/API/E2E smoke, lint/type/format ve gerÃƒÂ§ek CI.
- **GÃƒÂ¼venlik:** Secret scan, static/dependency/image audit; fake env, loopback local eriÃ…Å¸im, unsafe public config fail-fast, log redaction.
- **Performans:** Empty production bundle ve health latency baseline, bounded dependency timeout.
- **Mobil:** Minimal kabuk telefon/tablet/desktop, keyboard/focus/overflow; mevcut kontrollerin touch hedefi. Grafik olmadÃ„Â±Ã„Å¸Ã„Â± iÃƒÂ§in chart touch testi gerekÃƒÂ§eli uygulanamaz.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** UTC config, migration lifecycle; domain tablo/ledger/sayÃ„Â± hesaplarÃ„Â± kurulmaz. Decimal ve ilerideki doÃ„Å¸rulama politikasÃ„Â± belgelenir.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Master'Ã„Â±n **`PHASE 0 READY` yalnÃ„Â±z CI tamamen yeÃ…Å¸ilse** Ã…Å¸artÃ„Â± ve ilgili diÃ„Å¸er baseline kontrollerin gerÃƒÂ§ek kanÃ„Â±tÃ„Â±. PlanÃ„Â±n hazÃ„Â±r olmasÃ„Â± bu kapÃ„Â±yÃ„Â± geÃƒÂ§irmez.

### Phase 1 Ã¢â‚¬â€ AUTH, USER PROFILE, SECURITY FOUNDATION

- **Hedef/kapsam:** users/auth/profile schema, Argon2id, session/cookie rotation-revoke, ownership dependency, audit temeli, onboarding/settings/risk limits.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 0 READY; env/DB/migration/CI. Public auth tasarÃ„Â±mÃ„Â± fail-closed; local bypass yalnÃ„Â±z explicit loopback koÃ…Å¸uluyla.
- **Test:** Login success/fail, expiration/logout/revoke, session rotation, CSRF, user-scoped IDOR fixtures, profile sÃ„Â±nÃ„Â±rlarÃ„Â±, migration ve form E2E.
- **GÃƒÂ¼venlik:** Login rate limit, secure HttpOnly/SameSite cookie, CSRF, hashed password; auth/audit log redaction ve hesaplar arasÃ„Â± izolasyon.
- **Performans:** Password hash maliyeti ÃƒÂ¶lÃƒÂ§ÃƒÂ¼mÃƒÂ¼, bounded login resource kullanÃ„Â±mÃ„Â±, profil query sayÃ„Â±sÃ„Â± ve bundle farkÃ„Â±.
- **Mobil:** Onboarding/settings form, hata mesajÃ„Â±, klavye, focus, touch ve tÃƒÂ¼m viewportlar.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Profile yÃƒÂ¼zde/vade/enum/timezone doÃ„Å¸rulamasÃ„Â±; boÃ…Å¸ profile sÃ„Â±fÃ„Â±r risk varsayÃ„Â±lmaz; audit safe diff.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **User-scoped test olmadan finance data fazÃ„Â±na geÃƒÂ§ilmez.** Auth lifecycle, ownership ve profile E2E kanÃ„Â±tlÃ„Â±dÃ„Â±r.

### Phase 2 Ã¢â‚¬â€ INSTRUMENT MASTER + PROVIDER ABSTRACTION

- **Hedef/kapsam:** Instruments/mappings, quote DTO/freshness, provider interfaces ve deterministic mock, health, retry/rate-limit/circuit davranÃ„Â±Ã…Å¸Ã„Â±.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 1 READY; ownership testleri ve DB temeli. Provider seÃƒÂ§imi ayrÃ„Â± config, domain provider payload gÃƒÂ¶rmez.
- **Test:** Mock full contract, mapping/unit/UTC normalization, malformed payload/timeout/outage, freshness ve typed error fixture'larÃ„Â±.
- **GÃƒÂ¼venlik:** Provider secret server-side; host allowlist/SSRF sÃ„Â±nÃ„Â±rÃ„Â±; timeout/size/input limits. KullanÃ„Â±cÃ„Â± URL'si doÃ„Å¸rudan fetch edilmez.
- **Performans:** Batch quote sÃƒÂ¶zleÃ…Å¸mesi, retry cap/circuit/backpressure tasarÃ„Â±mÃ„Â±; outage request'i sÃ„Â±nÃ„Â±rsÃ„Â±z bloke etmez.
- **Mobil:** UI eklenmezse gerekÃƒÂ§eli uygulanamaz; health/freshness frontend DTO tÃƒÂ¼ketimine uygundur.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Canonical/native symbol ayrÃ„Â±mÃ„Â±, UUID/exchange/currency, explicit freshness, unknown timestamp durumlarÃ„Â±, negative/zero price reddi.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Mock provider ile full contract test; gerÃƒÂ§ek provider ayrÃ„Â± config.** Provider down uygulamayÃ„Â± ÃƒÂ§ÃƒÂ¶kertmez; mock gerÃƒÂ§ek/canlÃ„Â± gibi sunulmaz.

### Phase 3 Ã¢â‚¬â€ MARKET DATA INGESTION + HISTORICAL STORE

- **Hedef/kapsam:** Quote Redis cache, candles DB/index/unique policy, ayrÃ„Â± worker, checkpoint/batch ingest, gap ve timezone/final/adjusted yÃƒÂ¶netimi.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 2 READY; gerÃƒÂ§ek kaynak iÃƒÂ§in gÃƒÂ¶sterim/cache/history/rate-limit lisans kanÃ„Â±tÃ„Â±. EriÃ…Å¸im yoksa mock doÃ„Å¸rulama ayrÃ„Â±lÃ„Â±r, gerÃƒÂ§ek entegrasyon tamamlandÃ„Â± denmez.
- **Test:** Duplicate/out-of-order/non-final/missing/stale candles; holiday/yarÃ„Â±m seans, BIST kapalÃ„Â±/kripto aÃƒÂ§Ã„Â±k, wrong-timezone, retry/restart/checkpoint idempotency.
- **GÃƒÂ¼venlik:** Provider egress/SSRF/credentials; queue payload ve Redis izolasyonu; admin diagnostics varsa yetki sÃ„Â±nÃ„Â±rÃ„Â±.
- **Performans:** Batch ingest ÃƒÂ¶lÃƒÂ§ÃƒÂ¼mÃƒÂ¼, query `EXPLAIN`, 1Y history ve quote budget, cache cold/warm/hit ratio, pool/queue metrics; historical data tekrar ÃƒÂ§ekilmez.
- **Mobil:** Bu fazda yeni UI yoksa uygulanamaz; freshness ve bounded payload contract'Ã„Â± korunur.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Raw/adjusted provenance ve point-in-time policy, data version, source/ingest UTC, source mismatch, gap repair; corporate-action future leakage ÃƒÂ¶nlenir.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Master testleri + idempotent pipeline, index/benchmark ve outage/freshness kanÃ„Â±tlarÃ„Â±; kaynak lisansÃ„Â± ÃƒÂ§ÃƒÂ¶zÃƒÂ¼msÃƒÂ¼zse gerÃƒÂ§ek data gate kapalÃ„Â±dÃ„Â±r.

### Phase 4 Ã¢â‚¬â€ MARKET DASHBOARD + HIGH-QUALITY CHART FOUNDATION

- **Hedef/kapsam:** Temel dashboard/Piyasalar/detail, global instrument search, user-scoped watchlist; mum/hacim/timeframe, loading/error/empty/stale, provenance. Sonraki motorlara ait skorlar uydurulmaz.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 3 READY; quote/history contracts, Phase 1 user scope; chart sÃƒÂ¼rÃƒÂ¼mÃƒÂ¼/attribution Ã…Å¸artÃ„Â± doÃ„Å¸rulanÃ„Â±r.
- **Test:** Route/API/component/E2E, watchlist isolation, chart resize/incremental update/reconnect, empty/stale/outage; desktop+mobile screenshot incelemesi.
- **GÃƒÂ¼venlik:** Search rate/input limit; watchlist IDOR/CSRF; safe links; attribution; secret iÃƒÂ§ermeyen client bundle.
- **Performans:** 2K/10K chart benchmark, her tick full `setData` ve history reload yok; dashboard <400ms, query count/batch, lazy chart/targeted cache update; Web vitals lab kontrolÃƒÂ¼.
- **Mobil:** 360/390/430 zorunlu; tablet/desktop, touch pan/zoom/tooltip, collapsible controls, card/table ve safe-area navigation.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Price/source/as_of/delay, axis/units/timezone/percent, missing session gaps; closed market ve stale farklÃ„Â±dÃ„Â±r.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Chart desktop+mobile manual screenshot inspection + automated viewport tests**; performans ve freshness kanÃ„Â±tÃ„Â±. Briefing/portfolio/alerts gibi sonraki parÃƒÂ§alar tamamlandÃ„Â± sayÃ„Â±lmaz.

### Phase 5 Ã¢â‚¬â€ TECHNICAL ANALYSIS ENGINE

- **Hedef/kapsam:** SMA/EMA/RSI/MACD/Bollinger/ATR/hacim, trend/horizon configs, versioned analysis snapshots, UI cards ve chart panes.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 4 READY; kaliteli candles, worker ve chart. FormÃƒÂ¼l/smoothing/warm-up seÃƒÂ§imi resmi/birincil matematik referansÃ„Â± ve ADR/testle aÃƒÂ§Ã„Â±klanÃ„Â±r.
- **Test:** Her gÃƒÂ¶sterge golden + flat/monotonic/insufficient/missing/non-final/zero-volume/split fixture; determinism ve invariant/property testler.
- **GÃƒÂ¼venlik:** History/period input limits, backend-only calculation, typed boundary; kullanÃ„Â±cÃ„Â± snapshot scope varsa ownership.
- **Performans:** Worker precompute, yeni candle ile invalidation; request'te tekrar aÃ„Å¸Ã„Â±r hesap yok; batch/latency/bundle regression.
- **Mobil:** Pane okunabilirliÃ„Å¸i, toggle/legend/touch, metin ÃƒÂ¶zeti; tÃƒÂ¼m viewportlarda chart ve score cards.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Numerical tolerance gerekÃƒÂ§eli; authoritative para float'a dÃƒÂ¶nÃƒÂ¼Ã…Å¸mez; input timestamp/formula version, warm-up boÃ…Å¸luÃ„Å¸u, skor sahte kesinlik deÃ„Å¸il.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Golden testler olmadan kapanmaz.** Ã„Â°ndikatÃƒÂ¶r ve chart ÃƒÂ§Ã„Â±ktÃ„Â±sÃ„Â±nÃ„Â±n aynÃ„Â± backend snapshot'Ã„Â±nÃ„Â± kullandÃ„Â±Ã„Å¸Ã„Â± doÃ„Å¸rulanÃ„Â±r.

### Phase 6 Ã¢â‚¬â€ PATTERN + SUPPORT/RESISTANCE ENGINE

- **Hedef/kapsam:** Deterministik candle/chart pattern, swing/destek-direnÃƒÂ§, seÃƒÂ§ilmiÃ…Å¸ pattern kalite/invalidation/version, chart overlay.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 5 READY; validated candles/trends ve chart panes. Master Ã‚Â§9.5 ilk set; flag/pennant sonrasÃ„Â± ayrÃ„Â± iterasyon.
- **Test:** Synthetic positive/negative ve false-positive regression; boundary/insufficient history, confirmation timestamp ve yeniden ÃƒÂ¼retilebilir detection.
- **GÃƒÂ¼venlik:** Bounded algorithm inputs; LLM gÃƒÂ¶rselinden pattern/aksiyon kaynaÃ„Å¸Ã„Â± yapÃ„Â±lmaz; safe overlay content.
- **Performans:** Worker/precompute ve dataset maliyeti; bÃƒÂ¼yÃƒÂ¼k overlay render ve mobil CPU/memory regresyonu.
- **Mobil:** Marker touch/popover, dates/quality/invalidation okunabilir; chart gesture ÃƒÂ§akÃ„Â±Ã…Å¸malarÃ„Â±.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Start/end + detection/confirmation time ayrÃ„Â±mÃ„Â±; ileride backtest'te saÃ„Å¸ taraftaki future barlara erken eriÃ…Å¸im yok; pattern Ã¢â€°Â  AL/SAT.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Pozitif/negatif ve false-positive test kanÃ„Â±tlarÃ„Â±; versioned detector ile overlay ve kalite tutarlÃ„Â±lÃ„Â±Ã„Å¸Ã„Â±. EÃ„Å¸itim/backtest linki 12/15 gelince baÃ„Å¸lanÃ„Â±r.

### Phase 7 Ã¢â‚¬â€ FUNDAMENTALS + KAP + MACRO + NEWS PIPELINE

- **Hedef/kapsam:** Normalized financials/fundamental scores, KAP, EVDS, haber adapter'larÃ„Â±; source tiers/dedup/entity mapping/factual extraction ve ayrÃ„Â± sentiment/yorum.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 6 READY; provider/domain sÃ„Â±nÃ„Â±rlarÃ„Â±. KAP API Ã…Å¸artlarÃ„Â±, EVDS key/series semantiÃ„Å¸i, haber ve varsa social izinleri doÃ„Å¸rulanmÃ„Â±Ã…Å¸ olmalÃ„Â±.
- **Test:** Payload contracts, financial ratio/missing/negative inputs, period/consolidation, future publication fixture, dedup, attachment-only KAP ve ingestion lag; injection/malicious HTML/oversize.
- **GÃƒÂ¼venlik:** SSRF host/DNS/IP/redirect/content-type/size, sanitize, untrusted_document, no remote tool instructions, credential redaction.
- **Performans:** Async batch + worker, disclosure index, new-report score invalidation, bounded retry ve pipeline metrics.
- **Mobil:** Fact ve interpretation bÃƒÂ¶lÃƒÂ¼mleri, uzun baÃ…Å¸lÃ„Â±k/kaynak/tarih, statement cards/tables ve attachment mesajlarÃ„Â±.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** published_at Ã¢â€°Â  fiscal_period_end; raw inputs/version korunur, missing Ã¢â€°Â  0, sector peer baÃ„Å¸lamÃ„Â±, Tier 3 resmÃƒÂ® kanÃ„Â±t deÃ„Å¸ildir.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Fact/interpretation UI separation verified**; izinli gerÃƒÂ§ek entegrasyon, injection ve finans doÃ„Å¸ruluk kanÃ„Â±tÃ„Â±. Eksik provider yetkisi gizlenmez.

### Phase 8 Ã¢â‚¬â€ PORTFOLIO + PAPER PORTFOLIO + JOURNAL

- **Hedef/kapsam:** AyrÃ„Â± real/paper ledger, transactions/reversal, derived positions, P/L/fees/tax/cash/FX, benchmark/cashflow-aware returns, journal ve dashboard ÃƒÂ¶zeti.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 7 READY; Phase 1 ownership ve Phase 3 quote/history. Accounting/quantization ve TWR/XIRR seÃƒÂ§imi ADR ile; gerÃƒÂ§ek veri yazÃ„Â±lmadan backup/correction planÃ„Â±.
- **Test:** Multiple buy/partial-full sell/oversell/fee/tax/dividend/cashflow/FX/tiny rounding/missing quote; empty/all-cash/backdated, concurrency/double-submit, restore ve ledger reconciliation.
- **GÃƒÂ¼venlik:** TÃƒÂ¼m portfolio/transaction/journal IDOR ve CSRF, input/overflow, atomic writes/idempotency, audit safe diff; private exports/cache/log.
- **Performans:** Portfolio/executed_at index; batch valuation, transaction+quote invalidation, derived snapshot ledger'Ã„Â±n yerine geÃƒÂ§mez.
- **Mobil:** Real/paper ayrÃ„Â±mÃ„Â±, hÃ„Â±zlÃ„Â± reason form, history cards/secondary details, allocation/performance/benchmark chart ve empty state.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Decimal exact accounting; deposits getiri deÃ„Å¸ildir; weights cash dahil ~100%, missing quote sÃ„Â±fÃ„Â±r deÃ„Å¸il, immutable history/correction, short selling yok.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Ledger invariant tests %100 pass**; authoritative ledgerÃ¢â€ â€positions ve benchmark/math testleri, owner isolation, backup etkisi kanÃ„Â±tlÃ„Â±dÃ„Â±r.

### Phase 9 Ã¢â‚¬â€ RISK ENGINE + PRE-TRADE WHAT-IF

- **Hedef/kapsam:** Concentration/cash floor/position size/drawdown/volatility, yeterli veride correlation/liquidity; no-mutation what-if ve stop/target ÃƒÂ¶nerisi.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 8 READY; validated ledger/profile/history ve accounting policy.
- **Test:** Limit boundary, what-if ÃƒÂ¶ncesi/sonrasÃ„Â± aÃ„Å¸Ã„Â±rlÃ„Â±k, all-cash/missing history, correlation sample gate; DB'nin mutate edilmediÃ„Å¸i assertion.
- **GÃƒÂ¼venlik:** Ownership/rate/input validation, sensitive aggregate exposure, hesapla/kaydet akÃ„Â±Ã…Å¸larÃ„Â±nÃ„Â±n aÃƒÂ§Ã„Â±k ayrÃ„Â±mÃ„Â±.
- **Performans:** Bounded simulation, cache keys user/portfolio/input version; hesap yoÃ„Å¸unluÃ„Å¸u worker/snapshot ile kontrollÃƒÂ¼.
- **Mobil:** Dedicated step/bottom sheet; bÃƒÂ¼yÃƒÂ¼k gÃƒÂ¶rÃƒÂ¼nÃƒÂ¼r risk uyarÃ„Â±sÃ„Â±, touch ve viewport'a sÃ„Â±Ã„Å¸ma.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Deterministik Decimal etkiler; korelasyon eksikliÃ„Å¸i sÃ„Â±fÃ„Â±r risk deÃ„Å¸il; gap/slippage stop garantisi deÃ„Å¸ildir; limit ihlali kullanÃ„Â±cÃ„Â± iÃ…Å¸lemini otomatik yasaklamaz.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** DB no-mutation ve sÃ„Â±nÃ„Â±r testleri, aÃƒÂ§Ã„Â±klanabilir risk sonuÃƒÂ§larÃ„Â± ve responsive UI kanÃ„Â±tÃ„Â±.

### Phase 10 Ã¢â‚¬â€ DETERMINISTIC DECISION ENGINE

- **Hedef/kapsam:** BeÃ…Å¸ aksiyon, normalization/horizon/versioned weights, quality gate, Market View/Personal Action, immutable snapshot/reasons/detail/watchlist kararlarÃ„Â±; basit test edilebilir regime context.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 9 READY; 5/6/7 sinyalleri, 8 portfÃƒÂ¶y, 9 risk, 3 freshness. BaÃ…Å¸langÃ„Â±ÃƒÂ§ weights bir performans garantisi deÃ„Å¸ildir.
- **Test:** Golden positive/negative/mixed/low-quality/concentration; tÃƒÂ¼m action sÃ„Â±nÃ„Â±rlarÃ„Â±, replay/version, stale/missingÃ¢â€ â€™BEKLE; overconcentration Market View deÃ„Å¸iÃ…Å¸tirmeden action dÃƒÂ¼Ã…Å¸ÃƒÂ¼rebilir.
- **GÃƒÂ¼venlik:** Decision config mutation audit ve eriÃ…Å¸im; private action isolation; LLM'den baÃ„Å¸Ã„Â±msÃ„Â±z deterministik karar.
- **Performans:** Snapshot references, critical-input invalidation/version cache key, gereksiz request recompute yok.
- **Mobil:** Karar/detail/risk/reasons/vade, portfolio what-if linki ve chart baÃ„Å¸lantÃ„Â±larÃ„Â±; gÃƒÂ¼venilirlik ve data as_of gÃƒÂ¶rÃƒÂ¼nÃƒÂ¼r.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Reliability baÃ…Å¸arÃ„Â± ihtimali olarak sunulmaz; degraded KAP politikasÃ„Â± ÃƒÂ¶nceden sÃƒÂ¼rÃƒÂ¼mlÃƒÂ¼dÃƒÂ¼r; kritik market data yoksa BEKLE.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Golden karar ve replay/immutable/data safety kanÃ„Â±tlarÃ„Â±. Backtest motoru 15'e aittir; ÃƒÂ¼retim aÃ„Å¸Ã„Â±rlÃ„Â±k deÃ„Å¸iÃ…Å¸imi 15/16 evidence/governance olmadan yapÃ„Â±lmaz.

### Phase 11 Ã¢â‚¬â€ AI MENTOR

- **Hedef/kapsam:** Tool-first orchestration/chat, typed LLM aÃƒÂ§Ã„Â±klama, seviyeye gÃƒÂ¶re kÃ„Â±sa/detaylÃ„Â± yanÃ„Â±t, quick actions, privacy-aware conversations, kaynak/zaman; cached personal Daily Briefing.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 10 READY; domain facts/decisions ve user scope. LLM saÃ„Å¸layÃ„Â±cÃ„Â±sÃ„Â±na gÃƒÂ¶nderilecek minimum context ve retention politikasÃ„Â± belirli.
- **Test:** Action override reddi, olmayan price/KAP claim validation, malicious news injection, unknown symbol, missing tool ve AI outage; cache kullanÃ„Â±cÃ„Â± izolasyonu/conversation deletion.
- **GÃƒÂ¼venlik:** Prompt server-side, tool/argument allowlist, rate/token limits, sanitized Markdown, no arbitrary shell/URL, IDOR/CSRF, minimum sensitive context/log.
- **Performans:** Her render'da AI ÃƒÂ§aÃ„Å¸rÃ„Â±sÃ„Â± yok; snapshot/user briefing cache, bounded/async generation ve progress/degraded cevap; latency/cost metrics.
- **Mobil:** Chat keyboard/scroll, quick prompts, sources ve clear action, accessible messages.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** SayÃ„Â±lar backend/tool'dan, action sadece engine'den; stale risk gizlenmez; AI unavailable core hesaplarÃ„Â± durdurmaz.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Safety fixtures, gerÃƒÂ§ek tool integration ve source/numeric doÃ„Å¸rulama; kÃ„Â±sa TÃƒÂ¼rkÃƒÂ§e yanÃ„Â±t ve fallback kanÃ„Â±tÃ„Â±.

### Phase 12 Ã¢â‚¬â€ BÃ„Â°LGÃ„Â° MERKEZÃ„Â° + VISUAL EDUCATION

- **Hedef/kapsam:** Master Phase 12'deki 20 ilk kavram, canonical article/revision, search/ask/levels, deterministic visuals, glossary ve pattern eÃ„Å¸itim baÃ„Å¸lantÃ„Â±larÃ„Â±, ÃƒÂ¶Ã„Å¸renme ilerleme gÃƒÂ¶rÃƒÂ¼nÃƒÂ¼mÃƒÂ¼.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 11 READY; doÃ„Å¸rulanmÃ„Â±Ã…Å¸ domain kavramlarÃ„Â±, Mentor explanation level. EÃ„Å¸itsel temsili veri aÃƒÂ§Ã„Â±k etiketli.
- **Test:** Article schema/search/links, content technical+plain-language QA, misuse warning, visual-to-data doÃ„Å¸ruluÃ„Å¸u, component/E2E/a11y.
- **GÃƒÂ¼venlik:** Safe content/Markdown, content revision ownership, ask rate limit, canonical source governance; AI yeni kesin kural uyduramaz.
- **Performans:** Canonical content cache, lazy visuals, her kavram iÃƒÂ§in gereksiz AI ÃƒÂ§aÃ„Å¸rÃ„Â±sÃ„Â± yok; web budget/bundle kontrolÃƒÂ¼.
- **Mobil:** Popover/detail/interactive visual controls ve metin ÃƒÂ¶lÃƒÂ§ekleme tÃƒÂ¼m viewportlarda.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Her gÃƒÂ¶rsel gerÃƒÂ§ek/temsili ayrÃ„Â±mÃ„Â±, formÃƒÂ¼l/smoothing review, 30/70 gibi eÃ…Å¸ikler tek baÃ…Å¸Ã„Â±na AL/SAT deÃ„Å¸ildir.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Her canonical article iÃƒÂ§in teknik/sade anlatÃ„Â±m/yanÃ„Â±ltma sÃ„Â±nÃ„Â±rÃ„Â± review ve ÃƒÂ¶Ã„Å¸renme akÃ„Â±Ã…Å¸Ã„Â± E2E. **Minimum kullanÃ„Â±labilir ÃƒÂ¼rÃƒÂ¼n 0Ã¢â‚¬â€œ12; public izin anlamÃ„Â±na gelmez.**

### Phase 13 Ã¢â‚¬â€ FIRSAT TARAYICI + PERSONALIZED RANKING

- **Hedef/kapsam:** Worker universe scanner, filters/raw score/user fit/reasons, fÃ„Â±rsatlar sayfasÃ„Â± ve dashboard kiÃ…Å¸isel fÃ„Â±rsat alanÃ„Â±.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 12 READY; Phase 10 decisions, 9 risk, 3 universe/history/cache.
- **Test:** Filter/order/tie/empty/stale, aynÃ„Â± varlÃ„Â±k farklÃ„Â± portfÃƒÂ¶y uygunluÃ„Å¸u, snapshot versions ve account isolation.
- **GÃƒÂ¼venlik:** User-scoped ranking cache, filter/range validation/rate limits; manipÃƒÂ¼latif yatÃ„Â±rÃ„Â±m dili yok.
- **Performans:** **Request-time scanner yok; 100/500/1000 instrument benchmark**; worker throughput/queue depth/batch ve paginated liste.
- **Mobil:** Desktop table/mobile cards, filtre drawer, neden/risk/as_of eriÃ…Å¸ilebilirliÃ„Å¸i.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Raw fÃ„Â±rsat ile user-fit ayrÃ„Â±dÃ„Â±r; stale girdi gÃƒÂ¼ÃƒÂ§lÃƒÂ¼ fÃ„Â±rsat gibi gÃƒÂ¶rÃƒÂ¼nmez; kaynak/reason/version trace.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Benchmark raporu ve personalized ranking contract/UI testleri; garanti getiri iddiasÃ„Â± yok.

### Phase 14 Ã¢â‚¬â€ ALERTS + NOTIFICATIONS

- **Hedef/kapsam:** Price/RSI/KAP/news/decision/concentration/daily-loss rules, worker evaluation/dedup/cooldown/in-app history; watchlist shortcut ve dashboard alerts.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 13 READY; 3/5/7/9/10 event ve snapshotlarÃ„Â±, user scope. Push temeli opsiyonel, ana push 18.
- **Test:** Boundary crossing once, repeated same price no-spam, decision transition, failed delivery/retry/idempotency, stale provider no-misleading alarm.
- **GÃƒÂ¼venlik:** Alert IDOR/CSRF/input/rate limit; delivery destination validation, notification privacy.
- **Performans:** Worker batch/event fingerprint, cooldown, pagination; gereksiz polling ve tekrar provider fetch yok.
- **Mobil:** Rule form, unread/history/action navigation, safe area/touch; FOMO'suz metin.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** OlayÃ„Â±n source/as_of/fingerprint'Ã„Â±, stale quote alarmÃ„Â± tetiklemez; daily loss hesabÃ„Â± cash injection ile karÃ„Â±Ã…Å¸maz.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Dedup/state transition ve stale suppression kanÃ„Â±tÃ„Â±; in-app ruleÃ¢â€ â€™eventÃ¢â€ â€™history E2E.

### Phase 15 Ã¢â‚¬â€ BACKTEST ENGINE

- **Hedef/kapsam:** Strategy spec, event-safe data access, execution/cost/slippage, benchmark, frozen train/validation/test veya walk-forward/OOS; ÃƒÂ§oklu sonuÃƒÂ§ metriÃ„Å¸i/UI.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 14 READY; 3/7 point-in-time veri/provenance, 5/6/10 sÃƒÂ¼rÃƒÂ¼mlÃƒÂ¼ sinyaller. Universe/delist/corporate-action/publication yeterliliÃ„Å¸i doÃ„Å¸rulanmadan baÃ…Å¸arÃ„Â± deÃ„Å¸erlendirmesi aÃƒÂ§Ã„Â±lamaz.
- **Test:** Deliberate future/publication leakage, post-close fill, future-adjustment, surviving-only universe fixtures; aynÃ„Â± version/hash/params sonucu; holdout izolasyonu ve hindsight/repeated-test optimization yasaÃ„Å¸Ã„Â±.
- **GÃƒÂ¼venlik:** Expensive-run rate/resource limit, queue sandbox/input validation, user-owned result access; arbitrary strategy code/shell feature'Ã„Â± eklenmez.
- **Performans:** AyrÃ„Â± worker, dataset reuse/index/bounded jobs/backpressure, repeatable load ve result pagination.
- **Mobil:** Equity/drawdown/benchmark chart, cost/assumption/sample sayÃ„Â±sÃ„Â± ve limitations okunabilir; responsive result table.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Costs Ã¢â€°Â  varsayÃ„Â±lan sÃ„Â±fÃ„Â±r, publication zamanÃ„Â±na baÃ„Å¸lÃ„Â± eriÃ…Å¸im, corporate actions ve historical universe; win-rate tek metrik deÃ„Å¸il, sample/CI uygunluÃ„Å¸uyla CAGR/return/drawdown/expectancy/turnover/benchmark.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Completion'da ayrÃ„Â± bias audit:** look-ahead, publication, corporate actions, costs, survivorship. Bias kanÃ„Â±tÃ„Â± olmayan test baÃ…Å¸arÃ„Â± diye sunulmaz; veri eksikliÃ„Å¸i gate'i bloke eder. Backtest gelecek getiri garantisi deÃ„Å¸ildir.

### Phase 16 Ã¢â‚¬â€ DECISION OUTCOME TRACKING + CHAMPION/CHALLENGER

- **Hedef/kapsam:** +1/5/20/60 iÃ…Å¸lem gÃƒÂ¼nÃƒÂ¼ ve horizon outcomes, benchmark/sector/regime/action segmentleri, challenger/shadow ve bounded promotion.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 15 READY; immutable decisions/data versions, OOS/bias-safe evaluation.
- **Test:** Trading-day alignment, insufficient forward history, min N/confidence bounds/max change, rejected risk regression, replay/promotion/rollback.
- **GÃƒÂ¼venlik:** Versioned approval ve config audit, yalnÃ„Â±z yetkili promotion; her kayÃ„Â±pta otomatik production weight mutation yok.
- **Performans:** Daily idempotent worker, incremental forward outcomes, bounded shadow evaluation ve segment index.
- **Mobil:** Segment/performance/champion-challenger sunumu varsa okunabilir controls/table/chart ve aÃƒÂ§Ã„Â±klamalÃ„Â± ÃƒÂ¶rnek sayÃ„Â±sÃ„Â±.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Outcome yalnÃ„Â±z window tamamlanÃ„Â±nca, SAT opportunity cost/BEKLE davranÃ„Â±Ã…Å¸Ã„Â±; sample support ve benchmark, no hindsight tuning.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Governance gate olmadan otomatik production aÃ„Å¸Ã„Â±rlÃ„Â±k deÃ„Å¸iÃ…Å¸imi yok**; historical+forward shadow ve versioned promotion kanÃ„Â±tÃ„Â±.

### Phase 17 Ã¢â‚¬â€ PERSONAL BEHAVIOR ANALYTICS

- **Hedef/kapsam:** Journal reason performansÃ„Â±, FOMO proxy, horizon ihlali/yoÃ„Å¸unlaÃ…Å¸ma, Mentor followed/ignored baÃ„Å¸lamÃ„Â±; yargÃ„Â±lamayan insight.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 16 READY; 8 journal/cashflow-aware returns, 9 risk ve 16 outcome, yeterli kiÃ…Å¸isel ÃƒÂ¶rneklem.
- **Test:** Reason/horizon attribution, incomplete samples, empty/new user, benchmark/cashflow etkisi, language/ownership regression.
- **GÃƒÂ¼venlik:** Sensitive history minimizasyonu, no raw notes telemetry, private aggregate cache ve user scope.
- **Performans:** Precomputed grouped analytics; her chat/render full ledger taramasÃ„Â± yok.
- **Mobil:** Insights/card/chart ve aÃƒÂ§Ã„Â±klama drill-down; ÃƒÂ¶rneklem ve tarih aralÃ„Â±Ã„Å¸Ã„Â± gÃƒÂ¶rÃƒÂ¼nÃƒÂ¼r.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Proxy nedensellik deÃ„Å¸ildir; az veriyle genelleme yapÃ„Â±lmaz; yatÃ„Â±rÃ„Â±m sayÃ„Â±sÃ„Â±nÃ„Â± artÃ„Â±ran KPI kullanÃ„Â±lmaz.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** DoÃ„Å¸ru segment/matematik ve privacy testleri; ÃƒÂ¼rÃƒÂ¼n dili kullanÃ„Â±cÃ„Â±yÃ„Â± suÃƒÂ§lamaz veya daha fazla trade'e itmez.

### Phase 18 Ã¢â‚¬â€ PWA, MOBILE POLISH, OFFLINE/DEGRADED EXPERIENCE

- **Hedef/kapsam:** Installable PWA, safe cache/last-known offline etiketi, isteÃ„Å¸e baÃ„Å¸lÃ„Â± web push, gÃƒÂ¼nlÃƒÂ¼k touch kullanÃ„Â±m iyileÃ…Å¸tirmesi.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 17 READY; ÃƒÂ¶nceki tÃƒÂ¼m UI fazlarÃ„Â± zaten mobil gate'lerini geÃƒÂ§miÃ…Å¸ olmalÃ„Â±.
- **Test:** Install/update/offline/reconnect, logout/account-switch cache cleanup, notification opt-in/dedup, tÃƒÂ¼m route viewport ve touch E2E.
- **GÃƒÂ¼venlik:** Hassas API responses kontrolsÃƒÂ¼z service-worker cache'e yazÃ„Â±lmaz; push payload privacy ve session ayrÃ„Â±mÃ„Â±.
- **Performans:** Mobile cold/warm/offline, CPU/memory/network ve web bÃƒÂ¼tÃƒÂ§eleri; cache version/retention kontrolÃƒÂ¼.
- **Mobil:** Phone/tablet/desktop regresyonu, safe area/keyboard/touch/chart, install deneyimi.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Offline/cache Ã¢â€°Â  canlÃ„Â±; source age korunur, eski veriden yeni gÃƒÂ¼ÃƒÂ§lÃƒÂ¼ aksiyon/alarm yok.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** Offline/degraded freshness, cache privacy ve install/update gerÃƒÂ§ek doÃ„Å¸rulamasÃ„Â±.

### Phase 19 Ã¢â‚¬â€ PERFORMANCE HARDENING

- **Hedef/kapsam:** Profiling/slow SQL/index/cache/bundle/icon/chart/worker/AI darboÃ„Å¸azlarÃ„Â±nÃ„Â± ÃƒÂ¶lÃƒÂ§erek giderme; yeni feature yok.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 18 READY; ÃƒÂ¶nceki baselines ve yeterli temsilÃƒÂ® dataset/test ortamÃ„Â±.
- **Test:** k6/Locust eÃ…Å¸deÃ„Å¸eri yÃƒÂ¼k, concurrent dashboard/cold-warm cache, 10K chart, scanner, worker ve AI latency regression; functional tests korunur.
- **GÃƒÂ¼venlik:** Optimizasyon user scope/rate/privacy/freshness'i aÃ…Å¸amaz; shared cache veri sÃ„Â±zdÃ„Â±ramaz.
- **Performans:** Ã‚Â§24 bÃƒÂ¼tÃƒÂ§elerine gÃƒÂ¶re ÃƒÂ¶nce/sonra p75/p95, request/query counts, pool/queue/cache hit/bundle/memory; ortam ve ÃƒÂ¶rnek sayÃ„Â±sÃ„Â± yazÃ„Â±lÃ„Â±r.
- **Mobil:** DÃƒÂ¼Ã…Å¸ÃƒÂ¼k kaynaklÃ„Â± cihaz profili, touch INP, skeleton CLS ve chart CPU/memory kontrolÃƒÂ¼.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Downsampling/aggregation ve cached snapshot aynÃ„Â± semantiÃ„Å¸i taÃ…Å¸Ã„Â±r; stale label/invalidation kaybolmaz.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** **Performance budget report**; baÃ…Å¸arÃ„Â±sÃ„Â±z bÃƒÂ¼tÃƒÂ§e sessizce yÃƒÂ¼kseltilmez. Lab ÃƒÂ¶lÃƒÂ§ÃƒÂ¼mÃƒÂ¼ field p75 yerine gÃƒÂ¶sterilmez; veri yoksa ÃƒÂ¶lÃƒÂ§ÃƒÂ¼m sÃ„Â±nÃ„Â±rÃ„Â± aÃƒÂ§Ã„Â±ktÃ„Â±r.

### Phase 20 Ã¢â‚¬â€ SECURITY HARDENING + FINAL RELEASE AUDIT

- **Hedef/kapsam:** Threat model ve tÃƒÂ¼m kalite/regresyon, staging ZAP, secrets rotation, backup/restore, tÃƒÂ¼m ekran/mobile/data/license audit; `docs/FINAL_RELEASE_AUDIT.md`.
- **GiriÃ…Å¸/baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±k:** Phase 19 READY; staging test user, encrypted backup/retention, dependency/image/secret kanÃ„Â±tlarÃ„Â±. Public aÃƒÂ§Ã„Â±lÃ„Â±Ã…Å¸ iÃƒÂ§in Ã‚Â§75 uzman compliance artefact'larÃ„Â± gerekir.
- **Test:** Auth/IDOR/CSRF/XSS/SSRF/prompt-injection/rate/oversize; migration clean+previous upgrade; gerÃƒÂ§ek restore/reconciliation; staging smoke ve tÃƒÂ¼m ana E2E.
- **GÃƒÂ¼venlik:** TLS/CSP/HSTS/headers, DB/Redis public kapalÃ„Â±, secret rotation/runbooks; gitleaks/Trivy/audit/static/ZAP sonuÃƒÂ§larÃ„Â± ve aÃƒÂ§Ã„Â±k bulgular.
- **Performans:** Release production build ve bÃƒÂ¼tÃƒÂ§e regresyonlarÃ„Â±; cold/warm/degraded/load kanÃ„Â±tlarÃ„Â± final rapora baÃ„Å¸lanÃ„Â±r.
- **Mobil:** TÃƒÂ¼m ana ekranlarda otomatik viewport + gerÃƒÂ§ek gÃƒÂ¶rsel/touch/keyboard inceleme; yapÃ„Â±lmayan manuel QA aÃƒÂ§Ã„Â±kÃƒÂ§a NOT EXECUTED.
- **Veri doÃ„Å¸ruluÃ„Å¸u:** Source/freshness, no fake live, ledger/snapshot/math/bias/recovery; provider display/cache/history/redistribution haklarÃ„Â± ve no auto trade kontrolÃƒÂ¼.
- **Ãƒâ€¡Ã„Â±kÃ„Â±Ã…Å¸:** KanÃ„Â±tlÃ„Â± final release audit, kritik aÃƒÂ§Ã„Â±k baÃ…Å¸arÃ„Â±sÃ„Â±zlÃ„Â±k yok. Public/commercial iÃƒÂ§in **hukuk uzmanÃ„Â± incelemesi/sÃ„Â±nÃ„Â±flama/gerekli izinler/KVKK/sÃƒÂ¶zleÃ…Å¸meler/provider haklarÃ„Â±** belgelidir; yalnÃ„Â±z `LEGAL_COMPLIANCE_APPROVED=true` yetmez. Gerekli ÃƒÂ¼rÃƒÂ¼n dili deÃ„Å¸iÃ…Å¸ikliÃ„Å¸i master gÃƒÂ¼ncellenmeden yapÃ„Â±lmaz.

## 4. Faz listeleri arasÃ„Â±nda kaybolmayacak baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±klar

| Master kapsamÃ„Â± | Ã„Â°lk sahibi | Tamamlama baÃ„Å¸Ã„Â±mlÃ„Â±lÃ„Â±Ã„Å¸Ã„Â± |
|---|---|---|
| Onboarding ve Settings | 1 | Risk/portfÃƒÂ¶y ekranÃ„Â± 8Ã¢â‚¬â€œ9 ile baÃ„Å¸lanÃ„Â±r |
| Watchlist / global search | 4 | Karar 10, kavram search 12, alarm shortcut 14 |
| Ana Sayfa tam sÃ„Â±ralamasÃ„Â± | 4 temel | Portfolio 8, risk 9, briefing 11, learning 12, fÃ„Â±rsatlar 13, alerts 14 |
| Instrument detail tam kapsamÃ„Â± | 4 temel | Technical 5, pattern 6, fundamentals/KAP 7, risk 9, decisions 10, Mentor 11, backtest 15 |
| Portfolio cashflow/benchmark/curve | 8 | Drawdown/risk 9; reason/horizon analytics 17 |
| Pattern eÃ„Å¸itimi | 6 marker | 12 canonical article, 15 historical results |
| Basit market regime / sÃƒÂ¼rÃƒÂ¼mler | 10 | 15 evaluation, 16 segment/challenger |
| Publication/corporate-action/historical universe | 3/7 veri koruma | 15 test motoru; Phase 15'e kadar provenance kaybedilemez |
| Backup/restore ve retention | 0 prosedÃƒÂ¼r sÃ„Â±nÃ„Â±rÃ„Â±; 1/3/8/11 gerÃƒÂ§ek veri sahibi | Public veya korunmasÃ„Â± gereken gerÃƒÂ§ek veri kullanÃ„Â±mÃ„Â± ÃƒÂ¶ncesi uygulanÃ„Â±r; 20 final denetim |
| Ops metrics/runbooks | 0 log/health | 3 provider/worker/gaps, 7 KAP lag, 11 AI cost, 15 backtest, 16 version |

Ã„Â°steÃ„Å¸e baÃ„Å¸lÃ„Â± TimescaleDB, Zustand, dark/light theme, geliÃ…Å¸miÃ…Å¸ indicator/pattern seti, email/push ve admin diagnostics yalnÃ„Â±z master koÃ…Å¸ullarÃ„Â± ve somut ihtiyaÃƒÂ§la deÃ„Å¸erlendirilir. Fonlar/ABD hisseleri/read-only broker import/household/custom strategy gibi Ã‚Â§70 uzantÃ„Â±larÃ„Â± Ã…Å¸imdi uygulanmaz. Otomatik broker emri bu roadmap'in kapsamÃ„Â± deÃ„Å¸ildir.

## 5. BaÃ„Å¸Ã„Â±msÃ„Â±z completion ve kanÃ„Â±t sÃƒÂ¶zleÃ…Å¸mesi

Gelecekte her faz `docs/phases/phase_XX_completion.md` ÃƒÂ¼retir; Phase 0 raporu orada tek iÃƒÂ§erik olarak tutulabilir, istenirse kÃƒÂ¶kten yalnÃ„Â±z link verilir. Bu ÃƒÂ§alÃ„Â±Ã…Å¸tÃ„Â±rmada **hiÃƒÂ§bir completion raporu oluÃ…Å¸turulmadÃ„Â±**.

Master Ã‚Â§33'teki 22 alan zorunludur: scope, changed files, migrations, endpoints, UI routes, security, performance, gerÃƒÂ§ekten ÃƒÂ§alÃ„Â±Ã…Å¸tÃ„Â±rÃ„Â±lan automated tests ve exact counts, typecheck/lint/build/security scans, clean/upgrade migrations, mobile automated/manual QA, limitations/deferred items, rollback, evidence ve READY/NOT READY.

KanÃ„Â±t kaydÃ„Â± komut + cwd + tarih + commit/snapshot + ortam/dataset + exit code + test counts + artifact/run URL iÃƒÂ§ermelidir. Test sonucu `AUTOMATED PASS`, doÃ„Å¸rudan kod incelemesi `CODE INSPECTION PASS`, ÃƒÂ§alÃ„Â±Ã…Å¸tÃ„Â±rÃ„Â±lmayan kontrol `NOT EXECUTED` olarak ayrÃ„Â±lÃ„Â±r. GerÃƒÂ§ek manuel gÃƒÂ¶zlem ayrÃ„Â±ca cihaz/viewport/adÃ„Â±m/ÃƒÂ§Ã„Â±ktÃ„Â± ile yazÃ„Â±lÃ„Â±r. Ã¢â‚¬Å“Works/secure/optimized/production ready/fully responsive/all tests passÃ¢â‚¬Â gibi iddialar tek baÃ…Å¸Ã„Â±na kabul deÃ„Å¸ildir.

## 6. Readiness ve dÃ„Â±Ã…Å¸ kapÃ„Â±lar

Phase 0 baÃ…Å¸langÃ„Â±cÃ„Â± iÃƒÂ§in bilinen ÃƒÂ¼rÃƒÂ¼n/mimari blocker yoktur. KullanÃ„Â±cÃ„Â±nÃ„Â±n Docker'Ã„Â± aÃƒÂ§masÃ„Â±ndan sonra daemon salt okunur sorgusu baÃ…Å¸arÃ„Â±lÃ„Â±dÃ„Â±r (GAP E12). pnpm ÃƒÂ§alÃ„Â±Ã…Å¸Ã„Â±r; npm launcher hatasÃ„Â± nedeniyle plan pnpm'i ÃƒÂ¶nerir. uv kurulumu, dependency compatibility/registry, gerÃƒÂ§ek Compose, Git remote/CI eriÃ…Å¸imi implementation gÃƒÂ¶revlerinde doÃ„Å¸rulanacaktÃ„Â±r.

GerÃƒÂ§ek CI yeÃ…Å¸il sonucu olmadan Phase 0 kapanamaz. GerÃƒÂ§ek BIST/KAP/EVDS/haber kaynaÃ„Å¸Ã„Â± izinleri ilgili adapter aktivasyonundan ÃƒÂ¶nce; chart lisansÃ„Â± Phase 4'ten ÃƒÂ¶nce; point-in-time veri Phase 15 gate'inden ÃƒÂ¶nce doÃ„Å¸rulanÃ„Â±r. Public/commercial launch Ã‚Â§75 kanÃ„Â±tlarÃ„Â± tamamlanana kadar **BLOCKED**'dÃ„Â±r; bu durum local Phase 0 baÃ…Å¸langÃ„Â±cÃ„Â±nÃ„Â± engellemez.
 
 # # #   P O S T - V 1   I M P R O V E M E N T S  
 -   * * P H A S E   2 1 : * *   R e a l   M a r k e t   D a t a   I n t e g r a t i o n   &   U I / U X   O v e r h a u l   ( v 1 . 0 . 1 )  
     -   R e a l   B I S T 1 0 0   i n s t r u m e n t s ,   Y a h o o   F i n a n c e   w i r i n g ,   t r u e   h i s t o r i c a l   c h a r t s .  
     -   F i n t e c h - g r a d e   g l o b a l   n a v i g a t i o n ,   r e a l   d a s h b o a r d ,   h o n e s t   d a t a   s t a t e   r e p r e s e n t a t i o n .  
     -   C o m p l e t e   r e p l a c e m e n t   o f   m o c k   d a t a   w i t h   r e a l   d a t a   A P I s   o r   e x p l i c i t   U N A V A I L A B L E   s t a t e s .  
 