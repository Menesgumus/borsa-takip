# Borsa Takip — Geliştirme Roadmap'i

Tarih: 2026-09-05. **Planlama tamamlandı; implementation başlamadı.**

Tek nihai kaynak [BORSA_TAKIP_MASTER_SPEC.md](BORSA_TAKIP_MASTER_SPEC.md)'dir. Bu roadmap master'ın yerini almaz, gereksinimleri yeniden tanımlamaz. Kaynak hash'i ve gerçek repository kanıtları [GAP_ANALYSIS.md](GAP_ANALYSIS.md)'dedir. Yalnız Phase 0'ın ayrıntılı görev planı [phase_00_plan.md](phase_00_plan.md)'dedir.

Kullanıcının bu çalıştırmaya özel talebi nedeniyle bu dosya ve Phase 0 planı köktedir; master §76'daki ilk çalıştırmada implementation adımı uygulanmamıştır. Faz başlıkları **0–20 dahil 21 fazdır**. Tamamlanmış faz yoktur.

## 1. Faz sırası ve başlangıç durumu

Zorunlu sıra:

`00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20`

Her fazın giriş koşulu önceki fazın gerçek completion kanıtıyla kapanmasıdır. Aşağıda ek veri/domain bağımlılıkları ayrıca gösterilir. Bir önceki faz başarısızsa sonraki faz uygulanmaz. Alt görevler bölünebilir; kapsam veya exit gate sessizce gevşetilemez.

| Faz | Kısa ad | Implementation durumu | Plan / kabul durumu |
|---|---|---|---|
| 00 | Governance, scaffold, quality baseline | `COMPLETED` | Phase 00 READY, CI ve QA tamam |
| 01 | Auth, user profile, security | `IN_PROGRESS` | T02 otonom devam ediyor |
| 02 | Instrument master, provider abstraction | `NOT_IMPLEMENTED` | 01 çıkışını bekler |
| 03 | Market ingestion, history | `NOT_IMPLEMENTED` | 02 çıkışını bekler |
| 04 | Dashboard, markets, charts | `NOT_IMPLEMENTED` | 03 çıkışını bekler |
| 05 | Technical engine | `NOT_IMPLEMENTED` | 04 çıkışını bekler |
| 06 | Pattern, support/resistance | `NOT_IMPLEMENTED` | 05 çıkışını bekler |
| 07 | Fundamentals, KAP, macro, news | `NOT_IMPLEMENTED` | 06 çıkışını bekler |
| 08 | Real/paper portfolio, journal | `NOT_IMPLEMENTED` | 07 çıkışını bekler |
| 09 | Risk, pre-trade what-if | `NOT_IMPLEMENTED` | 08 çıkışını bekler |
| 10 | Deterministic decisions | `NOT_IMPLEMENTED` | 09 çıkışını bekler |
| 11 | AI Mentor | `NOT_IMPLEMENTED` | 10 çıkışını bekler |
| 12 | Bilgi Merkezi | `NOT_IMPLEMENTED` | 11 çıkışını bekler; minimum MVP sınırı |
| 13 | Opportunity scanner | `NOT_IMPLEMENTED` | 12 çıkışını bekler |
| 14 | Alerts, notifications | `NOT_IMPLEMENTED` | 13 çıkışını bekler |
| 15 | Backtest | `NOT_IMPLEMENTED` | 14 çıkışını bekler |
| 16 | Outcomes, champion/challenger | `NOT_IMPLEMENTED` | 15 çıkışını bekler |
| 17 | Personal behavior analytics | `NOT_IMPLEMENTED` | 16 çıkışını bekler |
| 18 | PWA, offline, mobile polish | `NOT_IMPLEMENTED` | 17 çıkışını bekler |
| 19 | Performance hardening | `NOT_IMPLEMENTED` | 18 çıkışını bekler |
| 20 | Security hardening, final release audit | `NOT_IMPLEMENTED` | 19 çıkışını bekler |

## 2. Her faza uygulanan ortak kapılar

Master §0.4, §33–40, §53, §71 tüm fazların kabul çerçevesidir. Her faz planı kapsam/kapsam dışı, data model/migration, API/UI, test komutları, güvenlik, performans, mobil, veri doğruluğu ve rollback'i açıkça tanımlar. İlgisiz kontrol ancak gerekçesiyle uygulanamaz olarak işaretlenebilir; çalıştırılmayan kontrol başarılı sayılamaz.

