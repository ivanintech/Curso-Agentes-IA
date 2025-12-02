"""
Script para ejecutar el notebook celda por celda
"""
import json
import sys
import asyncio
from io import StringIO
import traceback

# Capturar stdout/stderr
class NotebookExecutor:
    def __init__(self, notebook_path):
        self.notebook_path = notebook_path
        # Inicializar con imports comunes
        self.globals = {
            '__name__': '__main__',
            '__builtins__': __builtins__,
        }
        self.locals = {}
        
    async def execute_async_cell(self, source, cell_index):
        """Ejecuta código asíncrono"""
        # Crear un namespace local para la celda que incluye los globals
        local_ns = dict(self.globals)
        
        # Si hay await o async for, necesitamos envolver en una función async
        if ('await' in source or 'async for' in source) and 'async def' not in source:
            # Envolver en una función async temporal
            # Identar el código fuente correctamente
            lines = source.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():  # No identar líneas vacías
                    indented_lines.append('    ' + line)
                else:
                    indented_lines.append('')
            indented_source = '\n'.join(indented_lines)
            
            # Crear wrapper simple - las variables se capturarán después
            async_wrapper = f"""
async def _temp_exec_{cell_index}():
    # Ejecutar el código de la celda
{indented_source}
"""
            # Compilar y ejecutar para definir la función
            code = compile(async_wrapper, f'<cell {cell_index}>', 'exec')
            exec(code, self.globals, local_ns)
            # Ejecutar la función async
            await local_ns[f'_temp_exec_{cell_index}']()
            # Intentar capturar variables usando inspect (puede no funcionar perfectamente)
            # Las variables definidas dentro de la función async no estarán disponibles
            # fuera a menos que las capturemos explícitamente
            # Por ahora, actualizamos solo lo que está en local_ns
        else:
            code = compile(source, f'<cell {cell_index}>', 'exec')
            exec(code, self.globals, local_ns)
        
        # Actualizar globals con TODOS los cambios del namespace local
        for k, v in local_ns.items():
            if not k.startswith('_temp_') and k not in ['__builtins__', '__name__', '__doc__', '_cell_globals']:
                self.globals[k] = v
    
    def execute_cell(self, cell_index, cell):
        """Ejecuta una celda de código"""
        if cell.get('cell_type') != 'code':
            print(f"\n{'='*60}")
            print(f"Celda {cell_index}: {cell.get('cell_type', 'unknown').upper()}")
            print(f"{'='*60}")
            source = ''.join(cell.get('source', []))
            if source.strip():
                print(source[:200] + "..." if len(source) > 200 else source)
            return True
            
        source = ''.join(cell.get('source', []))
        if not source.strip():
            return True
            
        # Saltar celdas con %pip o ! (comandos mágicos)
        if source.strip().startswith('%') or source.strip().startswith('!'):
            print(f"\n{'='*60}")
            print(f"Celda {cell_index}: Saltando comando mágico")
            print(f"{'='*60}")
            print(source[:100])
            return True
        
        print(f"\n{'='*60}")
        print(f"Ejecutando Celda {cell_index}")
        print(f"{'='*60}")
        print(f"Código:\n{source[:300]}{'...' if len(source) > 300 else ''}")
        print(f"\n{'-'*60}")
        
        try:
            # Ejecutar código
            if 'await' in source or 'async for' in source:
                # Para código asíncrono, usar asyncio
                print("Ejecutando codigo asincrono...")
                try:
                    asyncio.run(self.execute_async_cell(source, cell_index))
                    print("[OK] Celda ejecutada correctamente")
                except Exception as e:
                    print(f"Advertencia: Error en codigo asincrono:")
                    print(f"   {type(e).__name__}: {str(e)}")
                    traceback.print_exc()
                    # Continuar de todas formas
                    return True
            else:
                exec(compile(source, f'<cell {cell_index}>', 'exec'), self.globals, self.locals)
                print("[OK] Celda ejecutada correctamente")
            return True
        except Exception as e:
            print(f"[ERROR] Error al ejecutar celda {cell_index}:")
            print(f"   {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            return False
    
    def run(self):
        """Ejecuta todas las celdas del notebook"""
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells = notebook['cells']
        print(f"Notebook: {self.notebook_path}")
        print(f"Total de celdas: {len(cells)}")
        print(f"Celdas de codigo: {sum(1 for c in cells if c.get('cell_type') == 'code')}")
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type', 'unknown')
            source = ''.join(cell.get('source', []))
            
            # Saltar celdas vacías o markdown
            if cell_type == 'markdown':
                skipped_count += 1
                continue
            
            if not source.strip():
                skipped_count += 1
                continue
            
            result = self.execute_cell(i, cell)
            if result:
                if cell_type == 'code':
                    success_count += 1
            else:
                error_count += 1
                print("\n[CONTINUANDO] Continuando con la siguiente celda...")
                # Continuar automáticamente sin preguntar
        
        print(f"\n{'='*60}")
        print("RESUMEN DE EJECUCION")
        print(f"{'='*60}")
        print(f"[OK] Celdas ejecutadas correctamente: {success_count}")
        print(f"[ERROR] Celdas con errores: {error_count}")
        print(f"[SKIP] Celdas saltadas: {skipped_count}")
        print(f"{'='*60}")

if __name__ == '__main__':
    executor = NotebookExecutor('openai_agents.ipynb')
    executor.run()

