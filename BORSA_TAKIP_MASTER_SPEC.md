# BORSA TAKİP — MASTER PRODUCT & ENGINEERING SPECIFICATION

> **Belge rolü:** Bu dosya Borsa Takip projesinin tek ana kaynak dokümanıdır (Single Source of Truth / SSOT).
>
> **Hedef okuyucu:** Codex veya projeyi geliştirecek başka bir yazılım ajanı / geliştirici.
>
> **Kural:** Codex, planlama veya kodlama yapmadan önce bu dosyanın tamamını okumalıdır. Bu dosyayla çelişen eski notlar, sohbet özetleri, rastgele TODO'lar veya varsayımlar geçersizdir. Bu dosya güncellenmedikçe ürün vizyonu ve mimari kararları değiştirilmemelidir.
>
> **Tarih:** 2026-09-05
>
> **Durum:** Ürün vizyonu ve ilk ana mimari donduruldu; implementasyon fazlara bölünerek ilerleyecek.

---

# 0. CODEX İÇİN ZORUNLU ÇALIŞMA SÖZLEŞMESİ

Bu bölüm proje boyunca **değişmez geliştirme kurallarıdır**. Her fazın başında ve sonunda kontrol edilmelidir.

## 0.1. Temel çalışma yöntemi

1. Önce bu `BORSA_TAKIP_MASTER_SPEC.md` dosyasını tamamen oku.
2. Mevcut repository varsa önce gerçek kodu, migration'ları, testleri ve dependency durumunu incele; eski raporlara güvenerek varsayım yapma.
3. Her faz başlamadan önce o faz için `docs/phases/phase_XX_plan.md` üret.
4. Plan; kapsamı, kapsam dışını, veri modelini, API değişikliklerini, UI değişikliklerini, testleri, güvenliği, performans hedeflerini ve rollback planını içermelidir.
5. Yalnızca aktif fazı uygula. Gelecek fazların işlevlerini “hazır olsun” diye önceden ekleme.
6. Her değişiklik test edilebilir, gözlemlenebilir ve geri alınabilir olmalıdır.
7. Her faz sonunda `docs/phases/phase_XX_completion.md` üret.
8. Completion raporu yalnızca gerçekten çalıştırılan testleri `AUTOMATED PASS`, doğrudan incelenen kodu `CODE INSPECTION PASS`, yapılmayan elle kontrolleri ise `NOT EXECUTED` olarak yazmalıdır. Hiçbir manuel kontrol yapılmadan “manuel QA geçti” yazılamaz.
9. Bir fazın çıkış kapısı başarısızsa sonraki faza geçme.
10. Testi geçsin diye ürün gereksinimini gevşetme; gereksinim değişecekse önce bu master spec güncellenmelidir.

## 0.2. Kesinlikle yapılmayacaklar

- “AI karar verir” diyerek finansal hesaplamaları LLM'ye bırakma.
- RSI, MACD, EMA, SMA, ATR, risk, P/L, ağırlık, ortalama maliyet vb. sayısal hesapları prompt içinde tahmin ettirme.
- Yetkisiz / kullanım koşullarına aykırı scraping'i sistemin temel veri kaynağı haline getirme.
- Borsa İstanbul gerçek zamanlı verisini lisans durumu doğrulanmadan “ücretsiz canlı veri” kabul etme.
- `float` ile para ve portföy muhasebesi yapma.
- Pozisyon tablosunu işlem geçmişinden bağımsız, elle güncellenen gerçek kaynak haline getirme.
- API anahtarı, şifre, token veya provider credential'larını repository'ye yazma.
- Sessiz `except Exception: pass` kullanma.
- Veri kaynağı hatasını eski veriyi “canlı” gibi göstererek gizleme.
- Haber / KAP metinlerini LLM prompt'una filtrelemeden talimat olarak dahil etme.
- Kullanıcının parasını otomatik broker emrine dönüştürme. V1 ve ana roadmap kapsamında **otomatik emir yürütme yoktur**.
- “Garantili getiri”, “kesin yükselecek”, “%X kesin kazanırsın” gibi dil üretme.
- Backtest sonucunu gelecek performans garantisi gibi gösterme.
- Look-ahead bias, survivorship bias veya corporate-action düzeltmelerini görmezden gelen backtest üretme.
- Testleri, lint'i, typecheck'i veya security scan'i kapatarak faz tamamlanmış sayma.

## 0.3. Mimari prensip

**Modüler monolit + ayrı background worker** kullanılacaktır.

Neden:
- Kişisel/erken aşama ürün için mikroservisler gereksiz ağ gecikmesi ve operasyon yükü yaratır.
- Finansal veri, portföy, sinyal ve karar motorları aynı transaction / domain sınırlarında daha güvenli yönetilir.
- Worker; veri çekme, indikatör ön hesaplama, KAP/haber işleme, backtest ve bildirim gibi kullanıcı isteğinden bağımsız işleri yürütür.
- Gelecekte gerçekten ihtiyaç oluşursa domain sınırları servisleşmeye uygundur.

## 0.4. Her fazın zorunlu kalite kapıları

Her faz için aşağıdakilerin ilgili olanları **geçmeden** faz kapanmaz:

- Unit test
- Integration test
- Migration test
- API contract test
- Frontend component test
- E2E smoke test
- Typecheck
- Lint
- Build
- Security static analysis
- Secret scan
- Dependency audit
- Performance regression kontrolü
- Accessibility kontrolü (UI fazlarında)
- Mobile viewport kontrolü (UI fazlarında)
- Veri provenance / freshness kontrolü (data fazlarında)
- Finansal hesap doğruluk testleri (calculation fazlarında)

---

# 1. ÜRÜN VİZYONU

## 1.1. Ürün adı

**Borsa Takip**

## 1.2. Ana amaç

Borsa Takip, “hangi hisse kesin yükselecek?” diyen bir tahmin botu değildir.

Ürünün amacı:

> **Piyasa verisini, teknik analizi, temel analizi, resmi açıklamaları, haberleri, portföy riskini, kullanıcının yatırım geçmişini ve eğitim içeriğini tek sistemde birleştirerek kullanıcının yatırım karar kalitesini artırmak ve yeni başlayan yatırımcının büyük hatalarını azaltmak.**

Ana ürün döngüsü:

> **Gör → Anla → Sor → Analiz et → Riski kontrol et → Karara bağla → Sonucu takip et → Öğren**

## 1.3. Kullanıcı profili

İlk hedef kullanıcı:
- Yatırıma yeni başlayan veya başlangıç/orta seviye bilgiye sahip.
- BIST başta olmak üzere altın, döviz ve kriptoyu takip ediyor.
- Bütün birikimini tek varlığa koymak yerine sepet mantığını öğrenmek istiyor.
- RSI, MACD, EMA/SMA, F/K, PD/DD gibi kavramları tam bilmiyor olabilir.
- Çok teknik araştırmanın sonucunu sade ve anlaşılır şekilde görmek istiyor.
- “Ne oluyor?” sorusunun yanında “Benim portföyüm açısından ne ifade ediyor?” sorusuna cevap arıyor.
- Sistemden net bir sonuç bekliyor fakat gerekçeleri ve riskleri de görmek istiyor.

## 1.4. Ürünün temel farklılaştırıcısı

Genel amaçlı AI'dan farkı sadece “AI olması” değildir.

Borsa Takip aynı anda şunları kullanır:
- Güncel/gecikmeli piyasa verisi ve veri zaman damgası.
- Tarihsel OHLCV verisi.
- Deterministik teknik indikatör motoru.
- Deterministik pattern / trend motoru.
- Temel finansal veriler.
- KAP açıklamaları.
- Makro veri.
- Güvenilir haber katmanı.
- Sosyal medya sentiment'i (kanıt değil yardımcı sinyal).
- Kullanıcının gerçek portföyü.
- Kullanıcının sanal portföyü.
- İşlem maliyeti ve işlem gerekçesi günlüğü.
- Kullanıcının risk profili ve kişisel limitleri.
- Kullanıcının geçmiş karar davranışı.
- Sistem kararlarının geçmiş performansı.
- Benchmark karşılaştırması.

Bu nedenle aynı hisse için iki farklı kullanıcıya farklı **portföy aksiyonu** üretilebilir.

## 1.5. Başarı tanımı

Ürünün başarısı sadece “TL olarak daha çok para kazandırmak” değildir.

Ana başarı ölçütleri:
1. Benchmark'a göre risk-ayarlı performans.
2. Büyük drawdown'ların ve yoğunlaşma hatalarının azalması.
3. Kullanıcının plansız/FOMO kaynaklı işlem oranının azalması.
4. Kullanıcının işlem öncesi gerekçesinin daha tutarlı hale gelmesi.
5. Mentor kararlarının kalibrasyonu ve geçmiş performansı.
6. Kullanıcının finansal kavramları öğrenme ilerlemesi.

**Ürün garantili getiri iddiasında bulunmaz.**

---

# 2. DONDURULMUŞ ÜRÜN KARARLARI

Aşağıdaki kararlar kullanıcı tarafından onaylanmıştır ve master spec değiştirilmedikçe geçerlidir.

## 2.1. Takip kapsamı

İlk ana kapsam:
- BIST hisseleri
- BIST100 / temel endeksler
- Gram altın
- Ons altın
- USD/TRY
- EUR/TRY
- Bitcoin
- İleride diğer majör kripto varlıklar

Fonlar, ABD hisseleri, Eurobond, türev ürünler ve benzeri varlıklar V1'in zorunlu kapsamı değildir; provider mimarisi genişlemeye hazır olacaktır.

## 2.2. Portföy

İki ayrı portföy tipi:
- **Gerçek Portföy**
- **Sanal / Paper Portföy**

Bu ikisi veri modelinde ve raporlamada karıştırılmayacaktır.

## 2.3. Mentor sonucu

Mentor yalnızca açıklama yapıp bırakmayacaktır.

Her yeterli analizde sonuç şu aksiyonlardan biriyle bağlanacaktır:
- **AL**
- **KADEMELİ AL**
- **BEKLE**
- **KADEMELİ SAT**
- **SAT**

Ancak veri yetersizse zorla pozitif/negatif sinyal üretmek yerine **BEKLE** sonucu verilecek ve `data_quality/insufficient_data` gerekçesi gösterilecektir.

## 2.4. Karar ve açıklama ayrımı

Karar LLM tarafından uydurulmaz.

Akış:

```text
Raw/Normalized Data
      ↓
Technical Engine
      ↓
Pattern / Trend Engine
      ↓
Fundamental Engine
      ↓
Disclosure / News Engine
      ↓
Portfolio Context
      ↓
Risk Engine
      ↓
Decision Engine
      ↓
Structured Decision Object
      ↓
AI Mentor Explanation
```

LLM'nin görevi **hesaplamak değil, açıklamak ve kullanıcı seviyesine uyarlamaktır**.

## 2.5. Vade

Analiz bazında seçilebilir:
- Kısa
- Orta
- Uzun

Varsayılan vade kullanıcı profilinden gelir. Aynı varlık farklı vadelerde farklı skor/karar üretebilir.

## 2.6. Risk

Kullanıcı kişisel sınırlar belirleyebilir:
- Tek hisse maksimum ağırlığı
- Tek sektör maksimum ağırlığı
- Kripto maksimum ağırlığı
- Minimum nakit oranı
- Maksimum işlem riski

Sistem limit aşımını engellemez; güçlü ve açık uyarı verir. Son karar kullanıcıdadır.

## 2.7. Temel analiz

Kapsam:
- Ciro
- Net kâr
- Brüt/operasyonel kârlılık uygun olduğunda
- Borçluluk
- Özkaynak
- F/K
- PD/DD
- ROE
- EPS / hisse başına kâr uygun olduğunda
- Büyüme trendleri
- Temettü geçmişi uygun olduğunda
- Sektör bazlı kıyaslar uygun veri varsa

## 2.8. Haber ve KAP

Haber yalnızca listelenmeyecek:
- Özetlenecek.
- Kaynak gösterilecek.
- Olay türü sınıflandırılacak.
- Şirkete/piyasaya muhtemel etkisinin **yorum** olduğu açıkça ayrılacak.

KAP / resmi açıklama gerçek veri; Mentor etkisi ise yorumdur. Bu ikisi UI'da karıştırılmamalıdır.

## 2.9. Sosyal medya

Sosyal medya sadece **sentiment / ilgi sinyali** olarak kullanılabilir.

- Kaynak gerçeklik doğrulaması değildir.
- Sosyal medya tek başına AL/SAT üretmemelidir.
- Manipülatif içerik ve bot davranışı riski UI'da belirtilmelidir.

## 2.10. Bilgi Merkezi

Bilgi Merkezi:
- Soru-cevap
- Kısa yazılı anlatım
- Basit görsel anlatım
- Gerçek/örnek grafik
- “Nasıl yorumlanır?”
- “Nerede yanıltır?”
- “Ne ile birlikte kullanılır?”
- “Daha teknik anlat” seviyesi