- **Doğrulama:** İlgili unit, integration, migration, API contract, component, E2E, lint, typecheck, build; security static scan, secret ve dependency/image audit. Hatalar gizlenmez, kontroller kapatılmaz.
- **Güvenlik:** User scope/IDOR ilk user endpointinden; CSRF cookie mutations'ta; parameterized SQL/input limits; XSS/SSRF ve untrusted içerik ilgili entegrasyondan itibaren; secret redaction, rate limits, audit ve privacy. Phase 20 ilk güvenlik uygulaması değildir.
- **Veri:** UTC internal / Europe-Istanbul varsayılan gösterim; backend Decimal/NUMERIC para muhasebesi; missing ≠ 0; source/source_timestamp/ingested_at/freshness; immutable decision ve correction ledger. LLM ve frontend authoritative finansal hesap kaynağı değildir.
- **Dayanıklılık:** Bounded timeout/retry, idempotency, cache yaşının görünürlüğü, semantik/lisans uyumlu fallback, worker backpressure. Kritik eksik/stale veri güçlü aksiyon üretemez; BEKLE ve reason code gerekir.
- **Mobil/erişilebilirlik:** UI olan her fazda 360/390/430 telefon, tablet portrait ve landscape, 1280+ ve geniş desktop; overflow/nav/touch (~44 CSS px)/dialog/chart/table/safe area. Otomatik viewport + gerekli gerçek görsel/touch/keyboard incelemesi. Phase 18'e ertelenmez.
- **Kapanış:** Gerçek çıktılarla completion; kritik başarısızlık varsa `NOT READY`. Scaffold veya UI mock, domain feature tamamlandı anlamına gelmez.

### Sabit performans bütçeleri ve kanıt ayrımı

| Alan | Master hedefi | Ölçüm/gate |
|---|---|---|
| Web | Production p75 LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 | İlk UI'dan production build lab kontrolü ve bundle baseline; gerçek field p75 yalnız yeterli gerçek ölçüm varsa. Lighthouse skoru INP/p75 kanıtının yerine geçmez. |
| Latest quote | Cache hit p95 <150ms | Phase 3/4'ten itibaren belirtilmiş dataset, altyapı, concurrency ve cache durumuyla |
| Dashboard | Cache hit p95 <400ms | Phase 4'ten aggregated/paralel fetch, request count ve N+1 kontrolü |
| Candles | Yaygın instrument 1Y daily p95 <500ms | Phase 3'ten indeks/EXPLAIN, bounded range ve cold/warm karşılaştırması |
| Chart | 2K ve 10K nokta benchmark; her tick full series reset yok | Phase 4'ten load/render/update/network/memory ve mobil touch kayıtları |
| Scanner | 100/500/1000 instrument benchmark | Phase 13 worker throughput; request-time tarama yok |
| Phase 0 | Empty app bundle ve health latency baseline | Sayısal sağlık endpoint SLA'sı master'da yok; ölçümün kendisi zorunlu, finans endpoint hedefi uydurulmaz |

Aynı provider verisinin tekrar çekilmesi, unbounded history, gereksiz polling/rerender, synchronous ağır AI/hesap, N+1 ve cache invalidation her ilgili fazda incelenir. Phase 19 mevcut bütçelerdeki regresyonları ölçümle giderir.

## 3. Faz hedefleri, girişleri ve çıkışları

### Phase 0 — PROJECT GOVERNANCE, SCAFFOLD, QUALITY BASELINE

- **Hedef/kapsam:** Monorepo, minimal Next.js/FastAPI app, PostgreSQL/Redis Compose, env/lockfiles, ADR, baseline Alembic, health/error/correlation, CI kalite zinciri. Finans özelliği yok.
- **Giriş/bağımlılık:** Tam master okuması ve repo denetimi tamam; kaynak değişikliklerini yeniden kontrol et. Docker daemon E12 ile erişilebilir; gerçek Compose, package install ve remote CI halen doğrulanacak.
- **Test:** Clean clone startup, DB/Redis integration, clean migration, frontend build, backend/component/API/E2E smoke, lint/type/format ve gerçek CI.
- **Güvenlik:** Secret scan, static/dependency/image audit; fake env, loopback local erişim, unsafe public config fail-fast, log redaction.
- **Performans:** Empty production bundle ve health latency baseline, bounded dependency timeout.
- **Mobil:** Minimal kabuk telefon/tablet/desktop, keyboard/focus/overflow; mevcut kontrollerin touch hedefi. Grafik olmadığı için chart touch testi gerekçeli uygulanamaz.
- **Veri doğruluğu:** UTC config, migration lifecycle; domain tablo/ledger/sayı hesapları kurulmaz. Decimal ve ilerideki doğrulama politikası belgelenir.
- **Çıkış:** Master'ın **`PHASE 0 READY` yalnız CI tamamen yeşilse** şartı ve ilgili diğer baseline kontrollerin gerçek kanıtı. Planın hazır olması bu kapıyı geçirmez.

### Phase 1 — AUTH, USER PROFILE, SECURITY FOUNDATION

- **Hedef/kapsam:** users/auth/profile schema, Argon2id, session/cookie rotation-revoke, ownership dependency, audit temeli, onboarding/settings/risk limits.
- **Giriş/bağımlılık:** Phase 0 READY; env/DB/migration/CI. Public auth tasarımı fail-closed; local bypass yalnız explicit loopback koşuluyla.
- **Test:** Login success/fail, expiration/logout/revoke, session rotation, CSRF, user-scoped IDOR fixtures, profile sınırları, migration ve form E2E.
- **Güvenlik:** Login rate limit, secure HttpOnly/SameSite cookie, CSRF, hashed password; auth/audit log redaction ve hesaplar arası izolasyon.
- **Performans:** Password hash maliyeti ölçümü, bounded login resource kullanımı, profil query sayısı ve bundle farkı.
- **Mobil:** Onboarding/settings form, hata mesajı, klavye, focus, touch ve tüm viewportlar.
- **Veri doğruluğu:** Profile yüzde/vade/enum/timezone doğrulaması; boş profile sıfır risk varsayılmaz; audit safe diff.
- **Çıkış:** **User-scoped test olmadan finance data fazına geçilmez.** Auth lifecycle, ownership ve profile E2E kanıtlıdır.

