# BORSA TAKİP — AUTONOMOUS HANDOFF & CONTINUATION PROTOCOL

> **Dosya rolü:** Bu dosya, Borsa Takip projesinin otonom Codex/AI geliştirme oturumları arasında kesintisiz devri için hazırlanmış kalıcı handoff ve çalışma durumu sözleşmesidir.
>
> **Amaç:** Kota, context, model değişimi, IDE kapanması, ajan değişimi veya çalışma oturumu kesintisi olduğunda yeni bir AI'nın sohbet geçmişine ihtiyaç duymadan repository'nin gerçek durumunu anlayıp **tam olarak kaldığı yerden** devam edebilmesini sağlamak.
>
> **Önemli:** Bu dosya ürün gereksinimlerini yeniden tanımlamaz. `BORSA_TAKIP_MASTER_SPEC.md` her zaman nihai ürün/mimari kaynağıdır.

---

# 0. EN TEMEL KURAL

Bu dosyanın amacı:

> **“Önceki AI ne düşündü?” sorusunu değil, “Repository şu anda gerçekte hangi durumda ve sıradaki kesin iş nedir?” sorusunu cevaplamaktır.**

Bu nedenle bu dosyada varsayım, belirsiz hatırlama, “muhtemelen çalışıyor”, “büyük ölçüde tamamlandı”, “sanırım test edildi” veya “önceki ajan söyledi” kanıt olarak kabul edilmez.

Her kritik durum gerçek repository, Git, test, migration, build, runtime veya ölçüm kanıtına dayanmalıdır.

---

# 1. KAYNAK ÖNCELİK SIRASI

Yeni bir AI/Codex oturumu başladığında şu kaynak sırası zorunludur:

1. `BORSA_TAKIP_MASTER_SPEC.md`
2. `ROADMAP.md`
3. Aktif phase planı: `docs/phases/phase_XX_plan.md` veya Phase 0 için mevcut canonical plan yolu
4. Önceki tamamlanmış phase raporu: `docs/phases/phase_YY_completion.md`
5. Bu dosya: `AUTONOMOUS_HANDOFF.md`
6. `GAP_ANALYSIS.md`
7. Repository'nin gerçek kodu, migration'ları, testleri ve Git geçmişi

## 1.1 Çelişki halinde

Öncelik:

`MASTER SPEC > ROADMAP > PHASE PLAN > VERIFIED REPOSITORY REALITY > HANDOFF NOTLARI`

Ancak repository gerçeği ile handoff çelişirse **repository gerçeği kazanır**.

Örneğin handoff “Backend testleri geçiyor.” diyorsa ama yeni oturumda testler fail ediyorsa durum `TEST SUITE CURRENTLY FAILING` olarak güncellenir. Eski PASS kaydı silinmez; fakat artık geçerli olmadığı açıkça yazılır.

---

# 2. BU DOSYANIN İKİ BÖLÜMÜ VARDIR

## A — IMMUTABLE PROTOCOL

Bu belgenin Bölüm 0–17 arası **protokol kısmıdır**. AI bunu kendi isteğiyle değiştirmemelidir.

Bir protokol değişikliği gerçekten gerekliyse:
1. nedenini açıkça belgelemeli,
2. Master Spec ile çelişmediğini göstermeli,
3. değişiklik tarihini yazmalıdır.

## B — MUTABLE PROJECT STATE

Bölüm 18 ve sonrası:
- canlı proje durumu,
- phase ilerlemesi,
- session logları,
- test durumu,
- blockerlar,
- next action

için sürekli güncellenir.

---

# 3. HANDOFF DOSYASI NE ZAMAN GÜNCELLENMELİ?

Aşağıdaki olaylardan herhangi biri gerçekleştiğinde güncellenmelidir:

1. Bir phase başladığında
2. Yeni phase planı oluşturulduğunda
3. Bir task başladığında
4. Bir task `DONE_VERIFIED` olduğunda
5. Önemli migration eklendiğinde
6. Yeni API contract eklendiğinde/değiştiğinde
7. Önemli mimari karar alındığında
8. Test sayıları anlamlı biçimde değiştiğinde
9. Full quality gate çalıştırıldığında
10. Security scan sonucu değiştiğinde
11. Performance benchmark alındığında
12. External blocker çıktığında
13. Product blocker çıktığında
14. Phase completion audit başladığında
15. Phase READY olduğunda
16. Phase NOT READY olduğunda
17. Büyük refactor tamamlandığında
18. Context/kota sınırına yaklaşırken
19. Çalışma oturumu bilinçli olarak kapatılmadan önce
20. Yeni AI'ya devir yapılacağını fark ettiğinde

## 3.1 Minimum checkpoint sıklığı

Uzun otonom çalışmada en geç her **2–4 anlamlı task** sonrasında veya büyük bir implementation dilimi sonrasında state güncellenmelidir.

Her küçük satır değişikliği için log spam yapılmamalıdır.

---

# 4. STATUS SÖZLEŞMESİ

## Task statüleri
- `NOT_STARTED`
- `IN_PROGRESS`
- `DONE_VERIFIED`
- `FAILED_NEEDS_FIX`
- `BLOCKED_EXTERNAL`
- `BLOCKED_PRODUCT`
- `DEFERRED_TO_PHASE_XX`

## Phase statüleri
- `NOT_STARTED`
- `IN_PROGRESS`
- `AUDIT_IN_PROGRESS`
- `PHASE_XX_READY`
- `PHASE_XX_NOT_READY`
- `PHASE_XX_NOT_READY_EXTERNAL_BLOCKER`
- `PHASE_XX_NOT_READY_PRODUCT_BLOCKER`

## Gate statüleri
- `AUTOMATED_PASS`
- `CODE_INSPECTION_PASS`
- `MANUAL_QA_PASS`
- `FAIL`
- `NOT_EXECUTED`
- `NOT_APPLICABLE_WITH_REASON`

### Çok önemli

`DONE` tek başına kullanılmaz.

Bir iş gerçekten doğrulanmışsa `DONE_VERIFIED` olmalıdır. Kod yazılmış ancak doğrulama eksikse `IN_PROGRESS` kalır.

---

# 5. “DONE_VERIFIED” NE DEMEKTİR?

Bir task ancak aşağıdaki koşullar uygunsa `DONE_VERIFIED` olabilir:

1. Planlanan implementation gerçekten repository'de mevcut.
2. İlgili testler gerçekten çalıştırılmış.
3. Test sonucu gerçek exit code ile doğrulanmış.
4. Varsa migration doğrulanmış.
5. Varsa security kontrolü uygulanmış.
6. Varsa veri doğruluğu kontrolü yapılmış.
7. Varsa mobile/UI kontrolü uygulanmış.
8. Başka bir task'ın davranışını bozmadığı en az ilgili regression testleriyle kontrol edilmiş.

Sadece dosya oluşturulması, kod yazılması, test dosyası yazılması, lint'in geçmesi veya build'in geçmesi task'ın fonksiyonel olarak tamamlandığını tek başına kanıtlamaz.

---

# 6. SESSION / KOTA BİTMEDEN ÖNCE ZORUNLU CHECKPOINT

AI context veya kota limitine yaklaştığını fark ettiğinde yeni büyük task'a başlamamalıdır.

Zorunlu sıra:

1. Mevcut yarım işi mümkünse küçük ve güvenli bir noktada tamamla.
2. Syntax/build kırığı bırakma.
3. Migration'ı yarım bırakma.
4. Çalışan test suite'i gereksiz yere kırık bırakma.
5. `git status` kontrol et.
6. Aktif task'ın durumunu yaz.
7. Son başarılı test komutlarını kaydet.
8. Son başarısız test varsa kaydet.
9. Son commit SHA'yı kaydet.
10. Working tree dirty ise hangi dosyaların neden dirty olduğunu kaydet.
11. Sıradaki **tek kesin adımı** yaz.
12. Bu dosyayı güncelle.

