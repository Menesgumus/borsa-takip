# Phase 01 Plan - Auth, User Profile, Security Foundation

## 1. Goal and Scope
- **Hedef/kapsam:** `users`, `auth`, `profile` tablolarının oluşturulması (schema), güvenli parola yönetimi (Argon2id), session/cookie rotation-revoke mekanizması, ownership bazlı (kullanıcıya ait) veri erişim temeli, audit logging temeli, onboarding/settings/risk limits veri yapılarının ve ilgili API/UI uçlarının kurulması.
- **Kapsam Dışı:** Finansal işlemler, portföy yönetimi, dış servis entegrasyonu. OAuth/SSO (eğer master'da belirtilmemişse). Email/SMS doğrulama (bu fazda basit username/password varsayılırsa).

## 2. Giriş ve Bağımlılıklar
- **Giriş:** Phase 00 READY durumunda olmalıdır (Gerçek CI engelinden dolayı lokal execution ile). Env, DB, migration ve test altyapısı mevcuttur.
- **Bağımlılıklar:** Public auth tasarımı fail-closed olmalı; test/local bypass yalnız `LOCAL_DEV=true` benzeri explicit loopback koşullarıyla olmalıdır.

## 3. Data Model & Migration
- **Tablolar:** `users`, `sessions` (veya JWT rotation tracking tablosu), `user_profiles`, `audit_logs` (temel yetki/giriş denetimleri için).
- **Migration:** Alembic ile `users` ve ilişkili tabloların `alembic revision --autogenerate` ile oluşturulması ve upgrade edilmesi.

## 4. API ve UI Uçları
- **API:**
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/me`
  - `PUT /api/v1/users/profile` (Onboarding/Settings/Risk limitleri)
- **UI:**
  - `/login`, `/register`, `/settings`, `/onboarding`
  - Next.js tarafında HttpOnly cookie'leri okuyarak veya middleware kullanarak Auth Context / Session yönetimi.

## 5. Security & Privacy (Zorunlu Kapılar)
- **Auth Limits:** Login rotasında strict rate limiting.
- **Session:** Secure, HttpOnly, SameSite cookie ile token yönetimi.
- **CSRF:** Gerekli cookie/token eşleştirmeleri.
- **Password:** Sadece Argon2id ile hashlenmiş şifreler.
- **Isolation:** Loglarda (audit/auth) parola veya PII leak edilmemeli.
- **IDOR:** Kullanıcı verisi getiren/yazan her endpoint kesinlikle `user_id` context'ini kontrol etmeli (User-scoped data ownership).

## 6. Performance Budget
- **Password Hash Cost:** Argon2id parametrelerinin makul saniye/maliyet sınırında olması (100-300ms arası hash maliyeti).
- **Session DB Query:** Profil / Session token doğrulamasının N+1 problemine yol açmaması.
- **Bundle:** Auth componentlerinin ana bundle'ı gereksiz yere şişirmemesi (Lazy load veya Server component optimizasyonları).

## 7. Mobile & UI/UX
- **Responsive:** Onboarding, ayarlar, login formları mobil cihazlarda (360/390/430px) bozulmamalı.
- **Input/Keyboard:** Form alanlarında doğru input tipleri (`type="email"`, `type="password"`) ve mobil klavye uyumluluğu.
- **Focus:** Hata mesajlarının ve form focuslarının accessibility'e uygunluğu.

## 8. Veri Doğruluğu
- **Profil Geçerliliği:** Zaman dilimi (UTC / Europe-Istanbul), yüzde, vade veya risk (enum) limitlerinin API seviyesinde `Pydantic` ile kesin doğrulanması.
- **Sıfır Risk Varsayımı:** Boş/yeni profilde kullanıcının risk toleransı rastgele "düşük" veya "yüksek" olarak hardcode edilmemeli, explicitly istenmeli veya null bırakılıp onboarding tetiklenmelidir.

## 9. Rollback & Hata Yönetimi
- **Hata Envelope:** Doğrulama hatalarında `401 Unauthorized` veya `403 Forbidden` şemalarının standard `DomainError` yapısına uygun dönmesi.
- **Kaba Kuvvet (Brute Force):** Hata mesajlarının `Invalid credentials` şeklinde jenerik olması (User exists / not exists ayrımını sızdırmaması).

## 10. Görev Dağılımı (Tasks)

### T00 - Phase 01 Planı Onayı
- Planın oluşturulması.

### T01 - Database Schema & Alembic Migrations
- **Task:** `users`, `user_profiles`, `sessions` tabloları için SQLAlchemy modellerini yazmak ve Alembic migration oluşturmak.
- **Validation:** `alembic upgrade head` ve DB tablolarının psql üzerinden varlığının doğrulanması.

### T02 - Backend Auth & Password Hashing
- **Task:** Argon2id tabanlı password hashing ve JWT / Session id altyapısını kurmak. Hashing süresi benchmarkını ölçmek.
- **Validation:** Hashing benchmark < 300ms. Unit test: Doğru parola geçmeli, yanlış kalmalı.

### T03 - Auth Endpoints & Rate Limiting
- **Task:** Login, Register, Logout endpointlerinin yazılması ve Login uçlarına memory-based veya Redis tabanlı rate limiting eklenmesi.
- **Validation:** Hatalı 5 giriş denemesi sonrası IP bazlı 429 Too Many Requests alınması.

### T04 - Session Management & Security Cookies
- **Task:** Endpointlerin tokenları HttpOnly, Secure, SameSite=Lax (veya Strict) olarak cookie'ye setlemesi ve silmesi.
- **Validation:** HTTP client veya Cypress/Playwright üzerinden auth flow'unda cookie parametrelerinin doğrulanması.

### T05 - Profile Settings & User Scope (IDOR Koruma)
- **Task:** `GET /me` ve `PUT /profile` endpointleri ile user_id contextinin JWT/Session'dan okunarak sadece yetkili profilin dönülmesi.
- **Validation:** Farklı user sessionları ile başkasının profiline erişim testi (Unit/Integration Test) -> 403 / 404 dönmeli.

### T06 - Frontend Auth Shell & Middleware
- **Task:** Next.js tarafında auth durumunu izleyen, korumalı sayfalara (örn. `/dashboard`) erişimi kısıtlayıp `/login` rotasına yönlendiren Middleware yapısının kurulması.
- **Validation:** Giriş yapmadan `dashboard` ziyaretinde login'e 307 Redirect.

### T07 - Auth Pages (Login/Register/Onboarding)
- **Task:** UI tasarımlarının Tailwind ile oluşturulması ve Pydantic validasyon hatalarının (422) UI'da gösterilmesi. Mobil klavye (type=email, vb.) uyumu.
- **Validation:** Responsive CSS testleri. `vitest` unit testleri ile form validasyonu.

### T08 - Auth E2E & A11y Tests
- **Task:** Playwright kullanılarak "Register -> Login -> Profile Edit -> Logout" flow'unun baştan sona (E2E) test edilmesi ve Axe-core ile taranması.
- **Validation:** Test counts, 7 farklı ekran boyutunda (360px - 1920px) geçişin kanıtlanması.

### T09 - Phase 01 Completion Audit & Evidence
- **Task:** Phase 01'in tüm tasklarının (Performance benchmark, Security rate limits, E2E test) evidence'larının toplanıp `phase_01_completion.md` hazırlanması.

## 11. Çıkış Kriterleri (Exit Criteria)
- Tüm tasklar tamamlanmış ve `DONE_VERIFIED` olmalı.
- User-scoped test olmadan (IDOR koruma kanıtı) süreç bitirilemez.
- Authentication lifecycle baştan sona kanıtlı olmalıdır.