### Phase 2 — INSTRUMENT MASTER + PROVIDER ABSTRACTION

- **Hedef/kapsam:** Instruments/mappings, quote DTO/freshness, provider interfaces ve deterministic mock, health, retry/rate-limit/circuit davranışı.
- **Giriş/bağımlılık:** Phase 1 READY; ownership testleri ve DB temeli. Provider seçimi ayrı config, domain provider payload görmez.
- **Test:** Mock full contract, mapping/unit/UTC normalization, malformed payload/timeout/outage, freshness ve typed error fixture'ları.
- **Güvenlik:** Provider secret server-side; host allowlist/SSRF sınırı; timeout/size/input limits. Kullanıcı URL'si doğrudan fetch edilmez.
- **Performans:** Batch quote sözleşmesi, retry cap/circuit/backpressure tasarımı; outage request'i sınırsız bloke etmez.
- **Mobil:** UI eklenmezse gerekçeli uygulanamaz; health/freshness frontend DTO tüketimine uygundur.
- **Veri doğruluğu:** Canonical/native symbol ayrımı, UUID/exchange/currency, explicit freshness, unknown timestamp durumları, negative/zero price reddi.
- **Çıkış:** **Mock provider ile full contract test; gerçek provider ayrı config.** Provider down uygulamayı çökertmez; mock gerçek/canlı gibi sunulmaz.

### Phase 3 — MARKET DATA INGESTION + HISTORICAL STORE

- **Hedef/kapsam:** Quote Redis cache, candles DB/index/unique policy, ayrı worker, checkpoint/batch ingest, gap ve timezone/final/adjusted yönetimi.
- **Giriş/bağımlılık:** Phase 2 READY; gerçek kaynak için gösterim/cache/history/rate-limit lisans kanıtı. Erişim yoksa mock doğrulama ayrılır, gerçek entegrasyon tamamlandı denmez.
- **Test:** Duplicate/out-of-order/non-final/missing/stale candles; holiday/yarım seans, BIST kapalı/kripto açık, wrong-timezone, retry/restart/checkpoint idempotency.
- **Güvenlik:** Provider egress/SSRF/credentials; queue payload ve Redis izolasyonu; admin diagnostics varsa yetki sınırı.
- **Performans:** Batch ingest ölçümü, query `EXPLAIN`, 1Y history ve quote budget, cache cold/warm/hit ratio, pool/queue metrics; historical data tekrar çekilmez.
- **Mobil:** Bu fazda yeni UI yoksa uygulanamaz; freshness ve bounded payload contract'ı korunur.
- **Veri doğruluğu:** Raw/adjusted provenance ve point-in-time policy, data version, source/ingest UTC, source mismatch, gap repair; corporate-action future leakage önlenir.
- **Çıkış:** Master testleri + idempotent pipeline, index/benchmark ve outage/freshness kanıtları; kaynak lisansı çözümsüzse gerçek data gate kapalıdır.

### Phase 4 — MARKET DASHBOARD + HIGH-QUALITY CHART FOUNDATION

- **Hedef/kapsam:** Temel dashboard/Piyasalar/detail, global instrument search, user-scoped watchlist; mum/hacim/timeframe, loading/error/empty/stale, provenance. Sonraki motorlara ait skorlar uydurulmaz.
- **Giriş/bağımlılık:** Phase 3 READY; quote/history contracts, Phase 1 user scope; chart sürümü/attribution şartı doğrulanır.
- **Test:** Route/API/component/E2E, watchlist isolation, chart resize/incremental update/reconnect, empty/stale/outage; desktop+mobile screenshot incelemesi.
- **Güvenlik:** Search rate/input limit; watchlist IDOR/CSRF; safe links; attribution; secret içermeyen client bundle.
- **Performans:** 2K/10K chart benchmark, her tick full `setData` ve history reload yok; dashboard <400ms, query count/batch, lazy chart/targeted cache update; Web vitals lab kontrolü.
- **Mobil:** 360/390/430 zorunlu; tablet/desktop, touch pan/zoom/tooltip, collapsible controls, card/table ve safe-area navigation.
- **Veri doğruluğu:** Price/source/as_of/delay, axis/units/timezone/percent, missing session gaps; closed market ve stale farklıdır.
- **Çıkış:** **Chart desktop+mobile manual screenshot inspection + automated viewport tests**; performans ve freshness kanıtı. Briefing/portfolio/alerts gibi sonraki parçalar tamamlandı sayılmaz.

### Phase 5 — TECHNICAL ANALYSIS ENGINE