Oturum ancak bundan sonra sona ermelidir.

---

# 7. YENİ AI İÇİN BOOTSTRAP PROSEDÜRÜ

Yeni bir AI bu repository'yi devraldığında **hemen kod yazmaya başlamaz**.

## 7.1 Oku

1. `BORSA_TAKIP_MASTER_SPEC.md`
2. `ROADMAP.md`
3. Aktif phase planı
4. Bu `AUTONOMOUS_HANDOFF.md`
5. Son tamamlanmış phase completion raporu
6. Aktif phase varsa önceki session logları

## 7.2 Doğrula

Gerçek ortamda yeniden kontrol et:
- current branch
- current commit SHA
- `git status`
- lockfile durumu
- active migration head
- gerekli container/service durumu
- kritik test suite'in en az smoke/targeted subset'i
- handoff'ta belirtilen blocker'ın hâlâ geçerli olup olmadığı

## 7.3 Karşılaştır

**Handoff iddiası** ile **gerçek repository** farklıysa `HANDOFF DRIFT` olarak logla.

## 7.4 Devam et

Yalnız bundan sonra `NEXT EXACT ACTION` alanında belirtilen işten devam et.

---

# 8. YENİ AI TÜM PROJEYİ BAŞTAN PLANLAMAMALI

Handoff düzgünse yeni ajan:
- Phase 0'dan tekrar başlamaz.
- Daha önce tamamlanmış task'ları tekrar implement etmez.
- Master Spec'i yeniden yorumlayıp mimariyi değiştirmez.
- Kendi tercihleriyle farklı framework'e geçmez.
- Eski phase planlarını gereksiz yeniden yazmaz.

Ancak gerçek repository ile belgeler uyuşmuyorsa önce farkı düzeltir.

---

# 9. AKTİF TASK HANDOFF FORMATI

Bir task yarım kalıyorsa aşağıdaki bilgiler zorunludur:

```yaml
task_id: TXX
task_title: ""
status: IN_PROGRESS

goal:
  ""

completed_work:
  - ""

remaining_work:
  - ""

files_changed:
  - path: ""
    purpose: ""

commands_executed:
  - command: ""
    cwd: ""
    exit_code: 0
    result: ""

tests:
  passed:
    - ""
  failed:
    - ""

known_issue:
  ""

important_code_locations:
  - file: ""
    symbol_or_lines: ""
    why: ""

next_exact_action:
  ""

do_not_repeat:
  - ""

risks:
  - ""
```

Yeni ajan bu block'u okuduğunda tekrar geniş keşif yapmak zorunda kalmamalıdır.

---

# 10. PHASE HANDOFF FORMATI

Her phase için bu dosyada özet kayıt tutulmalıdır.

```markdown
## Phase 01 — Auth, User Profile, Security Foundation

Status: PHASE_01_READY
Started: 2026-09-06
Completed: 2026-09-07

### Implemented
- Argon2id password hashing
- session rotation
- CSRF
- user ownership dependency
- onboarding profile
- risk limits

### Important files
- backend/app/auth/...
- backend/app/users/...
- frontend/app/onboarding/...

### Migrations
- revision: ...
- clean upgrade: PASS
- previous -> latest: PASS
- disposable downgrade: PASS

### Verification
- backend tests: exact count
- frontend tests: exact count
- E2E: exact count
- security: PASS
- IDOR matrix: PASS
- mobile: PASS

### Important decisions
- ...

### Known limitations
- ...

### Deferred
- ...

### Completion report
docs/phases/phase_01_completion.md

### Final commit
<sha>
```

Bu bölüm completion raporunun yerine geçmez. Sadece hızlı handoff özetidir.

---

# 11. PHASE İÇİN “NE YAPILDI?” KAYDI

Her phase'te aşağıdaki başlıklar tutulmalıdır:

1. **Hedef neydi?**
2. **Neler implement edildi?**
3. **Hangi dosyalar eklendi/değişti?**
4. **Veri tabanında ne değişti?**
5. **API'de ne değişti?**
6. **Frontend'de ne değişti?**
7. **Güvenlikte ne yapıldı?**
8. **Performansta ne yapıldı?**
9. **Mobilde ne yapıldı?**
10. **Hangi testler eklendi?**
11. **Hangi testler gerçekten çalıştırıldı?**
12. **Hangi hatalar çıktı ve nasıl çözüldü?**
13. **Ne yapılmadı?**
14. **Hangi teknik borç kaldı?**
15. **Son durum ne?**

Bu bölüm “Phase 1'de ne yaptı?” sorusuna tek bakışta cevap vermelidir.

---

# 12. TEST DURUMU HANDOFF'TA NASIL TUTULUR?

Yalnız “tests pass” yazılmaz.

| Suite | Command | Result | Count | Last Run | Commit |
|---|---|---|---:|---|---|
| Backend unit | `...` | PASS | 0 | ISO timestamp | SHA |
| Backend integration | `...` | PASS | 0 | ... | ... |
| Frontend unit | `...` | PASS | 0 | ... | ... |
| E2E | `...` | PASS | 0 | ... | ... |
| Typecheck | `...` | PASS | - | ... | ... |
| Lint | `...` | PASS | - | ... | ... |
| Build | `...` | PASS | - | ... | ... |
| Security scan | `...` | PASS | - | ... | ... |

Test sayıları tahmin edilmez. Run eski commit'e aitse yeni commit için otomatik PASS sayılmaz.

---

# 13. GIT / WORKING TREE HANDOFF

Handoff sırasında şu alanlar zorunludur:

```text
Current branch:
Current commit:
Last known good commit:
Working tree:
Remote:
Latest phase checkpoint commit:
```

Dirty working tree varsa:

```markdown
### Uncommitted changes

| File | Reason | Safe to keep? | Validation state |
|---|---|---|---|
| ... | ... | YES/NO | ... |
```

Yeni ajan uncommitted dosyaları kör şekilde silmemelidir.

---

# 14. MIGRATION HANDOFF

Her DB phase'inde kaydedilir:

```text
Current migration head:
Previous production/release migration:
New migrations this phase:
Clean DB -> head:
Previous -> head:
Downgrade disposable test:
Data preservation result:
Known irreversible operations:
```

Bir migration uygulanmış fakat test edilmemişse `IN_PROGRESS` olarak işaretlenir.

---

# 15. DIŞ SERVİS / CREDENTIAL HANDOFF

Secrets bu dosyaya **asla yazılmaz**.

Yalnız gereksinim/state yazılır:

```yaml
external_dependency:
  name: TCMB_EVDS
  credential_required: true
  credential_available: false
  environment_variable: TCMB_EVDS_API_KEY
  blocker: true
  reason: "Real adapter validation requires key."
```

API key, password, token, session cookie veya connection password yazılmaz.

---

# 16. BLOCKER HANDOFF

```markdown
## BLOCKER B-XXX

Type: EXTERNAL_BLOCKER
Phase: 07
Task: T04
Status: ACTIVE

### What is blocked?
...

### Evidence
...

### Why AI cannot solve it?
...

### What user must provide/do?
...

### What has already been completed?
...

### Exact resume action after resolution
...
```

Blocker kalkınca silinmez; `RESOLVED` olarak işaretlenir.

---

# 17. HANDOFF DOSYASI İÇİN KALİTE KURALLARI

