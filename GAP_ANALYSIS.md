# Master Spec / Repository Gap Analysis

Denetim tarihi: 2026-09-05. Durum: **PLANLAMA DENETİMİ — IMPLEMENTATION YAPILMADI**.

Nihai ürün ve mimari kaynağı yalnızca [BORSA_TAKIP_MASTER_SPEC.md](BORSA_TAKIP_MASTER_SPEC.md) dosyasıdır. Bu belge mevcut kanıtı, eksikleri ve doğrulanması gerekenleri kaydeder; ürün kararlarını değiştirmez. Faz eşlemesi [ROADMAP.md](ROADMAP.md), yalnız Phase 0 görevleri [phase_00_plan.md](phase_00_plan.md) içindedir.

## 1. Okuma ve denetim kapsamı

Master spec UTF-8 olarak, numaralı ve kesintisiz 1–650, 651–1300, 1301–1950, 1951–2600, 2601–3250, 3251–3918 satır aralıklarında tamamen okundu. Bölüm 0–76, bütün Phase 0–20 tanımları ve `END OF MASTER SPEC` dahildir. Dosya 89.172 bayttır.

Okunan kaynak SHA-256:

`9A11AEF132A6B2ADCD616B3908E283EA9F1CBB63C45E2BFC91085F5210753F74`

Repository incelemesi bu okuma tamamlandıktan sonra yapıldı. Kaynak dosya değiştirilmedi. Uygulama başlatılmadı, paket kurulmadı, Git deposu oluşturulmadı, container çalıştırılmadı, finansal hesap ya da feature yazılmadı.

## 2. Kanıt kayıtları

Komutlar proje kökünde, PowerShell oturumunda çalıştırıldı. Çıktı özeti gerçek gözlemdir; CLI bulunması çalışan geliştirme altyapısı anlamına gelmez.

| Kanıt | İşlem | Gözlem ve sınır |
|---|---|---|
| E01 | `Get-Item`, UTF-8 `Get-Content`, `Get-FileHash` | Master spec 3.918 satır, 89.172 bayt; yukarıdaki hash. Tam metin okundu. |
| E02 | `Get-ChildItem -Force`; `rg --files --hidden --no-ignore` (dependency/cache dizinleri hariç) | Planlama belgeleri oluşturulmadan önce kökte yalnız `BORSA_TAKIP_MASTER_SPEC.md` vardı. Alt dizin yoktu. |
| E03 | `git rev-parse --show-toplevel`; `git status --short --branch` | Her ikisi `fatal: not a git repository (or any of the parent directories): .git` döndürdü. Yerel Git deposu yok. |
| E04 | Kök ve `C:\` seviyesine kadar ebeveynlerde `AGENTS.md` varlık kontrolü | Bu zincirde `AGENTS.md` bulunmadı. E02 kapsamında alt dizin talimatı da yok. |
| E05 | `Get-Command` | git, rg, node, npm, pnpm, corepack, python, docker PATH üzerinde bulundu; `py` ve `uv` bulunmadı. PATH dışında kurulumlar araştırılmadı. |
| E06 | `git --version`; `node --version`; `python --version` | Git 2.54.0.windows.1, Node v24.13.1, Python 3.12.7. Bunlar kurulu sürümler; güncel stable/LTS veya proje uyumluluğu onayı değildir. |
| E07 | Ayrı çağrı olarak `npm --version` | Exit 1: `MODULE_NOT_FOUND`; kullanıcı npm dizinindeki `npm-cli.js` çözümlenemedi. npm.ps1 ve kurulumdaki npm-cli.js dosyaları incelendi/varlıkları kontrol edildi; ortam onarılmadı. |
| E08 | `pnpm --version` | Exit 0: 11.25.0. Paket kurma, registry erişimi ve build denenmedi. |
| E09 | `docker --version`; `docker compose version` | Docker 28.4.0, Compose v2.39.4-desktop.1. Her ikisi Docker config erişim uyarısı verdi. |
| E10 | `docker info --format '{{.ServerVersion}}'` | Exit 1. Docker config erişimi reddedildi; `//./pipe/docker_engine` bulunamadığı için daemon bağlantısı kurulamadı. Daemon kurulu değil, kesinlikle kapalı veya yalnız yetki sorunu var şeklinde daha ileri sonuç çıkarılamaz. |
| E11 | Kullanıcı Docker'ı açtıktan sonra aynı salt okunur kontrol | Kısıtlı oturumda exit 1; bu kez named-pipe için `Access is denied`. Kullanıcının Docker'ı açmış olması bağlantı doğrulamasının yerine geçirilmedi. |
| E12 | Aynı `docker info` kontrolü onaylı sandbox dışı erişimle | Exit 0: server version `28.4.0`. Daemon erişimi bu yürütme bağlamında doğrulandı. Container/Compose app çalıştırılmadı. |