özelliklerine sahip olacaktır.

## 2.11. Grafik

Grafikler:
- Mum grafiği
- Hacim
- RSI
- MACD
- EMA/SMA
- Bollinger
- Destek/direnç
- Pattern marker/overlay
- Zaman aralığı
- Dokunmatik/mobil kullanım
- Responsive yapı

destekleyecektir.

## 2.12. Sistem öz değerlendirmesi

Mentor kendi geçmiş kararlarını ölçmelidir.

Ölçülebilecekler:
- AL sonrası 1/5/20/60 işlem günü performansı
- SAT sonrası kaçınılan düşüş / fırsat maliyeti
- BEKLE kararlarının sonraki davranışı
- Vade bazında başarı
- Sektör bazında başarı
- Teknik/temel/haber kombinasyonu başarısı
- Benchmark'a göre sonuç

Kötü çalışan strateji ağırlıkları **otomatik ve kontrolsüz şekilde** değiştirilmeyecektir. Bkz. Adaptive Decision Governance.

---

# 3. KAPSAM DIŞI / NON-GOALS

İlk ana roadmap kapsamında yapılmayacaklar:

- Broker hesabına bağlanıp otomatik emir verme.
- Kullanıcı onayı olmadan alım/satım gerçekleştirme.
- HFT / milisaniyelik trading.
- Kaldıraçlı işlem optimizasyonu.
- Vadeli işlem / opsiyon motoru.
- Kesin fiyat tahmini iddiası.
- “Yarın şu fiyat olacak” merkezli ürün tasarımı.
- Sosyal medya copy-trading.
- Banka hesabından para transferi.
- Yetkisiz veri yeniden yayınlama.
- Sırf daha çok işlem yaptırmak için kullanıcıyı dürten gamification.

---

# 4. RESMİ VERİ VE LİSANS GERÇEKLERİ

Bu bölüm mimari gereksinimdir.

## 4.1. Borsa İstanbul

Borsa İstanbul resmi veri yayını sayfasına göre piyasa verileri gerçek zamanlı, gecikmeli ve gün sonu bazında **lisanslı veri dağıtıcıları** üzerinden yayımlanır.

Sonuç:
- Sistem bir `MarketDataProvider` abstraction'ına sahip olmak zorundadır.
- BIST gerçek zamanlı data availability hiçbir zaman hard-code edilmemelidir.
- UI her fiyat için `source`, `as_of`, `delay_status` veya eşdeğer freshness bilgisi taşımalıdır.
- Lisanssız gerçek zamanlı veriyi yeniden dağıtacak özellik yapılmamalıdır.

Resmi referans:
- https://www.borsaistanbul.com/en/data/data-dissemination

## 4.2. KAP

KAP, sermaye piyasası ve Borsa mevzuatı uyarınca kamuya açıklanması gereken bildirimlerin elektronik sistemidir ve MKK tarafından işletilir.

KAP sitesinde “Veri Yayın Servisi REST API Entegrasyonu” duyurusu bulunmaktadır; gerçek entegrasyon yapılmadan önce API erişim şartları / sözleşme / rate limit / kullanım koşulları doğrulanmalıdır.

Resmi referanslar:
- https://www.kap.org.tr/tr/about/genel-bilgi
- https://www.kap.org.tr/tr/

## 4.3. TCMB EVDS

TCMB EVDS web servisi API anahtarıyla veri sunar. Kur/makro veri entegrasyonu için öncelikli resmi kaynaklardan biridir.

Resmi referans:
- https://evds2.tcmb.gov.tr/index.php?/evds/userDocs=

## 4.4. Grafik kütüphanesi

Önerilen kütüphane: **TradingView Lightweight Charts**.

Neden:
- Finansal chart odaklı.
- Candlestick/line/histogram desteği.
- Mobil ve web için hafif.
- Büyük veri setleri için performans odaklı özellikleri var.
- Streaming update için son barı `update()` ile güncelleme modeli var.

Önemli:
- Kullanılan sürümün lisans ve attribution şartları uygulanmalıdır.
- Dokümantasyonda public page/app için TradingView attribution gereksinimi belirtilmektedir.

Resmi referans:
- https://tradingview.github.io/lightweight-charts/docs

---

# 5. ÖNERİLEN TEKNOLOJİ YIĞINI

Codex, önemli bir teknik engel bulmadıkça bu canonical stack'i kullanmalıdır. Sürüm numaralarını master spec'e sabitlemek yerine implementasyon anında güncel stable/LTS sürümleri doğrulanıp lockfile ile sabitlenmelidir.

## 5.1. Frontend

- **Next.js** (App Router)
- **React**
- **TypeScript strict mode**
- **Tailwind CSS**
- **shadcn/ui veya erişilebilir headless component yaklaşımı**
- **TanStack Query**: client-side server state / live refresh gerektiren yerlerde
- **Zustand**: yalnızca geçici UI state gerekiyorsa; global server state taşımak için kullanılmaz
- **Lightweight Charts**: finansal grafikler
- **React Hook Form + schema validation**
- **Zod** veya eşdeğer runtime contract doğrulama
- **PWA** desteği ilerleyen fazda

## 5.2. Backend

- **Python**
- **FastAPI**
- **Pydantic**
- **SQLAlchemy 2.x style**
- **Alembic migrations**
- **httpx** provider clients
- **Decimal** tabanlı finansal hesaplar
- NumPy / Pandas yalnızca veri analizi için kontrollü kullanım
- Kritik teknik indikatörlerde mümkün olduğunca kendi doğrulanmış fonksiyonlarımız veya güvenilir bağımlılık + golden test

## 5.3. Veri tabanı

- **PostgreSQL** authoritative relational store
- Timeseries hacmi büyüdüğünde **TimescaleDB extension** değerlendirilebilir; ilk günden zorunlu değildir ancak schema partitioning/indices buna engel olmamalıdır.
- JSONB yalnızca gerçekten şema-esnek provider payload / metadata için; core business data JSON blob'a gömülmemelidir.

## 5.4. Cache / Queue

- **Redis**
  - quote cache
  - distributed lock
  - rate limiting
  - job state/cache
- Background worker:
  - Celery + Redis veya proje ölçeğine uygun güvenilir queue sistemi
  - Seçim bir ADR ile belgelenmeli

## 5.5. Test / kalite

Backend:
- pytest
- pytest-asyncio
- Hypothesis uygun finansal/property testlerde
- Ruff
- mypy/pyright eşdeğeri
- pip-audit
- Bandit veya eşdeğer static security scan

Frontend:
- Vitest
- Testing Library
- Playwright
- ESLint
- TypeScript `tsc --noEmit`
- axe / accessibility testing
- Lighthouse CI uygun olduğunda

Infra/security:
- gitleaks
- Trivy
- OWASP ZAP baseline release aşamasında

## 5.6. Deployment

İlk hedef:
- Docker Compose local/dev
- Dockerized production
- Reverse proxy (Caddy/Nginx veya eşdeğer)
- TLS zorunlu public deployment'ta
- PostgreSQL ve Redis public internete açılmaz
- Backups encrypted/offsite politika ile

---

# 6. REPOSITORY YAPISI

Önerilen monorepo:

```text
borsa-takip/
├─ BORSA_TAKIP_MASTER_SPEC.md
├─ README.md
├─ .env.example
├─ .gitignore
├─ docker-compose.yml
├─ docs/
│  ├─ architecture/
│  │  ├─ adr/
│  │  ├─ data-flow.md
│  │  ├─ security-model.md
│  │  └─ provider-contracts.md
│  ├─ phases/
│  │  ├─ phase_00_plan.md
│  │  └─ ...
│  ├─ api/
│  └─ runbooks/
├─ frontend/
│  ├─ src/
│  │  ├─ app/
│  │  ├─ components/
│  │  ├─ features/
│  │  │  ├─ dashboard/
│  │  │  ├─ markets/
│  │  │  ├─ instrument/
│  │  │  ├─ opportunities/
│  │  │  ├─ portfolio/
│  │  │  ├─ mentor/
│  │  │  ├─ knowledge/
│  │  │  ├─ alerts/
│  │  │  └─ settings/
│  │  ├─ lib/
│  │  └─ types/
│  └─ tests/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ domains/
│  │  │  ├─ instruments/
│  │  │  ├─ market_data/
│  │  │  ├─ technical/
│  │  │  ├─ fundamentals/
│  │  │  ├─ disclosures/
│  │  │  ├─ news/
│  │  │  ├─ portfolio/
│  │  │  ├─ risk/
│  │  │  ├─ decisions/
│  │  │  ├─ backtests/
│  │  │  ├─ mentor/
│  │  │  ├─ knowledge/
│  │  │  ├─ alerts/
│  │  │  └─ users/
│  │  ├─ providers/
│  │  └─ workers/
│  ├─ migrations/
│  └─ tests/
├─ scripts/
└─ infra/
```

Domain'ler birbirinin database tablolarına rastgele erişmez. Repository/service boundary veya açık domain service kullanılmalıdır.

---

# 7. DOMAIN MODELİ VE VERİ ŞEMASI

Aşağıdaki isimler öneridir; gerçek migration'da isimler tutarlı biçimde uygulanmalıdır.

## 7.1. Global veri kuralları

- Tüm internal timestamp'ler UTC.
- UI kullanıcının timezone'unda gösterir; varsayılan `Europe/Istanbul`.
- Para ve fiyat alanları `NUMERIC/DECIMAL`; binary float authoritative finansal storage için kullanılmaz.
- Her market data kaydı `provider`, `source_timestamp`, `ingested_at`, `quality/freshness` bilgisini taşımalıdır.
- `created_at`, `updated_at` tutarlılığı sağlanmalıdır.
- Provider'ın native sembolü ile canonical instrument ID ayrılmalıdır.
- Soft-delete yalnızca gerçekten gerekli entity'lerde; finansal ledger kayıtlarında silme yerine reversal/correction tercih edilir.

## 7.2. Instruments

### `instruments`

Alanlar örneği:
- `id` UUID
- `symbol` canonical
- `name`
- `asset_class` (`equity`, `index`, `fx`, `commodity`, `crypto`...)
- `exchange`
- `currency`
- `sector` nullable
- `industry` nullable
- `is_active`
- `metadata`

### `instrument_provider_mappings`

- `instrument_id`
- `provider_id`
- `provider_symbol`
- `provider_exchange_code`
- `is_primary`

Amaç: veri sağlayıcı değiştiğinde domain sembolleri bozulmasın.

## 7.3. Market data

### `quotes_latest`

Cache/DB latest snapshot. Authoritative long history değildir.

- instrument
- bid/ask uygun olduğunda
- last
- change
- change_percent
- volume
- source timestamp
- ingested timestamp
- delay seconds/minutes if known
- freshness enum
- provider

### `candles`

- instrument_id
- timeframe
- open_time
- close_time
- open/high/low/close
- volume
- adjusted metadata
- provider
- is_final

Unique:
`instrument_id + timeframe + open_time + provider/canonical policy`

Index:
- `(instrument_id, timeframe, open_time DESC)`

Kurumsal aksiyon düzeltmeleri için raw ve adjusted yaklaşım dokümante edilmelidir.

## 7.4. Fundamentals

### `financial_periods`
- company/instrument
- fiscal_period_end
- statement_type
- consolidated flag
- source
- published_at

### `financial_metrics`
Normalized metric rows veya iyi tasarlanmış typed tables.

En az:
- revenue
- net_income
- equity
- total_assets
- total_liabilities / financial debt uygun veri varsa
- eps
- dividend

Derived multiples kaynağı ve hesap zamanı ile saklanabilir ancak raw inputs korunmalıdır.

## 7.5. Disclosures / KAP

### `disclosures`
- id
- instrument/company mapping
- source external id
- title
- category
- published_at
- source_url/reference
- raw_hash
- normalized_text
- attachments metadata
- ingestion_status

### `disclosure_analysis`
- disclosure_id
- event_type
- factual_summary
- extracted numeric facts structured JSON
- impact_label (commentary, not fact)
- model/version
- analysis confidence
- generated_at

Factual extraction ile interpretation ayrı kolon/obje olmalıdır.

## 7.6. News

### `news_items`
- provider article id
- title
- published_at
- source
- canonical url/reference
- instruments[] mapping relational join tercih
- content hash
- trust tier
- sentiment score optional

Duplicate detection hash + title/time similarity ile yapılabilir.

## 7.7. Users / profiles

İlk ürün tek kullanıcı olsa bile schema multi-user compatible olmalıdır.

### `users`
- id
- auth fields
- timezone
- locale

### `investment_profiles`
- experience level
- default horizon
- risk tolerance
- max_single_asset_pct
- max_sector_pct
- max_crypto_pct
- min_cash_pct
- explanation_level

## 7.8. Portfolios

