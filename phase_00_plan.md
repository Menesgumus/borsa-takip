# Phase 00 Plan — Governance, Scaffold, Quality Baseline

Tarih: 2026-09-05. **PLAN READY / IMPLEMENTATION NOT STARTED / PHASE 0 NOT READY.**

Bu belge yalnız [BORSA_TAKIP_MASTER_SPEC.md](BORSA_TAKIP_MASTER_SPEC.md)'ten türetilmiş uygulanabilir Phase 0 planıdır. Nihai karar kaynağı master'dır. [GAP_ANALYSIS.md](GAP_ANALYSIS.md) gerçek başlangıç kanıtını, [ROADMAP.md](ROADMAP.md) Phase 0–20 sırasını içerir. Bu tur hiçbir uygulama kodu, scaffold, test dosyası veya migration oluşturulmadı.

## 1. Başlangıç durumu ve yetki sınırı

- Master dosyanın 3.918 satırı, §0–76 ve bütün fazları tamamen okundu. Kaynak SHA-256: `9A11AEF132A6B2ADCD616B3908E283EA9F1CBB63C45E2BFC91085F5210753F74`.
- Denetim başlangıcında yalnız master vardı. Backend/frontend/Git/dependency/test/CI yok. Önceki tamamlanmış faz yok; eski implementasyon taşınmayacak.
- Node, Python ve pnpm sürüm komutları çalıştı; npm launcher bağımsız komutta başarısız. Kurulu sürüm listesi bir uyumluluk/LTS onayı değildir.
- Kullanıcı Docker'ı açtı. Kısıtlı oturum pipe erişimi reddedildi; onaylı sandbox dışı salt okunur `docker info` exit 0, server 28.4.0 döndürdü. Compose app, DB, Redis, image pull veya volume henüz doğrulanmadı.
- Kullanıcının açık talebi gereği bu dosya köktedir ve **bu çalıştırmada Phase 0 uygulanmaz**. Master §76 uygulama adımı bu tura uygulanmıyor. Bu plan sonraki implementation çalışmasının girdisidir.

## 2. Hedef, kapsam ve kapsam dışı

**Hedef:** Yeni bir checkout'tan, belgeli tek yerel akışla çalışan minimal frontend/backend/PostgreSQL/Redis ortamı; tekrarlanabilir bağımlılıklar, Alembic baseline, güvenli yapılandırma, health/error/logging temeli ve başarısızlığı gerçekten durduran CI.

**Kapsam:** Git/README/ADR düzeni; Next.js App Router + React + strict TypeScript + Tailwind minimal kabuk; FastAPI + typed config/Pydantic + SQLAlchemy 2 tarzı DB yaşam döngüsü; Alembic baseline; Redis bağlantısı; `/health` ailesi; standard error/correlation; Docker Compose dört servis; pytest/Vitest/Testing Library/Playwright smoke; lint/type/format/build; gitleaks/Bandit/pip-audit/pnpm audit/Trivy; bundle/health baseline; mobil/a11y kabuk QA; local runbook ve gerçek completion kanıtı.

**Kapsam dışı:** Auth/login/profile tabloları ve ekranı (Phase 1), instrument/provider/mock market DTO (2), ingest/worker executable job (3), piyasa dashboard/chart/watchlist (4), göstergeler/pattern/temel analiz (5–7), portföy/ledger/risk/karar (8–10), LLM ve bilgi merkezi (11–12), tarama/alerts/backtest/adaptive/behavior/PWA (13–18), public deployment ve hukuk onayı. Gelecek domainler için boş CRUD, sahte fiyat, skorlu demo, dummy user veya finansal tablo üretilmez.

Güvenlik, mobil ve performans kontrolleri kapsam dışı değildir. Phase 0'ın mevcut yüzeyleri hemen kontrol edilir; user-owned endpoint olmadığı için IDOR senaryosu ve chart olmadığı için chart gestures gibi kontroller gerekçeli olarak sonraki sahip faza bağlanır. Auth bulunmayan foundation public'e açılmaz.

## 3. Önerilen küçük teknik kararlar

Bunlar master'da serbest bırakılmış ayrıntılar için plan önerisidir; seçilen sürümler ve gerçek komut sözleşmesi T02–T03 sırasında resmi kaynaklarla doğrulanıp ADR/lockfile'a yazılır. Framework veya mimari alternatifi önerilmez.

| Karar | Öneri / gerekçe | Doğrulama ve sınır |
|---|---|---|
| JS package manager | **pnpm**, kökte `pnpm-workspace.yaml` + tek `pnpm-lock.yaml`; frontend workspace | Yerel `pnpm --version` başarılı; registry ve frozen install T02/T04'te. npm launcher onarımı Phase 0 için zorunlu bağımlılık yapılmaz. |
| Python package manager | **uv**, `backend/pyproject.toml` + `backend/uv.lock` | uv PATH'te yok; güvenilir/resmî dağıtım ve sürüm doğrulaması T02. Doğrulanmış CPython wheel/runtime, mevcut MSYS binary'ye kör bağımlılık yok. |
| Runtime/dependencies | Implementasyon günü uyumlu stable/LTS; manifest, runtime pin ve lockfile | Kurulu Node 24.13.1/Python 3.12.7 otomatik canonical kabul edilmez. Next/React/TS/Tailwind ve Python/FastAPI/Pydantic/SQLAlchemy uyumu resmi dokümantasyondan kontrol edilir. |
| Backend sınırları | `api`, `core`, `db`; domain katmanı ilk domain fazında | Pydantic DTO/config, ORM'dan ayrı. Mikroservis ve generic plugin/domain framework yok. |
| DB I/O | SQLAlchemy 2 async engine + uyumlu PostgreSQL driver; bounded pool/timeouts | Driver wheel/compatibility doğrulanır; Alembic URL/async köprüsü aynı ayar kaynağını kullanır. Migration request startup'ta otomatik çalışmaz. |
| Queue | **Celery + Redis önerisi ADR'de** | Worker ayrı process/container olarak Phase 3'te kurulacak. Phase 0'a Celery job/scheduler veya faz dışı precompute eklenmez. |
| Frontend state/UI | Server component ağırlıklı küçük kabuk; erişilebilir native/headless bileşen | TanStack/Lightweight Charts/RHF+Zod kendi tüketim fazında; Zustand ancak somut geçici cross-page UI ihtiyacı olursa. Core UI'da client JS gereksiz büyütülmez. |
| Local networking | Host erişimi yalnız loopback; DB/Redis internal Compose network | Backend container içinde `0.0.0.0` bind edebilir, host portu `127.0.0.1` ile sınırlandırılır. Container içi bind ile public host exposure karıştırılmaz. |
| CI | Mevcut remote yok; **GitHub Actions önerisi**, tek monorepo workflow ve aggregate required gate | Remote/runner gerçekten mevcut olunca kullanılabilir. Yeni remote oluşturma veya yayın bu planlama turunda yapılmaz. Başka mevcut CI varsa aynı gate'ler korunur, gereksiz platform göçü yok. |
| Formatting | Ruff format (Python), Prettier (frontend/docs), ESLint, mypy strict, `tsc --noEmit` | Formatter master dosyayı otomatik dönüştürmez; readonly SSOT dışlanır. Test amaçlı sahte tolerans veya toplu `any`/ignore yok. |
| Health | `/health` liveness alias; `/health/live`, `/health/ready`; detaylı dependency bilgisi local/internal | Liveness process; readiness bounded DB+Redis kontrolü. Provider outage ileride tüm core readiness'i düşürmez. Public bilgi sızıntısı yok. |
| API temel | İş API'leri ileride `/api/v1`; health sürümsüz operasyonel route | Bu faz error envelope/OpenAPI convention kurulur; finans endpoint stub'ı yok. |
| Observability | JSON logging, request/correlation ID ve request duration; düşük cardinality | Merkezi ayrı observability ürünü şart koşulmaz. Provider/queue/AI metrikleri sahip fazda. Sensitive body/header/SQL param log yok. |
| Public release | Bu faz yalnız local/dev; public config reddedilir, deployment job yok | İleride TLS/auth/headers/provider hakları + §75 gerçek compliance artefact/reference zorunlu. Flag tek başına gate değildir. |

## 4. Veri modeli, API, UI ve operasyon sözleşmesi

### Veri modeli ve migration

Phase 0 hiçbir business table oluşturmaz. Alembic metadata ve belgeli boş başlangıç revision'ı dışında user, instrument, ledger veya decision modeli yoktur. `Base`/engine/session lifecycle bağlantı altyapısı kurulabilir; application startup `create_all()` çalıştırmaz. Schema değişikliği yalnız Alembic'tendir.