E06 birden fazla komut içeren çağrıydı; son komutun exit kodu npm sonucunu temsil etmez. E07 bağımsız tekrar ile npm başarısızlığını doğrular. E09 CLI sürüm başarısı daemon erişiminin başarılı olduğu anlamına gelmez.

## 3. Statü kuralları

| Statü | Bu denetimde kullanım |
|---|---|
| `IMPLEMENTED` | Gereksinimi karşılayan gerçek uygulama kodu ve ilgili yapılandırma doğrudan doğrulanmış. Test çalıştırılmış olduğu ayrıca belirtilir. |
| `PARTIALLY_IMPLEMENTED` | Gereksinimin yalnız kanıtlanabilen bir kısmı kodda mevcut. |
| `NOT_IMPLEMENTED` | İncelenen dizinde ilgili uygulama, şema veya yapılandırma yok. |
| `CONFLICT` | Gerçek mevcut kod/yapılandırma master spec'in kesin kararına aykırı. |
| `NEEDS_VERIFICATION` | Dış servis, izin, lisans, çalışma ortamı veya ölçüm sonucu mevcut kanıtla doğrulanamıyor. |

**Hiçbir ürün özelliği `IMPLEMENTED` veya `PARTIALLY_IMPLEMENTED` değildir.** Dokümanda bir özelliğin yazılı olması implementasyon kanıtı değildir. Kod bulunmadığı için kod–spec `CONFLICT` saptanmadı. Aşağıdaki `NOT_IMPLEMENTED` satırlarının ortak fiziksel kanıtı E02/E03'tür; hayali dosya veya satır referansı verilmez.

## 4. Repository envanteri

Denetim öncesi ağaç:

```text
Borsa Takip Destek/
└── BORSA_TAKIP_MASTER_SPEC.md
```

| Alan | Statü | Doğrulanan durum | Sahip faz |
|---|---|---|---|
| Monorepo / Git / README / ADR | `NOT_IMPLEMENTED` | frontend, backend, docs, infra, scripts, .git, README yok | 0 |
| Backend / Python proje manifesti | `NOT_IMPLEMENTED` | FastAPI, Pydantic, SQLAlchemy, httpx kodu veya pyproject yok | 0; domainler kendi fazında |
| Frontend / JS manifesti | `NOT_IMPLEMENTED` | Next.js/React/TypeScript/Tailwind app ve package.json yok | 0 |
| Package manager / lockfile | `NOT_IMPLEMENTED` | Projede seçilmiş manager, pnpm/npm/uv lockfile yok; makinedeki CLI'lar E05–E08 | 0 |
| DB / migration | `NOT_IMPLEMENTED` | PostgreSQL bağlantısı, ORM, Alembic, migration yok | 0 baseline |
| Cache / worker / queue | `NOT_IMPLEMENTED` | Redis veya worker yapılandırması yok | 0 Redis ve queue ADR; 3 worker |
| Test altyapısı | `NOT_IMPLEMENTED` | pytest, Vitest, Testing Library, Playwright, test fixture yok | 0 baseline |
| Lint / typecheck / formatting | `NOT_IMPLEMENTED` | Ruff, mypy/pyright, ESLint, tsc, formatter config yok | 0 |
| Environment / secrets | `NOT_IMPLEMENTED` | .env.example, .gitignore, config doğrulaması yok | 0 |
| Docker / deployment | `NOT_IMPLEMENTED` | Dockerfile, Compose, reverse proxy, deployment manifesti yok | 0 local temel; public release gate öncesi deployment |
| CI/CD / scan | `NOT_IMPLEMENTED` | Pipeline, quality gate, gitleaks, Trivy config yok | 0 CI; 20 final audit |
| Authentication / authorization | `NOT_IMPLEMENTED` | Login, session, user scope, IDOR testleri yok | 1 |
| Güvenlik kontrolleri | `NOT_IMPLEMENTED` | Rate limit, CSRF, XSS/SSRF kontrolü, headers, audit log yok | 0 temel; ilgili endpointin geldiği faz |
| Reusable components / tasarım sistemi | `NOT_IMPLEMENTED` | Layout, form, card, chart, responsive component yok | 0 küçük kabuk; ilgili UI fazları |
| Market-data kodu | `NOT_IMPLEMENTED` | Provider adapter, DTO, canonical mapping, quote/candle yok | 2–3 |

## 5. Ürün, akış ve ekran gap matrisi

Her satırdaki alt gereksinimler kapsam dahilindedir; `uygun veri varsa`, `opsiyonel`, `sonraki iterasyon` nitelikleri master spec'teki anlamıyla korunur.