- **Hedef/kapsam:** SMA/EMA/RSI/MACD/Bollinger/ATR/hacim, trend/horizon configs, versioned analysis snapshots, UI cards ve chart panes.
- **Giriş/bağımlılık:** Phase 4 READY; kaliteli candles, worker ve chart. Formül/smoothing/warm-up seçimi resmi/birincil matematik referansı ve ADR/testle açıklanır.
- **Test:** Her gösterge golden + flat/monotonic/insufficient/missing/non-final/zero-volume/split fixture; determinism ve invariant/property testler.
- **Güvenlik:** History/period input limits, backend-only calculation, typed boundary; kullanıcı snapshot scope varsa ownership.
- **Performans:** Worker precompute, yeni candle ile invalidation; request'te tekrar ağır hesap yok; batch/latency/bundle regression.
- **Mobil:** Pane okunabilirliği, toggle/legend/touch, metin özeti; tüm viewportlarda chart ve score cards.
- **Veri doğruluğu:** Numerical tolerance gerekçeli; authoritative para float'a dönüşmez; input timestamp/formula version, warm-up boşluğu, skor sahte kesinlik değil.
- **Çıkış:** **Golden testler olmadan kapanmaz.** İndikatör ve chart çıktısının aynı backend snapshot'ını kullandığı doğrulanır.

### Phase 6 — PATTERN + SUPPORT/RESISTANCE ENGINE

- **Hedef/kapsam:** Deterministik candle/chart pattern, swing/destek-direnç, seçilmiş pattern kalite/invalidation/version, chart overlay.
- **Giriş/bağımlılık:** Phase 5 READY; validated candles/trends ve chart panes. Master §9.5 ilk set; flag/pennant sonrası ayrı iterasyon.
- **Test:** Synthetic positive/negative ve false-positive regression; boundary/insufficient history, confirmation timestamp ve yeniden üretilebilir detection.
- **Güvenlik:** Bounded algorithm inputs; LLM görselinden pattern/aksiyon kaynağı yapılmaz; safe overlay content.
- **Performans:** Worker/precompute ve dataset maliyeti; büyük overlay render ve mobil CPU/memory regresyonu.
- **Mobil:** Marker touch/popover, dates/quality/invalidation okunabilir; chart gesture çakışmaları.
- **Veri doğruluğu:** Start/end + detection/confirmation time ayrımı; ileride backtest'te sağ taraftaki future barlara erken erişim yok; pattern ≠ AL/SAT.
- **Çıkış:** Pozitif/negatif ve false-positive test kanıtları; versioned detector ile overlay ve kalite tutarlılığı. Eğitim/backtest linki 12/15 gelince bağlanır.

### Phase 7 — FUNDAMENTALS + KAP + MACRO + NEWS PIPELINE

- **Hedef/kapsam:** Normalized financials/fundamental scores, KAP, EVDS, haber adapter'ları; source tiers/dedup/entity mapping/factual extraction ve ayrı sentiment/yorum.
- **Giriş/bağımlılık:** Phase 6 READY; provider/domain sınırları. KAP API şartları, EVDS key/series semantiği, haber ve varsa social izinleri doğrulanmış olmalı.
- **Test:** Payload contracts, financial ratio/missing/negative inputs, period/consolidation, future publication fixture, dedup, attachment-only KAP ve ingestion lag; injection/malicious HTML/oversize.
- **Güvenlik:** SSRF host/DNS/IP/redirect/content-type/size, sanitize, untrusted_document, no remote tool instructions, credential redaction.
- **Performans:** Async batch + worker, disclosure index, new-report score invalidation, bounded retry ve pipeline metrics.
- **Mobil:** Fact ve interpretation bölümleri, uzun başlık/kaynak/tarih, statement cards/tables ve attachment mesajları.
- **Veri doğruluğu:** published_at ≠ fiscal_period_end; raw inputs/version korunur, missing ≠ 0, sector peer bağlamı, Tier 3 resmî kanıt değildir.
- **Çıkış:** **Fact/interpretation UI separation verified**; izinli gerçek entegrasyon, injection ve finans doğruluk kanıtı. Eksik provider yetkisi gizlenmez.

### Phase 8 — PORTFOLIO + PAPER PORTFOLIO + JOURNAL

- **Hedef/kapsam:** Ayrı real/paper ledger, transactions/reversal, derived positions, P/L/fees/tax/cash/FX, benchmark/cashflow-aware returns, journal ve dashboard özeti.
- **Giriş/bağımlılık:** Phase 7 READY; Phase 1 ownership ve Phase 3 quote/history. Accounting/quantization ve TWR/XIRR seçimi ADR ile; gerçek veri yazılmadan backup/correction planı.
- **Test:** Multiple buy/partial-full sell/oversell/fee/tax/dividend/cashflow/FX/tiny rounding/missing quote; empty/all-cash/backdated, concurrency/double-submit, restore ve ledger reconciliation.
- **Güvenlik:** Tüm portfolio/transaction/journal IDOR ve CSRF, input/overflow, atomic writes/idempotency, audit safe diff; private exports/cache/log.
- **Performans:** Portfolio/executed_at index; batch valuation, transaction+quote invalidation, derived snapshot ledger'ın yerine geçmez.
- **Mobil:** Real/paper ayrımı, hızlı reason form, history cards/secondary details, allocation/performance/benchmark chart ve empty state.
- **Veri doğruluğu:** Decimal exact accounting; deposits getiri değildir; weights cash dahil ~100%, missing quote sıfır değil, immutable history/correction, short selling yok.
- **Çıkış:** **Ledger invariant tests %100 pass**; authoritative ledger↔positions ve benchmark/math testleri, owner isolation, backup etkisi kanıtlıdır.

