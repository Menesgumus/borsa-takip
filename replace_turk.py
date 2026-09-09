import os

filepath = 'backend/app/services/ai_mentor.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("Goreceli Guc", "Göreceli Güç")
content = content.replace("gostergesi", "göstergesi")
content = content.replace("alis", "alış")
content = content.replace("satis", "satış")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