Clean DB `base → head` ve baseline `base → head` lifecycle test edilir. Gerçek previous release bulunmadığından `previous production release → latest` testi **NOT EXECUTED — ilk release yok** diye belirtilir; test-only dummy revision ile yapılmış migration framework kontrolü varsa bunun önceki üretim migration testi olmadığı açıkça yazılır. Sonraki migrationlı fazlarda previous-release upgrade zorunludur.

Global veri ADR'si UTC-aware timestamps, `Europe/Istanbul` UI default, backend Decimal/DB NUMERIC, numeric bounds ve missing ≠ 0 kuralını kaydeder. Tüm varlıklara keyfî tek scale veya kuruş yuvarlaması dayatılmaz. Alan-specific precision/scale/rounding/FX accounting kuralları ilk gerçek model ve formül fazında golden testle sabitlenir. Finansal API Decimal'ın kayıpsız taşınması için decimal string önerilir; JS number yalnız grafik kütüphanesi render sınırında, uygun doğrulamayla kullanılabilir, authoritative hesabın kaynağı olamaz.

### API

| Route / davranış | Phase 0 kapsamı | Kabul |
|---|---|---|
| `GET /health`, `GET /health/live` | Process liveness; minimal typed `status` | Dependency çağrısı yapmadan bounded response |
| `GET /health/ready` | DB `SELECT 1` ve Redis `PING` benzeri bounded dependency probes | Hazır 200; kritik dependency yok 503; connection leak ve secrets yok |
| Dependency detail | Local/internal diagnostic veya log; dışarıya connection string/host/password dökülmez | Beklenen auth/network sınırı açık |
| OpenAPI / docs | Dev contract inspection | Public exposure kapalı foundation config; consistent response/error şeması |
| Standard errors | 404/405/422/500 ve domain exceptions için typed envelope | Güvenli `error.code`, `error.message`, gerekirse güvenli field details + `correlation_id`; raw request body/stack/secrets yok |
| Correlation header | Bounded/validated incoming ID veya server-generated ID | Success/error/log aynı ID; CR/LF/oversize enjeksiyonu ve log cardinality kontrolü |

T09 API şemasını kesinleştirir. Error validation için gerçek user mutation eklenmez; gerekirse test-only route fixture kullanılır ve production router'a kaydedilmez. §69 domain error codes politika olarak belgelenir; var olmayan domainlere endpoint açılmaz.

### UI

Yalnız `/` üzerinde Türkçe minimal foundation durumu ve sade layout; varsa dev sağlık görüntüsü gerçek API state'inden gelir. Sahte piyasa/portföy/karar verisi yok. Loading/error/empty shell davranışı ve offline backend uyarısı, bu fazın mevcut etkileşimleri ölçüsünde uygulanır. Tüm ürün navigation destination'ları şimdiden boş sayfa olarak üretilmez; gelecek route sahipleri roadmap'tedir.

Responsive kontrol matrisi önerisi: 360×800, 390×844, 430×932; tablet 768×1024 ve 1024×768; desktop 1280×800 ve 1920×1080. Bunlar test viewportlarıdır, tasarım breakpoint kararı değildir. Mevcut butonlar ~44 CSS px, keyboard/focus/contrast/reduced-motion/overflow kontrolünden geçer. Chart/table bulunmuyorsa olmayan UI için manuel PASS yazılmaz.

### Backup / rollback / release

Phase 0 runbook restore yöntemini, ileride encrypted/offsite retention ve secret/key ayrımını tanımlar. Gerçek portföy olmadığı için üretim backup'ı kurulmuş sayılmaz. Test DB'sine uygulanacak migration downgrade yalnız disposable ortamda denenir. `docker compose down` veri volume'lerini korur; `down -v` kullanıcı verisine uygulanmaz. Gelecekte korunacak gerçek data kullanımı ve her public release öncesinde otomatik backup + gerçek restore testinin sahibi açık olmalıdır.

## 5. Görev bağımlılıkları ve uygulama sırası

Her Txx görevi ayrı küçük değişiklik kümesidir; tamamlanmış sayılması kendi kanıtına bağlıdır. Dosya yolları **gelecekte etkilenebilecek öneri yollarıdır**, bugün mevcut oldukları iddia edilmez.

| Sıra | Görev | Önkoşul | Somut çıktı |
|---|---|---|---|
| T01 | Başlangıç snapshot'ı ve scope kilidi | Bu plan | Master hash/working-tree tekrar kontrolü |
| T02 | Toolchain ve Docker/registry preflight | T01 | Resmî sürüm uyumu ve gerçek erişim kanıtı |
| T03 | ADR ve çalışma sözleşmesi | T02 | Az sayıda karar kaydı, exact gate tasarımı |
| T04 | Monorepo / Git / lockfile temeli | T03 | Küçük workspace/manifest/ignore/README |
| T05 | Backend minimal lifecycle | T04 | Minimal FastAPI + typed boundary |
| T06 | Güvenli config / env / exposure | T05 | Fail-fast config + fake env |
| T07 | PostgreSQL / Alembic baseline | T06 | Engine/session + migration lifecycle |
| T08 | Redis lifecycle | T06 | Bounded Redis connection/probe |
| T09 | Health / errors / correlation | T07, T08 | Typed operational API + redacted logs |
| T10 | Frontend responsive kabuk | T04, T09 contract | Minimal Next.js UI ve state'ler |
| T11 | Docker images / Compose | T06–T10 | Dört servisli local ortam |
| T12 | Backend test ve quality scripts | T05–T09, T11 integration | Gerçek negatif/unit/integration/contract tests |
| T13 | Frontend component/E2E/a11y gates | T10–T11 | UI ve responsive test harness |
| T14 | Security scans ve failure gates | T04, T11–T13 | Secret/static/dependency/image kontrolü |
| T15 | Bundle / health performans baseline | T09–T13 | Production build ölçümleri |
| T16 | Dev / migration / recovery runbooks | T11–T15 | Tekrarlanabilir işletim/rollback |
| T17 | CI ve required aggregate gate | T12–T16 | Gerçek remote run + SHA/artifact |
| T18 | Clean clone ve failure recovery | T17 | Fresh checkout entegrasyon kanıtı |
| T19 | Gerçek manuel UI/mobile QA | T13, T18 | Görsel/touch/keyboard gözlem kayıtları |
| T20 | Bağımsız completion ve phase audit | T14–T19 | Gerçek `phase_00_completion.md`, READY/NOT READY |

Örneğin T07/T08 birbirinden bağımsız okunabilir işlerdir; bu tablo çoklu ajan kullanma yetkisi oluşturmaz. Bu oturumda alt ajan kullanılmadı. Kod değişikliği sırasında her dilimin testleri aynı değişiklikle yazılır; T12/T13 testlerin faz sonuna bırakılması değil harness'in bütünleşik kabul adımıdır.

## 6. Ayrıntılı görevler

### T01 — Mevcut durumu tekrar doğrula ve scope'u sabitle

- **Task:** Implementation başlamadan root envanteri, master hash'i, varsa yeni Git/dosyalar ve bu planın uyumunu yeniden incele.
- **Purpose:** Bu plan oluşturulduktan sonra kullanıcı değişikliği olmuşsa üzerine yazmayı veya eski kanıta göre başlamayı önlemek.
- **Files:** Master salt okunur; GAP_ANALYSIS/ROADMAP/phase_00_plan ancak gerçek durum değişmişse güncellenebilir.
- **Implementation Notes:** Yeni master değişikliği varsa tamamını yeniden oku; artık repo varsa manifest/migrations/tests dahil yeniden audit et. Yalnız Phase 0 aktif.
- **Validation:** Inventory + hash + git state kanıtını tarihli kaydet; Phase 0 dışına taşacak plan satırı olmadığını kontrol et.
- **Security Check:** Env/secret içeriklerini çıktıya dökme; sadece isim/config schema incele. Kullanıcı verisine dokunma.
- **Performance Check:** Tarama dependency/cache dizinlerini gereksiz dolaşmaz; başlangıç gate'ine ürün benchmark sonucu uydurulmaz.
- **Mobile Check:** UI değişikliği yok; T10/T13/T19 matrisi korunur.
- **Data Integrity Check:** Master hash ve kaynak rolü değişmemiş; önceki completion yokluğu doğru kaydedilmiş.
- **Exit Criteria:** Gerçek başlangıç ve kapsam teyitli, yeni çatışma varsa açık BLOCKER kaydı.
- **Rollback:** Salt okuma geri alma gerektirmez; doküman değişikliği tek diff olarak geri alınabilir.

### T02 — Runtime, package manager ve Docker preflight