### Phase 9 — RISK ENGINE + PRE-TRADE WHAT-IF

- **Hedef/kapsam:** Concentration/cash floor/position size/drawdown/volatility, yeterli veride correlation/liquidity; no-mutation what-if ve stop/target önerisi.
- **Giriş/bağımlılık:** Phase 8 READY; validated ledger/profile/history ve accounting policy.
- **Test:** Limit boundary, what-if öncesi/sonrası ağırlık, all-cash/missing history, correlation sample gate; DB'nin mutate edilmediği assertion.
- **Güvenlik:** Ownership/rate/input validation, sensitive aggregate exposure, hesapla/kaydet akışlarının açık ayrımı.
- **Performans:** Bounded simulation, cache keys user/portfolio/input version; hesap yoğunluğu worker/snapshot ile kontrollü.
- **Mobil:** Dedicated step/bottom sheet; büyük görünür risk uyarısı, touch ve viewport'a sığma.
- **Veri doğruluğu:** Deterministik Decimal etkiler; korelasyon eksikliği sıfır risk değil; gap/slippage stop garantisi değildir; limit ihlali kullanıcı işlemini otomatik yasaklamaz.
- **Çıkış:** DB no-mutation ve sınır testleri, açıklanabilir risk sonuçları ve responsive UI kanıtı.

### Phase 10 — DETERMINISTIC DECISION ENGINE

- **Hedef/kapsam:** Beş aksiyon, normalization/horizon/versioned weights, quality gate, Market View/Personal Action, immutable snapshot/reasons/detail/watchlist kararları; basit test edilebilir regime context.
- **Giriş/bağımlılık:** Phase 9 READY; 5/6/7 sinyalleri, 8 portföy, 9 risk, 3 freshness. Başlangıç weights bir performans garantisi değildir.
- **Test:** Golden positive/negative/mixed/low-quality/concentration; tüm action sınırları, replay/version, stale/missing→BEKLE; overconcentration Market View değiştirmeden action düşürebilir.
- **Güvenlik:** Decision config mutation audit ve erişim; private action isolation; LLM'den bağımsız deterministik karar.
- **Performans:** Snapshot references, critical-input invalidation/version cache key, gereksiz request recompute yok.
- **Mobil:** Karar/detail/risk/reasons/vade, portfolio what-if linki ve chart bağlantıları; güvenilirlik ve data as_of görünür.
- **Veri doğruluğu:** Reliability başarı ihtimali olarak sunulmaz; degraded KAP politikası önceden sürümlüdür; kritik market data yoksa BEKLE.
- **Çıkış:** Golden karar ve replay/immutable/data safety kanıtları. Backtest motoru 15'e aittir; üretim ağırlık değişimi 15/16 evidence/governance olmadan yapılmaz.

### Phase 11 — AI MENTOR

- **Hedef/kapsam:** Tool-first orchestration/chat, typed LLM açıklama, seviyeye göre kısa/detaylı yanıt, quick actions, privacy-aware conversations, kaynak/zaman; cached personal Daily Briefing.
- **Giriş/bağımlılık:** Phase 10 READY; domain facts/decisions ve user scope. LLM sağlayıcısına gönderilecek minimum context ve retention politikası belirli.
- **Test:** Action override reddi, olmayan price/KAP claim validation, malicious news injection, unknown symbol, missing tool ve AI outage; cache kullanıcı izolasyonu/conversation deletion.
- **Güvenlik:** Prompt server-side, tool/argument allowlist, rate/token limits, sanitized Markdown, no arbitrary shell/URL, IDOR/CSRF, minimum sensitive context/log.
- **Performans:** Her render'da AI çağrısı yok; snapshot/user briefing cache, bounded/async generation ve progress/degraded cevap; latency/cost metrics.
- **Mobil:** Chat keyboard/scroll, quick prompts, sources ve clear action, accessible messages.
- **Veri doğruluğu:** Sayılar backend/tool'dan, action sadece engine'den; stale risk gizlenmez; AI unavailable core hesapları durdurmaz.
- **Çıkış:** Safety fixtures, gerçek tool integration ve source/numeric doğrulama; kısa Türkçe yanıt ve fallback kanıtı.

### Phase 12 — BİLGİ MERKEZİ + VISUAL EDUCATION

- **Hedef/kapsam:** Master Phase 12'deki 20 ilk kavram, canonical article/revision, search/ask/levels, deterministic visuals, glossary ve pattern eğitim bağlantıları, öğrenme ilerleme görünümü.
- **Giriş/bağımlılık:** Phase 11 READY; doğrulanmış domain kavramları, Mentor explanation level. Eğitsel temsili veri açık etiketli.
- **Test:** Article schema/search/links, content technical+plain-language QA, misuse warning, visual-to-data doğruluğu, component/E2E/a11y.
- **Güvenlik:** Safe content/Markdown, content revision ownership, ask rate limit, canonical source governance; AI yeni kesin kural uyduramaz.
- **Performans:** Canonical content cache, lazy visuals, her kavram için gereksiz AI çağrısı yok; web budget/bundle kontrolü.
- **Mobil:** Popover/detail/interactive visual controls ve metin ölçekleme tüm viewportlarda.
- **Veri doğruluğu:** Her görsel gerçek/temsili ayrımı, formül/smoothing review, 30/70 gibi eşikler tek başına AL/SAT değildir.
- **Çıkış:** Her canonical article için teknik/sade anlatım/yanıltma sınırı review ve öğrenme akışı E2E. **Minimum kullanılabilir ürün 0–12; public izin anlamına gelmez.**