| ID | Gereksinim / kabul kapsamı | Spec bölümü | Statü | Faz / bağımlılık |
|---|---|---|---|---|
| P01 | Gör → Anla → Sor → Analiz et → Risk → Karar → Takip → Öğren; başlangıç/orta düzey, Türkçe, kısa açıklama ve ayrıntı açılımı | 1, 49, 62–63, 72 | `NOT_IMPLEMENTED` | 1–17; tam döngü 16–17 ile |
| P02 | BIST hisseleri/endeksler, gram/ons altın, USD/TRY, EUR/TRY, BTC; provider genişleme sınırları | 2.1, 3, 70 | `NOT_IMPLEMENTED` | 2–4; majör kripto genişlemesi sonraki iterasyon |
| P03 | Onboarding: deneyim, vade, risk/limitler, real/paper ayrımı, gecikme ve Mentor sınırları | 21, 50, 59 | `NOT_IMPLEMENTED` | 1; gerçek portföy akışı 8 |
| P04 | Desktop sekiz bölüm; mobile 4–5 ana hedef + ikincil menü; safe area ve klavye erişimi | 21.1, 23, 29 | `NOT_IMPLEMENTED` | 0 kabuk; 1/4 ve ekran sahipleri |
| P05 | Global arama: sembol/şirket/varlık/kavram ve sonuç türü | 21.2, 60 | `NOT_IMPLEMENTED` | 4 instrument; 12 kavram |
| P06 | Ana Sayfa sırası: freshness, briefing, portföy, uyarılar, piyasalar, watchlist, fırsatlar, isteğe bağlı öğrenme önerisi | 21.3–4, 41 | `NOT_IMPLEMENTED` | 4 temel; 8/9/11/12/13/14 bağlı parçalar |
| P07 | Piyasalar altı üst kart, BIST/altın/döviz/kripto sekmeleri; fiyat/değişim/hacim ve skor sıralama | 21.5, 41 | `NOT_IMPLEMENTED` | 4 temel; 5/10 skorlar |
| P08 | Instrument detail fiyat/zaman/vade; chart, skorlar, Market View, Personal Action, reliability, risk, temel/KAP, Mentor, backtest ve portföy etkisi | 21.6, 41, 58, 66 | `NOT_IMPLEMENTED` | 4–11; 15 geçmiş bağlam |
| P09 | User-scoped watchlist add/remove, fiyat/değişim, karar ve alarm kısayolu | 60 | `NOT_IMPLEMENTED` | 4; 10 karar; 14 alarm |
| P10 | Gerçek/sanal portföy sekmeleri; değer, P/L, benchmark, dağılım, pozisyon, geçmiş, journal | 2.2, 21.8, 41, 61 | `NOT_IMPLEMENTED` | 8; 9 risk; 17 davranış |
| P11 | What-if, mevcut/sonraki ağırlık, limit uyarısı, pozisyon aralığı; mobil step/bottom sheet; kullanıcı son kararı verir | 2.6, 13, 21.11 | `NOT_IMPLEMENTED` | 9 |
| P12 | Mentor chat / quick prompts / Neden / Detaylandır; kaynak ve zaman; net beş aksiyon, yetersiz veride BEKLE | 2.3–4, 17, 21.9, 39, 41 | `NOT_IMPLEMENTED` | 10–11 |
| P13 | Bilgi Merkezi Q&A, arama/kategoriler, son öğrenilenler, üç seviye, 10 parçalı kavram şablonu, canonical içerik, term popover | 2.10, 18, 21.10, 67 | `NOT_IMPLEMENTED` | 12 |
| P14 | Eğitim içeriği: RSI/MACD/SMA/EMA/Bollinger/ATR/hacim/destek-direnç; F/K/PD-DD/ROE/ciro/kâr/borç; çeşitlendirme/volatilite/drawdown/korelasyon/faiz/enflasyon | Phase 12, 18 | `NOT_IMPLEMENTED` | 12; teknik ve sade anlatım review |
| P15 | Pattern marker: ad, tarihler, kalite, invalidation, kavram linki, varsa historical backtest | 65 | `NOT_IMPLEMENTED` | 6 marker; 12 eğitim; 15 sonuç |
| P16 | Fırsat filtreleri, raw opportunity / user fit ayrımı, neden/risk/veri zamanı; desktop table/mobile card | 19, 21.7, 41 | `NOT_IMPLEMENTED` | 13 |
| P17 | Bildirim kuralı/geçmişi; fiyat, RSI, KAP, haber, karar, yoğunlaşma, günlük kayıp; in-app, dedup/cooldown, FOMO'suz dil | 7.13, 20, 41 | `NOT_IMPLEMENTED` | 14; PWA push 18, email opsiyonel |
| P18 | Ayarlar: risk, vade, limitler, açıklama seviyesi | 7.7, 21, 41 | `NOT_IMPLEMENTED` | 1 |
| P19 | Başarı: benchmark'a göre risk-ayarlı performans, drawdown/yoğunlaşma/FOMO azalması, karar kalibrasyonu, öğrenme | 1.5, 16, 61–62 | `NOT_IMPLEMENTED` | 8/15/16/17; öğrenme 12 |
| P20 | Garanti getiri / auto trade / transfer / copy-trading / HFT / V1 short selling yok; kullanıcıya saygılı dil ve uygun disclaimer | 0.2, 3, 31.2, 49–50 | `NOT_IMPLEMENTED` | Tüm fazlarda kapsam ve negatif kabul kontrolü |

