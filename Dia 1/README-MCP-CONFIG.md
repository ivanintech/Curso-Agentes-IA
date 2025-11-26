# Configuración de Servidores MCP

Este proyecto incluye dos servidores MCP:

1. **Google Image Search MCP** - Para buscar, descargar y analizar imágenes
2. **Playwright MCP** - Para automatización de navegadores y scraping web

## Configuración en Cursor

Para usar estos servidores MCP en Cursor, necesitas añadir la configuración al archivo de configuración de MCP de Cursor.

### Ubicación del archivo de configuración

El archivo de configuración de MCP en Cursor generalmente se encuentra en:
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

### Configuración

Abre el archivo de configuración de MCP de Cursor y añade o actualiza con el siguiente contenido:

```json
{
  "mcpServers": {
    "search-images": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\ivanc\\Documents\\CursoAgentes\\google-image-search-mcp-python",
        "run",
        "main.py"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

### Requisitos previos

#### Para Google Image Search MCP:
1. Instalar [uv](https://github.com/astral-sh/uv)
2. Crear un archivo `.env` en `google-image-search-mcp-python/` con tu clave de SerpAPI:
   ```
   SERP_API_KEY=tu_clave_aqui
   ```
3. Instalar dependencias:
   ```powershell
   cd google-image-search-mcp-python
   uv venv
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

#### Para Playwright MCP:
1. Tener Node.js instalado
2. El servidor se instalará automáticamente la primera vez que se use mediante `npx`

### Verificación

Después de configurar, reinicia Cursor y verifica que ambos servidores MCP estén disponibles en la configuración de MCP.

## Herramientas disponibles

### Google Image Search MCP:
- `search_images_tool`: Buscar imágenes usando Google Image Search
- `download_image_tool`: Descargar imágenes a un directorio local
- `analyze_images_tool`: Analizar resultados de búsqueda de imágenes

### Playwright MCP:
- Navegación web
- Captura de pantallas
- Interacción con elementos de la página
- Ejecución de JavaScript
- Generación de código de pruebas
- Y más herramientas de automatización del navegador





