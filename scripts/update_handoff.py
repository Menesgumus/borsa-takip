import re

with open("AUTONOMOUS_HANDOFF.md", "r", encoding="utf-8") as f:
    content = f.read()

# Update Task Statuses in Phase Summary
content = re.sub(r'Current task\n`T07 — PostgreSQL / Alembic baseline`', 'Current task\n`T09 — Health, hata envelope ve correlation logging`', content)
content = re.sub(r'T01, T02, T03, T04, T05, T06 tamamlandı. Git init yapıldı, uv kuruldu, ADR\'ler yazıldı, backend app temeli atıldı.', 'T01, T02, T03, T04, T05, T06, T07, T08 tamamlandı. DB/Alembic baseline, Redis lifecycle eklendi.', content)
content = re.sub(r'### In-progress tasks\nT07', '### In-progress tasks\nT09', content)
content = re.sub(r'### Remaining tasks\nT08-T20', '### Remaining tasks\nT09-T20', content)

# Update Next AI Resume Block
content = re.sub(r'current_task: "T07"', 'current_task: "T09"', content)
content = re.sub(r'last_verified_commit: null', 'last_verified_commit: "6d37959"', content)
content = re.sub(r'last_known_good_commit: null', 'last_known_good_commit: "6d37959"', content)
content = re.sub(r'next_exact_action: >-\n    T07 - PostgreSQL ve Alembic baseline uygulamasını tamamla.\n\n', 'next_exact_action: >-\n    T09 - Health, hata envelope ve correlation logging uygulamasını tamamla.\n\n', content)
content = re.sub(r'current_commit: "8657ddb"', 'current_commit: "6d37959"', content)

with open("AUTONOMOUS_HANDOFF.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated AUTONOMOUS_HANDOFF.md")