### `portfolios`
- id
- user_id
- name
- type (`real`, `paper`)
- base_currency TRY
- active

### `portfolio_transactions`
**Authoritative ledger.**

- id
- portfolio_id
- instrument_id
- type: BUY/SELL/DIVIDEND/CASH_IN/CASH_OUT/FEE/TAX/ADJUSTMENT vb.
- quantity Decimal
- price Decimal nullable by type
- gross_amount
- fee
- tax
- currency
- fx_rate_to_base when needed
- executed_at
- reason_code
- reason_note
- source (`manual`, `mentor`, etc.)
- created_at

Kayıt sonradan sessizce değiştirilmez. Düzeltme gerekiyorsa audit trail veya correction transaction kullanılır.

### Positions

Pozisyon authoritative değildir; ledger'dan türetilir. Performans gerekirse materialized/cache snapshot tutulabilir.

Hesaplar:
- quantity
- weighted average cost (defined accounting rule)
- realized pnl
- unrealized pnl
- market value
- weight

Accounting yöntemi dokümante edilmeli ve unit testlerle sabitlenmelidir.

## 7.9. Journal / davranış

### `investment_journal_entries`
Her işlemle ilişkilendirilebilir.

Reason codes:
- technical
- fundamental
- news
- long_term_thesis
- price_drop
- social_media
- mentor_recommendation
- other

Ek:
- confidence before trade
- planned horizon
- planned stop/invalidating condition
- planned target optional
- notes

Sonradan outcome ile karşılaştırılır.

## 7.10. Signals

### `signal_snapshots`
- instrument
- horizon
- as_of
- signal family
- signal name
- raw value
- normalized score
- polarity
- version
- input data timestamp

Signal snapshot reproducible olmalıdır.

## 7.11. Decisions

### `decision_snapshots`
Bir karar sonradan yeniden üretilebilmelidir.

- user/portfolio nullable for market-only decision
- instrument
- horizon
- as_of
- technical_score
- fundamental_score
- news_score
- risk_reward_score
- portfolio_fit_score
- data_quality_score
- overall_score
- market_view
- user_action (`BUY`, `SCALE_IN`, `HOLD`, `SCALE_OUT`, `SELL`)
- confidence/reliability score
- reasons structured
- risks structured
- weights version
- decision engine version
- data snapshot references

**Karar snapshot immutable olmalıdır.** Yeni hesap yeni kayıt üretir.

## 7.12. Backtests

### `backtest_runs`
- strategy/version
- universe
- timeframe
- start/end
- benchmark
- costs/slippage assumptions
- data version
- params
- status

### `backtest_results`
- CAGR / total return appropriate
- max drawdown
- win rate
- expectancy
- Sharpe/Sortino where meaningful
- turnover
- benchmark delta
- sample count
- confidence intervals where feasible

## 7.13. Alerts

### `alerts`
Types:
- price threshold
- RSI threshold
- decision changed
- new KAP
- news event
- portfolio risk limit
- daily loss threshold

### `alert_events`
Dedup ve delivery state.

## 7.14. Audit

### `audit_logs`
Security/user-sensitive mutation için:
- actor
- action
- entity
- before/after safe diff
- timestamp
- request correlation id

Credential veya secret loglanmaz.

---

# 8. MARKET DATA PROVIDER MİMARİSİ

## 8.1. Provider interface

Backend domain provider-specific payload görmemelidir.

Örnek interface:

```python
class MarketDataProvider(Protocol):
    async def get_quote(self, instrument: InstrumentRef) -> Quote: ...
    async def get_quotes(self, instruments: list[InstrumentRef]) -> list[Quote]: ...
    async def get_candles(
        self,
        instrument: InstrumentRef,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> list[Candle]: ...
    async def health(self) -> ProviderHealth: ...
```

Her provider adapter:
- auth
- timeout
- retry
- rate-limit
- mapping
- schema validation
- unit conversion
- timestamp normalization
- provider error classification

yapar.

## 8.2. Provider fallback

Fallback yalnızca lisans ve veri semantiği uygunsa.

Örnek:
- Primary quote provider down.
- Secondary delayed provider available.
- Sistem fiyatı gösterir ancak `DELAYED_FALLBACK` etiketiyle.

**Eski cache “LIVE” diye gösterilemez.**

## 8.3. Freshness sınıfları

Öneri:
- `LIVE`
- `DELAYED`
- `END_OF_DAY`
- `STALE`
- `UNAVAILABLE`

Her UI price card'ı freshness durumunu anlayabilir olmalıdır.

## 8.4. Cache stratejisi

- Latest quote: Redis short TTL.
- Candle: DB + cache.
- Daily historical data gereksiz yere provider'dan tekrar çekilmez.
- Market closed ise refresh interval düşürülebilir.
- Batch provider endpoint varsa N+1 quote çağrısı yapma.

## 8.5. Websocket/SSE

Gerçek/veri sıklığı destekliyorsa:
- Server → client live update için WebSocket veya SSE.
- Connection kaybında exponential reconnect.
- Client full historical series'i her tick'te reload etmez.
- Chart `update()` ile son bar/quote günceller.

---

# 9. TEKNİK ANALİZ MOTORU

## 9.1. V1 zorunlu indikatörler

- SMA
- EMA
- RSI
- MACD
- Bollinger Bands
- ATR
- Volume averages / volume ratio

Sonraki iterasyon:
- ADX
- Stochastic
- OBV
- VWAP (veri uygunluğu doğrulanmalı)
- ROC / momentum
- Ichimoku

## 9.2. Hesaplama kuralları

- Formül referansı kod dokümanında yazılmalı.
- Warm-up period açıkça uygulanmalı.
- Eksik candle, split, timestamp anomalisi test edilmeli.
- Aynı input her zaman aynı output üretmeli.
- Hesap versiyonu saklanmalı.

## 9.3. Golden tests

Her indikatör için küçük sabit bir candle dataset'i ve beklenen sonuçlar repository'de bulunmalı.

Testler:
- exact/epsilon tolerance (appropriate numeric type)
- insufficient data
- flat prices
- monotonic prices
- missing/non-final candles
- zero volume

## 9.4. Trend engine

Algılanabilecek yapılar:
- HH/HL
- LH/LL
- MA alignment
- MA slope
- price above/below key averages
- breakout/breakdown
- support/resistance proximity

Trend `bullish/bearish` kelimesine indirgenmemeli; strength + horizon tutulmalıdır.

## 9.5. Pattern engine

İlk güvenilir pattern seti sınırlı tutulmalı:

Candlestick:
- Doji
- Hammer
- Shooting Star
- Bullish/Bearish Engulfing
- Morning/Evening Star uygun güvenilirlikte

Chart:
- Double Top/Bottom
- Triangle variants
- Head & Shoulders / inverse
- Flag/pennant sonradan

Kural:
- Pattern LLM ile “grafiğe bakıp” tahmin edilmeyecek.
- Deterministik/geometrik algorithm veya test edilebilir statistical detector kullanılacak.
- Her detection: start/end points, confidence/quality, invalidation, version taşır.
- Pattern adı doğrudan AL/SAT değildir.

## 9.6. Teknik skor

Skor 0-100 olabilir fakat kullanıcıya sahte kesinlik sunmamalıdır.

Örnek bileşen:
- Trend
- Momentum
- Volume confirmation
- Volatility context
- Pattern confirmation
- Support/resistance risk

Ağırlıklar horizon'a göre değişebilir ve versiyonlanmalıdır.

---

# 10. TEMEL ANALİZ MOTORU

## 10.1. Amaç

“Ucuz/pahalı” gibi tek oranlı hüküm yerine şirket sağlığı, büyüme, kârlılık ve değerleme bağlamı üretmek.

## 10.2. Bileşenler

- Revenue growth YoY / multi-period
- Net income trend
- Margin trend uygun data varsa
- ROE
- Leverage/debt trend
- Equity growth
- F/K
- PD/DD
- EPS
- Dividend history uygun olduğunda

## 10.3. Sektör bağlamı

F/K gibi oranlar sektörler arası doğrudan kıyaslanmamalıdır.

Mümkünse:
- sektör median
- şirket historical percentile
- BIST peer comparison

kullan.

## 10.4. Data-quality

Eksik finansal metrikler sıfır kabul edilmez.

`missing != 0`

Skor, eksik veri varsa quality penalty almalıdır.

---

# 11. KAP / HABER / SENTIMENT MOTORU

## 11.1. Kaynak güven seviyesi

Öneri:

**Tier 1 — Resmi**
- KAP
- TCMB
- TÜİK (entegrasyon olduğunda)
- şirket resmi yatırımcı ilişkileri
- SPK/Borsa İstanbul uygun olduğunda

**Tier 2 — Güvenilir haber**
- seçili finans haber kaynakları

**Tier 3 — Social sentiment**
- sosyal medya / forum

Tier 3 hiçbir zaman Tier 1 ile aynı kanıt statüsünde gösterilmez.

## 11.2. Haber pipeline

```text
Fetch
→ Validate
→ Deduplicate
→ Source Tier
→ Entity/Instrument Link
→ Factual Extraction
→ Sentiment/Event Classification
→ Cache/Store
→ Mentor-ready context
```

## 11.3. Prompt injection güvenliği

Haber/KAP dış içeriktir.

Kurallar:
- İçerik “instructions” olarak değil `untrusted_document` olarak prompt'a girer.
- “Ignore previous instructions” vb. metinler talimat kabul edilmez.
- HTML/script temizlenir.
- Remote content'ten tool çağırma talimatı alınmaz.
- Link açma/attachment işleme domain allowlist ve content-type kontrolünden geçer.

## 11.4. Fact vs interpretation

UI örneği:

**Doğrulanan bilgi**
- Kaynak: KAP
- Tarih
- Açıklanan sözleşme tutarı

**Mentor yorumu**
- Bu tutarın şirket ölçeğine göre anlamlı olabileceği vb.

Bu ayrım schema'da da korunmalıdır.

---

# 12. PORTFÖY MOTORU

## 12.1. Hesaplar

Zorunlu:
- quantity
- average cost
- market value
- realized P/L
- unrealized P/L
- total P/L
- day P/L uygun data varsa
- portfolio weight
- asset-class weight
- sector weight
- cash weight

## 12.2. Benchmark

Portföy performansı en az şu bağlamlardan biriyle kıyaslanabilir:
- BIST100
- Gram altın
- kullanıcının seçtiği benchmark

İleride multi-benchmark.

## 12.3. Cash flow etkisi

Kullanıcının sonradan para yatırması “yatırım getirisi” gibi sayılmamalıdır.

Return hesabı:
- basit toplam farkın yanı sıra cashflow-aware metrik kullanılmalıdır.
- TWR/XIRR türü yaklaşım gereksinimi ayrı ADR ile seçilebilir.

## 12.4. İşlem günlüğü

Her BUY/SELL için mümkünse:
- neden
- planlanan vade
- giriş tezi
- invalidation/stop düşüncesi
- confidence

saklanır.

Ama kullanıcıyı aşırı form doldurmaya zorlamamak için hızlı seçenekler olmalıdır.

---

# 13. RİSK MOTORU

## 13.1. Amaç

Risk motoru yalnızca volatilite skoru değildir. Kullanıcının belirli işlemi sonrası portföyünün nasıl değişeceğini hesaplar.

## 13.2. Zorunlu risk kontrolleri

- Single asset concentration
- Sector concentration
- Asset-class concentration
- Crypto concentration
- Cash floor
- Position size
- Volatility
- Drawdown
- Correlation uygun history varsa
- Liquidity risk uygun veri varsa

## 13.3. İşlem öncesi kontrol

Kullanıcı örneğin ASELS'e 2.000 TL eklemeyi düşündüğünde sistem “what-if” hesaplar:

- Mevcut ağırlık
- İşlem sonrası ağırlık
- Sektör ağırlığı değişimi
- Risk score change
- Limit ihlalleri
- Önerilen maksimum aralık (kişisel risk profilinden)

UI:

```text
İŞLEM ÖNCESİ KONTROL
Varlık: ASELS
Plan: 2.000 TL alım

Tek hisse ağırlığı: %7 → %21
Sektör ağırlığı: %19 → %33
Risk: ORTA → YÜKSEK

UYARI: Kişisel sektör limitiniz %30.
Mentor önerisi: Pozisyon büyüklüğünü azaltmayı değerlendir.
```

Son kararı kullanıcı verir.

## 13.4. Stop / take profit

V1'de:
- Sistem teknik seviyelere göre **öneri** üretebilir.
- Otomatik emir vermez.
- Stop seviyesi “garanti zarar sınırı” gibi anlatılmaz; gap/slippage riski açıklanır.

---

# 14. DECISION ENGINE

Bu projenin kritik domain'idir.

## 14.1. İki ayrı sonuç

Sistem şu ikisini ayırmalıdır:

1. **Market View** — Varlığın teknik/temel bağlamı.
2. **User Action** — Kullanıcının portföyü/riskine göre aksiyon.