## Yapılacak
- Kısa ama kanıtlı yaz.
- Dosya yollarını gerçek kullan.
- Commit SHA yaz.
- Test command yaz.
- Exit code yaz.
- Açık issue yaz.
- Sıradaki kesin adımı yaz.
- Eski önemli kararları koru.
- Büyük değişikliklerde phase logunu güncelle.

## Yapılmayacak
- Chain-of-thought yazma.
- Uzun iç muhakeme dump etme.
- Secret yazma.
- Tüm terminal logunu yapıştırma.
- Gereksiz kod blokları kopyalama.
- README'nin tamamını çoğaltma.
- Master Spec'i burada tekrar yazma.
- “Her şey iyi” gibi belirsiz durum yazma.
- Çalıştırılmamış testi PASS gösterme.
- Eski problemi kayıttan gizleme.

Handoff karar/rationale özetini içerebilir; gizli düşünme zinciri içermemelidir.

---

# 18. LIVE PROJECT STATE — MUTABLE

> **Bu bölüm Codex/AI tarafından sürekli güncellenmelidir.**
>
> İlk implementation oturumu başlamadan önce mevcut repository gerçeğine göre doldurulmalıdır.

**Checkpoint kapsamı (2026-09-05 / S-20260905-02):** Belge okuma + repository/GitHub doğrulama + handoff Git/GitHub alanlarını gerçek duruma göre güncelleme. Kullanıcının açık talimatı: **implementation başlatma**; bir sonraki mesaj otonom implementation talimatı olacak. Protokol (Bölüm 0–17 ve §31–END) değiştirilmedi.

Ürün/mimari kararı bakımından Master Spec, ROADMAP ve Phase 0 planıyla çelişki saptanmadı. Kaynak önceliği: `MASTER SPEC > ROADMAP > ACTIVE PHASE PLAN > VERIFIED REPOSITORY REALITY > AUTONOMOUS_HANDOFF > GAP_ANALYSIS`. **Ne yapılmış olduğu** konusunda doğrulanmış repository gerçeği handoff notundan üstündür.

`NOT_STARTED`, mevcut Phase 0 yürütme statüsüdür; planın hazır olması `PHASE_00_READY` değildir. Bu oturumdaki denetimler T01'i `DONE_VERIFIED` yapmaz; Git init / scaffold / remote add henüz yapılmadı (T04 kapsamı).

## 18.1 Project Identity

```yaml
project: Borsa Takip
master_spec: BORSA_TAKIP_MASTER_SPEC.md
roadmap: ROADMAP.md
handoff_file: AUTONOMOUS_HANDOFF.md
current_phase: "00"
current_phase_status: "IN_PROGRESS"
current_task: "T07"
current_task_status: "IN_PROGRESS"
active_phase_plan: "phase_00_plan.md"
current_activity: "IMPLEMENTING_PHASE_00"
implementation_started: true
execution_hold: "NONE"
last_updated_at: "2026-09-05T18:55:13.005Z"
updated_by_model: "Composer (Cursor Auto); exact model identifier not exposed"
session_id: "S-20260905-02"
```

---

# 19. CURRENT REPOSITORY SNAPSHOT

```yaml
git:
  initialized: true
  current_branch: "main"
  current_commit: "8657ddb"
  last_known_good_commit: null
  latest_phase_checkpoint_commit: null
  last_pushed_commit: null
  working_tree: "clean"
  remote_origin_local: null
  remote_sync_status: "LOCAL_GIT_ABSENT; CANONICAL_REMOTE_DECLARED_AND_VERIFIED_EMPTY"
  canonical_remote:
    full_name: "Menesgumus/borsa-takip"
    default_branch: "main"
    ssh: "git@github.com:Menesgumus/borsa-takip.git"
    https: "https://github.com/Menesgumus/borsa-takip.git"
    url: "https://github.com/Menesgumus/borsa-takip"
    verified_at: "2026-09-05T18:55:13Z"
    remote_state: "EXISTS_EMPTY; size=0; ls-remote empty; commits API 409 Git Repository is empty"
  evidence: "V01-V04: local git status/branch/rev-parse/remote each fatal not a git repository; .git absent. V20-V22: GitHub API + git ls-remote confirm empty canonical remote."

environment:
  os: "Microsoft Windows NT 10.0.26200.0"
  powershell: "5.1.26100.9278 (this Cursor shell session; prior handoff recorded pwsh 7.6.5 — see HD-006)"
  node: "v22.22.0; version probe only — drifted from prior v24.13.1 (HD-003)"
  pnpm: "11.25.0; version probe only"
  npm: "11.6.1; now works in this session — prior MODULE_NOT_FOUND was H13/E07 (HD-005)"
  python: "3.13.14; version probe only — drifted from prior 3.12.7 (HD-004)"
  uv: "NOT_FOUND_ON_CURRENT_PATH; other installation locations not audited"
  docker: "daemon ServerVersion 28.4.0 reachable (V10)"
  docker_compose: "v2.39.4-desktop.1 (V11)"
  gh_cli: "NOT_FOUND_ON_CURRENT_PATH; GitHub verified via git ls-remote + REST API"
  dependency_install_build_registry_validation: "NOT_EXECUTED"

database:
  engine: "PostgreSQL planned; no project database configuration exists"
  migration_tool: "Alembic planned; no migration files/configuration exist"
  current_head: null
  previous_release_head: null
  new_migrations: []
  migration_cli_run: "NOT_EXECUTED; no Alembic project"
  clean_upgrade: "NOT_EXECUTED"
  previous_upgrade: "NOT_EXECUTED; previous release absent"
  disposable_downgrade: "NOT_EXECUTED"
  data_preservation_restore: "NOT_EXECUTED; no application data"
  irreversible_operations: []

cache:
  redis: "planned; no project Redis configuration exists"

services:
  frontend: "NOT_DEFINED_IN_REPOSITORY"
  backend: "NOT_DEFINED_IN_REPOSITORY"
  postgres: "NOT_DEFINED_IN_REPOSITORY"
  redis: "NOT_DEFINED_IN_REPOSITORY"
  compose_definition: "ABSENT"
  matching_project_containers: 0
  container_scope: "Exact com.docker.compose.project.working_dir label filter; other labels/host services not exhaustively audited"
  app_startup: "NOT_EXECUTED"
```

### Mevcut dosyalar ve checkpoint fingerprint'leri

Kök dizinde aşağıdaki **beş Markdown dosyası** var; alt dizin yok (V00). Application/scaffold/CI yok.

| Dosya | Rol / bu oturumda değişiklik | Doğrulanan SHA-256 |
|---|---|---|
| `BORSA_TAKIP_MASTER_SPEC.md` | Tamamen okundu (bu oturum); salt okunur; hash değişmedi | `9A11AEF132A6B2ADCD616B3908E283EA9F1CBB63C45E2BFC91085F5210753F74` |
| `ROADMAP.md` | Tamamen okundu; değiştirilmedi | `5E32D7C0D300EB8BD05C33116795088DF86A1F0722B60272EC3839A5ACC01BDF` |
| `phase_00_plan.md` | Tamamen okundu; değiştirilmedi | `CCC4C8C9CFB773FA93491B869AEEDAEF89F8C8A71E5F79D6C0921291A43EF66C` |
| `GAP_ANALYSIS.md` | Tamamen okundu; değiştirilmedi | `0665CDC6B7D4A0A8136AADFFE8658E570863AE8A6A1FDE9A62B0B9380463677D` |
| `AUTONOMOUS_HANDOFF.md` | Tamamen okundu; yalnız Mutable Project State güncelleniyor | Otutum başı full-file: `D648ACBF465F9A8CD4B29B59029A4D76D5DE518FD7F5B54C8C33B124E5EC4AE8`; güncelleme sonrası full-file hash farklı olacaktır |