## 6. Mimari ve domain gap matrisi

| ID | Gereksinim | Spec bölümü | Statü | Faz |
|---|---|---|---|---|
| A01 | Modüler monolit + ayrı worker, açık domain service sınırları; mikroservis eklenmemesi | 0.3, 6 | `NOT_IMPLEMENTED` | 0 ADR; 3 worker |
| A02 | Canonical frontend stack; server/client sınırı; TanStack server state, URL filtre/vade, local UI state, Zustand yalnız ihtiyaç varsa | 5.1, 53, 68 | `NOT_IMPLEMENTED` | 0 temel; kullanıldığı fazda kütüphane |
| A03 | FastAPI/Pydantic/SQLAlchemy 2 tarzı/Alembic/httpx; public boundary type hints, saf hesaplar; PostgreSQL authoritative | 5.2–3, 53 | `NOT_IMPLEMENTED` | 0 temel |
| A04 | UUID canonical instruments, provider sembol eşlemesi, exchange/currency/sector; rename/delist/suspension | 7.1–2, 48 | `NOT_IMPLEMENTED` | 2; historical universe 15 |
| A05 | Quote snapshot geçmiş kaynağı değildir; candles unique policy/compound index, final/raw/adjusted ayrımı | 7.3, 26, 54 | `NOT_IMPLEMENTED` | 3 |
| A06 | Financial periods: dönem sonu/published_at/consolidation/source; typed metrics, raw girdiler, derived provenance | 7.4, 10 | `NOT_IMPLEMENTED` | 7 |
| A07 | Disclosure external ID/hash/attachments/ingestion; factual extraction ve interpretation ayrı; haber join/hash/trust tier | 7.5–6, 11 | `NOT_IMPLEMENTED` | 7 |
| A08 | Multi-user uyumlu users/profile; gerçek ve paper portfolios; ayrı ownership | 7.7–8 | `NOT_IMPLEMENTED` | 1, 8 |
| A09 | Authoritative transaction ledger; BUY/SELL/DIVIDEND/CASH_IN/OUT/FEE/TAX/ADJUSTMENT, Decimal quantity/price/fee/tax/FX; correction/reversal | 7.8, 12, 26.1 | `NOT_IMPLEMENTED` | 8 |
| A10 | Ledger'dan positions; belgeli average cost, realized/unrealized P/L, cash/sector/asset weights; cache yalnız türev | 7.8, 12, 31.2 | `NOT_IMPLEMENTED` | 8 |
| A11 | Cashflow-aware getiri (TWR/XIRR ADR), benchmark, equity/drawdown/allocation history, eksik fiyat ≠ sıfır | 12.2–3, 61 | `NOT_IMPLEMENTED` | 8–9; karşılaştırma 15 |
| A12 | Journal reason codes, confidence/vade/tez/invalidation; hızlı giriş; davranış segmentleri ve yargılamayan açıklama | 7.9, 12.4, Phase 17 | `NOT_IMPLEMENTED` | 8; 17 analiz |
| A13 | Signal snapshots input/as_of/horizon/raw score/version; immutable decision snapshots, weights/engine/data references | 7.10–11, 43 | `NOT_IMPLEMENTED` | 5–10 |
| A14 | Backtest run/result şeması: universe/params/versions/costs/status/benchmark; örnek sayısı ve çoklu metrik | 7.12, 15 | `NOT_IMPLEMENTED` | 15 |
| A15 | Alert rule/event fingerprint/delivery state; audit actor/action/entity/safe diff/request ID | 7.13–14 | `NOT_IMPLEMENTED` | 1 audit temel; 14 alerts |
| A16 | MarketDataProvider: batch/single quote, candles, health; timeout/retry/rate-limit/map/schema/unit/UTC/error | 4, 8 | `NOT_IMPLEMENTED` | 2–3 |
| A17 | BIST lisanslı capability; KAP erişim şartları; TCMB EVDS key; haber/makro/KAP adapter sınırları | 4, 7, 11, 73, 75 | `NOT_IMPLEMENTED` | 2–3 market; 7 diğer kaynaklar |
| A18 | LIVE/DELAYED/EOD/STALE/UNAVAILABLE; source/ingestion zamanı; lisans ve semantik uyumlu labeled fallback | 8, 28, 37, 47, 58, 64 | `NOT_IMPLEMENTED` | 2–4; 10/14 fail-safe |
| A19 | Deterministik SMA/EMA/RSI/MACD/Bollinger/ATR/hacim; formül, warm-up, golden/edge fixtures, version | 9.1–3, 31.3 | `NOT_IMPLEMENTED` | 5 |
| A20 | Trend HH/HL, LH/LL, MA alignment/slope, breakout, destek/direnç yakınlığı; strength + horizon | 9.4 | `NOT_IMPLEMENTED` | 5–6 |
| A21 | Doji/Hammer/Shooting Star/Engulfing; yeterli güvenilirlikte Morning/Evening Star; Double Top/Bottom, triangles, H&S/inverse; test edilebilir detector, kalite/invalidation/version | 9.5 | `NOT_IMPLEMENTED` | 6; flag/pennant sonraki iterasyon |
| A22 | Teknik skor bileşenleri ve horizon ağırlıkları; ADX/Stochastic/OBV/VWAP/ROC/Ichimoku sonraki iterasyon | 9.1, 9.6 | `NOT_IMPLEMENTED` | 5 çekirdek; ekler ayrıca planlanır |
| A23 | Temel motor: büyüme/kârlılık/borç/ROE/EPS/F-K/PD-DD/temettü; sektör bağlamı; missing != 0, quality penalty | 2.7, 10 | `NOT_IMPLEMENTED` | 7 |
| A24 | Fetch→validate→dedup→tier→entity→facts→event/sentiment→store; social tek başına sinyal değildir | 2.8–9, 11 | `NOT_IMPLEMENTED` | 7 |
| A25 | Risk: yoğunlaşma/cash floor/position size/volatilite/drawdown; yeterli history'de korelasyon, uygun veride likidite; no-mutation what-if | 13 | `NOT_IMPLEMENTED` | 9 |
| A26 | Deterministik beş aksiyon, Market View ≠ User Action; data quality BEKLE, versiyonlu eşikler/reasons, reliability başarı olasılığı değildir | 2.3–4, 14, 66 | `NOT_IMPLEMENTED` | 10 |
| A27 | Mentor tool-first, typed output, numeric/action override engeli; provider/tool hatası açık, AI yokken core hesap devam | 17, 28, 39, 46 | `NOT_IMPLEMENTED` | 11 |
| A28 | Backtest event-time erişimi; future/publication leakage, survivorship, corporate action, fill timing, cost/slippage, OOS/walk-forward, frozen test set | 15, 31.4, 38; kullanıcı talebi | `NOT_IMPLEMENTED` | 3/7 veriyi korur; 15 motor |
| A29 | Outcome +1/5/20/60 işlem günü, benchmark/segment/regime; min N/confidence/bounded change, shadow champion/challenger, sürümlü promotion | 16, 42–43 | `NOT_IMPLEMENTED` | 10 basit regime; 15 doğrulama; 16 governance |
| A30 | Versioned `/api/v1`, typed DTO/OpenAPI, standard errors/correlation, pagination/range/rate limits, freshness payload | 30, 69 | `NOT_IMPLEMENTED` | 0 sözleşme temeli; ilgili domain fazları |