Örnek:

```text
Market View: POZİTİF
User Action: BEKLE
Reason: Portföyde aynı sektöre maruziyet zaten limit üzerinde.
```

Bu ayrım zorunludur.

## 14.2. Girdiler

- technical score
- fundamental score
- news/disclosure score
- risk/reward score
- data quality
- volatility
- portfolio fit
- horizon
- recent event risk

## 14.3. Çıktı

Structured object örneği:

```json
{
  "instrument": "ASELS",
  "horizon": "MEDIUM",
  "as_of": "...",
  "market_view": "POSITIVE",
  "user_action": "SCALE_IN",
  "scores": {
    "technical": 82,
    "fundamental": 75,
    "news": 71,
    "risk_reward": 73,
    "portfolio_fit": 66,
    "data_quality": 94,
    "overall": 76
  },
  "reliability": 0.74,
  "positive_factors": [],
  "risk_factors": [],
  "invalidation_conditions": [],
  "engine_version": "..."
}
```

## 14.4. Karar mapping

Exact thresholds kodla versiyonlanacak ve test edilecektir.

Genel davranış:
- Strong favorable + acceptable risk → AL
- Favorable but entry/portfolio concentration caution → KADEMELİ AL
- Mixed / low-quality / insufficient edge → BEKLE
- Deteriorating but not full invalidation / excessive concentration → KADEMELİ SAT
- Strong negative/invalidation → SAT

**Data quality düşükse otomatik default: BEKLE.**

## 14.5. Reliability

“Güven %74” ifadesi gerçek başarı olasılığı gibi sunulmamalıdır.

Adlandırma tercihi:
- `Analiz Güvenilirliği`
- `Veri ve sinyal uyumu`

Bu skor:
- data completeness
- signal agreement
- backtest sample support
- model stability

gibi faktörlerden türetilmelidir.

## 14.6. Ağırlık yönetişimi

Decision weights configuration/version tablosunda tutulabilir.

Her değişiklik:
- backtest
- out-of-sample validation
- regression comparison
- change reason
- version

taşımalıdır.

---

# 15. BACKTEST MOTORU

## 15.1. Ana amaç

“Bu pattern internette bullish yazıyor” yerine:

> Bu sinyal/koşul bu veri evreninde geçmişte nasıl davranmış?

sorusunu cevaplamak.

## 15.2. Zorunlu bias kontrolleri

- **Look-ahead bias yok.** Bir timestamp'te sadece o anda bilinebilecek veri kullanılabilir.
- **Survivorship bias** mümkün olduğunca ele alınır; historical universe gerektiğinde saklanır.
- **Corporate actions** adjusted data ile doğru ele alınır.
- **Publication timing:** bilanço/KAP verisi yayınlanmadan önce backtest'e giremez.
- **Transaction costs** sıfır varsayılmamalı; configurable cost/slippage.
- **Signal close timing:** kapanış verisi kullanılan sinyal aynı kapanış fiyatından hayali olarak sınırsız fill olmamalıdır; execution assumption açık olmalıdır.

## 15.3. Evaluation

- Train/validation/test veya walk-forward
- Out-of-sample
- Benchmark
- Multiple horizons
- Minimum sample size
- Confidence interval mümkün olduğunda

## 15.4. “Win rate” tek metrik değildir

Göster:
- total return
- max drawdown
- expectancy
- profit factor uygun olduğunda
- average gain/loss
- win rate
- turnover
- benchmark delta
- Sharpe/Sortino uygun olduğunda

## 15.5. Reproducibility

Her run:
- data version/hash
- strategy version
- parameters
- code commit SHA mümkünse
- costs
- universe

saklamalıdır.

---

# 16. ADAPTIVE DECISION GOVERNANCE — SİSTEMİN KENDİNİ DEĞERLENDİRMESİ

Kullanıcı sistemin kendi kararlarının başarısını ölçmesini istemektedir. Bu özellik “model kendi kendine kontrolsüz öğrenir” şeklinde yapılmayacaktır.

## 16.1. Tracking

Her decision snapshot için forward outcome hesaplanır:
- +1 trading day
- +5
- +20
- +60
- seçilen horizon'a uygun ek window

Benchmark-adjusted outcome da hesaplanır.

## 16.2. Strategy performance

Grupla:
- signal family
- horizon
- sector
- market regime
- decision action
- technical/fundamental/news combination

## 16.3. Minimum sample guardrail

Çok az örnekle weight değişmez.

Örn. exact threshold master spec'e sabitlenmek zorunda değildir ama implementation'da:
- minimum N
- confidence bounds
- bounded max change

zorunludur.

## 16.4. Champion / Challenger

- `Champion`: production decision config
- `Challenger`: yeni ağırlık/config

Challenger önce historical + forward shadow evaluation görür.

Production'a promotion:
- automated quality gates
- no catastrophic risk regression
- versioned approval

sonrası olur.

## 16.5. No online runaway

Her kayıptan sonra anlık weight değiştirmek yasaktır.

Amaç:
- overfitting'i önlemek
- regime noise'a aşırı tepkiyi önlemek
- denetlenebilirlik

---

# 17. AI MENTOR MİMARİSİ

## 17.1. Rol

Mentor:
- Kullanıcının sorusunu anlar.
- Gerekli domain tool/service sonuçlarını toplar.
- Structured facts/decision object üzerinden cevap üretir.
- Kullanıcının bilgi seviyesine göre sadeleştirir.
- Kaynakları ve veri zamanını gösterir.

Mentor **financial calculator veya market data provider değildir**.

## 17.2. Tool-first yaklaşım

Örnek soru: “ASELS nasıl?”

Mentor orchestration:
1. Instrument resolve.
2. Fresh quote + candles.
3. Technical snapshot.
4. Fundamentals.
5. Latest relevant KAP/news.
6. User portfolio exposure.
7. Risk engine.
8. Decision engine.
9. Explanation.

Bir tool başarısızsa bunu gizleme.

## 17.3. Cevap formatı

Varsayılan kısa cevap:

```text
ASELS — Orta Vade
Karar: KADEMELİ AL
Analiz güvenilirliği: 74/100
Risk: Orta

Neden?
• Trend ve momentum olumlu.
• Temel görünüm destekliyor.
• Ancak mevcut fiyat direnç bölgesine yakın.
• Portföyünde sektör ağırlığı artacağı için tam pozisyon yerine kademeli giriş daha dengeli.

Dikkat:
• ...

Veri zamanı: ...
```

Kullanıcı “detaylandır” derse genişlet.

## 17.4. Net karar zorunluluğu

Yeterli bağlam varsa cevap sonunda action olmalıdır.

Yetersiz veri:

```text
Karar: BEKLE
Sebep: Güncel fiyat/finansal veri güvenilirliği yeterli değil.
```

## 17.5. Hallucination guardrails

Mentor:
- kaynaksız güncel fiyat uyduramaz
- olmayan KAP açıklaması uyduramaz
- bilinmeyen bilanço rakamını tahmin edemez
- tool sonucu ile çelişen sayısal iddia kuramaz
- hesap yapması gerekiyorsa backend calculator/domain function kullanır

## 17.6. Model output validation

LLM internal response mümkün olduğunda typed schema ile alınır:
- summary
- positive factors
- risks
- educational links
- caveat

User action engine'den gelir; LLM değiştiremez.

## 17.7. Caching

Aynı instrument/horizon/data snapshot için Mentor base explanation kısa TTL cache edilebilir; kişisel portfolio bölümü ayrı üretilebilir.

---

# 18. BİLGİ MERKEZİ / ÖĞRENME SİSTEMİ

## 18.1. Amaç

Çok teknik araştırmayı yeni başlayan kişinin anlayabileceği hale getirmek.

Sistem teknik doğruluktan vazgeçmeden **basit anlatır**.

## 18.2. Her kavram için standart içerik şablonu

1. **30 saniyede nedir?**
2. **Ne ölçer / ne anlatır?**
3. **Grafikte nasıl görünür?**
4. **Basit yorumlama**
5. **Nerede yanıltabilir?**
6. **Tek başına kullanılır mı?**
7. **Hangi göstergelerle birlikte anlamlı?**
8. **Gerçek veya açıkça “temsili” grafik örneği**
9. **Daha teknik anlat**
10. İlgili kavramlar

## 18.3. Seviyeler

- Başlangıç
- Orta
- Teknik

Default kullanıcı profiline göre.

## 18.4. Görsel bileşenler

Generative image zorunlu değildir. Kavram eğitimi için deterministic SVG/Canvas/chart component tercih edilir.

Örnek:
- RSI 0–100 scale
- 30/70 zones
- MACD / signal crossover
- EMA/SMA reaction comparison
- Bollinger band expansion
- support/resistance illustration

**Temsili veri ile gerçek veri görsel olarak etiketlenmelidir.**

## 18.5. Terime dokun

Mentor/hisse ekranında:
- `RSI`
- `ATR`
- `PD/DD`

kelimeleri bilgi kartına linklenebilir.

Mini popover + “Detaylı öğren” akışı.

## 18.6. Knowledge source governance

Canonical içerik mümkün olduğunca editlenebilir structured knowledge article olarak saklanır.

AI her seferinde internetten sıfırdan “RSI nedir” uydurmak yerine canonical verified content'i sadeleştirir.

---

# 19. FIRSAT TARAYICI

## 19.1. Amaç

“Bugün kesin alınacak hisseler” listesi değil.

Başlık:
- “Dikkat Çekenler”
- “Sistem Tarafından İlginç Bulunanlar”

## 19.2. Filtreler

- Horizon
- Risk level
- Technical strength
- Fundamental quality
- News catalyst
- Volume anomaly
- Portfolio fit

## 19.3. Personalized ranking

Raw opportunity score ile user-fit score ayrıdır.

Bir banka hissesi objektif olarak güçlü olabilir; kullanıcı bankacılıkta aşırı yoğunlaşmışsa kişisel listede aşağı düşebilir.

## 19.4. Explainability

Her item:
- Neden listede?
- Hangi sinyaller?
- Riskler?
- Data as-of?
- Portfolio etkisi?

---

# 20. BİLDİRİM SİSTEMİ

## 20.1. V1 alert türleri

- Price > / < threshold
- RSI threshold
- New KAP disclosure
- Important news
- Decision changed
- Portfolio concentration limit
- Daily portfolio loss threshold

## 20.2. Dedup

Aynı KAP veya aynı threshold olayı kullanıcıyı spamlememeli.

- event fingerprint
- cooldown
- state transition

## 20.3. Delivery

Başlangıç:
- in-app

Sonra:
- Web Push/PWA
- email opsiyonel

## 20.4. Notification ethics

“FOMO” yaratıcı dil kullanma.

Kötü:
> HEMEN AL! KAÇIYOR!

Doğru:
> ASELS için sistem kararı BEKLE → KADEMELİ AL olarak değişti. Nedenlerini görmek için aç.

---

# 21. UI / UX MİMARİSİ

## 21.1. Genel navigasyon

Desktop sidebar:
- Ana Sayfa
- Piyasalar
- Fırsatlar
- Portföy
- Mentor
- Bilgi Merkezi
- Bildirimler
- Ayarlar

Mobile bottom navigation için 4–5 ana destination; diğerleri More/Menu içinde.

Önerilen mobile ana:
- Ana Sayfa
- Piyasalar
- Fırsatlar
- Portföy
- Mentor

Bilgi/Bildirim/Ayarlar secondary menu.

## 21.2. Global search

Arayabilir:
- symbol
- company name
- asset
- concept (`RSI nedir`)

Search result type açık olmalı.

## 21.3. Ana Sayfa

Order:
1. Header + data freshness/global market status
2. Mentor Daily Briefing
3. Portfolio summary
4. Important personal alerts
5. Markets strip
6. Watchlist
7. Personalized opportunities
8. Learning suggestion optional

Ana sayfa sonsuz kart yığını olmamalıdır.

## 21.4. Daily Briefing

Kısa:
- Bugün piyasa ne durumda?
- Portföyümde ne önemli?
- Yeni resmi açıklama var mı?
- Riskte önemli değişim?
- 1–3 dikkat çekici item.

Kullanıcı detail açabilir.

## 21.5. Piyasalar

Top cards:
- BIST100
- USD/TRY
- EUR/TRY
- Gram altın
- Ons altın
- BTC

Tab sections:
- BIST
- Altın
- Döviz
- Kripto

Sort:
- performance
- volume
- technical score
- overall score

## 21.6. Instrument Detail

Above fold:
- Symbol/name
- price + freshness
- day change
- market view
- user action
- reliability
- risk
- horizon selector

Then:
- Chart
- score cards
- Mentor summary
- fundamentals
- KAP/news
- backtest/context
- portfolio impact

## 21.7. Fırsatlar

Card/table responsive hybrid.

Desktop table; mobile cards.

## 21.8. Portföy

