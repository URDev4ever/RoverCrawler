<h1 align="center">RoverCrawler 🕷️🚀</h1>
<p align="center">
  🇺🇸 <a href="README.md"><b>English</b></a> |
  🇪🇸 <b>Español</b>
</p>
<p align="center">
  <img width="498" height="214" alt="image-removebg-preview (43)" src="https://github.com/user-attachments/assets/ae86bcac-179c-4b62-add8-79dc082d94de" />
</p>
<h2 align="center">Crawler web de un solo archivo para mapear la estructura de sitios</h2>

<h3 align="center">
  RoverCrawler es un crawler web en Python de un solo archivo, diseñado para explorar sitios web y generar una representación en forma de árbol de su estructura.
  Soporta modo interactivo, uso por línea de comandos, salida en árbol con colores, limitación de velocidad y exportación de resultados — todo sin necesidad de una estructura de proyecto externa.
</h3>

> Construido para claridad, portabilidad y crawling controlado.

---

## ✨ Características

* 📄 **Un solo archivo Python** (`rovercrawler.py`)
* 🌳 **Mapeo de estructura del sitio basado en árbol** (salida por defecto)
* 🎨 **Salida con colores sutiles** (multiplataforma mediante `colorama`)
* 🧭 **Modo de configuración interactivo**
* 🖥️ **Soporte completo de CLI (argparse)**
* 🔍 **Crawling restringido al dominio** (enlaces externos opcionales)
* 🛑 **Límites de seguridad** (profundidad máxima y páginas máximas)
* ⏱️ **Limitación de velocidad** para evitar sobrecargar servidores
* 📊 **Estadísticas del rastreo** (páginas, enlaces, errores, velocidad)
* 📦 **Exportación de resultados** a:

  * JSON
  * Texto plano
* 💻 **Multiplataforma** (Windows / Linux / macOS)

---

## 🖥️ Instalación

Simplemente cloná este repositorio: (NECESITÁS tener `git` instalado para poder clonarlo)

```bash
git clone https://github.com/URDev4ever/RoverCrawler.git
cd RoverCrawler/
```

---

## 📦 Requisitos

Python **3.8+** recomendado.

Dependencias externas (instalar una sola vez):

```bash
pip install requests beautifulsoup4 colorama
```

---

## 🚀 Uso

### 1️⃣ Modo Interactivo (recomendado para escaneos manuales)

Simplemente ejecutá el script sin argumentos:

```bash
python rovercrawler.py
```

Se te pedirá configurar:

* URL objetivo
* Profundidad máxima de rastreo
* Máximo de páginas
* Modo detallado (verbose)
* Seguimiento de enlaces externos

---

### 2️⃣ Modo Línea de Comandos (CLI)

Uso básico:

```bash
python rovercrawler.py https://example.com
```

Con opciones:

```bash
python rovercrawler.py https://example.com -d 4 -p 200 -v --external
```

---

## ⚙️ Opciones de Línea de Comandos

| Opción               | Descripción                                 |
| -------------------- | ------------------------------------------- |
| `url`                | URL objetivo a rastrear                     |
| `-d`, `--depth`      | Profundidad máxima de rastreo               |
| `-p`, `--pages`      | Máximo de páginas a rastrear                |
| `-v`, `--verbose`    | Habilitar salida detallada                  |
| `-e`, `--external`   | Seguir enlaces externos (fuera del dominio) |
| `-t`, `--timeout`    | Tiempo de espera de solicitudes (segundos)  |
| `--export-json FILE` | Exportar resultados como JSON               |
| `--export-txt FILE`  | Exportar resultados como texto plano        |
| `--no-banner`        | Desactivar banner ASCII                     |
| `--no-colors`        | Desactivar salida con colores               |

---

## 🌳 Ejemplo de Salida (Vista en Árbol)

```
/
├── /about
│   ├── /team
│   └── /history
├── /blog
│   ├── /post-1
│   └── /post-2
└── /contact
```

* Los enlaces internos se muestran en **cian**
* Los enlaces externos (si están habilitados) se marcan y colorean en **amarillo**
* La salida respeta la profundidad y evita bucles

---

## 📤 Exportación de Resultados

### Exportar a JSON

```bash
python rovercrawler.py https://example.com --export-json results.json
```

El JSON preserva la **estructura en árbol**, ideal para post-procesamiento o visualización.

---

### Exportar a Texto Plano

```bash
python rovercrawler.py https://example.com --export-txt results.txt
```

* Los colores se eliminan automáticamente
* Incluye metadatos y estadísticas del rastreo

---

## 📊 Estadísticas del Rastreo

Al final de cada rastreo, RoverCrawler informa:

* Páginas rastreadas
* Enlaces descubiertos
* Errores encontrados
* Tiempo total transcurrido
* Velocidad promedio de rastreo (páginas/seg)

Ejemplo:

```
Pages crawled: 87
Links found:  412
Errors:       2
Time elapsed: 12.4 seconds
Avg speed:    7.0 pages/sec
```

---

## 🧠 Notas Técnicas

* Usa **BFS (Breadth-First Search / Búsqueda en Anchura)** para una profundidad de árbol predecible
* Normaliza URLs (esquema, dominio, ruta)
* Omite extensiones binarias/estáticas comunes
* Ignora fragmentos, mailto, javascript y enlaces tel
* Aplica limitación de velocidad por solicitud
* Usa una única `requests.Session()` para mayor eficiencia

---

## ⚠️ Descargo de Responsabilidad

RoverCrawler está destinado a **fines educativos, de investigación y pruebas legítimas**.
Respetá siempre:

* Los términos de servicio del sitio web
* `robots.txt`
* Las leyes locales aplicables

Vos sos responsable del uso que le des a esta herramienta.

---

## ⭐ Contribuir

Las pull requests son bienvenidas si:

* Mejoran la confiabilidad del crawling, la normalización de URLs o la precisión del árbol estructural sin introducir comportamientos agresivos
* Mejoran el rendimiento, la lógica de rate limiting o las capacidades de exportación manteniendo el proyecto en un solo archivo y limpio
* Mantienen la filosofía de crawling controlado y respetuoso (sin explotación, sin técnicas de bypass, sin funciones de evasión)

---

Hecho con <3 por URDev.