## 7. Çapraz kalite ve operasyon gap matrisi

| ID | Gereksinim | Spec bölümü | Statü | Faz / kabul yaklaşımı |
|---|---|---|---|---|
| Q01 | Her aktif fazda plan, gerçek completion, başarısız exit'te durma; global DoD ve 15 kabul sorusu | 0, 33–34, 71, 76 | `NOT_IMPLEMENTED` | 0 süreç altyapısı; bu belgeler yalnız planlama çıktısı |
| Q02 | Unit/integration/migration/API contract/component/E2E; lint/type/build; Hypothesis/golden/negatif testler | 0.4, 5.5, 31 | `NOT_IMPLEMENTED` | 0 harness; her domain kendi kanıtı |
| Q03 | Financial precision: UTC, Decimal/NUMERIC, quantization/accounting policy, overflow/missing kontrolü | 7.1, 25.4, 31, 53 | `NOT_IMPLEMENTED` | 0 politika; 2/3/5/7/8/9/10/15 gerçek hesap testleri |
| Q04 | Production p75 LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 | 24.1 | `NOT_IMPLEMENTED` | İlk UI'dan ölçüm; field p75 yalnız gerçek örneklem varsa |
| Q05 | Quote cache-hit p95 <150ms; dashboard cache-hit <400ms; 1Y daily candles <500ms | 24.2 | `NOT_IMPLEMENTED` | 3–4 onward; 0 health ayrı baseline |
| Q06 | N+1 yok, batch, async I/O, pools, gerçek indeks/EXPLAIN, bounded payload, aggregated dashboard | 24, 35, 54 | `NOT_IMPLEMENTED` | İlk data/UI fazından |
| Q07 | Redis TTL; history DB/cache; cache key versions; candle/report/transaction/quote/snapshot invalidation; closed-market refresh | 8.4, 55 | `NOT_IMPLEMENTED` | 3, 5, 7–11 |
| Q08 | Worker precompute technical/fundamental/risk/scanner/briefing; idempotency, checkpoints, locks, backpressure, circuit, retention/gap repair | 24, 47, 56 | `NOT_IMPLEMENTED` | 3 worker; domain işi ilgili faz |
| Q09 | SSE/WebSocket uygun veri sıklığında, exponential reconnect, hedefli query cache update, gereksiz polling/rerender yok | 8.5, 68 | `NOT_IMPLEMENTED` | 4; provider capability'ye göre |
| Q10 | Lightweight Charts mum/hacim/panes/crosshair/tooltips/timeframe/overlay; attribution; 2K/10K benchmark, incremental update/lazy/aggregation | 2.11, 4.4, 22 | `NOT_IMPLEMENTED` | 4–6; eğitim 12 |
| Q11 | Grafik axis/percent/absolute/timezone/gaps doğruluğu; portföy allocation/performance/drawdown/benchmark charts | 22, 61 | `NOT_IMPLEMENTED` | 4, 8–9 |
| Q12 | 360/390/430 telefon, tablet portrait/landscape, 1280+/wide desktop; ≥~44 CSS px, touch, taşma/dialog/safe area, card/table | 23, 40 | `NOT_IMPLEMENTED` | Her UI fazı; 18'e ertelenmez |
| Q13 | Semantic HTML, keyboard/focus, WCAG AA hedefi, renk+metin/ikon, screen reader errors, reduced motion, chart metin özeti | 22, 29 | `NOT_IMPLEMENTED` | Her UI fazı |
| Q14 | Argon2id, secure HttpOnly SameSite session, rotation/revoke; local bypass yalnız explicit loopback | 25.1 | `NOT_IMPLEMENTED` | 0 exposure guard; 1 auth |
| Q15 | User-scope / IDOR portfolios/transactions/journal/alerts/mentor; CSRF state-changing cookie endpoints | 25.2–3 | `NOT_IMPLEMENTED` | 1 temel; her user-data fazı |
| Q16 | Backend input/overflow/enum/date validation; parameterized SQL; XSS safe Markdown; no raw HTML | 25.4–6 | `NOT_IMPLEMENTED` | Endpoint/içerik geldiği faz |
| Q17 | SSRF allowlist/DNS-private IP/redirect/timeout/size/content-type; tool allowlist, no arbitrary URL/shell; untrusted documents | 11.3, 25.7, 25.10 | `NOT_IMPLEMENTED` | 2/3, 7/11 |
| Q18 | Secret gitignore/fake env/production store/redaction; rate limits login/search/AI/alerts/backtest | 25.8–9 | `NOT_IMPLEMENTED` | 0 secrets; 1/4/11/14/15 limits |
| Q19 | gitleaks, dependency audits, Bandit/eşdeğer, Trivy CI; ZAP staging; checks kapatılarak geçiş yok | 0, 5.5, 25.11 | `NOT_IMPLEMENTED` | 0 baseline; 20 final |
| Q20 | TLS, DB/Redis public değil; CSP/HSTS/nosniff/frame/referrer/permissions headers | 5.6, 25.12 | `NOT_IMPLEMENTED` | 0 local güvenlik; public'e açılmadan prod kontrol |
| Q21 | Auth/ledger/risk/decision mutations audit; JSON request/job/provider/duration/error logs; secret/prompt/notes minimizasyonu | 7.14, 25.13, 27, 45 | `NOT_IMPLEMENTED` | 0 correlation; 1 audit ve ilgili fazlar |
| Q22 | API/provider latency-errors/freshness, queue depth/failure/cache/AI cost/DB pool, gaps/lag/divergence metrics | 27 | `NOT_IMPLEMENTED` | 0 health/log; kaynak oluştuğu faz |
| Q23 | Liveness/readiness/dependencies ayrı; provider outage core'u kapatmaz; partial/stale/AI-unavailable durumları | 27.4, 28, 47 | `NOT_IMPLEMENTED` | 0 health; 2–4/10/11 |
| Q24 | Alembic-only; clean→head/previous→head, destructive approval, backup/rollback; ledger atomic ve ingestion idempotent | 26 | `NOT_IMPLEMENTED` | 0 baseline; 3/8 ve tüm migrationlar |
| Q25 | Otomatik PostgreSQL backup, encrypted/offsite, retention ve gerçek restore testi | 5.6, 26.3 | `NOT_IMPLEMENTED` | 0 runbook kapsamı; 8 veri koruma; public release öncesi, 20 final tekrar |
| Q26 | History/immutable decisions uzun retention; ledger correction; kullanıcı chat silebilir; sınırlı log/audit retention | 44–45 | `NOT_IMPLEMENTED` | 1 politika; 3/8/10/11 uygulama |
| Q27 | Finansal veri analytics/log'a gitmez; LLM minimum context, user/snapshot cache izolasyonu, token budget/latency | 17.7, 45–46 | `NOT_IMPLEMENTED` | 0 log politika; 11 |
| Q28 | PWA safe cache, install/offline labels, hassas responses kontrolsüz cache olmaz, push isteğe bağlı | Phase 18 | `NOT_IMPLEMENTED` | 18; temel mobile ilk günden |
| Q29 | Dev mock/staging allowed provider+test user/prod backup+smoke; riskli provider/weights/pattern/challenger feature flags | 52 | `NOT_IMPLEMENTED` | 0 ayrım; ilgili fazlar |
| Q30 | Ops diagnostics yalnız admin: health/ingest/stale/jobs/version | 57 | `NOT_IMPLEMENTED` | Opsiyonel; ihtiyaç olan data fazında, yeni büyük admin ürün kapsamı değil |
| Q31 | Kanıtlı public/commercial SPK değerlendirmesi, izin/ortaklık gerekiyorsa tamamlanması, sözleşme/KVKK/veri lisansı; flag yeterli değil | 75 | `NOT_IMPLEMENTED` | Public açılış öncesi ayrı zorunlu kapı |