Tabs:
- Gerçek
- Sanal

Top:
- value
- P/L
- benchmark delta
- risk health

Then:
- allocation charts
- positions
- risk flags
- transaction history
- journal insights

## 21.9. Mentor

Chat layout fakat finance-specific quick prompts:
- Portföyümü değerlendir
- Bu hisseyi analiz et
- Bu kararı neden verdin?
- 2.000 TL eklesem riskim nasıl değişir?
- Bu terim ne demek?

## 21.10. Bilgi Merkezi

- Search/Ask prominent
- Categories
- Recent learned
- Concept article
- interactive/visual sections

## 21.11. İşlem Öncesi Kontrol

Modal yerine mobile bottom sheet / dedicated step uygun olabilir.

Asla küçük kırmızı text'e gömülü önemli risk uyarısı yapılmaz.

---

# 22. TASARIM SİSTEMİ VE GRAFİK KALİTESİ

## 22.1. Tasarım hedefi

- Modern
- Finans uygulaması ciddiyeti
- Yoğun bilgi ama temiz hierarchy
- “Casino/trading neon” estetiğinden kaçın
- Dark ve light theme desteklenebilir

## 22.2. Renk

Renk tek başına anlam taşımamalı.

Pozitif/negatif:
- ikon + text + color birlikte

Color-blind erişilebilir palet.

## 22.3. Grafikler

### Finansal chart
- Lightweight Charts
- Candlestick
- Volume histogram
- Indicator panes
- Crosshair
- Tooltip
- responsive resize
- touch pan/zoom

### Portfolio charts
- Allocation donut/bar
- performance line
- drawdown chart
- benchmark comparison
- sector exposure

## 22.4. Grafik performansı

- Chart component lazy loaded where possible.
- Visible range kadar data yükleme stratejisi değerlendir.
- Büyük history dataset'te server aggregation/downsampling.
- Streaming update'de full `setData` tekrarı yapma; incremental update.
- 10K+ points için library'nin data conflation özelliği güncel sürümde değerlendirilebilir.

## 22.5. Görsel doğruluk

- Y-axis scales doğru.
- Percent vs absolute mode açık.
- Timezone label.
- Missing session gaps gizlenmemeli/yanlış interpolate edilmemeli.
- Log scale gelecekte opsiyonel.

---

# 23. MOBİL UYUMLULUK — ZORUNLU

Mobil “sonradan responsive yaparız” değildir. Her UI fazı mobile-first kontrol edilir.

## 23.1. Breakpoint yaklaşımı

Exact px design system'de tanımlanabilir; test viewport minimum:
- ~360px phone
- ~390/430px modern phone
- tablet portrait
- tablet landscape
- desktop 1280+
- wide desktop

## 23.2. Mobile chart

- Minimum readable height.
- Horizontal scroll yerine responsive layout.
- Indicator controls collapsible.
- Touch target >= ~44 CSS px hedeflenmeli.
- Tooltip parmağın altında kaybolmamalı.
- Bottom sheet kullanımı.

## 23.3. Mobile tables

Geniş finans tabloları küçük ekranda zorla sıkıştırılmaz.

- important columns card'a dönüşür
- secondary data accordion/detail
- sticky symbol/price gerekirse

## 23.4. E2E mobile

Playwright viewport tests zorunlu.

Her ana route için en az:
- no horizontal overflow
- nav usable
- chart loads
- action buttons visible
- dialogs fit viewport

---

# 24. PERFORMANS — BİRİNCİ SINIF GEREKSİNİM

Kullanıcı için sistemin hızlı olması kritik gereksinimdir.

## 24.1. Frontend performance budget

Hedefler production p75, gerçekçi ölçüm altyapısı oluştuğunda:
- LCP ≤ 2.5s
- INP ≤ 200ms
- CLS ≤ 0.1

Local/dev yerine production build ölçülmeli.

## 24.2. API budget

Cache hit:
- latest quote endpoint p95 hedef < 150ms
- dashboard aggregated endpoint p95 hedef < 400ms

DB/history endpoint:
- common instrument 1Y daily candles p95 < 500ms hedef

Bu hedefler infra kapasitesine göre ölçülür; regression gate oluşturulur.

## 24.3. Dashboard

- Browser'dan 15 ayrı endpoint waterfall yapma.
- `dashboard` BFF/aggregated endpoint veya paralel fetch.
- Non-critical widgets lazy/deferred.
- Skeleton layout stable olmalı; CLS yapmamalı.

## 24.4. Backend

- Async I/O for providers.
- connection pooling.
- batch quote fetch.
- Redis cache.
- proper DB indexes.
- N+1 query test/inspection.
- expensive scoring request thread'de gereksiz tekrar hesaplanmaz.

## 24.5. Precomputation

Worker precompute:
- latest technical snapshots
- opportunity rankings
- daily fundamentals scores
- portfolio risk snapshots where useful

User request geldiğinde her şeyi sıfırdan pandas ile hesaplama.

## 24.6. Load shedding

Provider down veya worker overload durumunda:
- stale-but-labeled data
- partial response
- queue backpressure
- circuit breaker

yaklaşımı.

## 24.7. Performance test

Release öncesi:
- API k6/Locust equivalent
- chart large dataset test
- Lighthouse
- cold/warm cache comparison

---

# 25. SECURITY MODEL

Finansal uygulama olduğu için portföy verisi hassas kabul edilir.

## 25.1. Authentication

Public deployment:
- secure password hashing: Argon2id önerilir
- secure HTTP-only cookies veya iyi tasarlanmış token session
- `Secure`, `HttpOnly`, uygun `SameSite`
- refresh/session rotation
- logout revocation

Tek kullanıcı local mode varsa auth bypass yalnızca explicit local/dev config ile ve public interface'e bind edilmeden.

## 25.2. Authorization

Her user-owned entity query'sinde user scope zorunlu.

IDOR testi:
- portfolio
- transaction
- journal
- alert
- mentor conversation

## 25.3. CSRF

Cookie auth kullanılıyorsa state-changing endpoints CSRF korumalı olmalıdır.

## 25.4. Input validation

Backend authoritative validation:
- quantity > 0
- impossible prices
- date ranges
- symbol lookup
- percentage limits
- numeric overflow
- enum whitelist

Frontend validation UX içindir, güvenlik değildir.

## 25.5. SQL injection

ORM parameterization. Raw SQL kullanılırsa param binding zorunlu.

## 25.6. XSS

News/KAP/AI content HTML olarak raw render edilmez.

Markdown renderer:
- sanitization
- disallow dangerous HTML
- safe link attributes

## 25.7. SSRF

Backend arbitrary URL fetch endpoint sunmamalıdır.

External fetch:
- allowlisted provider hosts
- DNS/IP private network protection
- redirect limits
- timeout
- content-size limit

## 25.8. Secrets

- `.env` gitignore
- `.env.example` fake values
- production secret store/environment
- logs mask secrets
- CI gitleaks

## 25.9. Rate limiting

- login
- mentor AI calls
- search
- alerts creation
- expensive backtest

## 25.10. AI abuse / prompt injection

- system/developer prompt server-side
- untrusted external docs delimited
- tool allowlist
- schema validation
- LLM cannot invoke arbitrary shell/URL
- tool arguments validated

## 25.11. Dependency/security scans

CI:
- npm audit appropriate severity gate
- pip-audit
- gitleaks
- Trivy image scan
- static security scan

Release:
- OWASP ZAP baseline against staging

## 25.12. Headers

Production:
- CSP
- HSTS
- X-Content-Type-Options
- frame-ancestors / clickjacking protection
- Referrer-Policy
- Permissions-Policy appropriate

## 25.13. Audit logging

Loglanacak:
- auth events
- portfolio mutation
- transaction create/correct
- risk settings changes
- decision config changes

Loglanmayacak:
- password
- token
- provider secret
- full sensitive prompt if not necessary

---

# 26. VERİ GÜVENLİĞİ / BÜTÜNLÜĞÜ

## 26.1. Financial ledger

Portfolio transaction writes DB transaction içinde.

## 26.2. Idempotency

Provider ingestion:
- external id / timestamp unique constraint
- retry duplicate yaratmamalı

Transaction API'de kullanıcı double-submit riski varsa idempotency key değerlendir.

## 26.3. Backup

Production:
- automatic PostgreSQL backup
- restore test
- retention policy
- encrypted storage

Backup alınması tek başına yeterli değildir; **restore testi** release checklist'e girer.

## 26.4. Migration safety

- Alembic only
- forward migration automated test
- clean DB 0 → latest
- previous release → latest
- destructive migration explicit approval
- migration backup/rollback note

---

# 27. OBSERVABILITY

## 27.1. Structured logging

JSON logs recommended.

Fields:
- timestamp
- level
- service
- correlation/request id
- user id hashed/internal when needed
- provider
- job id
- duration
- error code

## 27.2. Metrics

- API latency
- error rate
- provider latency/error
- quote freshness
- worker queue depth
- job failures
- cache hit ratio
- AI call latency/cost
- DB pool saturation

## 27.3. Data quality metrics

- stale instruments count
- candle gap count
- KAP ingestion lag
- provider divergence if multiple sources

## 27.4. Health endpoints

- liveness
- readiness
- dependency status

Readiness provider outage yüzünden tüm app'i kapatmamalı; core DB/critical dependency mantığı ayrılmalı.

---

# 28. HATA YÖNETİMİ VE DEGRADE MODES

Kullanıcıya “Something went wrong” dışında anlamlı durum göster.

Örnek:

### Piyasa verisi gecikti
> Son doğrulanmış fiyat 18 dakika önce alındı. Bu analiz yeni işlem için güncel kabul edilmedi ve karar BEKLE'ye düşürüldü.

### KAP unavailable
> Resmi açıklama kaynağı şu anda kontrol edilemedi. Haber skoru karar ağırlığından çıkarıldı.

### Mentor unavailable
Deterministik skorlar gösterilmeye devam eder; AI summary unavailable mesajı.

AI çökmesi uygulamanın bütün finansal hesaplarını durdurmamalıdır.

---

# 29. ACCESSIBILITY

- Semantic HTML
- Keyboard navigation
- Visible focus
- WCAG AA contrast hedefi
- Color not only signal
- aria labels for chart controls
- reduced motion support
- form errors screen-reader friendly
- tables accessible

Grafikte sadece görsel bilgi bulunan kritik değerler metin özetinde de bulunmalıdır.

---

# 30. API TASARIMI

Örnek route'lar; exact naming API planında finalize edilir.

```text
GET  /api/v1/markets/overview
GET  /api/v1/instruments
GET  /api/v1/instruments/{id}
GET  /api/v1/instruments/{id}/quote
GET  /api/v1/instruments/{id}/candles
GET  /api/v1/instruments/{id}/analysis
GET  /api/v1/instruments/{id}/fundamentals
GET  /api/v1/instruments/{id}/disclosures
GET  /api/v1/opportunities

GET  /api/v1/portfolios
POST /api/v1/portfolios
GET  /api/v1/portfolios/{id}
POST /api/v1/portfolios/{id}/transactions
POST /api/v1/portfolios/{id}/what-if
GET  /api/v1/portfolios/{id}/risk
GET  /api/v1/portfolios/{id}/performance

POST /api/v1/mentor/query
GET  /api/v1/knowledge/search
GET  /api/v1/knowledge/{slug}

GET  /api/v1/alerts
POST /api/v1/alerts
PATCH /api/v1/alerts/{id}
DELETE /api/v1/alerts/{id}
```

## 30.1. API conventions

- versioned `/api/v1`
- typed response schema
- standard error envelope
- correlation id
- pagination
- max range on candle/history endpoints
- rate-limit expensive endpoints

## 30.2. Data freshness in responses

Analysis response:

```json
{
  "data_as_of": "...",
  "freshness": "DELAYED",
  "provider": "...",
  "analysis_version": "...",
  "data_quality": 91
}
```

---

# 31. TEST STRATEJİSİ

## 31.1. Test piramidi

### Unit
- calculations
- scoring
- mappings
- validators

### Integration
- DB
- Redis
- provider adapters mocked/contract fixture
- worker jobs

### Contract
- provider payload fixtures
- API OpenAPI compatibility

### E2E
- login
- dashboard
- instrument detail
- add transaction
- what-if risk
- ask Mentor
- knowledge article
- alert create

## 31.2. Finansal invariant testleri

Örnek:
- BUY increases quantity.
- SELL cannot make negative quantity unless short selling explicitly supported (V1: desteklenmiyor).
- Fees reduce realized result appropriately.
- Cash flow is not investment return.
- Portfolio weights sum ~100% including cash.
- Missing price does not become zero market value silently.
- P/L calculations preserve Decimal precision.

## 31.3. Indicator invariant

- EMA first values/warmup defined.
- RSI flat market behavior defined.
- MACD signal consistent.
- Bollinger upper >= mid >= lower for nonnegative std.
- ATR nonnegative.