### Phase 13 — FIRSAT TARAYICI + PERSONALIZED RANKING

- **Hedef/kapsam:** Worker universe scanner, filters/raw score/user fit/reasons, fırsatlar sayfası ve dashboard kişisel fırsat alanı.
- **Giriş/bağımlılık:** Phase 12 READY; Phase 10 decisions, 9 risk, 3 universe/history/cache.
- **Test:** Filter/order/tie/empty/stale, aynı varlık farklı portföy uygunluğu, snapshot versions ve account isolation.
- **Güvenlik:** User-scoped ranking cache, filter/range validation/rate limits; manipülatif yatırım dili yok.
- **Performans:** **Request-time scanner yok; 100/500/1000 instrument benchmark**; worker throughput/queue depth/batch ve paginated liste.
- **Mobil:** Desktop table/mobile cards, filtre drawer, neden/risk/as_of erişilebilirliği.
- **Veri doğruluğu:** Raw fırsat ile user-fit ayrıdır; stale girdi güçlü fırsat gibi görünmez; kaynak/reason/version trace.
- **Çıkış:** Benchmark raporu ve personalized ranking contract/UI testleri; garanti getiri iddiası yok.

### Phase 14 — ALERTS + NOTIFICATIONS

- **Hedef/kapsam:** Price/RSI/KAP/news/decision/concentration/daily-loss rules, worker evaluation/dedup/cooldown/in-app history; watchlist shortcut ve dashboard alerts.
- **Giriş/bağımlılık:** Phase 13 READY; 3/5/7/9/10 event ve snapshotları, user scope. Push temeli opsiyonel, ana push 18.
- **Test:** Boundary crossing once, repeated same price no-spam, decision transition, failed delivery/retry/idempotency, stale provider no-misleading alarm.
- **Güvenlik:** Alert IDOR/CSRF/input/rate limit; delivery destination validation, notification privacy.
- **Performans:** Worker batch/event fingerprint, cooldown, pagination; gereksiz polling ve tekrar provider fetch yok.
- **Mobil:** Rule form, unread/history/action navigation, safe area/touch; FOMO'suz metin.
- **Veri doğruluğu:** Olayın source/as_of/fingerprint'ı, stale quote alarmı tetiklemez; daily loss hesabı cash injection ile karışmaz.
- **Çıkış:** Dedup/state transition ve stale suppression kanıtı; in-app rule→event→history E2E.

### Phase 15 — BACKTEST ENGINE

- **Hedef/kapsam:** Strategy spec, event-safe data access, execution/cost/slippage, benchmark, frozen train/validation/test veya walk-forward/OOS; çoklu sonuç metriği/UI.
- **Giriş/bağımlılık:** Phase 14 READY; 3/7 point-in-time veri/provenance, 5/6/10 sürümlü sinyaller. Universe/delist/corporate-action/publication yeterliliği doğrulanmadan başarı değerlendirmesi açılamaz.
- **Test:** Deliberate future/publication leakage, post-close fill, future-adjustment, surviving-only universe fixtures; aynı version/hash/params sonucu; holdout izolasyonu ve hindsight/repeated-test optimization yasağı.
- **Güvenlik:** Expensive-run rate/resource limit, queue sandbox/input validation, user-owned result access; arbitrary strategy code/shell feature'ı eklenmez.
- **Performans:** Ayrı worker, dataset reuse/index/bounded jobs/backpressure, repeatable load ve result pagination.
- **Mobil:** Equity/drawdown/benchmark chart, cost/assumption/sample sayısı ve limitations okunabilir; responsive result table.
- **Veri doğruluğu:** Costs ≠ varsayılan sıfır, publication zamanına bağlı erişim, corporate actions ve historical universe; win-rate tek metrik değil, sample/CI uygunluğuyla CAGR/return/drawdown/expectancy/turnover/benchmark.
- **Çıkış:** **Completion'da ayrı bias audit:** look-ahead, publication, corporate actions, costs, survivorship. Bias kanıtı olmayan test başarı diye sunulmaz; veri eksikliği gate'i bloke eder. Backtest gelecek getiri garantisi değildir.

### Phase 16 — DECISION OUTCOME TRACKING + CHAMPION/CHALLENGER