## 8. Dış doğrulamalar ve gerçek engeller

Bu çalışma lisans, hukuk veya güncel sürüm araştırması yapmış sayılmaz. Master spec'teki referanslar sağlanan metin olarak okundu; harici sayfaların güncel şartları, erişim sözleşmeleri ve gerçek provider credentials doğrulanmadı. Aşağıdaki sonuçlar dış dünyaya ilişkin doğrulanmış hukuki/teknik hüküm değildir.

| ID | Statü | Bulgular / gereken kanıt | Hangi işi engeller? |
|---|---|---|---|
| ENV-01 | `NEEDS_VERIFICATION` | E10/E11 ilk erişim hataları, kullanıcının Docker'ı açması sonrası E12'de onaylı yürütme bağlamında başarılı daemon sorgusuyla çözüldü. Compose servisleri/volume/network/image çekme henüz denenmedi. | **Önceki daemon erişim blocker'ı giderildi.** Gerçek Compose ve DB/Redis testleri Phase 0 görevleridir. Kısıtlı oturum named-pipe erişimi ayrıca sınır olarak kaydedilir. |
| ENV-02 | `NEEDS_VERIFICATION` | npm launcher E07 başarısız; pnpm E08 çalışıyor. Plan pnpm önerir. Registry/network erişimi ve frozen install ayrıca denenmeli. | pnpm ile planlanan başlangıç için kanıtlı blocker değil. npm kullanan komutlar için önce onarım veya doğrulanmış alternatif gerekir. |
| ENV-03 | `NEEDS_VERIFICATION` | uv PATH üzerinde yok; Python binary var fakat wheel/toolchain uyumluluğu denenmedi. | Phase 0 toolchain görevinin giriş kontrolü. Kurulum gereksinimi tek başına ürün blocker'ı değil. |
| CI-01 | `NEEDS_VERIFICATION` | Yerel Git yok; remote/CI hesabı/runner erişimi denetlenemedi. Seçilen remote'da gerçek yeşil run URL/SHA yok. | **Zorunlu kapanış önkoşulu:** CI kanıtı olmadan `PHASE 0 READY` yazılamaz. Remote erişiminin imkânsız olduğu iddia edilmez. |
| EXT-01 | `NEEDS_VERIFICATION` | Runtime/framework stable/LTS, peer compatibility, lockfile ve image/tag/digest henüz seçilmedi. | Phase 0 bağımlılık pinleme öncesi resmi kaynak kontrolü. Kurulu sürümler onaylanmış sürüm değildir. |
| EXT-02 | `NEEDS_VERIFICATION` | BIST gösterim/cache/history/redistribution, realtime/delayed/EOD hakları; fallback semantiği | Gerçek provider aktivasyonu Phase 3 ve public kullanım. Phase 2 deterministic mock mümkün. |
| EXT-03 | `NEEDS_VERIFICATION` | KAP sözleşmesi/API/rate limit; EVDS API erişimi/key/seri semantiği; haber ve varsa sosyal kaynak kullanım izinleri | Phase 7 gerçek entegrasyon; sağlayıcı yokluğu sessiz feature iptali yapılamaz. |
| EXT-04 | `NEEDS_VERIFICATION` | Kullanılacak Lightweight Charts sürümünün lisans/attribution ve API özellikleri | Phase 4 chart entegrasyonu/dağıtımı öncesi. |
| LEGAL-01 | `NEEDS_VERIFICATION` | §75 kapsamındaki uzman yazılı analizi, ürün sınıflaması, gerekirse izin, KVKK/sözleşmeler ve provider izinleri yok | **BLOCKER: public/commercial açılış.** Kişisel/local foundation başlangıcını engellemez. |
| DATA-01 | `NEEDS_VERIFICATION` | Point-in-time history, geçmiş universe/delist, publication timing ve corporate-action verisi doğrulanmadı | Phase 3/7 kaynak seçimi ve Phase 15 bias gate. Eksik veriyle yanıltıcı başarı raporu üretilemez. |