## 31.4. Backtest anti-lookahead test

Deliberately create future publication event; ensure engine cannot access before publication timestamp.

## 31.5. Decision regression fixtures

Golden decision snapshots:
- clear positive
- clear negative
- mixed
- low data quality
- portfolio concentration override

## 31.6. Security tests

- IDOR
- auth bypass
- CSRF
- XSS sanitized content
- invalid URLs / SSRF
- rate limits
- oversized payload

## 31.7. Performance tests

- 100/500/1000 instruments scanner batch
- 10K candle chart payload
- cache hit/miss
- concurrent dashboard

---

# 32. PHASE YAPISI

Aşağıdaki fazlar sıralıdır. Codex gerçek repo durumuna göre alt task'ları bölebilir fakat master amaç ve kalite kapıları değişmez.

---

# PHASE 0 — PROJECT GOVERNANCE, SCAFFOLD, QUALITY BASELINE

## Amaç

Repository, local dev, CI ve kalite mekanizmasını kurmak. Finans özelliklerine başlamadan foundation.

## Yapılacaklar

- Monorepo scaffold.
- Frontend/backend minimal app.
- Docker Compose: frontend/backend/postgres/redis.
- `.env.example`.
- Dependency lockfiles.
- CI pipeline.
- Ruff/lint/typecheck/test/build.
- Gitleaks.
- Basic Trivy/dependency audit.
- Structured backend config.
- `/health` endpoints.
- Error envelope.
- Logging correlation ID.
- `docs/architecture/adr/` sistemi.

## Test

- Clean clone startup.
- DB reachable.
- Redis reachable.
- Frontend build.
- Backend test.
- Migration baseline.
- CI all green.

## Güvenlik kontrolü

- No secret committed.
- Dev default credentials public deployment için güvenli değilse fail-fast.

## Performans kontrolü

- Empty app build bundle baseline kaydı.
- Health endpoint latency baseline.

## Exit Gate

**PHASE 0 READY** yalnızca CI tamamen yeşilse.

---

# PHASE 1 — AUTH, USER PROFILE, SECURITY FOUNDATION

## Amaç

Kullanıcı ve risk profili güvenli biçimde oluşturulsun.

## Yapılacaklar

- users/auth schema.
- login/session.
- Argon2id.
- secure cookies/session handling.
- investment profile.
- risk limits.
- settings UI.
- user ownership middleware/dependency.
- audit log foundation.

## Test

- login success/fail.
- session expiration.
- logout revoke.
- IDOR fixtures.
- settings validation.
- CSRF where applicable.

## Exit Gate

User-scoped test olmadan finance data fazına geçilmez.

---

# PHASE 2 — INSTRUMENT MASTER + PROVIDER ABSTRACTION

## Amaç

Veri kaynağına bağımlı olmayan canonical instrument katmanı.

## Yapılacaklar

- instruments.
- provider mappings.
- provider interfaces.
- mock deterministic provider.
- provider health.
- quote DTO.
- freshness model.
- rate limit/retry/circuit behavior.

## Kontrol

Provider down testinde app crash olmamalı.

## Exit Gate

Mock provider ile full contract test; gerçek provider seçimi ayrı config.

---

# PHASE 3 — MARKET DATA INGESTION + HISTORICAL STORE

## Amaç

Quote/candle pipeline.

## Yapılacaklar

- quote cache.
- candle storage.
- background ingestion.
- gaps detection.
- timestamp normalization.
- historical sync checkpoints.
- provider idempotency.

## Test

- duplicate ingestion.
- out-of-order candles.
- partial/non-final candle.
- stale provider.
- market closed behavior.

## Performance

- batch ingest benchmark.
- common candle query index EXPLAIN inspection.

---

# PHASE 4 — MARKET DASHBOARD + HIGH-QUALITY CHART FOUNDATION

## Amaç

Kullanıcı ilk gerçek piyasa deneyimini görür.

## UI

- dashboard market cards.
- Piyasalar page.
- Instrument detail basic.
- responsive candlestick chart.
- volume.
- timeframe selector.
- data freshness labels.

## Grafik

- Lightweight Charts attribution.
- resize observer.
- incremental updates.
- loading/error/stale modes.

## Mobile

360/390/430 widths mandatory.

## Performance

- chart 2K / 10K point benchmark.
- no full series reset each tick.

## Exit Gate

Chart desktop+mobile manual screenshot inspection + automated viewport tests.

---

# PHASE 5 — TECHNICAL ANALYSIS ENGINE

## Amaç

RSI/MACD/EMA/SMA/Bollinger/ATR/hacim ve trend skorları.

## Yapılacaklar

- indicator module.
- golden fixtures.
- analysis snapshot.
- horizon configs.
- technical UI cards.
- chart indicator panes.

## Strict Gate

Golden testler olmadan phase close yok.

---

# PHASE 6 — PATTERN + SUPPORT/RESISTANCE ENGINE

## Amaç

Sınırlı ama güvenilir pattern detection.

## Yapılacaklar

- deterministic candle patterns.
- swing detection.
- support/resistance.
- selected chart patterns.
- chart overlays/markers.
- pattern quality.

## Test

Synthetic positive/negative fixtures.

False positive regression dataset oluştur.

---

# PHASE 7 — FUNDAMENTALS + KAP + MACRO + NEWS PIPELINE

## Amaç

Teknik dışı bağlam.

## Yapılacaklar

- financial statements normalized ingestion.
- KAP adapter terms verified.
- KAP disclosure store.
- EVDS client.
- news adapters.
- source tiers.
- dedup.
- factual extraction.
- sentiment separated.

## Security

Prompt injection fixtures.
- malicious HTML
- instruction injection
- oversized attachment metadata

## Exit Gate

Fact/interpretation UI separation verified.

---

# PHASE 8 — PORTFOLIO + PAPER PORTFOLIO + JOURNAL

## Amaç

Gerçek ve sanal portföyün authoritative ledger ile yönetilmesi.

## Yapılacaklar

- portfolios.
- transaction ledger.
- derived positions.
- realized/unrealized P/L.
- fees.
- cash flows.
- transaction reason/journal.
- responsive portfolio UI.

## Strict accounting tests

- partial sell.
- full sell.
- multiple buys.
- fees.
- missing quote.
- cash in/out.

## Exit Gate

Ledger invariant tests %100 pass.

---

# PHASE 9 — RISK ENGINE + PRE-TRADE WHAT-IF

## Amaç

Kullanıcıyı tek-varlık/sektör/asset-class yoğunlaşması konusunda korumak.

## Yapılacaklar

- risk profile evaluation.
- concentration.
- drawdown.
- volatility.
- correlation when enough data.
- what-if endpoint.
- pre-trade UI.
- suggested position range.
- stop/target suggestion v1.

## Test

What-if transaction DB'yi mutate etmemeli.

Risk limit boundary tests.

---

# PHASE 10 — DETERMINISTIC DECISION ENGINE

## Amaç

AL / KADEMELİ AL / BEKLE / KADEMELİ SAT / SAT.

## Yapılacaklar

- score normalization.
- horizon weights.
- data quality gate.
- market_view vs user_action.
- immutable decision snapshot.
- versioning.
- explainable reason codes.

## Test

Golden decision fixtures mandatory.

Data missing → BEKLE.

Portfolio overconcentration can downgrade user action without changing market view.

---

# PHASE 11 — AI MENTOR

## Amaç

Deterministik sistemi anlaşılır doğal dil arayüzüne çevirmek.

## Yapılacaklar

- mentor chat.
- orchestration tool layer.
- structured LLM output.
- user explanation level.
- source/time display.
- conversation storage privacy.
- quick actions.

## Safety/quality tests

- LLM tries to change action → rejected.
- fake price not in tool data → validation/fail.
- malicious news prompt injection → ignored.
- missing provider → transparent BEKLE/partial explanation.

---

# PHASE 12 — BİLGİ MERKEZİ + VISUAL EDUCATION

## Amaç

Başlangıç seviyesindeki kullanıcı teknik kavramları basitçe öğrenir.

## İlk içerikler

- RSI
- MACD
- SMA
- EMA
- Bollinger
- ATR
- Hacim
- Support/resistance
- F/K
- PD/DD
- ROE
- Ciro
- Net kâr
- Borç
- Diversification
- Volatility
- Drawdown
- Correlation
- Interest
- Inflation

## Yapılacaklar

- canonical article schema.
- search.
- ask-a-concept.
- interactive visual components.
- “daha teknik anlat”.
- inline glossary popovers.

## Content QA

Her canonical article için:
- technical fact review
- simple explanation review
- misuse warning
- no guaranteed trading rule

---

# PHASE 13 — FIRSAT TARAYICI + PERSONALIZED RANKING

## Amaç

Piyasayı tarayıp kullanıcı için “dikkat çekici” varlıkları sıralamak.

## Yapılacaklar

- precomputed universe scanner.
- filters.
- raw score.
- portfolio-fit score.
- explainability.
- opportunities UI.

## Performance

Scanner request-time çalışmamalı; worker precompute.

## Gate

100/500/1000 instruments benchmark.

---

# PHASE 14 — ALERTS + NOTIFICATIONS

## Amaç

Fiyat/sinyal/KAP/risk değişiminde kullanıcıyı kontrollü bilgilendirmek.

## Yapılacaklar

- alert rules.
- worker evaluation.
- dedup/cooldown.
- in-app notification.
- optional PWA push foundation.

## Test

- boundary crossing once.
- repeated same price no spam.
- decision transition.
- provider stale no misleading price alarm.

---

# PHASE 15 — BACKTEST ENGINE

## Amaç

Sinyal ve kararların geçmiş performansını bilimsel olarak test etmek.

## Yapılacaklar

- strategy spec.
- event-safe data access.
- costs/slippage.
- benchmark.
- walk-forward/out-of-sample.
- results UI.

## Strict bias audit

Completion report ayrı bölüm:
- look-ahead audit
- publication timestamp audit
- corporate action audit
- cost assumptions
- survivorship limitations

---

# PHASE 16 — DECISION OUTCOME TRACKING + CHAMPION/CHALLENGER

## Amaç

Sistem kendi kararlarını ölçer.

## Yapılacaklar

- forward returns.
- benchmark-adjusted outcomes.
- segment performance.
- challenger config.
- shadow evaluation.
- bounded promotion process.

## Safety

No auto production weight mutation without governance gate.

---

# PHASE 17 — PERSONAL BEHAVIOR ANALYTICS

## Amaç

Mentor yalnızca piyasayı değil kullanıcının karar alışkanlıklarını da değerlendirsin.

## Örnek insight

- Social-media reason trades performance.
- FOMO proxy: large recent rise before entry.
- planned horizon violation.
- concentration behavior.
- mentor-followed vs ignored outcomes (without shaming).

## UX

Dil yargılayıcı olmayacak.

> “Son 8 kısa vadeli işleminin 6'sında pozisyon, fiyatın önceki 10 günde güçlü yükselişinden sonra açılmış. Bu işlem grubunun performansı portföy ortalamanın altında.”

---

# PHASE 18 — PWA, MOBILE POLISH, OFFLINE/DEGRADED EXPERIENCE

## Amaç

Mobil web uygulamasını gerçek günlük kullanım seviyesine getirmek.

## Yapılacaklar

- installable PWA.
- safe cache policy.
- last-known data clearly stale/offline label.
- web push if enabled.
- mobile performance.
- touch UX.

## Security

Sensitive API responses service worker cache'e kontrolsüz yazılmaz.

---

# PHASE 19 — PERFORMANCE HARDENING

## Amaç

Gerçek ölçümlerle darboğazları kapatmak.

## Yapılacaklar

- profiling.
- SQL slow query audit.
- index tuning.
- caching audit.
- bundle split.
- image/icon optimization.
- chart large history.
- worker throughput.
- AI latency.

## Gate

Performance budget report.

---

# PHASE 20 — SECURITY HARDENING + FINAL RELEASE AUDIT

## Amaç

Production readiness.

## Security

- threat model review.
- dependency audit.
- gitleaks.
- Trivy.
- ZAP staging baseline.
- auth/IDOR regression.
- CSP.
- backup/restore test.
- secrets rotation procedure.

## Product

- all screens mobile.
- data freshness.
- disclaimers.
- provider licensing docs.
- no auto trade.
- no fake live data.

## Final report

`docs/FINAL_RELEASE_AUDIT.md`

Her iddia evidence ile.

---

# 33. PHASE COMPLETION REPORT STANDARDI

Her `phase_XX_completion.md` şu başlıklara sahip olmalıdır:

1. Scope implemented
2. Files changed
3. DB migrations
4. API endpoints
5. UI routes/components
6. Security controls
7. Performance controls
8. Automated tests actually executed
9. Test exact counts
10. Typecheck result
11. Lint result
12. Build result
13. Security scan result
14. Migration from clean DB
15. Upgrade migration test
16. Mobile automated test result
17. Manual QA actually executed
18. Known limitations
19. Deferred items (must belong future phases)
20. Rollback considerations
21. Evidence / command outputs summary
22. `PHASE XX READY` or `NOT READY`