Immutable prefix (dosya başından §18 başlığına kadar) **12.713 bayt**, SHA-256 `E1068D4C4762D8A3B16EDE60EC667F7DCC62A069645B883F2305584C13C15926` — bu oturumda doğrulandı (V14). §31–END protokol metni dokunulmadı.

### Git / GitHub özet alanları (zorunlu)

```text
Remote: canonical Menesgumus/borsa-takip (SSH git@github.com:Menesgumus/borsa-takip.git); local origin NOT CONFIGURED (no .git)
Current branch: null (no local Git)
Current commit: null
Last known good commit: null
Latest phase checkpoint commit: null
Last pushed commit: null
Remote sync status: LOCAL_GIT_ABSENT; remote EXISTS_EMPTY (default branch name main; no commits yet)
```

`git remote add origin` bu oturumda **çalıştırılmadı**: local Git deposu yok; remote eklemek `git init` gerektirir ve bu T04 / implementation kapsamındadır. Yanlış ikinci origin oluşturulmadı.

### Git dışındaki yerel değişiklik

| Dosya | Neden | Korunmalı mı? | Validation state |
|---|---|---|---|
| `AUTONOMOUS_HANDOFF.md` | Mutable state: GitHub canonical remote, toolchain drift, verify-only session | EVET | Bu oturum V00–V22 |

Git olmadığı için bu tablo `git diff` sonucu değildir. Git init + `origin` hizalaması açık implementation talimatından sonra T04'e aittir.

---

# 20. CURRENT PHASE SUMMARY

## Phase 00 — Governance, Scaffold, Quality Baseline

****Status:** `IN_PROGRESS`

### Objective
Master Spec ve `phase_00_plan.md` doğrultusunda tekrarlanabilir monorepo, frontend/backend, PostgreSQL/Redis local environment, migration baseline, quality/security/test/CI temelini kurmak.

### Current task
`T07 — PostgreSQL / Alembic baseline`

### Completed tasks
T01, T02, T03, T04, T05, T06 tamamlandı. Git init yapıldı, uv kuruldu, ADR'ler yazıldı, backend app temeli atıldı.

### In-progress tasks
T07

### Remaining tasks
T08-T20

### Current blockers
Phase 0 başlangıcını engelleyen kanıtlı ürün/mimari blocker yok. Şu anki durma nedeni **kullanıcının verify-only / no-implementation kapsamıdır**. Canonical GitHub remote (`Menesgumus/borsa-takip`) doğrulandı ve **boş**; local Git olmadığı için `origin` henüz bağlanamaz — bu T04 işidir, product blocker değildir. Docker daemon erişimi yeniden doğrulandı. Registry/uv, gerçek Compose ve CI T02/T11/T17 görevleridir.

### Next exact action
Tek canonical `next_exact_action` §28'dedir. Bu oturumda T01/T02 veya Git init yapılmaz.

---

# 21. ACTIVE TASK DETAIL

```yaml
task_id: "T01"
task_title: "Mevcut durumu tekrar doğrula ve scope'u sabitle"
status: "NOT_STARTED"

goal:
  - "Implementation başlamadan önce gerçek başlangıç durumunu doğrulamak."

completed_work: []

bookkeeping_observations_only:
  - "Master/ROADMAP/phase_00_plan/GAP/handoff fully read this session; fingerprints V00."
  - "Local Git absent; branch/SHA/status/remote probes fatal; V01-V04."
  - "Canonical GitHub Menesgumus/borsa-takip verified empty via API + ls-remote; V20-V22."
  - "Toolchain drift vs prior handoff recorded HD-003..HD-007; repository inventory still five MD files."
  - "These verify-only observations do not start or close T01."

remaining_work:
  - "Açık implementation talimatı geldikten sonra T01 giriş doğrulamasını güncel snapshot üzerinde yap."
  - "Master hash, repository/Git, scope ve T01 Exit Criteria sonuçlarını o oturumun kanıtlarıyla kaydet."
  - "T04'te git init + branch main + origin = Menesgumus/borsa-takip hizalaması."
  - "Phase 0 T02-T20 henüz başlamadı."

files_changed:
  - path: "AUTONOMOUS_HANDOFF.md"
    purpose: "Mutable state: GitHub canonical remote fields, HANDOFF DRIFT, verify-only session"
commands_executed:
  - reference: "V00-V22 in section 22; read-only verification, not T01 implementation evidence"

tests:
  passed: []
  failed: []
  not_executed:
    - "All application tests, lint, typecheck, build, security scans, migration, performance and mobile QA; no implementation exists."
  application_tests_executed: 0
  test_suite_counts: null

known_issue: "uv absent from PATH. Toolchain versions drifted vs prior handoff (node/python/npm/shell). Local Git absent so origin cannot be configured yet."
important_code_locations:
  - file: "phase_00_plan.md"
    symbol_or_lines: "T01 — Mevcut durumu tekrar doğrula ve scope'u sabitle"
    why: "First implementation-session entry task after explicit start instruction; application code does not yet exist."

next_action_reference: "Section 28 resume.next_exact_action is the single canonical action."

do_not_repeat:
  - "Master Spec'i ürün açısından yeniden tasarlama."
  - "Phase 0 READY olmadan Phase 1 implement etme."
  - "Bu verify-only oturumu implementation yetkisi sayma."
  - "Git init / remote add / scaffold'ı bu hold altında yapma."
  - "Handoff doğrulamalarını Phase 0 DONE_VERIFIED diye işaretleme."

risks:
  - "CLI version probe is not dependency compatibility, installation, app startup or CI evidence."
  - "No local Git: current/last-known-good/pushed commit cannot be supplied until T04."
  - "Remote is empty; first push must follow secret scan and quality checks — not this session."
```

---

# 22. CURRENT VERIFICATION MATRIX

### Ürün / phase gate'leri

**Gerçek çalıştırılmış uygulama testi sayısı: 0.** Suite toplamları/pass/fail sayıları `null` (suite yok); bu durum “0 test geçti” demek değildir. Aşağıdaki komutlar **planlanan** komutlardır, bu tur çalıştırılmadı. Exit code ve last-run bu nedenle `—`. Commit tüm satırlarda yok: Git deposu yok.

| Gate | Planlanan command / kaynak | Status | Exit code | Count / neden |
|---|---|---|---|---|
| Backend tests | backend cwd: `uv run --frozen pytest -q` | NOT_EXECUTED | — | null; kod/suite/env yok |
| Backend typecheck | backend cwd: `uv run --frozen mypy app tests` | NOT_EXECUTED | — | null; kod/config yok |
| Backend lint / format | backend cwd: `uv run --frozen ruff check .` / `ruff format --check .` uv üzerinden | NOT_EXECUTED | — | null; kod/config yok |
| Frontend tests | root: `pnpm --dir frontend test:unit` | NOT_EXECUTED | — | null; workspace/script yok |
| Frontend typecheck / lint / format | `phase_00_plan.md` §7 | NOT_EXECUTED | — | null; workspace/config yok |
| Frontend / image build | `pnpm --dir frontend build`; `docker compose build` | NOT_EXECUTED | — | null; app/Dockerfile yok |
| E2E | `pnpm --dir frontend test:e2e` | NOT_EXECUTED | — | null; UI/config yok |
| Migration clean | backend cwd: `uv run --frozen alembic upgrade head` | NOT_EXECUTED | — | null; Alembic/DB yok |
| Upgrade migration | `phase_00_plan.md` T07/T12 | NOT_EXECUTED | — | null; previous release yok |
| Security scans | T14 gitleaks/Bandit/pip-audit/pnpm audit/Trivy | NOT_EXECUTED | — | null; scan araçları kurulup çalıştırılmadı |
| Docker/Compose app startup | `docker compose up -d --wait` | NOT_EXECUTED | — | null; Compose/app yok |
| CI | T17 gerçek remote/runner/current SHA | NOT_EXECUTED | — | null; local Git yok; remote EXISTS_EMPTY; workflow yok |
| Performance | T15 production bundle + health latency | NOT_EXECUTED | — | null; app/ölçüm yok |
| Mobile automated / accessibility | T13 viewport/axe | NOT_EXECUTED | — | null; UI/test yok |
| Manual UI QA | T19 gerçek tarayıcı/viewport/touch/keyboard | NOT_EXECUTED | — | null; UI yok |
| Backup / restore | T16 runbook; sonraki data/release gate | NOT_EXECUTED | — | null; proje DB/data yok |

