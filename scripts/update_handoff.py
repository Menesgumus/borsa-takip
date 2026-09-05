import re

with open("AUTONOMOUS_HANDOFF.md", "r", encoding="utf-8") as f:
    content = f.read()

# Update Task Statuses in Phase Summary
content = re.sub(r'Current task\n`T09 — Health, hata envelope ve correlation logging`', 'Current task\n`T11 — Docker images ve Local Compose ayağa kalkışı`', content)
content = re.sub(r'T01, T02, T03, T04, T05, T06, T07, T08 tamamlandı. DB/Alembic baseline, Redis lifecycle eklendi.', 'T01-T10 tamamlandı. Backend logging, health endpoints ve frontend minimal Next.js framework hazır.', content)
content = re.sub(r'### In-progress tasks\nT09', '### In-progress tasks\nT11', content)
content = re.sub(r'### Remaining tasks\nT09-T20', '### Remaining tasks\nT11-T20', content)

# Update Next AI Resume Block
content = re.sub(r'current_task: "T09"', 'current_task: "T11"', content)
content = re.sub(r'last_verified_commit: "6d37959"', 'last_verified_commit: "823bbde"', content)
content = re.sub(r'last_known_good_commit: "6d37959"', 'last_known_good_commit: "823bbde"', content)
content = re.sub(r'next_exact_action: >-\n    T09 - Health, hata envelope ve correlation logging uygulamasını tamamla.\n\n', 'next_exact_action: >-\n    T11 - Dockerfile (frontend, backend) ve docker-compose.yml tamamla, konteynerleştirme yapılarını hazırla.\n\n', content)
content = re.sub(r'current_commit: "6d37959"', 'current_commit: "823bbde"', content)

with open("AUTONOMOUS_HANDOFF.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated AUTONOMOUS_HANDOFF.md for T11")