“Ready” yazmak için kritik test failure olamaz.

---

# 34. DEFINITION OF DONE — GLOBAL

Bir özellik “done” sayılmaz eğer:

- yalnız backend var UI yok ve user-facing feature ise
- yalnız UI mock var real domain entegrasyonu yok
- error/loading/empty state yok
- mobile bozuk
- accessibility temel kontrolleri yok
- unit/integration test yok
- log/metric yok (kritik pipeline ise)
- data source/freshness görünmüyor (market data ise)
- authorization test yok (user data ise)
- docs güncel değil

---

# 35. PERFORMANS REGRESSION CHECKLIST

Her önemli UI/data fazında:

- [ ] Dashboard request count kontrol edildi.
- [ ] N+1 API/query yok.
- [ ] Quote fetch batch.
- [ ] Redis TTL doğru.
- [ ] Historical candles indexed.
- [ ] Chart streaming incremental.
- [ ] Large lists virtualized/paginated.
- [ ] Bundle growth incelendi.
- [ ] Mobile CPU/memory aşırı değil.
- [ ] Worker ağır hesapları request thread'den aldı.
- [ ] Provider timeout tüm dashboard'u bloklamıyor.

---

# 36. SECURITY CHECKLIST

Her phase completion'da ilgili maddeler:

- [ ] Auth required where expected.
- [ ] User ownership enforced.
- [ ] Input schema validation.
- [ ] Decimal finance calculations.
- [ ] CSRF considered.
- [ ] XSS sanitized.
- [ ] SSRF protected.
- [ ] Provider secrets masked.
- [ ] No secret in repo.
- [ ] Rate limits.
- [ ] Audit logging.
- [ ] Prompt injection treated.
- [ ] External content untrusted.
- [ ] Dependency audit.
- [ ] Migration safe.
- [ ] Backup impact considered.

---

# 37. DATA QUALITY CHECKLIST

- [ ] Source identified.
- [ ] Source timestamp stored.
- [ ] Ingestion timestamp stored.
- [ ] Timezone normalized.
- [ ] Delayed/live status known or marked unknown.
- [ ] Stale threshold defined.
- [ ] Missing != zero.
- [ ] Duplicates handled.
- [ ] Out-of-order data handled.
- [ ] Corporate actions policy documented.
- [ ] Provider mismatch observable.
- [ ] Decision refuses low-quality data.

---

# 38. BACKTEST QUALITY CHECKLIST

- [ ] No look-ahead.
- [ ] Publication date respected.
- [ ] No future adjusted info leakage.
- [ ] Transaction costs.
- [ ] Slippage assumption.
- [ ] Benchmark.
- [ ] Out-of-sample.
- [ ] Sample size displayed.
- [ ] Max drawdown.
- [ ] Win rate not sole metric.
- [ ] Reproducible strategy/data version.
- [ ] Survivorship limitation documented.

---

# 39. AI MENTOR QUALITY CHECKLIST

- [ ] Numeric facts from tools/domain only.
- [ ] User action from Decision Engine only.
- [ ] LLM cannot override action.
- [ ] Data timestamp visible.
- [ ] Source visible for news/KAP.
- [ ] Facts vs interpretation separated.
- [ ] Low data quality → BEKLE.
- [ ] No guaranteed-return language.
- [ ] External document injection ignored.
- [ ] Beginner language default.
- [ ] “Daha teknik anlat” available.

---

# 40. MOBİL QA CHECKLIST

Her ana ekran:

- [ ] 360px no horizontal overflow.
- [ ] 390px usable.
- [ ] 430px usable.
- [ ] Tablet portrait.
- [ ] Chart touch gestures.
- [ ] No clipped dialog.
- [ ] Bottom nav safe area.
- [ ] Tables transform to cards/scroll intentionally.
- [ ] Buttons touch-friendly.
- [ ] Text readable without zoom.
- [ ] Skeleton does not jump layout.

---

# 41. ANA EKRANLARIN KABUL KRİTERLERİ

## Ana Sayfa

- Personal briefing < 1 screen initial summary.
- Portfolio summary.
- Important alerts.
- Market overview.
- Opportunities.
- All data shows freshness.

## Piyasalar

- Categories.
- search/sort.
- price + change.
- score.
- mobile cards.

## Instrument Detail

- price/freshness.
- horizon.
- market view.
- user action.
- chart.
- scores.
- fundamentals.
- disclosure/news.
- risk/portfolio impact.

## Fırsatlar

- filters.
- personalized.
- why listed.
- no “guaranteed picks”.

## Portföy

- real/paper separation.
- P/L.
- allocation.
- benchmark.
- risk.
- journal.

## Mentor

- real tools.
- structured decision.
- clear action.
- short default explanation.

## Bilgi Merkezi

- question search.
- simple answer.
- visual.
- limitations.
- deeper level.

## Notifications

- rule creation.
- dedup.
- history.

## Settings

- risk profile.
- horizon.
- max weights.
- explanation level.

---

# 42. MARKET REGIME — İLERİ SEVİYE AMA ÖNEMLİ

Decision Engine zamanla market regime context kullanabilir:
- trending
- range-bound
- high volatility
- low volatility
- risk-on/risk-off proxy

Neden:
- RSI mean reversion güçlü trendde farklı davranabilir.
- Pattern başarı oranı rejime göre değişebilir.

Ancak ilk implementasyon basit, test edilebilir regime classification ile başlamalıdır.

---

# 43. MODEL / STRATEGY VERSIONING

Versiyonlanacak:
- technical formula version if changed
- pattern detector version
- fundamental score version
- risk engine version
- decision weights version
- Mentor prompt/version
- knowledge article revision

Amaç eski decision snapshot'ın “neden böyle dediğini” açıklayabilmek.

---

# 44. DATA RETENTION

- Market history: ihtiyaca göre uzun süreli.
- Decision snapshots: uzun süreli; performans için gerekli.
- Portfolio transactions: silinmemeli/correction audit.
- Mentor chat: kullanıcı silebilmeli; retention config düşünülebilir.
- Logs: sınırlı retention.
- Security audit logs: policy.

---

# 45. PRIVACY

Portföy tutarları ve işlem geçmişi hassas kişisel finansal veri olarak ele alınır.

- Minimum collection.
- UI analytics varsa fiyat/portföy rakamı telemetry'ye gitmez.
- LLM provider'a gönderilen context minimum gerekli bilgiyle sınırlandırılır.
- Full transaction history her prompt'a dökülmez; aggregate/relevant context.
- Production logs transaction notes içermemeli unless necessary.

---

# 46. AI COST / LATENCY CONTROL

Mentor her dashboard render'da gereksiz AI çağrısı yapmaz.

Öneri:
- Daily briefing cached by data snapshot/user.
- Static knowledge answers canonical content first.
- Small summarization tasks cheaper model if quality sufficient.
- Complex portfolio/market synthesis frontier model only when needed.
- Token budget.
- Context compression.

AI unavailable olsa core app çalışır.

---

# 47. PROVIDER OUTAGE RUNBOOK

1. Health detects failure.
2. Circuit opens.
3. Cache age measured.
4. Valid fallback varsa switch + label.
5. Yoksa STALE/UNAVAILABLE.
6. Decision data quality drops.
7. Action forced to BEKLE if critical current market data absent.
8. Alert workers price alert üretmez from stale price.
9. Ops log/metric.

---

# 48. IMPORTANT DOMAIN EDGE CASES

Codex test planına eklemeli:

- Market holiday.
- Half-day/session variations if data source has them.
- Weekend FX/crypto vs BIST closed.
- Instrument symbol rename.
- Delisted/suspended instrument.
- Stock split/bonus/corporate action.
- Dividend.
- Missing candles.
- Provider duplicate candle.
- Quote timestamp in wrong timezone.
- Negative/zero malformed price.
- SELL > owned quantity.
- Transaction in past before historical price data.
- New user empty portfolio.
- Portfolio all cash.
- Very small amount/rounding.
- Different currency assets.
- News duplicated by multiple providers.
- KAP attachment only event.
- Mentor asks unknown symbol.

---

# 49. USER EXPERIENCE LANGUAGE RULES

Mentor ve UI:
- Türkçe birincil.
- Teknik terim ilk kullanımda Türkçe açıklama.
- Gereksiz jargon yok.
- Sürekli örnekle konuşmaz; varsayılan kısa ve net.
- Gerektiğinde “Neden?” açılır.

Kullanıcıya tepeden bakan dil yok.

Yasak tone:
- “Kesin fırsat”
- “Kaçırma”
- “Garantili”
- “Bunu alırsan kazanırsın”

Tercih:
- “Sistem kararı”
- “Analiz güvenilirliği”
- “Risk”
- “Veri zamanı”
- “Bu sonucun ana nedenleri”

---

# 50. DISCLAIMER / ÜRÜN SINIRI

UI'nin uygun yerlerinde kısa, rahatsız etmeyen açıklama:

> Borsa Takip bir karar destek ve eğitim aracıdır. Sistem değerlendirmeleri garanti getiri veya kişiye özel profesyonel yatırım danışmanlığı taahhüdü değildir. Piyasa verileri gecikmeli olabilir ve tüm yatırımlar kayıp riski taşır.

Bu metin her karta spam olarak konulmaz; onboarding/settings/decision detail gibi doğru yerlerde görünür.

---

# 51. MVP TANIMI

“İlk kullanılabilir ürün” aşağıdaki fazlar tamamlanınca oluşur:

- Phase 0–12 minimum.

MVP'de kullanıcı:
1. giriş yapabilir.
2. risk profilini belirler.
3. piyasayı görür.
4. güzel responsive chart kullanır.
5. teknik analiz görür.
6. temel/KAP bağlamını görür.
7. gerçek ve paper portfolio tutar.
8. riskini görür.
9. AL/KADEMELİ AL/BEKLE/KADEMELİ SAT/SAT kararını görür.
10. Mentor'a sorar.
11. Bilgi Merkezi'nde kavram öğrenir.

Fırsatlar/alerts/backtest/adaptive phases MVP sonrası güçlü genişleme olabilir.

---

# 52. RELEASE STRATEJİSİ

## Development
- mock provider
- deterministic fixtures

## Staging
- gerçek provider credentials if allowed
- anonymized/test user
- no production portfolio

## Production
- migrations backup aware
- health verified
- warm caches optional
- smoke tests

Feature flags kullanılabilecek riskli alanlar:
- new decision weights
- new provider
- new pattern engine
- adaptive challenger

---

# 53. CODING STANDARDS

## Backend

- Type hints mandatory public service boundaries.
- Pydantic schemas distinct from ORM.
- Domain exceptions.
- No giant `services.py`.
- No circular imports.
- Pure calculation functions where possible.
- `Decimal` quantization rule documented.

## Frontend

- strict TypeScript.
- no `any` without documented reason.
- feature-based components.
- server/client component boundary conscious.
- avoid global state for server data.
- loading/error/empty states.

## General

- Meaningful names.
- No TODO as hidden incomplete requirement.
- ADR for substantial deviation.

---

# 54. DATABASE PERFORMANCE RULES

- Index by real query patterns, not every column.
- Candle compound index.
- Disclosures instrument/published_at.
- transactions portfolio/executed_at.
- decisions instrument/horizon/as_of.
- alerts user/enabled.

Use `EXPLAIN ANALYZE` for slow queries.

Avoid unbounded history endpoint.

---

# 55. CACHING INVALIDATION RULES

Examples:
- Quote TTL short.
- Technical snapshot invalidated/new candle.
- Fundamental score invalidated on new financial report.
- KAP cache invalidated new disclosure.
- Portfolio summary invalidated transaction + quote change.
- Decision invalidated when critical input snapshot changes.

Cache key includes engine version where necessary.

---

# 56. SYSTEM JOBS

Worker schedule categories:

### High frequency (provider/license permitting)
- quote refresh

### Candle interval
- finalize bars
- technical recalculation

### Event-driven
- KAP ingest
- news ingest
- alert evaluation

### Daily
- opportunity scan
- portfolio daily snapshot
- decision outcome updates
- briefing precompute

### Periodic maintenance
- stale data audit
- data gap repair
- performance aggregation
- cleanup retention

Jobs idempotent olmalı.

---

# 57. OPERATIONAL ADMIN / INTERNAL VIEW

Public user UI dışında küçük admin diagnostics düşünülebilir:
- provider health
- last ingest
- stale symbols
- worker queue
- failed jobs
- latest decision version

Admin endpoint normal kullanıcıya açık olmaz.

---

# 58. SOURCE PROVENANCE UI

Her önemli güncel bilgi tıklanınca:
- Kaynak
- Veri zamanı
- Gecikme durumu
- Son güncelleme

görülebilmeli.

