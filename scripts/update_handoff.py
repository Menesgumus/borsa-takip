import re

with open("AUTONOMOUS_HANDOFF.md", "r", encoding="utf-8") as f:
    content = f.read()

# Update Project Identity
content = re.sub(r'current_phase: "00"\ncurrent_phase_status: "NOT_STARTED"\ncurrent_task: "T01"\ncurrent_task_status: "NOT_STARTED"',
                 'current_phase: "00"\ncurrent_phase_status: "IN_PROGRESS"\ncurrent_task: "T07"\ncurrent_task_status: "IN_PROGRESS"', content)

content = re.sub(r'current_activity: "GITHUB_REMOTE_ALIGNMENT_HANDOFF"\nimplementation_started: false\nexecution_hold: "USER_REQUEST_VERIFY_ONLY_NO_IMPLEMENTATION"',
                 'current_activity: "IMPLEMENTING_PHASE_00"\nimplementation_started: true\nexecution_hold: "NONE"', content)

# Update Repository Snapshot
content = re.sub(r'git:\n  initialized: false\n  current_branch: null\n  current_commit: null',
                 'git:\n  initialized: true\n  current_branch: "main"\n  current_commit: "8657ddb"', content)

content = re.sub(r'working_tree: "NOT_A_GIT_REPOSITORY; clean/dirty not applicable"',
                 'working_tree: "clean"', content)

# Update Task Statuses in Phase Summary
content = re.sub(r'Status:\*\* `NOT_STARTED`', '**Status:** `IN_PROGRESS`', content, count=1)
content = re.sub(r'Current task\n`T01 — Mevcut durumu tekrar doğrula ve scope\'u sabitle`', 'Current task\n`T07 — PostgreSQL / Alembic baseline`', content)
content = re.sub(r'### Completed tasks\nPhase 0 implementation görevi tamamlanmadı\..*', '### Completed tasks\nT01, T02, T03, T04, T05, T06 tamamlandı. Git init yapıldı, uv kuruldu, ADR\'ler yazıldı, backend app temeli atıldı.', content)
content = re.sub(r'### In-progress tasks\nHenüz yok\.', '### In-progress tasks\nT07', content)
content = re.sub(r'### Remaining tasks\nPhase planındaki T01–T20\.', '### Remaining tasks\nT08-T20', content)

# Update Next AI Resume Block
content = re.sub(r'current_task: "T01"', 'current_task: "T07"', content)
content = re.sub(r'task_status: "NOT_STARTED"', 'task_status: "IN_PROGRESS"', content)
content = re.sub(r'phase_status: "NOT_STARTED"', 'phase_status: "IN_PROGRESS"', content)
content = re.sub(r'execution_hold: "USER_REQUEST_VERIFY_ONLY_NO_IMPLEMENTATION"\n  start_condition: "A new explicit user instruction starts autonomous implementation; none has been issued for this checkpoint beyond verify/handoff update."',
                 'execution_hold: "NONE"\n  start_condition: "NONE"', content)

content = re.sub(r'next_exact_action: >-[\s\S]*?stop_conditions:', 'next_exact_action: >-\n    T07 - PostgreSQL ve Alembic baseline uygulamasını tamamla.\n\n  stop_conditions:', content)

with open("AUTONOMOUS_HANDOFF.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated AUTONOMOUS_HANDOFF.md")