### Bu verify oturumunda gerçekten çalıştırılan kontroller

CWD: `C:\Users\muham\Desktop\Her Şey\Yazılım projeleri\Borsa Takip Destek`. UTC ~`2026-09-05T18:53:57Z`–`18:55:13Z`. App testleri değildir.

| ID | Gerçek command / işlem | Exit | Gerçek sonuç / sınır |
|---|---|---:|---|
| V00 | Inventory `Get-ChildItem -Force`; path existence checks; SHA-256 hashes | 0 | Beş MD, alt dizin yok. Master hash beklenenle aynı. ROADMAP/plan/GAP hash'leri önceki checkpoint ile aynı. Handoff full-file oturum başı `D648ACBF...`. |
| V01 | `git status --short --branch` | 128 | `fatal: not a git repository` |
| V02 | `git branch --show-current` | 128 | Aynı; branch yok |
| V03 | `git rev-parse HEAD` | 128 | Aynı; commit yok |
| V04 | `git remote -v` | 128 | Aynı; local origin yok — `git remote add` yapılamaz |
| V05 | `node --version` | 0 | v22.22.0 (**HD-003** vs prior v24.13.1) |
| V06 | `pnpm --version` | 0 | 11.25.0 |
| V07 | `python --version` | 0 | Python 3.13.14 (**HD-004** vs prior 3.12.7) |
| V08 | `uv --version` / Get-Command uv | non-zero / False | uv current PATH'te yok |
| V09 | `$PSVersionTable.PSVersion`; OS | 0 | PowerShell 5.1.26100.9278; Windows 10.0.26200 (**HD-006** vs prior pwsh 7.6.5) |
| V10 | `docker info --format '{{.ServerVersion}}'` | 0 | 28.4.0 |
| V11 | `docker compose version` | 0 | v2.39.4-desktop.1 |
| V12 | Project-label `docker ps --all --filter ...working_dir=...Borsa Takip Destek` | 0 | Boş; matching container 0 |
| V13 | `npm --version` | 0 | 11.6.1 (**HD-005** vs prior MODULE_NOT_FOUND) |
| V14 | Immutable prefix SHA-256 (§18 boundary) | 0 | 12.713 bayt; `E1068D4C...C15926` — protokol prefix değişmedi |
| V20 | `git ls-remote` SSH + HTTPS `Menesgumus/borsa-takip` | 0 | Boş çıktı (commit yok); erişim başarılı |
| V21 | GitHub REST `GET /repos/Menesgumus/borsa-takip` | 0 | full_name=Menesgumus/borsa-takip; default_branch=main; private=False; size=0; ssh/https URLs match declaration |
| V22 | GitHub REST commits?per_page=1 | 409 | `Git Repository is empty.` — remote EXISTS_EMPTY |
| V23 | `gh` CLI | n/a | PATH'te yok; doğrulama git+REST ile yapıldı |

Önceki S-20260905-01 H00–H14 kayıtları tarihsel kanıt olarak §27'de korunur; güncel runtime gerçeği V00–V23'tür.

### H14 / önceki belge doğrulaması (tarihsel)

S-20260905-01 H14 sonucu korunur. Bu oturumda V00+V14 master/plan/GAP/prefix hash'lerini yeniden doğruladı.

---

# 23. CURRENT KNOWN ISSUES

| ID | Severity | Phase | Description | Status | Owner/Next action |
|---|---|---:|---|---|---|
| I-ENV-NPM | Ortam / düşük | 00 | Önceki E07/H13 MODULE_NOT_FOUND; bu oturumda npm 11.6.1 çalıştı (V13). Ortam farkı mümkün; global onarım yapılmadı | OPEN→DRIFTED; başlangıç blocker değil | T02; pnpm hâlâ önerilen manager |
| I-ENV-UV | Kurulum önkoşulu | 00 | uv current PATH'te yok (V08) | OPEN / NOT_STARTED | T02 |
| I-ENV-RUNTIME | Kurulum önkoşulu | 00 | Node/Python sürümleri önceki handoff kaydından saptı (HD-003/004); stable/LTS uyumu henüz seçilmedi | OPEN | T02 resmi kaynak doğrulaması |
| I-GIT-LOCAL | Kurulum önkoşulu | 00 | Local `.git` yok; origin bağlanamaz | OPEN / expected | T04 git init + main + origin |
| I-CI | Kapanış önkoşulu | 00 | Local Git yok; remote boş; workflow yok; gerçek yeşil CI run yok | PENDING | T04 Git; T17 CI. CI olmadan Phase 0 READY yok |
| I-DOCKER | Yürütme bağlamı | 00 | Daemon 28.4.0 erişilebilir (V10); Compose CLI var; proje Compose/app yok | RESOLVED for daemon; app startup NOT_EXECUTED | T11 |
| I-GH-CLI | Opsiyonel tooling | 00 | `gh` PATH'te yok; remote API+ls-remote ile doğrulandı | OPEN / non-blocking | İsteğe bağlı kurulum; zorunlu değil |

### HANDOFF DRIFT / düzeltme kaydı

| ID | Önceki handoff ifadesi | Doğrulanan durum / çözüm | Statü |
|---|---|---|---|
| HD-001 | Phase 00 History “Important files: Henüz yok”; canlı envanter placeholder | H00/H09: master + planlama belgeleri + handoff mevcut | RESOLVED (S-01) |
| HD-002 | §20/§21/§28 doğrudan T01 başlatıyordu | Verify/handoff-only guard | RESOLVED (S-01); S-02'de verify-only devam |
| INIT-001 | working_tree/services/runtime UNKNOWN | NOT_A_GIT_REPOSITORY + servis yok | INITIALIZED (S-01) |
| HD-003 | environment.node = v24.13.1 | Bu oturum `node --version` → **v22.22.0** | ACTIVE — HANDOFF DRIFT; T02'de pinlenecek |
| HD-004 | environment.python = 3.12.7 | Bu oturum `python --version` → **3.13.14** | ACTIVE — HANDOFF DRIFT; T02'de pinlenecek |
| HD-005 | npm MODULE_NOT_FOUND (H13/E07) | Bu oturum `npm --version` → **11.6.1** | ACTIVE — HANDOFF DRIFT; historical E07 silinmedi |
| HD-006 | powershell = 7.6.5 | Bu Cursor shell → **5.1.26100.9278** | ACTIVE — session shell farkı; ürün blocker değil |
| HD-007 | git.remote = null; GitHub yok sayılmış | Kullanıcı canonical remote bildirdi; API+ls-remote: **Menesgumus/borsa-takip EXISTS_EMPTY**, default `main`. Local origin hâlâ yok | ACTIVE — declared remote verified; local bind deferred to T04 |

Immutable §7 kısa bootstrap listesi completion/handoff sırasını §1'den farklı yazıyor. Bu editte değiştirilmedi; kullanıcının kesin okuma sırası geçerlidir.

---

