"""
Script para adaptar el notebook de OpenAI a Nebius
Ejecuta este script para reemplazar automáticamente todas las referencias
"""

import json
import re

# Leer el notebook
with open('backtothebasics_openai.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Reemplazos a realizar
replacements = [
    # Reemplazar client = OpenAI() por get_nebius_client()
    (r'client = OpenAI\(\s*\)', 'client = get_nebius_client()'),
    (r'client = OpenAI\(\)', 'client = get_nebius_client()'),
    
    # Reemplazar modelos GPT por NEBUS_MODEL
    (r'model="gpt-[^"]*"', 'model=NEBUS_MODEL'),
    (r"model='gpt-[^']*'", "model=NEBUS_MODEL"),
    (r'model = "gpt-[^"]*"', 'model = NEBUS_MODEL'),
    (r"model = 'gpt-[^']*'", "model = NEBUS_MODEL"),
]

# Procesar cada celda
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Aplicar reemplazos
        for pattern, replacement in replacements:
            source = re.sub(pattern, replacement, source)
        
        # Actualizar la celda
        cell['source'] = source.split('\n')

# Guardar el notebook actualizado
with open('backtothebasics_nebius.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Notebook adaptado guardado como 'backtothebasics_nebius.ipynb'")





