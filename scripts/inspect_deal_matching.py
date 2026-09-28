with open('scripts/parser_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2050, 2220):
    print(f"{i+1}: {ascii(lines[i])}")