## 9. Talimat farklılıkları ve küçük kararlar

1. Master §0/§76 `docs/ROADMAP.md` ve `docs/phases/phase_00_plan.md` önerir. Bu oturumdaki açık kullanıcı talebi kök dosyaları istediğinden `ROADMAP.md` ve `phase_00_plan.md` köktedir. İki ayrı içerik kopyası tutulmaz. İleride gerekiyorsa docs altında yalnız yönlendirme dosyası oluşturulur; master içerik değişmez.
2. Master §76 ilk çalıştırma adım 5 uygulamayı söyler; kullanıcı bu çalıştırmada açıkça yasakladı. Bu tur yalnız analiz ve plan üretir, completion üretmez.
3. Master §76 içindeki “20 faz” ifadesine rağmen açık başlıklar 0–20, yani 21 fazdır. Sıralı başlıkların tamamı roadmap'e alınmıştır; Phase 20 düşürülmez. Bu sayım farkı ürün davranışı blocker'ı değildir.
4. Watchlist, onboarding, Daily Briefing, global search, benchmark, basit market regime ve öğrenme bağlantıları bazı faz listelerinde tekrarlanmıyor. Yukarıdaki sahip fazlar master'daki var olan kapsamın izlenebilir eşlemesidir; yeni feature değildir.
5. §14.6 ağırlık değişikliğinde backtest/OOS ister; tam backtest motoru Phase 15'tedir. Phase 10 ilk sürümü açıkça başlangıç config'i olarak kaydeder, ölçülmüş başarı iddia etmez. Phase 15/16 doğrulaması ve governance tamamlanmadan üretim ağırlık ayarı/promotion yapılmaz. Phase 10'a backtest motoru taşınmaz.
6. §28'de KAP eksikliğinde haber ağırlığının çıkarılması yalnız önceden tanımlı, sürümlü degraded policy ile uygulanır. Kritik güncel veri eksikliği her durumda BEKLE'ye götürür; hata anında sessiz ağırlık optimizasyonu yapılmaz.
7. Backtest için survivorship sınırlamasını yazmak tek başına başarı gate'ini geçirmez. Gerekli point-in-time veri yoksa çalışma sınırlı keşif olarak ayrılır; bias güvenliği doğrulanmadan genellenebilir strateji başarısı veya release kabulü iddia edilmez. Bu, kullanıcının daha sıkı bias şartını korur.

## 10. Sonuç

**Ürün/mimari çelişkisi: saptanmadı. Phase 0 planlama: hazır. Phase 0 implementation: başlamadı. Phase 0 tamamlanma statüsü: NOT READY.**

Kullanıcının Docker'ı açması sonrası E12 ile daemon erişimi doğrulandı; önceki ENV-01 başlangıç engeli giderildi. Başlangıcı durduran bilinen ürün/mimari veya daemon blocker'ı kalmadı. Gerçek Compose çalışması ve CI kanıtı henüz yoktur ve kapanış için zorunludur. Provider/lisans/hukuk doğrulamaları kendi aktivasyon ve public release kapılarında kalır; yerel foundation için gereksiz onay sorusu oluşturmaz.

Ürün testleri, typecheck, lint, build, security scan, migration, performans ölçümü, manuel UI/mobile QA ve restore: **NOT EXECUTED — çalıştırılacak uygulama/altyapı yoktu.** CLI ve dosya denetimi sonuçları bu kontrollerin yerine geçmez.