- **Task:** pnpm/uv ve uyumlu runtime sürümlerini resmi kaynaklardan doğrula; Docker daemon/Compose, registry/image erişimi ve çalışma dizini koşullarını denetle.
- **Purpose:** Build/CI'da farklı sürüm, bozuk npm veya erişilemeyen daemon nedeniyle foundation'ın tekrarlanamaz olmasını önlemek.
- **Files:** Önerilen runtime pin dosyaları, `docs/architecture/adr/0001-toolchain.md`, ileride manifests/locks.
- **Implementation Notes:** uv güvenilir kaynaktan task/proje için kurulabilir; global PATH onarımı varsayılmaz. Var olan pnpm sürümünü uyumluluk olmadan sabitleme. Sürüm tarih/kaynak/compatibility kaydı tut. Borsa/KAP/LLM credentials bu faz için gerekmez.
- **Validation:** Her CLI komutu ayrı exit code; registry resolution ve küçük kontrollü install/build proof T04'e bağlanır; `docker info` ve `docker compose version`. Sadece `Get-Command` PASS sayılmaz.
- **Security Check:** Unknown installer script çalıştırma; lock/pin ve kaynak doğrula; Docker config/credential çıktısını loglama. Runtime erişim kısıtı varsa uygun onaylı yürütme kullanılır.
- **Performance Check:** Aynı dependencies tekrar indirilmez; CI cache anahtarı runtime + lockfile bazlı tasarlanır.
- **Mobile Check:** UI yok; tarayıcı test runtime gereksinimleri kayda alınır.
- **Data Integrity Check:** Production data/provider kullanılmaz; proje runtime'ı ile test runtime'ı aynı sürüm ailesinde.
- **Exit Criteria:** Seçilen toolchain kurulabilir/çalışabilir ve kaynakları kayıtlı; unresolved registry/runtime sorunu varsa bağımlı görev BLOCKED.
- **Rollback:** Proje içi kurulum/pin değişiklikleri geri alınır; kullanıcı global ortamına plansız müdahale edilmez.

### T03 — Küçük ADR seti ve kalite sözleşmesi

- **Task:** Modüler monolit/ayrı worker, toolchain, veri/API kuralları, local security ve kalite/evidence kararlarını kısa ADR'lerle kaydet.
- **Purpose:** Açık bırakılmış teknik ayrıntıları açıklanabilir kılmak; master'ı çoğaltmadan değişiklik kontrolü sağlamak.
- **Files:** `docs/architecture/adr/README.md`, `0001-toolchain.md`, `0002-modular-monolith-worker.md`, `0003-data-api-conventions.md`, `0004-local-security-quality.md`; gerekirse `data-flow.md`, `security-model.md`.
- **Implementation Notes:** ADR status/context/decision/consequence/version; worker Celery+Redis seçimi belge, executable Phase 3. DTO/ORM ayrımı, UTC/Decimal, auth Phase 1 öncesi public kapalı. §§14.6/15/16 weight governance dependency açık.
- **Validation:** Her karar master referansı + sınır + sonraki faz sahibiyle okunur; önemli sapma yok, gereksiz domain framework yok.
- **Security Check:** Threat inventory: config leak/public bind/log injection/dependency risk; ileriki IDOR/CSRF/SSRF/XSS/AI yüzeylerinin sahibi. Public legal flag yeterli değil.
- **Performance Check:** §24 sayılarını ve Phase 0 baseline ayrımını yaz; ölçüm dataset/ortam/percentile kanıtı standardı.
- **Mobile Check:** Telefon/tablet/desktop/a11y matrisi ilk UI görevinin şartı.
- **Data Integrity Check:** Para accounting float değildir; alan precision/scale sahibinin gelecekteki görevleri belli; stale BEKLE şartı kaybolmaz.
- **Exit Criteria:** Uygulanabilir, master'ı değiştirmeyen ADR seti ve evidence şablonu; karar alınmış gibi gösterilen dış doğrulama yok.
- **Rollback:** ADR yeni revision/superseded kaydıyla geri alınabilir; master değiştirilmez.

### T04 — Monorepo, Git ve dependency lock temelini oluştur