# 24. CURRENT EXTERNAL BLOCKERS

Şu anda kanıtlı Phase 0 başlangıç external/product blocker'ı yok. Verify-only kullanıcı sınırı bir izin/çalışma kapsamıdır. Canonical GitHub remote mevcut ve boştur; bu local Phase 0 başlangıcını engellemez. Şu aşamada kullanıcıdan yeni bilgi veya onay istenmiyor.

| ID | Phase | Dependency | Status | Required user action |
|---|---:|---|---|---|
| B-HIST-DOCKER | 00 | Önceki Docker daemon/pipe erişimi | RESOLVED — E12/H10/V10 başarılı | Bu checkpoint'te işlem gerekmiyor |
| G-GITHUB | 00 Git/CI | Canonical remote `Menesgumus/borsa-takip` | VERIFIED_EXISTS_EMPTY; local origin unbound until T04 | Implementation başlayınca T04'te bağlanacak |
| G-CI | 00 kapanış | Gerçek remote/runner + current SHA yeşil CI | PENDING_VERIFICATION | T17; bu tur işlem yok |
| G-PROVIDER | 03/07 aktivasyon | BIST/KAP/EVDS/haber erişim/lisans | NEEDS_VERIFICATION; local Phase 0 blocker'ı değil | İlgili gate'e gelince |
| G-PUBLIC | Public/commercial release | Master §75 compliance artefact'ları | PUBLIC RELEASE BLOCKED | Launch öncesi; şimdi yayın yok |

---

# 25. CURRENT IMPORTANT TECHNICAL DECISIONS

| Decision | Phase | Reason summary | ADR/Source | Still active? |
|---|---:|---|---|---|
| Modular monolith + separate worker | 00 | Master Spec kararı | Master Spec | YES |
| pnpm workspace | 00 | Phase plan recommendation; implementation sırasında doğrulanacak | phase_00_plan | VERIFY |
| PostgreSQL authoritative DB | 00 | Master Spec kararı | Master Spec | YES |
| Redis cache/worker support | 00+ | Master/roadmap kararı | Master Spec / Roadmap | YES |
| Next.js App Router/React/strict TS/Tailwind; FastAPI/Pydantic/SQLAlchemy/Alembic | 00+ | Canonical stack korunur; hiçbir framework kurulmadı | Master §5; phase_00_plan §3 | YES as requirements |
| uv; Celery + Redis | 00 / 03 | Plan önerisi; uv kurulu doğrulanmadı, worker executable Phase 3 | phase_00_plan §3/T02/T03 | PROPOSED, ADR not yet created |
| Phase 0 dört servis / business table yok / auth öncesi public kapalı | 00 | Phase kapsamını büyütmeden güvenli foundation | phase_00_plan §2–4 | YES as plan |
| Decimal/NUMERIC; deterministic engines; AI yalnız açıklama | Tüm | Sayısal doğruluk ve decision authority sınırı | Master §§7, 14, 17 | YES |
| Root Phase 0 planı canonical; mutable handoff ayrı | 00+ | Kopya plan/state otoritesi oluşturmamak | Kullanıcı talebi; ROADMAP/phase_00_plan | YES |
| Handoff-only; açık sonraki talimat gelmeden implementation yok | Bu checkpoint | Son kullanıcı mesajı verify-only | §18/§28 | YES until explicit start instruction |
| Canonical GitHub remote = Menesgumus/borsa-takip (SSH); default branch main | 00+ | Kullanıcı bildirimi + API doğrulama; local origin T04'te | User message 2026-09-05; V20–V22 | YES |
| Phase checkpoint push to GitHub main when Phase READY | 00+ | User GitHub discipline; Phase READY değilse fake READY yok | User message 2026-09-05 | YES |
| Meaningful small commits at task/phase boundaries; no force push / history rewrite | 00+ | Canonical remote artık gerçek geçmiş | User message 2026-09-05 | YES |

Kararın ayrıntısı ADR'de bulunuyorsa burada tekrar uzun yazılmaz.

---

# 26. PHASE HISTORY

Tamamlanan phase'ler silinmez. Her phase “Phase X'te ne yapıldı?” sorusuna cevap verecek şekilde güncellenir.

## Phase 00 History

**Status:** `NOT_STARTED`

### Goal
Foundation ve quality baseline.

### What was implemented
Uygulama implementation'ı başlamadı; Phase 0 T01–T20 `NOT_STARTED`. Planlama belgeleri mevcut. Bu oturumda (S-02) beş belge tamamen okundu, repository/Git/toolchain/Docker doğrulandı, canonical GitHub remote boş olduğu API+ls-remote ile doğrulandı; yalnız handoff mutable state güncellendi. Foundation feature veya phase exit başarısı değildir.

### Important files
`BORSA_TAKIP_MASTER_SPEC.md` (salt okunur), `ROADMAP.md`, `phase_00_plan.md`, `GAP_ANALYSIS.md`, `AUTONOMOUS_HANDOFF.md` (mutable state). Fingerprint'ler §19'da; application/test/migration dosyası yok. Canonical remote: `https://github.com/Menesgumus/borsa-takip` (empty).

### Database changes
Yok.

### API changes
Yok.

### Frontend changes
Yok.

### Security changes
Kodda güvenlik kontrolü uygulanmadı. Plan T06/T14 ve public gate'ler korundu; state'e credential/secret yazılmadı. Security scan çalıştırılmadı. Immutable protocol metnine dokunulmadığının belge hash kontrolü security scan'in yerine geçmez.

### Performance work
Ölçüm yok. Empty bundle/health baseline T15 ve master bütçeleri plan olarak korunuyor. Docker CLI sürüm kontrolü performans testi değildir.

### Mobile work
UI yok, automated viewport/a11y/manual QA çalıştırılmadı. Plan T13/T19 yedi viewport ve gerçek inceleme kapsamını tanımlıyor.

### Tests added
Yok.

### Tests actually executed
App testi sayısı 0; suite/pass/fail sayıları null. Bu oturum salt okunur belge/Git/CLI/Docker/GitHub kontrolleri V00–V23. Uygulama suite'i yerine PASS denmez.

### Problems encountered
Önceki Docker/npm kayıtları korunur. Bu oturumda npm çalıştı; Node/Python/shell sürümleri önceki handoff'tan saptı (HD-003–006). Canonical GitHub remote boş ve local Git yok (HD-007). uv PATH'te yok. Kod olmadığı için implementation bug yoktur.

### What was not done / remaining work
Git init/commit/push, `origin` bind, dependency install, scaffold, API/UI, migration, container startup, test/build/scan/benchmark/mobile QA ve completion yapılmadı. Phase 0 T01–T20 bekliyor.

### Deferred
Phase planındaki scope dışı alanlar.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Yok.


---

## Phase 01 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 02 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 03 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 04 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 05 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 06 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 07 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 08 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 09 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 10 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 11 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 12 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 13 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 14 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 15 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 16 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 17 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 18 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 19 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

## Phase 20 History

**Status:** `NOT_STARTED`

### Goal
ROADMAP ve ilgili phase planından doldurulacak.

### What was implemented
Henüz yok.

### Important files
Henüz yok.

### Database changes
Henüz yok.

### API changes
Henüz yok.

### Frontend changes
Henüz yok.

### Security changes
Henüz yok.

### Performance work
Henüz yok.

### Mobile work
Henüz yok.

### Tests added
Henüz yok.

### Tests actually executed
Henüz yok.

### Problems encountered
Henüz yok.

### Deferred
Henüz yok.

### Completion report
Henüz yok.

### Final status
`NOT_STARTED`

### Final commit
Henüz yok.


---

# 27. SESSION LOG

Her otonom çalışma oturumu için kısa fakat yeterli kayıt tutulur.