- **Hedef/kapsam:** +1/5/20/60 işlem günü ve horizon outcomes, benchmark/sector/regime/action segmentleri, challenger/shadow ve bounded promotion.
- **Giriş/bağımlılık:** Phase 15 READY; immutable decisions/data versions, OOS/bias-safe evaluation.
- **Test:** Trading-day alignment, insufficient forward history, min N/confidence bounds/max change, rejected risk regression, replay/promotion/rollback.
- **Güvenlik:** Versioned approval ve config audit, yalnız yetkili promotion; her kayıpta otomatik production weight mutation yok.
- **Performans:** Daily idempotent worker, incremental forward outcomes, bounded shadow evaluation ve segment index.
- **Mobil:** Segment/performance/champion-challenger sunumu varsa okunabilir controls/table/chart ve açıklamalı örnek sayısı.
- **Veri doğruluğu:** Outcome yalnız window tamamlanınca, SAT opportunity cost/BEKLE davranışı; sample support ve benchmark, no hindsight tuning.
- **Çıkış:** **Governance gate olmadan otomatik production ağırlık değişimi yok**; historical+forward shadow ve versioned promotion kanıtı.

### Phase 17 — PERSONAL BEHAVIOR ANALYTICS

- **Hedef/kapsam:** Journal reason performansı, FOMO proxy, horizon ihlali/yoğunlaşma, Mentor followed/ignored bağlamı; yargılamayan insight.
- **Giriş/bağımlılık:** Phase 16 READY; 8 journal/cashflow-aware returns, 9 risk ve 16 outcome, yeterli kişisel örneklem.
- **Test:** Reason/horizon attribution, incomplete samples, empty/new user, benchmark/cashflow etkisi, language/ownership regression.
- **Güvenlik:** Sensitive history minimizasyonu, no raw notes telemetry, private aggregate cache ve user scope.
- **Performans:** Precomputed grouped analytics; her chat/render full ledger taraması yok.
- **Mobil:** Insights/card/chart ve açıklama drill-down; örneklem ve tarih aralığı görünür.
- **Veri doğruluğu:** Proxy nedensellik değildir; az veriyle genelleme yapılmaz; yatırım sayısını artıran KPI kullanılmaz.
- **Çıkış:** Doğru segment/matematik ve privacy testleri; ürün dili kullanıcıyı suçlamaz veya daha fazla trade'e itmez.

### Phase 18 — PWA, MOBILE POLISH, OFFLINE/DEGRADED EXPERIENCE

- **Hedef/kapsam:** Installable PWA, safe cache/last-known offline etiketi, isteğe bağlı web push, günlük touch kullanım iyileştirmesi.
- **Giriş/bağımlılık:** Phase 17 READY; önceki tüm UI fazları zaten mobil gate'lerini geçmiş olmalı.
- **Test:** Install/update/offline/reconnect, logout/account-switch cache cleanup, notification opt-in/dedup, tüm route viewport ve touch E2E.
- **Güvenlik:** Hassas API responses kontrolsüz service-worker cache'e yazılmaz; push payload privacy ve session ayrımı.
- **Performans:** Mobile cold/warm/offline, CPU/memory/network ve web bütçeleri; cache version/retention kontrolü.
- **Mobil:** Phone/tablet/desktop regresyonu, safe area/keyboard/touch/chart, install deneyimi.
- **Veri doğruluğu:** Offline/cache ≠ canlı; source age korunur, eski veriden yeni güçlü aksiyon/alarm yok.
- **Çıkış:** Offline/degraded freshness, cache privacy ve install/update gerçek doğrulaması.

### Phase 19 — PERFORMANCE HARDENING

- **Hedef/kapsam:** Profiling/slow SQL/index/cache/bundle/icon/chart/worker/AI darboğazlarını ölçerek giderme; yeni feature yok.
- **Giriş/bağımlılık:** Phase 18 READY; önceki baselines ve yeterli temsilî dataset/test ortamı.
- **Test:** k6/Locust eşdeğeri yük, concurrent dashboard/cold-warm cache, 10K chart, scanner, worker ve AI latency regression; functional tests korunur.
- **Güvenlik:** Optimizasyon user scope/rate/privacy/freshness'i aşamaz; shared cache veri sızdıramaz.
- **Performans:** §24 bütçelerine göre önce/sonra p75/p95, request/query counts, pool/queue/cache hit/bundle/memory; ortam ve örnek sayısı yazılır.
- **Mobil:** Düşük kaynaklı cihaz profili, touch INP, skeleton CLS ve chart CPU/memory kontrolü.
- **Veri doğruluğu:** Downsampling/aggregation ve cached snapshot aynı semantiği taşır; stale label/invalidation kaybolmaz.
- **Çıkış:** **Performance budget report**; başarısız bütçe sessizce yükseltilmez. Lab ölçümü field p75 yerine gösterilmez; veri yoksa ölçüm sınırı açıktır.

### Phase 20 — SECURITY HARDENING + FINAL RELEASE AUDIT