- **Task:** Yalnız gerekli root/frontend/backend/docs/infra yapısını, manifests/locks/ignore/README ve Git çalışma temelini kur.
- **Purpose:** Tekrarlanabilir dependency çözümü, temiz checkout ve izlenebilir küçük değişiklikler.
- **Files:** `.gitignore`, `.dockerignore` gereken bağlamlarda, `README.md`, root `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `frontend/package.json`, `backend/pyproject.toml`, `backend/uv.lock`, runtime pins.
- **Implementation Notes:** Git henüz yok; güvenli ignore sonrasında local init ve incelenmiş başlangıç snapshot'ı. İlk snapshot öncesi gitleaks'in doğrulanmış CLI'sı bu görevde sağlanıp working tree taranır; T14'ün CI/history/image entegrasyonu beklenmez. Otomatik remote oluşturma/push kapsamı bu hazırlık görevi değildir. Generated lockfiles elle uydurulmaz. Domain klasörleri ihtiyaca göre ilgili fazda.
- **Validation:** Frozen JS/Python install, tracked dosya envanteri, lock drift yok; README komutları mevcut scripts'e karşı kontrol edilir.
- **Security Check:** `.env`, keys, venv/node_modules, DB dumps ve sensitive artifacts gitignore; `.env.example` istisnası açık. İlk snapshot öncesi secret scan.
- **Performance Check:** Lockfile cache ve tek manager; gereksiz chart/LLM/analiz bağımlılığı eklenmez.
- **Mobile Check:** UI henüz yok; framework seçimi canonical ve responsive kabuk sonraki görev.
- **Data Integrity Check:** Master byte hash aynı; business state/fixtures yok; test bağımlılıkları üretim grubundan ayrılır.
- **Exit Criteria:** Workspace ve iki manifest lock'la yeniden kurulabilir; Git state kanıtı ve dependency kapsamı incelenmiş.
- **Rollback:** Yalnız task dosyaları geri alınır; `.git` veya kullanıcı dosyaları topluca silinmez. Snapshotlar zorla reset edilmez.

### T05 — Minimal FastAPI application lifecycle

- **Task:** App factory/lifespan, core/api/db package sınırı ve typed backend entrypoint kur.
- **Purpose:** Config, resource lifecycle ve error handling için küçük test edilebilir uygulama temeli.
- **Files:** `backend/app/main.py`, gerekli `__init__.py` dosyaları, `backend/tests/test_app.py`, `backend/pyproject.toml`.
- **Implementation Notes:** Finans route/model/service yok; public boundaries type hints; import sırasında dış servise bağlanma yok. Shutdown resource cleanup için tek lifecycle yolu.
- **Validation:** App import/factory, startup/shutdown ve exception propagation unit smoke; Ruff/mypy kontrolü.
- **Security Check:** Debug stack public response'a çıkmaz; production config T06'dan geçer; test-only router üretimde kayıtlı değil.
- **Performance Check:** Import/startup'ta provider/AI/ağ işi yok; sync blocking işler request yoluna eklenmez.
- **Mobile Check:** API temeli; UI yok, uygulanamaz gerekçesi kaydedilir.
- **Data Integrity Check:** Schema/table otomatik oluşturulmaz, fake market data yok.
- **Exit Criteria:** Minimal app lifecycle testle doğrulanır; sonraki kaynak yönetimi eklenebilecek açık sınır vardır.
- **Rollback:** App temel dosyalarının tek değişiklik kümesi geri alınabilir; DB değişikliği yok.

### T06 — Güvenli config ve environment yönetimi

- **Task:** Typed server config, `.env.example`, local/private exposure guard ve güvenli varsayılanları uygula.
- **Purpose:** Eksik/yanlış config ile sessiz çalışma, credential leak veya auth öncesi public exposure riskini başlangıçta kapatmak.
- **Files:** `backend/app/core/config.py`, `.env.example`, frontend safe env erişimi gerekirse `frontend/src/lib/env.ts`, config unit tests, README.
- **Implementation Notes:** Dev/test/prod ayrımı explicit; server secrets `NEXT_PUBLIC_*` olmaz. Local fake credentials yalnız dev/test. Phase 0 public/prod app start hedefi desteklenmez; unsafe public flag/bind/default credential fail-fast. Compose içi bind ile host exposure ayrı doğrulanır.
- **Validation:** Missing/invalid/unsafe config parametrized tests; safe local başarı, public/default-secret kombinasyonları reddedilir; env dosyası tracked değil.
- **Security Check:** Config/validation log'ları secret redaction; CORS allowlist, no wildcard credentials; production stacktrace/docs exposure policy; .env.example yalnız fake değer.
- **Performance Check:** Config request başına yeniden parse edilmez; bounded pool/connection/read timeout ayarları test edilir.
- **Mobile Check:** Client error mesajı sade; server secret UI'ya gitmez. Ekran yoksa sadece contract sınırı.
- **Data Integrity Check:** UTC-aware politika, timezone doğrulama, DB/Redis test/prod ayrımı; fixture yanlış production URL ile çalışamaz.
- **Exit Criteria:** Negatif config/exposure tests PASS; default local private, public gate kapalı; env ve docs uyumlu.
- **Rollback:** Config değişikliği geri alınır; güvenlik gate'ini devre dışı bırakmak rollback yöntemi değildir, servis durdurulabilir.

### T07 — PostgreSQL ve Alembic baseline

- **Task:** Async engine/session cleanup, metadata boundary ve business table içermeyen Alembic baseline kur.
- **Purpose:** Tek schema otoritesi, test edilebilir migration ve bounded bağlantı yaşam döngüsü.
- **Files:** `backend/app/db/base.py`, `session.py`, `backend/alembic.ini`, `backend/migrations/env.py`, baseline revision, migration/DB tests.
- **Implementation Notes:** `create_all()` app startup'ta yok; migration explicit komut. Connection strings gizli. Dev DB ile isolated test DB ayrı; Alembic clean test DB'ye uygulanır.
- **Validation:** Gerçek PostgreSQL `SELECT 1`, session rollback/cleanup; clean base→head/current, tekrar upgrade idempotence; disposable DB'de downgrade→upgrade. Previous-release yokluğu doğru raporlanır.
- **Security Check:** DB host public portu yok; least privilege hedefi/runbook; parameterization; destructive migration yok, olsa explicit approval gerektirir.
- **Performance Check:** Bounded pool size/timeout; failed connection sınırsız beklemez, test sonunda connections kapanır.
- **Mobile Check:** UI yok, uygulanamaz.
- **Data Integrity Check:** Business data/schema yok; yalnız baseline version metadata. UTC DB/session policy; doğru test DB kullanımı assertion.
- **Exit Criteria:** Clean migration ve DB lifecycle gerçek PostgreSQL üzerinde kanıtlı; önceki üretim upgrade testi yapılmış gibi sunulmaz.
- **Rollback:** Disposable DB baseline downgrade; kullanıcı volume/data silinmez. İleriki gerçek data için backup/restore yolu T16'da.

### T08 — Redis resource lifecycle

- **Task:** Typed Redis bağlantısı, bounded ping, startup/shutdown cleanup ve test namespace temeli.
- **Purpose:** Health ve ileride cache/rate-limit/queue için güvenilir connection boundary oluşturmak.
- **Files:** `backend/app/core/redis.py` veya tek tutarlı altyapı modülü, Redis lifecycle tests/config.
- **Implementation Notes:** Phase 0 quote cache, distributed job veya worker schedule yok. Test keyleri namespace/TTL içerir; global `FLUSHALL` kullanılmaz.
- **Validation:** Gerçek Redis PING, bağlantı kesilince timeout/hata, shutdown cleanup; testte yaratılan scoped key varsa cleanup.
- **Security Check:** Redis public değil; URI redaction; test instance guard ve namespace izolasyonu.
- **Performance Check:** Bounded connection pool/timeouts; request başına yeni pool oluşturulmaz.
- **Mobile Check:** UI yok, uygulanamaz.
- **Data Integrity Check:** Redis authoritative finansal store değildir; test data kullanıcı cache'ini etkilemez.
- **Exit Criteria:** Redis bağlantı/kapama/failure testleri gerçek servisle çalışır; gerekçesiz retry loop yok.
- **Rollback:** Connection modülü geri alınır; Redis volume/global keys silinmez.

### T09 — Health, hata envelope ve correlation logging

- **Task:** Operasyonel route'lar, standart safe error responses, correlation propagation ve structured request logs uygula.
- **Purpose:** Uygulama/bağımlılık durumunu ayırmak ve hataları secret sızdırmadan izleyebilmek.
- **Files:** `backend/app/api/health.py`, `core/errors.py`, `core/logging.py`, request middleware, typed schemas, API/contract/log tests.
- **Implementation Notes:** Live DB/Redis çağırmaz; ready bounded probe yapar ve 503 döner. Error code/message alanı tutarlı; ID validate/generate; log timestamp/level/service/request/duration/error. Provider status ileride core readiness'ten ayrı.
- **Validation:** Healthy/DB-down/Redis-down; 404/405/422/500 envelope; same ID response/log; malformed ID/CRLF/large input, cancellation ve resource cleanup; OpenAPI schema snapshot.
- **Security Check:** Password/token/cookie/connection URL/request body/traceback log veya response'ta yok. Error details rejected secret value yansıtmaz; dependency detail local/internal.
- **Performance Check:** Liveness bağımsız; ready timeout toplamı ölçülür; log handler request'i ağır synchronous I/O ile bloke etmez; baseline T15.
- **Mobile Check:** Hata mesajları frontend localized map'e uygun; backend-only görevi.
- **Data Integrity Check:** Health timestamp UTC; readiness market freshness kanıtı değildir; provider unavailable uygulama core'unu ileride yanlış kapatmaz.
- **Exit Criteria:** Contract/failure/redaction tests gerçek çıktı ile geçer; errors sessiz `except: pass` ile gizlenmez.
- **Rollback:** Middleware/route commit'i geri alınabilir; hatayı gizleyerek yeşil health verme rollback değildir.

### T10 — Minimal responsive Next.js kabuk

- **Task:** App Router/React/strict TS/Tailwind ile küçük Türkçe başlangıç ekranı ve mevcut health durumunun loading/error/empty/success davranışını kur.
- **Purpose:** İlk günden gerçek backend bağlantısı ve mobil/a11y temelini doğrulamak; domain UI'sına erken girmemek.
- **Files:** `frontend/src/app/layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx` ihtiyaca göre, `globals.css`, az sayıda shell/status component, API boundary, frontend configs/tests.
- **Implementation Notes:** Server/client boundary bilinçli; yalnız gerekliyse client interaction. Sahte fiyat/portföy/karar, boş gelecek route'lar ve chart paketi yok. Health görüntüsü public diagnostics açma gerekçesi değil.
- **Validation:** Gerçek backend sağlıklı/erişilemez durum; component tests, strict type/lint/build; T13 viewport/axe ve T19 manuel QA.
- **Security Check:** Raw HTML/unsafe Markdown yok; client bundle/env secret taraması, internal host/config dışarı gösterilmez; safe error message.
- **Performance Check:** Minimal JS, stable skeleton, polling yok veya explicit kullanıcı retry; production route bundle T15. Her render gereksiz aynı API çağrısı yapmaz.
- **Mobile Check:** Yedi viewport; overflow/nav/text/focus, varsa button touch ~44 px; reduced motion/contrast. Chart/table yokluğu kayıtlı.
- **Data Integrity Check:** Ekran yalnız gerçek health state'i gösterir; finansal değer ve “canlı piyasa” iddiası yok; unavailable başarı gibi görünmez.
- **Exit Criteria:** Foundation UI actual backend state ile çalışır; hata/boş/yüklenme ve responsive/a11y kontrolleri kanıtlanabilir.
- **Rollback:** Shell değişiklikleri geri alınır; master veya gelecek ürün kararları etkilenmez.

### T11 — Docker images ve dört servisli Compose

- **Task:** frontend/backend images, PostgreSQL/Redis ve private local networking/healthcheck/volumes ile Compose kur.
- **Purpose:** Host toolchain farklarından bağımsız tekrarlanabilir local/dev ve CI integration ortamı.
- **Files:** `frontend/Dockerfile`, `backend/Dockerfile`, ilgili `.dockerignore`, `docker-compose.yml`, gerekiyorsa `infra/compose.test.yml`.
- **Implementation Notes:** Runtime/image sürümleri doğrulanıp pinlenir; multi-stage/non-root mümkün olan app image'larında; dev/test ayrımı açık. Migration explicit one-off command; dört servis dışında worker/LLM/monitoring cluster eklenmez. Production frontend build local APP_ENV ile ölçülebilir; `NODE_ENV=production` public release izni değildir.
- **Validation:** `docker compose config --quiet`, build, up/health, backend→DB/Redis, frontend→backend; host publish adresleri ve container restart. Image tag varlığı çalışma kanıtı değil.
- **Security Check:** Host portlar loopback; DB/Redis host'a publish edilmez; images içinde .env/.git/keys yok; runtime root gerekçesiz değil; no Docker socket mount; secret build args/layers'a yazılmaz.
- **Performance Check:** Healthcheck interval/retry bounded; build layer cache/lockfile doğruluğu, container startup süresi ve pool ayarları.
- **Mobile Check:** Production build tarayıcıdan aynı viewport matrisi ile test edilebilir; UI T13/T19'da.
- **Data Integrity Check:** Kalıcı DB volume ile restart veri kaybı yaratmaz; test volume ayrı; destructive cleanup varsayılan değil.
- **Exit Criteria:** Dört servis gerçek Compose altında birbirine erişir, exposure/health/image safety gözlemi var; image scans T14'e bağlanır.
- **Rollback:** App servislerini durdur/önceki image'a dön; volume'leri koru. Silme yalnız explicit disposable test hedefi doğrulandıysa.

### T12 — Backend quality ve anlamlı test harness

- **Task:** pytest/pytest-asyncio, Ruff lint/format, mypy strict; gerçek DB/Redis integration, config/error/health/migration testleri ve deterministic test isolation kur.
- **Purpose:** İlk bug/unsafe config/contract değişikliğini otomatik yakalayacak kapı sağlamak.
- **Files:** `backend/tests/unit/`, `integration/`, `contract/`, fixtures/config; `backend/pyproject.toml`; gerekirse `scripts/` test yardımcıları.
- **Implementation Notes:** Testler T05–T09 değişiklikleriyle yazılır. T12 harness ve gerçek servis bütünleşmesini kapatır. Sadece import smoke ile her şey test edilmiş sayılmaz; test-only route production'a çıkmaz. Hypothesis finans fazında gerçek invariant için kullanılır, Phase 0'a göstermelik math testi yok.
- **Validation:** Exact test counts, skip/xfail listesi, failed assertion'ın gate'i gerçekten nonzero yapması; clean migration gerçek PostgreSQL üzerinde. Mock test Redis/DB integration yerine geçmez.
- **Security Check:** Test DB guard, .env override isolation, config redaction/unsafe exposure/malformed correlation/oversize input testleri; credentials output'a düşmez.
- **Performance Check:** Bounded failure duration, connections closed; retry log/test storm yok; health baseline suite'ten ayrı yük ölçümü.
- **Mobile Check:** Backend görevi; UI testleri T13/T19 sahibi.
- **Data Integrity Check:** Clean baseline Alembic state, test rollback/isolation; domain calculation absent olduğu için financial golden test NOT EXECUTED, finans feature tamamlandı denmez.
- **Exit Criteria:** Anlamlı test suite, Ruff/mypy/format nonzero failure gate; gerçek DB/Redis testleri kanıtlı.
- **Rollback:** Harness config/dosya değişikliklerini geri al; ürün kusurunu test silerek veya skip ederek gizleme.

### T13 — Frontend component, E2E ve erişilebilirlik harness

- **Task:** Vitest/Testing Library/Playwright/axe, ESLint/tsc/format scripts; minimal shell'in state ve viewport testlerini kur.
- **Purpose:** Responsive/a11y/type kontratını ilk UI'dan itibaren doğrulamak.
- **Files:** `frontend/vitest.config.*`, `playwright.config.*`, `eslint.config.*`, `tsconfig.json`, test setup, `frontend/tests/`, package scripts, root formatter config.
- **Implementation Notes:** Component tests role/text/observable behavior; E2E production build ve gerçek backend ile smoke. Yedi viewport, keyboard focus, overflow, görünür kontrol ve error UI. Test runner fixture'ları dış provider gerektirmez.
- **Validation:** `vitest run`, `playwright test`, ESLint, `tsc --noEmit`, format ve build; exact counts/viewport/browser sürümleri; axe violations. Screenshot artifact oluşturmak tek başına manuel inceleme değildir.
- **Security Check:** Error content escaped; secrets client build'de yok; test-only diagnostic production route değil; browser artifacts sensitive payload içermez.
- **Performance Check:** E2E test request sayısı gözlemi, stable skeleton ve gereksiz polling yok; browser production build kullanır.
- **Mobile Check:** 360/390/430, tablet iki yön, desktop/wide; touch emulation ve focus/zoom/dialog varsa kontrol. Gerçek cihaz QA yapılmadıysa iddia yok.
- **Data Integrity Check:** Status UI gerçek health/error cevabını doğru eşler; temsili finans veri üretilmez.
- **Exit Criteria:** Automated UI/a11y/viewport ve type/lint/format/build sonuçları gerçek; manuel kontroller T19'a açık atanmış.
- **Rollback:** UI/harness diff'i geri alınır; test threshold gevşetilmez veya a11y rule sebepsiz kapatılmaz.

### T14 — Secret, static, dependency ve image security gates

- **Task:** gitleaks, Bandit, pip-audit, pnpm audit ve Trivy'yi exact sürüm ve fail policy ile quality zincirine bağla.
- **Purpose:** Secret ve bilinen dependency/container risklerini foundation bitmeden yakalamak.
- **Files:** Security tool config yalnız gerekliyse; quality scripts, package/pyproject dev deps, CI taslağı, ADR security policy.
- **Implementation Notes:** High/critical dependency/image bulguları kapanış engeli; diğer bulgular gerekçeli triage. Tool/network/DB update hatası PASS değildir. Broad allowlist/no-check/`continue-on-error` yok. Gerekli false-positive istisnası dar kapsam, kanıt, sorumlu ve süreyle kayıtlı olur; gerçek kritik kusur istisna ile kapatılmaz.
- **Validation:** Tracked/history ve working tree uygun secret kapsamı; Python static, JS/Python locked deps, iki app image ve kullanılan temel image politikası. Isolated test fixture'da synthetic canary ile scanner failure davranışı; secret canary gerçek repo history'sine commit edilmez.
- **Security Check:** Scanner stdout/artifacts redacted; actual key yok; image layers/env/client public vars kontrolü; tarayıcı/integration ayrı auth gerektirmez.
- **Performance Check:** Cache security DB ve lock bazlı tekrar kullanılır fakat scan atlanmaz; timeout/network failures görünür.
- **Mobile Check:** Doğrudan UI değişikliği yok; security fix sonrası ilgili viewport smoke yeniden çalışır.
- **Data Integrity Check:** Audit lockfile'daki gerçek bağımlılık setini inceler; başarısız tool exit code örtülmez, counts/status doğru raporlanır.
- **Exit Criteria:** Gerçek scan sonuçları, açık bulgular ve remediation kayıtlı; kritik çözülmemiş risk veya scanner failure yok.
- **Rollback:** Uyumlu önceki güvenli dependency/image'a dönüş; scan kapatma rollback değildir.

### T15 — Empty app bundle ve health latency baseline

- **Task:** Production frontend build'in route/JS/bundle boyutunu, health cold/warm latency dağılımını ve failure timeout davranışını ölç.
- **Purpose:** Hızın sonraki faza ertelenmesini önlemek; ileriki gerçek büyümeyi karşılaştırılabilir baseline ile izlemek.
- **Files:** `docs/performance/phase_00_baseline.md`, ölçüm scripti gerekirse `scripts/performance/`, ignored ham çıktı artifact dizini.
- **Implementation Notes:** Planlanan ölçüm protokolü: donanım/OS/runtime/commit, build mode, DB/Redis durumu, warm-up ve request/sample/concurrency sayısı yazılır. Öneri başlangıç 20 warm-up + 200 ölçülen request, concurrency 1 ve 10; sonuç ve test makinesine göre protokol belgeli. Cold-start ayrı. Bunlar ürün SLA'sı değildir.
- **Validation:** Başarılı/başarısız response sayısı, min/median/p95/max ve error rate; health latency regression kaydı. Production route bundle parsed/gzip ölçüsü yöntemle birlikte. Lab LCP/CLS ve interaction trace kaydedilebilir; gerçek production p75 INP iddiası yok.
- **Security Check:** Load yalnız local/test allowlisted endpoint; logs correlation/credentials redacted; yük aracı public sunucuya yönlenmez.
- **Performance Check:** Empty app baseline + dependency timeout cap kanıtı; development server sonucu production diye yazılmaz. Beklenmedik provider/AI request ve sürekli polling sıfır olmalı.
- **Mobile Check:** Belirtilen phone viewport/throttling ile lab örneği, layout stability; gerçek cihaz ölçümü yoksa belirtilir.
- **Data Integrity Check:** Timeout/failure örnekleri latency dağılımından sessizce çıkarılmaz; dataset finansal değil, sentetik health yüküdür.
- **Exit Criteria:** Yeniden çalıştırılabilir baseline raporu ve raw evidence; master'da olmayan health sayısal SLA'sı “geçti” denmez.
- **Rollback:** Ölçüm script/raporu düzeltilebilir; performans kusurunu baseline'ı yükselterek gizleme.

### T16 — Local dev, migration ve recovery runbook'ları

- **Task:** Clean startup/test commands, env, migration/rollback, DB/Redis outage ve ileriki backup/restore sorumluluklarını kısa runbook'lara yaz.
- **Purpose:** Başka bir checkout'un gizli yerel bilgiye ihtiyaç duymaması ve veri korumasının unutulmaması.
- **Files:** `README.md`, `docs/runbooks/local-development.md`, `migrations.md`, `backup-restore.md`, `dependency-outage.md`.
- **Implementation Notes:** Komut cwd/önkoşul/expected result/troubleshooting içerir. Windows PowerShell'de boşluk/Türkçe yol örnekleri uygun quoting ile. Backup encrypted/offsite/retention/key erişimi plan; şu an prod backup var denmez. İlk gerçek ledger öncesi gerçek restore/reconciliation gate'i roadmap'te.
- **Validation:** Runbook komutlarını disposable checkout/DB'de T18 ile uygula; link ve script adlarını kontrol et. Reset/delete yerine veri koruyan stop/downgrade/restore yolları açık.
- **Security Check:** Env örnekleri fake, private portlar, secret rotation ve public deploy kapısı; config dosyasını paylaş/loglama talimatı yok.
- **Performance Check:** Cached setup ve dependency health timeout'ları, ölçüm tekrar prosedürü; sınırsız retry loop yok.
- **Mobile Check:** UI QA viewport ve artifact inceleme adımları; chart henüz yok notu.
- **Data Integrity Check:** Backup alınması ≠ restore testi; baseline DB boş oluşu ≠ finansal restore correctness; previous-release test yokluğu belgeli.
- **Exit Criteria:** T18 ile uygulanabilen dev/migration/outage runbook; gelecekteki backup gate'inin sahibi ve zamanı açık.
- **Rollback:** Belge düzeltmesi; runbook örnekleri kullanıcı volume'lerine destructive varsayılan komut vermez.

### T17 — Gerçek CI ve required aggregate gate

- **Task:** Seçilen Git remote/runner üzerinde locked installs, test/lint/type/format/build/migration/security/performance/mobile jobs ve aggregate gate kur.
- **Purpose:** Local başarıyla yetinmeden master'ın “CI tamamen yeşil” çıkış şartını gerçek bir run ile karşılamak.
- **Files:** Öneri `.github/workflows/ci.yml`, CI docs ve test/performance scripts; başka mevcut CI varsa eşdeğeri.
- **Implementation Notes:** Remote yok; implementation çalışmasında erişilebilir repo/runner bilgisi doğrulanır. Remote yayın/oluşturma otomatik varsayılmaz. Workflow read-only minimum token izinleri, pinlenmiş actions, timeouts; DB/Redis ephemeral services. Aggregate job required tüm işler başarılı olmadıkça success vermez. Path filters zorunlu job'ları tümüyle skip ettirmemeli.
- **Validation:** Exact current commit SHA için hosted/self-hosted gerçek CI URL/job/artifacts; fail fixture/check failure'ın aggregate gate'i kırdığı kontrollü kanıt. Branch protection mümkünse doğrula, yoksa NOT VERIFIED; local script sonucu CI run yerine sunulmaz.
- **Security Check:** PR secret exposure, script injection ve untrusted fork code; no production/provider credentials; redacted artifacts, dependency/secret scans hard gate. Public deploy job bulunmaz.
- **Performance Check:** Cache keys lock/runtime; parallel jobs yalnız güvenli bağımsızlıkta; prod build/baseline artifact, kaynak/time limits.
- **Mobile Check:** T13 bütün gerekli viewports automated CI'da; browser sürümleri/artifacts pinli, el QA yerine geçmez.
- **Data Integrity Check:** Migration real PostgreSQL, DB/Redis test isolation; summary exact counts/exit; not-executed job PASS diye sayılmaz.
- **Exit Criteria:** CI current SHA'da tamamen yeşil, required chain doğru; erişilebilir remote/runner yoksa **Phase 0 kapanış BLOCKER**, belge onayıyla bypass edilemez.
- **Rollback:** Önceki workflow revision; failure checks kaldırılarak kapanış yok. Üretim deployment/secret değişikliği yapılmaz.

### T18 — Clean clone startup ve bağımlılık kesintisi doğrulaması

- **Task:** Yalıtılmış yeni checkout'ta yalnız belgeler ve tracked dosyalarla install/build/Compose/migration/smoke çalıştır; DB/Redis kesinti/recovery davranışını dene.
- **Purpose:** Kullanıcının mevcut shell/cache/env durumuna bağımlı gizli gereksinimleri bulmak.
- **Files:** Runbook düzeltmeleri, gerektiğinde küçük startup fix, ignored evidence artifacts; temiz checkout test dizini.
- **Implementation Notes:** Disposable clone yolu önce absolute resolve edilerek çalışma/test sınırında doğrulanır; kullanıcı repo/volume silinmez. Git checkout gerçek incelenmiş SHA'dan. Fake test env, ayrı Compose project name/volume; host Docker erişimi uygun execution bağlamıyla.
- **Validation:** Frozen installs, Compose build/up, Alembic base→head, health ve UI smoke; DB/Redis stop→ready 503/live 200; recovery→ready 200, resource cleanup. Testlerden önce keyfi global cache flush yok.
- **Security Check:** Host port inspection, public/default config fail-fast, no secrets snapshot; shell çıktılarında connection string yok.
- **Performance Check:** Cold start/install ayrı, warm app baseline T15 ile aynı yöntem; kesinti blocking süresi bounded.
- **Mobile Check:** Clean clone production build üzerinde automated viewport smoke; eski dev server'a yanlış bağlanmadığı doğrulanır.
- **Data Integrity Check:** Baseline migration version tutarlı; isolated volumes; recovery için user data silinmez. Financial ledger olmadığı için finans restore testi iddia edilmez.
- **Exit Criteria:** Temiz checkout'tan documented startup ve dependency recovery gerçek çıktıyla doğrulanır; fix olduysa ilgili tests ve CI yeni SHA'da tekrar.
- **Rollback:** Test servislerini durdur; sadece doğrulanmış disposable kaynaklar temizlenebilir; kalıcı proje volume ve working tree korunur.

### T19 — Gerçek manuel desktop/tablet/mobile ve a11y incelemesi

- **Task:** Production build kabuğunu gerçek tarayıcıda gözle ve etkileşimle incele; screenshot artifact'larını açıp layout/state'leri değerlendir.
- **Purpose:** Otomatik testlerin kaçırabildiği görsel okunabilirlik, touch/focus ve taşma sorunlarını saptamak.
- **Files:** Gerekirse küçük UI fix; completion evidence/ignored screenshots; `docs/phases/` QA referansları.
- **Implementation Notes:** Yedi viewport + başarı/yüklenme/backend-down durumu. Klavye tab/focus, text zoom, touch emulator/gerçek cihaz ayrımı, button hedefi. Chart/table/dialog yoksa bunlar için PASS değil gerekçeli uygulanamaz.
- **Validation:** Her gözlem tarih/browser/viewport/adımlar/screenshot/reviewer ile; artifact'ın yalnız alınması inceleme sayılmaz. axe otomasyonu ayrı kayıt. Fiziksel cihaz testi yapılmadıysa açıkça NOT EXECUTED.
- **Security Check:** Screenshot/loglarda secret/env/internal diagnostics sızıntısı; unsafe error content render edilmez.
- **Performance Check:** Layout jump/polling/etkileşim gecikmesi gözlemi; gözle “optimized” denmez, T15 ölçümüne bağlanır.
- **Mobile Check:** Overflow, okunabilirlik, safe area, varsa touch target ≥~44 px; tablet iki yön ve wide desktop dahil.
- **Data Integrity Check:** Gerçek health state ile ekrandaki mesaj tutarlı; fake finance verisi yok.
- **Exit Criteria:** Yapılmış manuel QA kanıtı veya açık NOT EXECUTED engeli; fix varsa etkilenen automated gates + yeni CI run. Genel “fully responsive” iddiası kullanılmaz.
- **Rollback:** UI fix ayrı diff; reviewer bulgusunu gizleme veya görüntü yerine mock değiştirme yok.

### T20 — Completion raporu ve bağımsız Phase 0 audit

- **Task:** Master §33'ün 22 alanıyla yalnız gerçek evidence üzerinden `docs/phases/phase_00_completion.md` oluştur ve roadmap statüsünü bu kanıta göre güncelle.
- **Purpose:** Başka bir denetçinin kod/komut/ölçüm/CI sonuçlarını tekrar kontrol edip fazı bağımsız değerlendirmesi.
- **Files:** `docs/phases/phase_00_completion.md`, `ROADMAP.md`, GAP_ANALYSIS durum güncellemesi; master değiştirilmez.
- **Implementation Notes:** Scope/files/API/UI/migration + exact test counts/exit codes/SHA/run URL; unit/integration/contract/mobile ayrı; known limitations/deferred owner/rollback. Root'ta ikinci completion içeriği kopyalanmaz; gerekirse link.
- **Validation:** Güncel source SHA için T12–T19 kanıtları; CI aggregate yeşil, secret/static/dependency/image scans başarılı; clean migration/startup ve manuel QA; tüm §71 soruları cevaplı.
- **Security Check:** Kritik unresolved bulgu, skipped security job, raw secret artifact veya public deploy varsa NOT READY.
- **Performance Check:** Empty bundle/health latency baseline gerçek ölçüm; lab/production field farkı belirtilmiş; gerekli metrics/logging var.
- **Mobile Check:** Automated counts + gerçekten incelenen viewport/screenshots; fiziksel cihaz/yapılmayan kontroller uydurulmaz.
- **Data Integrity Check:** Baseline migration ve config doğruluğu; hiçbir finansal feature/math pass iddiası yok; source hash/decision scope korunmuş.
- **Exit Criteria:** Yalnız bütün zorunlu kanıtlar yeterliyse **PHASE 0 READY**. Aksi **NOT READY**, her failure için somut görev/kanıt eksikliği. Bu görev tamamlanınca dahi Phase 1 kendiliğinden bu scope'a eklenmez.
- **Rollback:** Rapor hatası düzeltilir; yanlış READY kaydı geri çekilir, evidence geçmişi korunur.

## 7. Planlanan doğrulama komut sözleşmesi

**Aşağıdaki komutlar bu planlama turunda çalıştırılmadı.** İlgili script/config/dependency T02–T14 sırasında oluşturulacak ve seçilmiş sürümün resmi CLI belgeleriyle doğrulanacaktır. Her komut ayrı çalıştırılıp kendi exit code'u kaydedilir. Fail eden komut sonrasında başarılı başka bir komut ilk hatayı gizleyemez.

| CWD | Planlanan komut | Kapsam / önkoşul |
|---|---|---|
| root | `git status --short --branch` | Git init sonrası tracked/untracked değişiklik kanıtı |
| root | `pnpm install --frozen-lockfile` | JS locked install; lock oluşturma T04'te normal install ile bir kez |
| backend | `uv sync --frozen` | Python lock doğrulaması ve dev test env |
| backend | `uv run --frozen ruff check .` | Python lint |
| backend | `uv run --frozen ruff format --check .` | Python formatting |
| backend | `uv run --frozen mypy app tests` | Strict typecheck; doğrulanmış config/module kapsamı |
| backend | `uv run --frozen pytest -q --junitxml=../artifacts/phase_00/backend-junit.xml` | Unit/integration/contract; gerçek test PostgreSQL/Redis ve ayrı test env gerekir |
| backend | `uv run --frozen alembic upgrade head` | Yalnız disposable/test DB üzerinde clean→head |
| backend | `uv run --frozen alembic current` | Revision gözlemi; fresh DB'de expected head |
| backend | `uv run --frozen alembic downgrade base` | Yalnız disposable baseline DB; ardından upgrade head tekrar |
| root | `pnpm --dir frontend lint` | Script ESLint çağırmalı; kaldırılmış framework lint wrapper'ına kör bağımlılık yok |
| root | `pnpm --dir frontend typecheck` | Script `tsc --noEmit` |
| root | `pnpm --dir frontend test:unit` | Script `vitest run`, JUnit/report konfigürasyonu |
| root | `pnpm --dir frontend build` | Production frontend build, build output ve bundle artifact |
| root | `pnpm --dir frontend test:e2e` | Script `playwright test`; production build + gerçek backend/test services |
| root | `pnpm format:check` | Root script Prettier; readonly master dosyayı dönüştürmez/kapsamaz |
| backend | `uv run --frozen bandit -r app` | Static security, config hatası nonzero |
| backend | `uv run --frozen pip-audit` | Kilitli env dependency audit; network DB hatası başarısızdır |
| root | `pnpm audit --audit-level high` | JS workspace audit, tüm bulgular kaydedilir; high/critical hard gate |
| root | `gitleaks git --redact .` | Seçilen CLI sürümünde git history taraması; ilk commit/working tree kapsamı ayrıca aşağıdaki tarama |
| root | `gitleaks dir --redact .` | Working tree scanner kapsamı; dependency/artifact ignore yalnız gerekçeli |
| root | `docker compose config --quiet` | .env/config validation; secrets gösteren expanded config çıktısı paylaşılmaz |
| root | `docker compose build` | Frontend/backend image build; image isimleri T11'de belirlenir |
| root | `docker compose up -d --wait` | Test/local dört servis; desteklenen Compose sürümü doğrulanır |
| root | `docker compose ps` | Health ve port exposure gözlemi |
| root | `docker compose exec backend alembic upgrade head` | Image içinde executable PATH doğrulanır; explicit local/test migration, startup otomatik değil |
| root | `docker compose down` | Non-destructive servis kapatma; volume silme flag'i yok |
| root | `trivy image --exit-code 1 --severity HIGH,CRITICAL <image-ref>` | T11'in ürettiği her app image için gerçek tag/digest konur; placeholder çalıştırılmaz |

T15 performance script'inin adı ve exact invocation'ı implemente edildiğinde baseline raporuna yazılır; şu an var olmayan ölçüm aracının çıktısı uydurulmaz. Health request/load için k6/Locust eşdeğeri veya küçük kontrollü ölçüm aracı seçilebilir. Local stdout yanında JUnit/Playwright/scan/benchmark artifact'ları kaydedilir. CI tetikleme ve izleme komutu gerçek remote/runner seçildiğinde README'ye eklenir; mevcut olmayan repository URL'si icat edilmez.

## 8. Test ve risk kabul matrisi

| Risk / kontrol | Phase 0 gerçek doğrulaması | Sonraki sahip / sınır |
|---|---|---|
| Auth bypass/public expose | Public config fail-fast; loopback ports; foundation'da protected user endpoint yok | 1 login/session + user-scope/CSRF/IDOR |
| Secret leakage | Env gitignore/fake example, client bundle/layer inspect, redaction ve scanner | Her faz, 20 final |
| SQL injection / yanlış DB | Parameterized probe, test DB guard, no raw unbound SQL | 2+ domain query; 8 ledger |
| XSS / unsafe content | Shell escaped error content; raw HTML yok | 7/11 haber/KAP/AI sanitization tests |
| SSRF | Bu faz arbitrary URL fetch yok; core dependency URLs server config only | 2/3/7 provider host/DNS/private-IP/redirect gate |
| CSRF / IDOR | Yalnız safe operational GET; production mutation yok; uygulanamaz gerekçesi | İlk cookie mutation 1; user domains kendi fazında |
| Rate limiting | Bounded probe/resources ve private exposure; login/AI/search endpoint henüz yok | 1/4/11/14/15 endpoint gelirken zorunlu |
| Prompt injection | LLM/dış haber işlenmiyor; no raw content/tool path | 7/11 adversarial fixtures |
| Dependency supply chain | Locks, official versions, Bandit/pip-audit/pnpm audit/gitleaks/Trivy + fail policy | CI her faz |
| Connection leaks/blocking | DB/Redis lifecycle/failure/cancel/timeout tests, health latency | Provider/worker eklendiğinde 2/3 |
| Financial precision | UTC/Decimal/NUMERIC politika ve no-financial-feature scope inspection | Alan/formül geldiğinde golden/property; görsel doğruluk tek başına yetmez |
| UI responsiveness | Automated viewport+axe, production build gerçek gözlem | Her UI fazı; PWA 18 ayrı |
| Migration/restore | Clean baseline lifecycle; disposable DB guard; recovery runbook | Önceki release yoksa upgrade NOT EXECUTED; 8/20 gerçek finans restore |
| Legal/provider permissions | Public deployment yok; gate ve artefact şartı belgeli | Kaynak aktivasyonu 3/7; §75 her public/commercial launch öncesi |

“Uygulanamaz” bir PASS statüsü değildir. Completion'da neden mevcut yüzeye uygulanmadığı ve hangi fazda zorunlu olacağı yazılır. Mevcut kontrolün testini yapmamak için kullanılamaz.

## 9. Evidence ve completion standardı

Her kontrol için kayıt: `control_id`, task, master reference, komut/cwd, timestamp, source commit SHA (henüz Git yoksa dosya snapshot/hash), runtime/OS/DB/Redis/browser sürümleri, dataset/viewport/concurrency, exit code, exact pass/fail/skip/xfail sayısı, artifact path/CI run URL, reviewer/inspection kapsamı ve limitation.

- `AUTOMATED PASS`: gerçekten çalıştırılan ve geçen test/command; exact count/exit + evidence gerekir.
- `CODE INSPECTION PASS`: doğrudan incelenen gerçek dosya/satır ve kapsam; test veya penetration test yerine geçmez.
- `NOT EXECUTED`: çalıştırılmayan test/manuel QA/scan/measurement; nedeni yazılır.
- Başarısız kontrol açık `FAIL` sonucu ve engellediği gate ile kaydedilir. Planlama denetimi uygulama test PASS'i değildir.
- Gerçek manuel QA ayrıca gözlem/adım/viewport/screenshot/reviewer ile anlatılır; kullanılmayan fiziksel cihaz için PASS yazılmaz.

Completion'da master §33'ün alanları eksiksiz olmalı:

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
19. Deferred items — yalnız doğru future phase'e ait işler
20. Rollback considerations
21. Evidence / command outputs summary
22. `PHASE 0 READY` veya `NOT READY`

Bu tur `phase_00_completion.md` oluşturulmaz. Kod yokken “works”, “secure”, “optimized”, “production ready”, “fully responsive”, “all tests pass” iddiaları kullanılamaz. Sonraki turda da iddia yalnız doğrulanan kapsamı anlatmalıdır.

## 10. Phase 0 giriş ve çıkış checklist'i

### Başlangıç

- [x] Master'ın tamamı okundu; kaynak hash kaydedildi.
- [x] Repository gerçek envanteri çıkarıldı; uygulama/Git olmadığı doğrulandı.
- [x] Gap analizi ve 0–20 roadmap hazırlandı.
- [x] Scope yalnız foundation; product/mimari blocker saptanmadı.
- [x] Docker kullanıcı tarafından açıldıktan sonra daemon salt okunur sorgu ile doğrulandı.
- [ ] T02 güncel stable/LTS/peer uyumu, uv/registry ve gerçek Compose erişimini doğrulayacak.
- [ ] Implementation başladığında T01 kaynak ve repository değişikliğini tekrar kontrol edecek.

### Kapanış — şu anda hiçbiri tamamlandı iddiası değildir

- [ ] Clean checkout'ta frozen install ve belgeli dört servis startup.
- [ ] DB/Redis integration, bounded health/failure/recovery ve safe error/correlation.
- [ ] Alembic clean baseline; gerçek previous release olmadığının doğru raporu.
- [ ] Backend unit/integration/contract; frontend component/E2E/a11y; exact test counts.
- [ ] Ruff/format/mypy + ESLint/tsc/format + frontend/backend image build.
- [ ] Secret/static/dependency/image scans gerçek ve kritik açık bulgu yok.
- [ ] Loopback/env/public fail-fast/redaction kontrolleri.
- [ ] Production empty bundle + health latency baseline raporu.
- [ ] Phone/tablet/desktop automated QA ve gerçekten yapılmış manuel shell incelemesi.
- [ ] README/ADR/runbook/rollback güncel; SSOT hash değişmedi.
- [ ] **Güncel SHA için gerçek CI tamamen yeşil; aggregate gate required işleri doğru kapsıyor.**
- [ ] Completion master §33 alanları ve evidence ile independently audit edilebilir.

## 11. Planın kendi iç audit'i

Bu bölüm doküman incelemesidir, implementation testi değildir. İlgili karşılıklar bu dosyanın gerçek metni üzerinde kontrol edilmiştir.

| Master §71 sorusu | Plan karşılığı | Plan denetimi |
|---|---|---|
| 1. Hangi faz? | Başlık, §1–2: Phase 0, implementation başlamadı | Karşılandı |
| 2. Önceki faz gerçek durumu? | §1, GAP E02/E03: tamamlanmış faz/kod yok | Karşılandı |
| 3. Kapsam? | §2 ve T01–T20 | Karşılandı |
| 4. Kapsam dışı? | §2; gelecek domain/feature yok | Karşılandı |
| 5. Veri modeli? | §4: business tablo yok, base/session/metadata | Karşılandı |
| 6. Migration? | §4/T07: Alembic boş baseline, clean ve previous ayrımı | Karşılandı |
| 7. API? | §4/T09 route/error/correlation contract | Karşılandı |
| 8. UI? | §4/T10 minimal kabuk ve state'ler | Karşılandı |
| 9. Mobil? | §4/T13/T19 yedi viewport ve gerçek QA | Karşılandı |
| 10. Performance budget? | §3/T15/ROADMAP sabit ürün bütçeleri ve health baseline ayrımı | Karşılandı |
| 11. Security threats? | §8, her task Security Check | Karşılandı |
| 12. Yazılacak testler? | Her task Validation, T12/T13 ve §8 | Karşılandı |
| 13. Çalıştırılacak komutlar? | §7 cwd/önkoşul; kurulacak scriptlerle bağlı | Karşılandı; seçilen sürümde T02/T14 doğrular |
| 14. Rollback? | §4 ve her task Rollback | Karşılandı |
| 15. Completion kanıtı? | T20, §9–10; exact counts/CI SHA/status | Karşılandı |

Ek çapraz kontrol:

- Phase 0 master yapılacakları T03–T17 arasında bire bir sahiplenildi; küçük shell UI'sının test/mobil kontrolleri dışlanmadı.
- Dependency sırası döngüsüz: T04 manifest→T05–T10 app→T11 Compose→T12/13 integration→T14/15 gates→T16/17 runbook/CI→T18/19 gerçek QA→T20 evidence. T17 ilk CI'dır; T18/T19 düzeltmesi varsa yeni SHA'da tekrar CI gerekir.
- Auth Phase 1'e aittir; Phase 0 public kapalıdır. Böylece güvenlik açığı oluşturup “sonra auth” denmez, Phase 1 feature'ı erken uygulanmaz.
- Ayrı worker mimarisi ADR'de korunur, çalışan iş kuyruğu Phase 3'e aittir. Phase 0'ın dört Compose servisi korunur.
- Current-data source/freshness/stale BEKLE, deterministic Decision Engine ve AI explanation ayrımı veri/API ADR'sinde korunur; henüz finans kodu eklenmez.
- Market View/User Action, immutable snapshots, Decimal ledger, point-in-time backtest ve bounded weight governance roadmap'te açık bağımlılıklardır.
- Chart attribution, provider sözleşmeleri ve SPK/KVKK gate'leri ilgili aktivasyon/public sınırlarından önce; bir flag hukuki kanıt değildir.
- Phase 18/19/20 başlıkları erken mobile/performance/security'yi erteleme gerekçesi yapılmadı.
- Root doküman konumu ve bu tur implementation yasağı açık kullanıcı talebine göre çözüldü; master değiştirilmedi.
- Runtime/tool sürümleri, workflow erişimi ve test sonuçları doğrulanmış gibi sunulmadı; `Files` alanları gelecekteki etki listesi olarak etiketlendi.

## 12. Readiness ve blocker kararı

**Phase 0 planı uygulanmaya hazırdır. Bu çalıştırmada Phase 0 başlamamıştır ve tamamlanmış değildir.**

Başlangıcı durduran ürün davranışı/mimari çelişkisi bulunmadı. Docker daemon erişimi kullanıcı açtıktan sonra doğrulandı; önceki bağlantı sorunu giderildi. Kısıtlı oturumun pipe yetkisi ile Docker'ın çalışır olması farklı koşullardır; implementation'da Docker komutları uygun izinli yürütme bağlamında çalışmalıdır.

Şu anki doğrulama borçları T02/T04/T11/T17'nin doğal kapsamıdır: runtime/uv/registry uyumu, Git/workspace kurulumu, gerçek Compose/DB/Redis, remote/runner ve gerçek CI. Bunlar tamamlanmadan `PHASE 0 READY` yazılamaz. Özellikle remote/CI evidence üretilemezse kapanış **BLOCKER** olur; local testler bunun yerine geçmez.

Public/commercial launch için master §75 compliance artefact'ları henüz yoktur ve **public launch BLOCKED** kalır. Gerçek provider licensing/data availability sonraki ilgili faz gate'leridir; local Phase 0 scaffold başlangıcını engellemez. Küçük teknik ayrıntılar yukarıdaki güvenli önerilerle çözüldü; kullanıcıya yeni onay sorusu yöneltilmedi.

## 13. Bu planlama turunda gerçekten yapılan belge doğrulaması

2026-09-05 tarihinde PowerShell ile yalnız belge/klasör denetimi çalıştırıldı:

- Master SHA-256 beklenen değerle aynı: **değiştirilmedi**.
- Roadmap başlıkları 0–20 sırasında: **21 faz, eksik veya sıra değişikliği yok**.
- Ayrıntılı plan: **20 görev**; her görevde Task, Purpose, Files, Implementation Notes, Validation, Security Check, Performance Check, Mobile Check, Data Integrity Check, Exit Criteria ve Rollback var.
- Üç planlama belgesindeki mevcut dosyalara verilen Markdown bağlantıları çözümlendi: **kırık bağlantı yok**. Gelecekte oluşturulacak dosya yolları mevcut dosya kanıtı olarak sunulmuyor.
- Root dosya envanteri yalnız değişmemiş master ve üç yeni Markdown belgesidir; Git, scaffold, application/test code veya completion raporu oluşturulmadı.
- İçerik denetiminde ilk Git snapshot'ının secret kontrolünün T14'ü beklememesi gerektiği netleştirildi; T04 içinde ön tarama, T14'te kapsamlı CI/history/image gate'i vardır.

Bu sonuçlar **belge yapısı ve plan tutarlılığı doğrulamasıdır**. Ürün testleri, build, security scan, CI, migration, performans benchmark'ı veya manuel UI QA çalıştırılmış sayılmaz.