Format:

```markdown
## Session S-YYYYMMDD-NN

Model:
Started:
Ended:
Start commit:
End commit:
Phase:
Tasks touched:

### Goal
...

### Completed
- ...

### Verification
- command / result

### Failed attempts worth knowing
- ...

### Important decisions
- ...

### Working tree at handoff
...

### Next exact action
...

### Context for next AI
...
```

## Kurallar
- Her küçük komut için session log satırı ekleme.
- Yeni ajanı yanlış yola sokabilecek önemli başarısız denemeleri kaydet.
- Başarısız denemeden neden vazgeçildiğini kısa yaz.
- Hidden chain-of-thought yazma.
- Teknik karar sonucunu ve kanıtını yaz.

## Session S-20260905-01 — Handoff protokolünü devreye alma

- **Model:** Codex; exact model identifier not exposed.
- **Date:** 2026-09-05. Kesin oturum başlangıç saati kaydedilmedi; salt okunur komut grubu H01–H09 başlangıcı `18:37:52Z`. Checkpoint zamanı §18'de; son belge kontrolü H14'tedir.
- **Start/end commit:** null / null — Git deposu yok.
- **Phase / tasks:** 00 / T01 referans; T01–T20 başlatılmadı. Çalışma türü yalnız handoff bookkeeping.

### Goal
Kullanıcının sağladığı handoff dosyasının tamamını okumak, Master/ROADMAP/Phase 0 planı/gerçek durumla karşılaştırmak ve yalnız Mutable Project State'i güncellemek.

### Completed
- Handoff girdi dosyası 2.099 satırın tamamı okundu; immutable protocol (0–17) sınırı ve §31–END hash'i kaydedildi.
- Değişmemiş master hash'i ve mevcut plan/roadmap/GAP fingerprint'leri doğrulandı; repository beş Markdown dosyası, alt dizin yok.
- Git branch/SHA/status/remote, migration/test/config dosyaları, CLI ve Docker kontrolleri gerçek exit code'larıyla kaydedildi.
- Current Project State, Active Task, Verification Matrix, issues/drift, Phase 00 History ve NEXT AI block güncellendi. Diğer 20 fazın mevcut NOT_STARTED history kayıtları korunuyor.

### Verification
H00–H13, §22. App test/build/scan/CI/migration/benchmark/mobile işlemlerinin tümü NOT_EXECUTED. H14 yalnız belge hash/kapsam/başlık/status/next-action kontrolüdür.

### Failed attempts worth knowing
- H01–H04 exit 1: Git repository yok. Çalışma ağacı temiz/kirli veya branch adı uydurulmadı; Git kurulmadı.
- H13 exit 1: npm MODULE_NOT_FOUND; daha önceki GAP E07 hatası silinmedi. Bu tur package manager onarımı yapılmadı.
- Docker'ın geçmiş E10/E11 başarısızlıkları ve E12/H10 çözümü korundu. Compose CLI'daki config permission warning H12'de hâlâ mevcut; onaylı daemon sorgusu başarılı.

### Important decisions
Ekli otonom directive de okundu; son kullanıcı talebindeki “henüz implementation başlatma” sınırı geçerli. Immutable protokol yeniden yazılmadı. `AUTONOMOUS_HANDOFF.md` tek operasyonel hafıza; ekli metinde önerilen ayrı `docs/AUTONOMOUS_STATE.md` oluşturulmadı. Ürün/stack/phase gate kararı değiştirilmedi.

### Working tree at handoff
NOT_A_GIT_REPOSITORY. Bu oturumda yalnız `AUTONOMOUS_HANDOFF.md` mutable bölümü değiştirildi; diğer dört MD korunur. Scaffold/test/migration/commit/container yaratılmadı.

### Next exact action
§28 `resume.next_exact_action` tek canonical eylemdir. Başlama yetkisi henüz verilmedi; bu checkpoint kendi başına T01'i tetiklemez.

### Context for next AI
Eski sohbet gerekmez: §19 mevcut fingerprints ve Git yokluğunu; §22 gerçek komutları; §23 eski sorun/drift çözümlerini; §28 kesin eylemi ve başlatma önkoşulunu içerir. Yeni user instruction gelirse execution scope'u ona göre güncelle, kanıt olmadan status yükseltme.

## Session S-20260905-02 — GitHub remote alignment + verify-only handoff

- **Model:** Composer (Cursor Auto); exact model identifier not exposed.
- **Date:** 2026-09-05. Verify window ~`18:53:57Z`–`18:55:13Z` UTC.
- **Start/end commit:** null / null — local Git deposu yok.
- **Phase / tasks:** 00 / T01 referans; T01–T20 başlatılmadı. Çalışma türü: belge okuma + repository/GitHub doğrulama + mutable handoff update.

### Goal
Master → ROADMAP → phase_00_plan → AUTONOMOUS_HANDOFF → GAP sırasıyla tam okuma; repository gerçeğini doğrula; canonical GitHub remote'u hizala/kaydet; implementation başlatmadan hazır olduğunu bildir.

### Completed
- Beş proje belgesi tamamen okundu; Master hash değişmedi.
- Local Git yokluğu, beş-MD envanter, migration/test/Compose yokluğu doğrulandı.
- Canonical remote `Menesgumus/borsa-takip` API + ls-remote ile EXISTS_EMPTY / default `main` doğrulandı.
- Toolchain drift HD-003–007 kaydedildi; Docker daemon 28.4.0 yeniden doğrulandı.
- Mutable handoff Git/GitHub alanları ve session/resume güncellendi. Protocol dokunulmadı. `git init` / `remote add` / scaffold yapılmadı.

### Verification
V00–V23, §22. App test/build/scan/CI/migration/benchmark/mobile: NOT_EXECUTED.

### Failed attempts worth knowing
- V01–V04: local not a git repository — origin eklenemez; sessizce git init yapılmadı.
- V08: uv yok.
- `gh` CLI yok — REST + git ls-remote yeterli kanıt sağladı.
- İlk `docker info --format` denemesinde PowerShell quoting kaynaklı exit 125 görüldü; düzgün quoting ile V10 exit 0 / 28.4.0.

### Important decisions
Implementation hold devam. Canonical remote kullanıcı bildirimi + canlı doğrulama. Local `origin` T04'e ertelendi. Phase 00 / T01 `NOT_STARTED` korundu.

### Working tree at handoff
NOT_A_GIT_REPOSITORY. Yalnız `AUTONOMOUS_HANDOFF.md` mutable bölümü değişti.

### Next exact action
§28 `resume.next_exact_action`. Explicit implementation talimatı bekleniyor.

### Context for next AI
Başlangıç: Phase 00 T01. Remote URL hazır; local Git yok. Toolchain sürümlerini T02'de yeniden doğrula (HD-003/004). Push yok; remote boş.

---

# 28. NEXT AI — IMMEDIATE RESUME BLOCK

Bu bölüm **her checkpoint'te güncellenmelidir**.