- **Hedef/kapsam:** Threat model ve tüm kalite/regresyon, staging ZAP, secrets rotation, backup/restore, tüm ekran/mobile/data/license audit; `docs/FINAL_RELEASE_AUDIT.md`.
- **Giriş/bağımlılık:** Phase 19 READY; staging test user, encrypted backup/retention, dependency/image/secret kanıtları. Public açılış için §75 uzman compliance artefact'ları gerekir.
- **Test:** Auth/IDOR/CSRF/XSS/SSRF/prompt-injection/rate/oversize; migration clean+previous upgrade; gerçek restore/reconciliation; staging smoke ve tüm ana E2E.
- **Güvenlik:** TLS/CSP/HSTS/headers, DB/Redis public kapalı, secret rotation/runbooks; gitleaks/Trivy/audit/static/ZAP sonuçları ve açık bulgular.
- **Performans:** Release production build ve bütçe regresyonları; cold/warm/degraded/load kanıtları final rapora bağlanır.
- **Mobil:** Tüm ana ekranlarda otomatik viewport + gerçek görsel/touch/keyboard inceleme; yapılmayan manuel QA açıkça NOT EXECUTED.
- **Veri doğruluğu:** Source/freshness, no fake live, ledger/snapshot/math/bias/recovery; provider display/cache/history/redistribution hakları ve no auto trade kontrolü.
- **Çıkış:** Kanıtlı final release audit, kritik açık başarısızlık yok. Public/commercial için **hukuk uzmanı incelemesi/sınıflama/gerekli izinler/KVKK/sözleşmeler/provider hakları** belgelidir; yalnız `LEGAL_COMPLIANCE_APPROVED=true` yetmez. Gerekli ürün dili değişikliği master güncellenmeden yapılmaz.

## 4. Faz listeleri arasında kaybolmayacak bağımlılıklar

| Master kapsamı | İlk sahibi | Tamamlama bağımlılığı |
|---|---|---|
| Onboarding ve Settings | 1 | Risk/portföy ekranı 8–9 ile bağlanır |
| Watchlist / global search | 4 | Karar 10, kavram search 12, alarm shortcut 14 |
| Ana Sayfa tam sıralaması | 4 temel | Portfolio 8, risk 9, briefing 11, learning 12, fırsatlar 13, alerts 14 |
| Instrument detail tam kapsamı | 4 temel | Technical 5, pattern 6, fundamentals/KAP 7, risk 9, decisions 10, Mentor 11, backtest 15 |
| Portfolio cashflow/benchmark/curve | 8 | Drawdown/risk 9; reason/horizon analytics 17 |
| Pattern eğitimi | 6 marker | 12 canonical article, 15 historical results |
| Basit market regime / sürümler | 10 | 15 evaluation, 16 segment/challenger |
| Publication/corporate-action/historical universe | 3/7 veri koruma | 15 test motoru; Phase 15'e kadar provenance kaybedilemez |
| Backup/restore ve retention | 0 prosedür sınırı; 1/3/8/11 gerçek veri sahibi | Public veya korunması gereken gerçek veri kullanımı öncesi uygulanır; 20 final denetim |
| Ops metrics/runbooks | 0 log/health | 3 provider/worker/gaps, 7 KAP lag, 11 AI cost, 15 backtest, 16 version |

İsteğe bağlı TimescaleDB, Zustand, dark/light theme, gelişmiş indicator/pattern seti, email/push ve admin diagnostics yalnız master koşulları ve somut ihtiyaçla değerlendirilir. Fonlar/ABD hisseleri/read-only broker import/household/custom strategy gibi §70 uzantıları şimdi uygulanmaz. Otomatik broker emri bu roadmap'in kapsamı değildir.

## 5. Bağımsız completion ve kanıt sözleşmesi

Gelecekte her faz `docs/phases/phase_XX_completion.md` üretir; Phase 0 raporu orada tek içerik olarak tutulabilir, istenirse kökten yalnız link verilir. Bu çalıştırmada **hiçbir completion raporu oluşturulmadı**.

Master §33'teki 22 alan zorunludur: scope, changed files, migrations, endpoints, UI routes, security, performance, gerçekten çalıştırılan automated tests ve exact counts, typecheck/lint/build/security scans, clean/upgrade migrations, mobile automated/manual QA, limitations/deferred items, rollback, evidence ve READY/NOT READY.

Kanıt kaydı komut + cwd + tarih + commit/snapshot + ortam/dataset + exit code + test counts + artifact/run URL içermelidir. Test sonucu `AUTOMATED PASS`, doğrudan kod incelemesi `CODE INSPECTION PASS`, çalıştırılmayan kontrol `NOT EXECUTED` olarak ayrılır. Gerçek manuel gözlem ayrıca cihaz/viewport/adım/çıktı ile yazılır. “Works/secure/optimized/production ready/fully responsive/all tests pass” gibi iddialar tek başına kabul değildir.

## 6. Readiness ve dış kapılar

Phase 0 başlangıcı için bilinen ürün/mimari blocker yoktur. Kullanıcının Docker'ı açmasından sonra daemon salt okunur sorgusu başarılıdır (GAP E12). pnpm çalışır; npm launcher hatası nedeniyle plan pnpm'i önerir. uv kurulumu, dependency compatibility/registry, gerçek Compose, Git remote/CI erişimi implementation görevlerinde doğrulanacaktır.

Gerçek CI yeşil sonucu olmadan Phase 0 kapanamaz. Gerçek BIST/KAP/EVDS/haber kaynağı izinleri ilgili adapter aktivasyonundan önce; chart lisansı Phase 4'ten önce; point-in-time veri Phase 15 gate'inden önce doğrulanır. Public/commercial launch §75 kanıtları tamamlanana kadar **BLOCKED**'dır; bu durum local Phase 0 başlangıcını engellemez.