KAP/news:
- source reference
- published time

Mentor:
- “Bu değerlendirme şu veri snapshot'ına göre üretildi.”

---

# 59. KULLANICI ONBOARDING

İlk açılış:

1. Deneyim seviyesi.
2. Varsayılan vade.
3. Risk toleransı.
4. Portföy limitleri için önerilen başlangıç değerleri; kullanıcı değiştirebilir.
5. Gerçek vs paper portfolio açıklaması.
6. Data delay açıklaması.
7. Mentor'un ne yapıp ne yapmadığı.

Onboarding yatırım getirisi sözü vermez.

---

# 60. WATCHLIST

Küçük ama önemli core feature.

- instrument add/remove.
- price.
- daily change.
- decision.
- alert shortcut.

Watchlist user scoped.

Dashboard'a entegre edilir.

---

# 61. PORTFOLIO PERFORMANCE ANALYTICS

Zamanla:
- equity curve
- benchmark curve
- drawdown
- allocation history
- realized vs unrealized
- reason-code performance
- horizon adherence

Cash injection etkisini düzgün ayır.

---

# 62. USER BEHAVIOR SAFETY

Sistem kullanıcıyı daha çok işlem yapmaya teşvik etmek üzerine optimize edilmemelidir.

No engagement KPI like:
- trades/day increase
- notification clickbait

Daha iyi KPI:
- decision review completion
- risk warning adherence
- learning usage
- reduced concentration

---

# 63. KALİTE ÖNCELİK SIRASI

Çelişki olduğunda:

1. Veri doğruluğu
2. Güvenlik / privacy
3. Finansal hesap doğruluğu
4. Explainability
5. Hız
6. Mobil kullanılabilirlik
7. Görsel kalite
8. Feature breadth

Ancak “hız” ve “mobil” sonradan eklenecek şey değildir; her fazda ölçülür.

---

# 64. PROJEDE “GERÇEK ZAMANLI” KELİMESİNİN KULLANIMI

UI/API yalnızca provider gerçekten real-time lisanslı veri sağlıyorsa `canlı/real-time` diyebilir.

Aksi:
- 15 dk gecikmeli
- gecikmeli
- gün sonu
- son doğrulanmış

şeklinde doğru etiket.

Bu ürün güveni açısından zorunludur.

---

# 65. GRAFİKLERDE PATTERN EĞİTİMİ

Instrument chart'ta detected pattern marker'a basınca:
- pattern name
- detected dates
- quality
- invalidation condition
- “Bu formasyon nedir?” Knowledge Center
- historical backtest if available

Bu, analiz ile öğrenmeyi birleştirir.

---

# 66. DECISION DETAIL — ÖNERİLEN UI

```text
ASELS
Orta Vade

SİSTEM KARARI
KADEMELİ AL

Analiz güvenilirliği: 74/100
Risk: Orta
Veri: 15 dk gecikmeli • 16:42

Teknik        82
Temel         75
Haber/KAP     71
Risk/Getiri   73
Portföy Uyumu 66

ANA NEDENLER
+ Trend güçlü
+ Hacim destekliyor
+ Temel görünüm pozitif

DİKKAT
! Dirence yakın
! Sektör ağırlığın artıyor

Önerilen işlem boyutu: portföyün %5–8'i aralığı
[İşlem Öncesi Kontrol]
[Neden?]
[Grafikte Göster]
```

Exact score/amount yalnızca gerçek engine output ile.

---

# 67. KNOWLEDGE CENTER ÖRNEK İÇERİK STANDARDI — RSI

Bu örnek içerik kalıbıdır; production canonical article teknik review görmelidir.

### 30 saniyede
RSI, son dönemde fiyat hareketinin yukarı mı aşağı mı daha güçlü olduğunu gösteren bir momentum göstergesidir.

### Basit okuma
0–100 arasında hareket eder. 70/30 seviyeleri sık kullanılan referanslardır ancak **tek başına AL/SAT kuralı değildir**.

### Nerede yanıltır?
Güçlü trendde RSI uzun süre yüksek veya düşük kalabilir.

### Birlikte bak
Trend, hacim, support/resistance.

### Daha teknik
Period, average gains/losses, smoothing açıklaması.

Bu standard tüm kavramlara uygulanır.

---

# 68. FRONTEND STATE STRATEJİSİ

- URL state: filters/horizon where shareable.
- TanStack Query: API data.
- Local component state: UI.
- Zustand only cross-page ephemeral needs.
- Portfolio authoritative state backend; optimistic update only safe mutations.

WebSocket updates query cache'i targeted update eder; tüm app rerender olmamalı.

---

# 69. ERROR CODES

Backend machine-readable codes:
- `AUTH_REQUIRED`
- `FORBIDDEN_RESOURCE`
- `INSTRUMENT_NOT_FOUND`
- `PROVIDER_UNAVAILABLE`
- `DATA_STALE`
- `INSUFFICIENT_DATA`
- `INVALID_TRANSACTION`
- `RISK_CALCULATION_UNAVAILABLE`
- `MENTOR_UNAVAILABLE`
- `RATE_LIMITED`

Frontend localized message map.

---

# 70. FUTURE EXTENSION HOOKS

Schema/mimari engellemeyecek ancak şimdi uygulanmayacak:
- mutual funds
- US equities
- multiple currencies
- broker import CSV
- broker read-only sync
- tax report
- household portfolios
- custom strategy builder

Broker **trade execution** ayrı risk/legal project'tir.

---

# 71. FINAL MASTER ACCEPTANCE

Codex bu master dosyayı okuduktan sonra yeni plan üretecekse plan şu soruların hepsini cevaplamalıdır:

1. Hangi fazdayız?
2. Önceki fazların gerçek durumu ne?
3. Bu fazın kapsamı ne?
4. Kapsam dışı ne?
5. Veri modeli ne değişecek?
6. Migration ne?
7. API ne?
8. UI ne?
9. Mobil davranış ne?
10. Performance budget ne?
11. Security threat'leri ne?
12. Hangi testler yazılacak?
13. Hangi test komutları çalıştırılacak?
14. Rollback nasıl?
15. Completion kanıtı nasıl üretilecek?

Bu 15 sorudan biri eksikse faz planı tamamlanmış sayılmaz.

---

# 72. KISA ÜRÜN ÖZETİ — CODEX BUNU KAYBETMEMELİ

**Borsa Takip**, yeni başlayan yatırımcıya piyasa verisini göstermenin ötesinde:

- piyasayı öğretir,
- teknik ve temel analizi deterministik motorlarla hesaplar,
- KAP/haber/makro bağlamını toplar,
- kullanıcının gerçek ve sanal portföyünü izler,
- risk ve yoğunlaşmayı kontrol eder,
- kararını `AL / KADEMELİ AL / BEKLE / KADEMELİ SAT / SAT` şeklinde netleştirir,
- ancak bu kararı LLM'ye uydurtmaz,
- AI Mentor ile sonucu anlaşılır Türkçe açıklar,
- sistemin kendi kararlarının geçmiş başarısını backtest ve forward tracking ile ölçer,
- kullanıcının yatırım davranışından öğrenmesine yardımcı olur,
- hızlı, güvenli, mobile-first ve yüksek kaliteli finansal grafiklere sahip olur.

Ürünün vaadi **bedava para veya garantili piyasa tahmini değildir**.

Ürünün vaadi:

> **Daha düzenli veri, daha iyi risk farkındalığı, daha açıklanabilir analiz ve daha disiplinli yatırım kararları.**

---

# 73. OFFICIAL REFERENCES — IMPLEMENTASYON SIRASINDA TEKRAR DOĞRULA

Bu bağlantılar master tasarım hazırlanırken doğrulanmıştır; API sözleşmeleri ve lisans şartları implementasyon gününde tekrar kontrol edilmelidir.

- Borsa İstanbul Data Dissemination: https://www.borsaistanbul.com/en/data/data-dissemination
- KAP General Information: https://www.kap.org.tr/tr/about/genel-bilgi
- KAP Home / REST data service announcement context: https://www.kap.org.tr/tr/
- TCMB EVDS User Docs: https://evds2.tcmb.gov.tr/index.php?/evds/userDocs=
- TradingView Lightweight Charts Docs: https://tradingview.github.io/lightweight-charts/docs

---

# 74. SON TALİMAT

Codex:

- Bu dosyayı parçalara bölüp daha küçük phase planları üretebilir.
- `docs/phases/` altında detayları genişletebilir.
- Architecture Decision Records oluşturabilir.
- Gerçek repo durumuna göre task sıralamasında küçük teknik düzeltmeler yapabilir.

Ancak **ürünün temel davranışını, güvenlik sınırlarını, karar motorunun deterministik olmasını, mobile-first gereksinimini, performance-first yaklaşımını, provider abstraction'ını ve faz kalite kapılarını master spec güncellenmeden değiştiremez.**


# 75. PUBLIC / COMMERCIAL RELEASE — SPK COMPLIANCE GATE

Bu proje kişisel/local kullanım prototipi olarak geliştirilebilir; ancak **başka kullanıcılara açılacak, ücretli hale getirilecek veya kişilerin portföy/risk bilgisine göre yönlendirici AL/SAT önerileri sunacak public sürüm**, yalnızca bir “disclaimer ekleyerek” otomatik olarak mevzuata uygun kabul edilmemelidir.

SPK'nın güncel Yatırım Hizmetleri ve Kuruluşları Rehberi yatırım danışmanlığı ile genel yatırım tavsiyelerini düzenleyen çerçeveye atıf yapmaktadır ve yatırım danışmanlığı için faaliyet izni süreçleri bulunmaktadır. Ürünün kişiye özel portföy verisini kullanarak yönlendirici aksiyon üretmesi hukuki sınıflandırma bakımından özellikle incelenmelidir.

**Bu nedenle public/commercial launch öncesi zorunlu gate:**

1. Güncel 6362 sayılı Sermaye Piyasası Kanunu ve ilgili SPK tebliğ/rehberlerinin hukuk uzmanı tarafından değerlendirilmesi.
2. `AL / KADEMELİ AL / BEKLE / KADEMELİ SAT / SAT` dilinin ürünün hedef kitlesi ve kişiselleştirme derecesi bakımından hangi düzenleyici kategoriye girdiğinin yazılı analizi.
3. Gerekirse ürün dilinin “market view / risk support / educational decision support” biçimine revize edilmesi.
4. Faaliyet izni, iş ortaklığı veya lisans gereksinimi çıkarsa public kullanıcı onboarding'i açılmadan tamamlanması.
5. Kullanıcı sözleşmesi, risk bildirimi, privacy/KVKK ve veri işleme metinlerinin uzman incelemesi.
6. Veri sağlayıcı sözleşmelerinin son kullanıcı gösterimi, cache, redistribution ve historical storage izinlerinin doğrulanması.

**Release rule:** `LEGAL_COMPLIANCE_APPROVED=true` benzeri teknik flag koymak tek başına yeterli değildir; gerçek bir compliance artefact/reference olmadan public production deployment pipeline'ı açılmamalıdır.

Kişisel prototip ile public finansal hizmet ürünü aynı hukuki risk seviyesinde değerlendirilmemelidir.

Resmi referanslar:
- SPK Yatırım Hizmetleri ve Kuruluşları Rehberi: https://spk.gov.tr/kurumlar/yatirim-kuruluslari/araci-kurumlar/yatirim-hizmetleri-ve-kuruluslari-rehberi
- SPK yatırım kuruluşları faaliyet izinleri / başvuru süreçleri: https://spk.gov.tr/kurumlar/yatirim-kuruluslari/araci-kurumlar/basvuru-surecleri

---

# 76. CODEX İLK ÇALIŞTIRMA TALİMATI

Bu master spec yeni bir repository'ye ilk kez konulduğunda Codex doğrudan tüm 20 fazı kodlamaya başlamamalıdır.

İlk görev sırası:

1. Repository'yi incele; boşsa bunu açıkça kaydet.
2. Bu master spec'ten `docs/ROADMAP.md` üret; yalnızca faz bağımlılıklarını ve statülerini özetle, master gereksinimleri tekrar kopyalama.
3. `docs/phases/phase_00_plan.md` üret.
4. Phase 0 planını implementasyona hazır hale getir.
5. Sadece Phase 0'ı uygula.
6. Gerçek komutları çalıştır ve `phase_00_completion.md` oluştur.
7. Çıkış kapısı yeşil değilse Phase 1'e geçme.
8. Her sonraki fazda master spec + mevcut gerçek repo + önceki completion evidence birlikte okunmalıdır.

Codex hiçbir zaman “master spec çok büyük, ilgili kısmı okudum” varsayımıyla çalışma yapmamalıdır. Ürün sınırları birbiriyle bağlantılıdır; özellikle security, performance, provider licensing, decision governance ve mobile kuralları tüm fazlara çapraz gereksinimdir.

---

**END OF MASTER SPEC**