```yaml
resume:
  current_phase: "00"
  phase_status: "IN_PROGRESS"
  current_task: "T07"
  task_status: "IN_PROGRESS"
  active_phase_plan: "phase_00_plan.md"
  execution_hold: "NONE"
  start_condition: "NONE"
  handoff_checkpoint: "S-20260905-02"
  last_verified_commit: null
  last_known_good_commit: null
  last_pushed_commit: null
  working_tree: "NOT_A_GIT_REPOSITORY"
  remote_origin_local: null
  canonical_remote: "git@github.com:Menesgumus/borsa-takip.git"
  remote_sync_status: "LOCAL_GIT_ABSENT; REMOTE_EXISTS_EMPTY; default_branch=main"
  related_phase_completion: null

  must_read:
    - "BORSA_TAKIP_MASTER_SPEC.md"
    - "ROADMAP.md"
    - "phase_00_plan.md"
    - "Relevant phase completion if it exists; none exists at this checkpoint."
    - "AUTONOMOUS_HANDOFF.md"
    - "GAP_ANALYSIS.md"
    - "Actual repository code/test/migration/Git state; currently no implementation."

  verify_before_editing:
    - "Master hash against section 19; if changed, read the complete new master."
    - "git status --short --branch, git branch --show-current, git rev-parse HEAD, git remote -v; absence is not a clean working tree."
    - "If Git still absent at implementation start: init only under T04 after T01–T03 as planned; then git branch -M main; git remote add origin git@github.com:Menesgumus/borsa-takip.git (only if origin missing)."
    - "Repository inventory and lockfiles; do not assume the five-file checkpoint is still current."
    - "Migration head if Alembic exists; currently absent."
    - "Service/container state with project scope; daemon connectivity alone is not app startup."
    - "Critical targeted/smoke tests if code and test environment now exist; currently NOT_EXECUTED because absent."
    - "Check old failures/blockers/HD-* for drift; record HANDOFF DRIFT without erasing previous evidence."
    - "Before any push: secret scan, .gitignore/.env exclusion, lockfiles, Master Spec unchanged, no broken build/tests."

  next_exact_action: >-
    T07 - PostgreSQL ve Alembic baseline uygulamasını tamamla.

  stop_conditions:
    - "No explicit implementation start instruction: finish verify-only work, do not start T01."
    - "Real EXTERNAL_BLOCKER"
    - "Real PRODUCT_BLOCKER"
    - "For Phase 01 onward: previous phase gate not READY. Phase 00 has no predecessor."

  do_not_do:
    - "Do not restart planning from scratch."
    - "Do not skip phase gates."
    - "Do not mark unexecuted checks as PASS."
    - "Do not modify Master Spec product decisions."
    - "Do not treat handoff bookkeeping as DONE_VERIFIED implementation."
    - "Do not create Git/scaffold/dependencies/containers until implementation is explicitly started."
    - "Do not change immutable protocol sections or erase historical failures."
    - "Do not force-push, rewrite history, or push secrets/.env."
    - "Do not invent a second origin; align to Menesgumus/borsa-takip only."
```

---

# 29. QUOTA / CONTEXT EMERGENCY CHECKPOINT TEMPLATE

**Current emergency state:** INACTIVE. Kota/context nedeniyle yarım bırakılmış implementation, migration veya kırık test suite yok. Bu oturum normal handoff-only checkpoint'inde durur; §18/§21/§22/§26/§27/§28 gerçek durumu taşır. Aşağıdaki şablon doldurulmuş bir emergency kaydı değildir.

Kota bitecekse aşağıdaki block mutlaka doldurulur.

```markdown
# EMERGENCY HANDOFF CHECKPOINT

Timestamp:
Model:
Reason: QUOTA / CONTEXT / SESSION END

## Current phase
Phase XX

## Current task
TXX — ...

Status:
IN_PROGRESS / DONE_VERIFIED / FAILED_NEEDS_FIX

## Last completed safe point
...

## Files currently being worked on
- ...

## Working tree
Clean / Dirty

## If dirty, why?
...

## Last command executed
...

Exit code:
...

## Last passing verification
...

## Current failure
...

## Root cause known?
YES / NO

## If known
...

## Exact next command/action
...

## DO NOT
- ...
```

Yeni AI önce bu emergency block'u okur; sonra repository ile doğrular.

---

# 30. HANDOFF COMPLETENESS CHECK

Oturum bitmeden:

- [x] Current phase doğru: 00, NOT_STARTED
- [x] Current task doğru: T01, implementation oturumu henüz başlamadı
- [x] Task status doğru: NOT_STARTED; DONE_VERIFIED görev yok
- [x] Current commit doğru: null; local Git yok (V03)
- [x] Working tree doğru: NOT_A_GIT_REPOSITORY
- [x] Canonical remote kaydedildi: Menesgumus/borsa-takip EXISTS_EMPTY; local origin unbound
- [x] Last pushed / phase checkpoint / remote sync status alanları güncel
- [x] Son test sonuçları güncel: uygulama testleri NOT_EXECUTED, executed 0
- [x] Migration durumu: yok; head null
- [x] API/UI durumu: yok
- [x] Blocker/önkoşul ve HANDOFF DRIFT (HD-003–007) kaydedilmiş
- [x] Phase 00 History güncellenmiş; 01–20 NOT_STARTED korunmuş
- [x] Session S-20260905-02 logu eklenmiş
- [x] NEXT AI resume block güncellenmiş; explicit start önkoşulu var
- [x] Tek canonical next_exact_action: T01 master hash karşılaştırması
- [x] Secret değeri yazılmadı; scanner çalıştırıldığı iddia edilmedi
- [x] Çalıştırılmamış uygulama kontrolü PASS yazılmamış
- [x] Master Spec / ROADMAP / plan / GAP / immutable protocol korunmuş
- [x] git init / remote add / push / scaffold yapılmadı

**Checkpoint sonucu:** Verify + GitHub alignment handoff tamam. Implementation başlatılmadı; Phase 0 READY değildir. Sıradaki açık autonomous implementation talimatı Phase 00 / T01'den başlamalıdır.

---

# 31. PHASE READY SONRASI HANDOFF İŞLEMİ

Bir phase READY olduğunda:

1. Full quality gate tamamlanır.
2. Completion report üretilir.
3. Completion report audit edilir.
4. ROADMAP statüsü güncellenir.
5. GAP gerekiyorsa güncellenir.
6. Bu dosyada Phase History tamamlanır.
7. Phase final commit SHA yazılır.
8. NEXT AI block sonraki phase planlamasına taşınır.
9. Sonraki phase planı oluşturulur/audit edilir.
10. Otonom directive izin veriyorsa implementasyona devam edilir.

---

# 32. PHASE NOT READY SONRASI HANDOFF İŞLEMİ

Phase NOT READY ise:

1. FAIL gate'ler açıkça listelenir.
2. Fixable olanlar task olarak kaydedilir.
3. Root cause biliniyorsa yazılır.
4. Next exact action ilk fix task'ı olur.
5. Phase status READY yapılmaz.
6. Sonraki phase'e geçilmez.

External blocker varsa `PHASE_XX_NOT_READY_EXTERNAL_BLOCKER` kullanılır.

---

# 33. FINAL PROJECT HANDOFF — PHASE 20

Phase 20 tamamlandığında final state şunları açıkça ayırmalıdır:

```text
TECHNICAL BUILD STATUS
PUBLIC / COMMERCIAL RELEASE STATUS
```

Teknik sistem tamamlanmış olsa bile BIST lisansı, yatırım danışmanlığı/compliance, dış sağlayıcı sözleşmeleri, production secret/infra veya public release security gate eksikse public release READY yazılmaz.

---

# 34. SON TALİMAT

Bu dosya bir günlük veya sohbet özeti değildir.

Bu dosya:

> **başka bir AI'nın repository'yi güvenli, hızlı ve deterministik biçimde devralmasını sağlayan operasyonel hafızadır.**

Her güncellemede şu testi uygula:

> “Ben şimdi tamamen farklı bir model olsaydım ve önceki konuşmaları hiç görmemiş olsaydım, sadece Master Spec + Roadmap + aktif phase planı + bu dosya + repository ile kaldığım yerden güvenle devam edebilir miydim?”

Cevap **hayır** ise handoff eksiktir.

---

# END OF AUTONOMOUS HANDOFF PROTOCOL
