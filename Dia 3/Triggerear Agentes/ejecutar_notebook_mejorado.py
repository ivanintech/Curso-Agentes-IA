"""
Script mejorado para ejecutar el notebook celda por celda
Nota: Las celdas con código async pueden tener limitaciones en la propagación de variables
"""
import json
import sys
import asyncio
import traceback

class NotebookExecutor:
    def __init__(self, notebook_path):
        self.notebook_path = notebook_path
        self.globals = {
            '__name__': '__main__',
            '__builtins__': __builtins__,
        }
        self.locals = {}
        self.errors = []
        
    async def execute_async_cell(self, source, cell_index):
        """Ejecuta código asíncrono"""
        local_ns = dict(self.globals)
        
        if ('await' in source or 'async for' in source) and 'async def' not in source:
            # Envolver en función async y pasar variables globales
            lines = source.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():
                    indented_lines.append('    ' + line)
                else:
                    indented_lines.append('')
            indented_source = '\n'.join(indented_lines)
            
            # Crear código que inyecte todas las variables globales en el scope local
            # Usar una lista de nombres de variables válidas
            valid_vars = [k for k in self.globals.keys() 
                         if not k.startswith('_') or k in ['__name__', '__builtins__', '__doc__']]
            globals_inject = '\n'.join([f'    {k} = _cell_globals.get("{k}")' for k in valid_vars])
            
            # Envolver el código en una función async que use el namespace global
            # Identar el código fuente
            lines = source.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():
                    indented_lines.append('    ' + line)
                else:
                    indented_lines.append('')
            indented_source = '\n'.join(indented_lines)
            
            # Envolver el código en una función async
            # Identar el código fuente
            lines = source.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():
                    indented_lines.append('    ' + line)
                else:
                    indented_lines.append('')
            indented_source = '\n'.join(indented_lines)
            
            # Envolver el código en una función async que use el namespace global
            # Identar el código fuente
            lines = source.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():
                    indented_lines.append('    ' + line)
                else:
                    indented_lines.append('')
            indented_source = '\n'.join(indented_lines)
            
            # Crear función async que ejecute el código usando exec() con el namespace global
            # Usar el código fuente original (sin indentar) para compilarlo
            safe_source = repr(source)  # Código fuente original, no indentado
            async_wrapper = f"""
# Guardar referencia al namespace global
_cell_globals = globals()

async def _temp_exec_{cell_index}():
    # Ejecutar el código usando exec con _cell_globals como namespace de globals
    # Esto hace que todas las variables en _cell_globals estén disponibles
    _code_str = {safe_source}
    exec(compile(_code_str, '<cell_exec>', 'exec'), _cell_globals, locals())
    # Capturar variables definidas y actualizarlas en _cell_globals
    import inspect
    frame = inspect.currentframe()
    if frame:
        for name, value in list(frame.f_locals.items()):
            if not name.startswith('_') or name in ['__name__', '__doc__']:
                _cell_globals[name] = value
"""
            # Compilar y ejecutar usando self.globals como namespace
            code = compile(async_wrapper, f'<cell {cell_index}>', 'exec')
            exec(code, self.globals, local_ns)
            # Ejecutar la función async
            await local_ns[f'_temp_exec_{cell_index}']()
            # Las variables ya están en self.globals (porque _cell_globals apunta a él)
        else:
            code = compile(source, f'<cell {cell_index}>', 'exec')
            exec(code, self.globals, local_ns)
        
        # Actualizar globals
        for k, v in local_ns.items():
            if not k.startswith('_temp_') and k not in ['__builtins__', '__name__', '__doc__', '_cell_globals']:
                self.globals[k] = v
    
    def execute_cell(self, cell_index, cell):
        """Ejecuta una celda de código"""
        if cell.get('cell_type') != 'code':
            return True
            
        source = ''.join(cell.get('source', []))
        if not source.strip():
            return True
            
        if source.strip().startswith('%') or source.strip().startswith('!'):
            return True
        
        print(f"\n{'='*60}")
        print(f"Ejecutando Celda {cell_index}")
        print(f"{'='*60}")
        print(f"Código:\n{source[:200]}{'...' if len(source) > 200 else ''}")
        print(f"\n{'-'*60}")
        
        try:
            if 'await' in source or 'async for' in source:
                print("Ejecutando codigo asincrono...")
                try:
                    asyncio.run(self.execute_async_cell(source, cell_index))
                    print("[OK] Celda ejecutada")
                    return True
                except Exception as e:
                    error_msg = f"Celda {cell_index}: {type(e).__name__}: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"[ERROR] {error_msg}")
                    print("NOTA: Variables definidas en código async pueden no estar disponibles")
                    return False
            else:
                exec(compile(source, f'<cell {cell_index}>', 'exec'), self.globals, self.locals)
                print("[OK] Celda ejecutada")
                return True
        except Exception as e:
            error_msg = f"Celda {cell_index}: {type(e).__name__}: {str(e)}"
            self.errors.append(error_msg)
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            return False
    
    def run(self):
        """Ejecuta todas las celdas del notebook"""
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells = notebook['cells']
        print(f"Notebook: {self.notebook_path}")
        print(f"Total de celdas: {len(cells)}")
        
        success_count = 0
        error_count = 0
        
        for i, cell in enumerate(cells):
            if cell.get('cell_type') != 'code':
                continue
            
            source = ''.join(cell.get('source', []))
            if not source.strip() or source.strip().startswith('%') or source.strip().startswith('!'):
                continue
            
            result = self.execute_cell(i, cell)
            if result:
                success_count += 1
            else:
                error_count += 1
        
        print(f"\n{'='*60}")
        print("RESUMEN")
        print(f"{'='*60}")
        print(f"[OK] Celdas ejecutadas: {success_count}")
        print(f"[ERROR] Celdas con errores: {error_count}")
        if self.errors:
            print(f"\nErrores encontrados:")
            for error in self.errors[:10]:  # Mostrar primeros 10
                print(f"  - {error}")

if __name__ == '__main__':
    executor = NotebookExecutor('openai_agents.ipynb')
    executor.run()

