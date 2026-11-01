# Termux Package Catalog — English translation design

- **Date:** 2026-11-01
- **Status:** approved (design), pending implementation plan
- **Source project:** Vlsy46 2.0.0 by Lucas Sogaray (MIT)
- **Target:** `GeneralKaos666/termux-pkg-catalog`, version 1.0.0

## 1. Intent

Re-publish Vlsy46 as a new, independent English-language project on the
maintainer's GitHub account. Every line of code, every user-visible string,
every file name, the catalog data keys and the README become English. No
behaviour is added or removed.

**Success criteria**

1. `grep` finds no Spanish word or accented character in `*.py`, `*.json` or
   `README.md`.
2. The program runs identically: same screens, same flow, English text.
3. `catalog.json` holds exactly the same 250 package → command pairs as
   `HEAD:catalogo.json`, re-parented under English category keys.
4. AutoSync downloads from the new repository's `catalog.json`.
5. `python3 -m py_compile` passes for all modules and the program exits
   cleanly when stdin is closed.

## 2. Decisions

| Decision | Choice | Reason |
|---|---|---|
| UI language | English only | Requested; no locale layer, no string table indirection |
| Catalog URL | Clean break, new repo path | New project, not an upgrade of the old one |
| Old installs | Untouched | They point at `lucassogarayDA/Vlsy46/catalogo.json`, which still exists |
| Project name | `termux-pkg-catalog` | Requested |
| Repo owner | `GeneralKaos666` | Maintainer's GitHub account |
| App version | `1.0.0` | Fresh project numbering |
| `catalog_version` | `1` | Fresh catalog history |
| `schema_version` | `1` (unchanged) | Validation rule must keep accepting it |
| Attribution | `LICENSE` keeps the original copyright line | MIT requires keeping the notice |
| Confirmation words | `y` / `yes` | Spanish `s` / `si` / `sí` dropped, not kept as aliases |

## 3. Files

| Now | After |
|---|---|
| `Vlsy46.py` | `termux_pkg_catalog.py` |
| `catalogo.py` | `catalog.py` |
| `catalogo.json` | `catalog.json` |
| `autosync.py` | `autosync.py` (unchanged name) |
| `catalogo_cache.json` (generated at runtime) | `catalog_cache.json` |
| `README.md` | `README.md` (translated, retitled) |
| `LICENSE` | `LICENSE` (copyright notice retained) |
| `docs/specs/…` | this document |

Repository layout after the change:

```text
termux-pkg-catalog/
├── termux_pkg_catalog.py
├── catalog.py
├── catalog.json
├── autosync.py
├── README.md
├── LICENSE
└── docs/specs/2026-11-01-translate-to-english-design.md
```

## 4. Identifier translation

Rule: every identifier, parameter, docstring and local variable is English.
No Spanish token survives, including loop variables. Public names below are
the ones other modules import; locals follow the same rule.

### `termux_pkg_catalog.py`

| Now | After |
|---|---|
| `COLORES`, `COLORES_ACTIVOS` | `COLORS`, `COLORS_ENABLED` |
| `"cian"`, `"verde"`, `"amarillo"`, `"rojo"`, `"gris"`, `"negrita"` | `"cyan"`, `"green"`, `"yellow"`, `"red"`, `"gray"`, `"bold"` |
| `estilo(texto, *colores)` | `style(text, *colors)` |
| `limpiar()` | `clear_screen()` |
| `leer_entrada(mensaje)` | `read_input(message)` |
| `pausar(mensaje)` | `pause(message)` |
| `mostrar_encabezado()` | `show_header()` |
| `buscar_paquetes(consulta)` | `search_packages(query)` |
| `mostrar_busqueda()` | `show_search()` |
| `mostrar_menu()` | `show_menu()` |
| `analizar_comando_instalacion(comando)` | `parse_install_command(command)` |
| `ejecutar_instalacion(comando)` | `run_install(command)` |
| `mostrar_categoria(categoria)` | `show_category(category)` |
| `sincronizar_catalogo(origen)` | `sync_catalog(origin)` |
| `main()` | `main()` |

Locals: `coincidencias→matches`, `lista_paquetes→package_list`,
`categoria→category`, `nombre→name`, `comando→command`, `gestor→manager`,
`argumentos→arguments`, `comando_visible→visible_command`,
`respuesta→answer`, `resultado→result`, `origen→origin`, `remoto→remote`,
`version_remota→remote_version`, `nuevos→added`, `modificados→modified`,
`retirados→removed`, `actuales→current`, `elementos→entries`,
`opcion→choice`, `numero→number`, `cantidad→count`, `prefijo→prefix`.

### `catalog.py`

| Now | After |
|---|---|
| module docstring | `"""Local package and install-command catalog for Termux Package Catalog."""` |
| `paquetes` | `packages` |
| `VERSION_CATALOGO` | `CATALOG_VERSION` |

### `autosync.py`

| Now | After |
|---|---|
| `ErrorCatalogo` | `CatalogError` |
| `URL_CATALOGO` | `CATALOG_URL` |
| `ARCHIVO_CACHE` | `CACHE_FILE` |
| `validar_catalogo(datos)` | `validate_catalog(data)` |
| `cargar_cache()` | `load_cache()` |
| `descargar_catalogo()` | `download_catalog()` |
| `guardar_cache(datos)` | `save_cache(data)` |
| module docstring | `"""Safe synchronization of the remote catalog."""` |

Locals: `datos→data`, `categoria→category`, `elementos→entries`,
`nombre→name`, `comando→command`, `solicitud→request`, `respuesta→response`,
`contenido→content`, `archivo→file`, `temporal→temp_file`.

## 5. Catalog keys

34 categories in `catalog.json`, 22 in the local fallback in `catalog.py`.
Only the keys change; every value stays byte-identical.

| Now | After |
|---|---|
| sistema | system |
| red | network |
| lenguaje | language |
| bases de datos | databases |
| servidores | servers |
| multimedia | multimedia |
| formatos | formats |
| diversion | fun |
| datos | data |
| web | web |
| machine learning | machine learning |
| utilidades | utilities |
| seguridad | security |
| testing | testing |
| automatizacion | automation |
| publicacion | publishing |
| GUI / CLI / Cloud | GUI / CLI / Cloud |
| juegos | games |
| ciencia | science |
| fechas | dates |
| desarrollo | development |
| archivos | files |
| compilacion | compilation |
| documentacion | documentation |
| configuracion | configuration |
| texto y web | text and web |
| red y protocolos | network and protocols |
| validacion y datos | validation and data |
| terminal y logs | terminal and logs |
| archivos y multimedia | files and multimedia |
| fechas y observabilidad | dates and observability |
| desarrollo y testing | development and testing |

`catalog.json` is pure ASCII today; translating the keys keeps it ASCII.
`updated_at` is set to `2026-11-01` for the new catalog version.

## 6. User-visible strings

All strings below become English. The banner box is widened so the new
product name and attribution fit without breaking the frame.

### Header and menu

| Now | After |
|---|---|
| `Vlsy46` (banner) | `Termux Package Catalog` |
| `versión {}` | `version {}` |
| `Creado por Lucas Sogaray` | `Based on Vlsy46 by Lucas Sogaray` |
| `CATÁLOGO DE PAQUETES` | `PACKAGE CATALOG` |
| `Categorías:` / `Paquetes:` | `Categories:` / `Packages:` |
| `[{} paquetes]` | `[{} packages]` |
| `B. Buscar paquetes` | `B. Search packages` |
| `U. Buscar actualizaciones` | `U. Check for updates` |
| `0. Salir` | `0. Exit` |
| `Selecciona una categoría, B para buscar o U para actualizar: ` | `Select a category, B to search or U to update: ` |
| `¡Hasta luego!` | `Goodbye!` |
| `Entrada no válida. Escribe un número, B o U. Presiona Enter...` | `Invalid input. Enter a number, B or U. Press Enter...` |
| `Opción fuera del menú. Presiona Enter para continuar...` | `Option outside the menu. Press Enter to continue...` |

### Search

| Now | After |
|---|---|
| `BÚSQUEDA GLOBAL` | `GLOBAL SEARCH` |
| `Busca por nombre de paquete o categoría.` | `Search by package name or category.` |
| `Buscar: ` | `Search: ` |
| `La búsqueda está vacía. Presiona Enter para continuar...` | `The search is empty. Press Enter to continue...` |
| `RESULTADOS PARA: {}` | `RESULTS FOR: {}` |
| `No se encontraron coincidencias.` | `No matches found.` |
| `Coincidencias:` | `Matches:` |
| `Categoría:` | `Category:` |
| `Presiona Enter para volver al catálogo...` | `Press Enter to return to the catalog...` |

### Category view

| Now | After |
|---|---|
| `Selecciona un paquete para ver su comando o instalarlo.` | `Select a package to view its command or install it.` |
| `Paquetes disponibles:` | `Available packages:` |
| `0. Volver` | `0. Back` |
| `Selecciona un paquete: ` | `Select a package: ` |
| `Selección no válida. Presiona Enter para continuar...` | `Invalid selection. Press Enter to continue...` |
| `PAQUETE: {}` | `PACKAGE: {}` |
| `Comando del catálogo:` | `Catalog command:` |

### Package Runner

| Now | After |
|---|---|
| `PACKAGE RUNNER` | `PACKAGE RUNNER` (unchanged) |
| `Gestor:` / `Paquete:` / `Comando:` | `Manager:` / `Package:` / `Command:` |
| `Comando no permitido. Solo se aceptan instalaciones pkg o pip.` | `Command not allowed. Only pkg or pip installs are accepted.` |
| `El instalador puede modificar el entorno de Termux/Python.` | `The installer may modify your Termux/Python environment.` |
| `¿Ejecutar la instalación? [s/N]: ` | `Run the installation? [y/N]: ` |
| `Instalación cancelada.` | `Installation cancelled.` |
| `Iniciando instalación...` | `Starting installation...` |
| `No se encontró el ejecutable necesario para {}.` | `Required executable for {} was not found.` |
| `No se pudo iniciar el instalador: {}` | `Could not start the installer: {}` |
| `Instalación finalizada correctamente.` | `Installation completed successfully.` |
| `El instalador terminó con código {}.` | `The installer exited with code {}.` |
| `Presiona Enter para volver a los paquetes...` | `Press Enter to return to packages...` |

### AutoSync

| Now | After |
|---|---|
| `AUTOSYNC` | `AUTOSYNC` (unchanged) |
| `Consultando el catálogo remoto...` | `Checking the remote catalog...` |
| `No se pudo comprobar: {}` | `Check failed: {}` |
| `Presiona Enter para volver al menú...` | `Press Enter to return to the menu...` |
| `Ya tienes la versión más reciente del catálogo.` | `You already have the latest catalog version.` |
| `El catálogo remoto tiene una versión anterior. No se aplicaron cambios.` | `The remote catalog is older. No changes applied.` |
| `Actualización disponible: catálogo {} → {}` | `Update available: catalog {} → {}` |
| `Paquetes nuevos:` / `Comandos modificados:` / `Paquetes retirados:` | `New packages:` / `Modified commands:` / `Removed packages:` |
| `Se muestran hasta 12 elementos por tipo.` | `Showing up to 12 items per type.` |
| `¿Aplicar esta actualización? [s/N]: ` | `Apply this update? [y/N]: ` |
| `Actualización cancelada. Se conserva el catálogo actual.` | `Update cancelled. The current catalog is kept.` |
| `Catálogo actualizado correctamente.` | `Catalog updated successfully.` |
| `Operación cancelada. ¡Hasta luego!` | `Operation cancelled. Goodbye!` |

### AutoSync validation errors

| Now | After |
|---|---|
| `El documento remoto no es un objeto JSON.` | `The remote document is not a JSON object.` |
| `Versión de formato de catálogo no compatible.` | `Unsupported catalog format version.` |
| `La versión del catálogo no es válida.` | `The catalog version is invalid.` |
| `El catálogo no contiene categorías válidas.` | `The catalog contains no valid categories.` |
| `El catálogo supera el límite de categorías.` | `The catalog exceeds the category limit.` |
| `Se encontró una categoría sin nombre.` | `A category without a name was found.` |
| `Categoría inválida: {}` | `Invalid category: {}` |
| `Paquete sin nombre en {}.` | `Unnamed package in {}.` |
| `Comando inválido para {}.` | `Invalid command for {}.` |
| `Entrada demasiado larga: {}` | `Entry too long: {}` |
| `El catálogo remoto supera el tamaño permitido.` | `The remote catalog exceeds the allowed size.` |
| `GitHub respondió con HTTP {}.` | `GitHub responded with HTTP {}.` |
| `No se pudo conectar con GitHub.` | `Could not connect to GitHub.` |
| `La conexión falló o agotó el tiempo de espera.` | `The connection failed or timed out.` |
| `El catálogo remoto no usa UTF-8 válido.` | `The remote catalog is not valid UTF-8.` |
| `GitHub devolvió un JSON inválido.` | `GitHub returned invalid JSON.` |
| `No se pudo guardar el catálogo local.` | `Could not save the local catalog.` |

## 7. Contracts kept unchanged

- `schema_version == 1`, `catalog_version >= 1` integer (not bool).
- Limits: ≤ 200 categories, ≤ 1000 entries per category, name ≤ 120 chars,
  command ≤ 500 chars, body ≤ 2 MiB, 8 s timeout.
- Install commands still parsed by the strict `(pkg|pip) install <name>`
  regex and executed as an argument list — never through a shell.
- Cache written to a temp file then `os.replace`d into place.
- `ensure_ascii=False`, 2-space indent, trailing newline in the cache.
- Colours disabled when stdout is not a TTY or `NO_COLOR` is set.
- Exit path on `EOFError` / `KeyboardInterrupt` unchanged (`SystemExit(0)`).

## 8. Verification plan

1. `python3 -m py_compile termux_pkg_catalog.py catalog.py autosync.py`.
2. `python3 termux_pkg_catalog.py </dev/null` → English banner/menu, exit 0.
3. Data diff: apply the category map to `git show HEAD:catalogo.json` and
   compare package→command pairs with `catalog.json`; expect 34 categories,
   250 packages, `catalog_version` 1.
4. `validate_catalog(load("catalog.json"))` passes; mutated copies with
   `schema_version: 2`, `catalog_version: 0` and `packages: {}` raise
   `CatalogError`.
5. Residue audit: `grep -nP "[áéíóúñÁÉÍÓÚÑ¿¡]|Catalogo|catalogo|paquete|paquetes"`
   over `*.py`, `*.json`, `README.md` → no hits.
6. Manual TUI pass: menu → category → package, global search for `git`,
   install prompt answered `n`, AutoSync with the network unavailable.

## 9. Rollout

Three commits, then the remote change:

1. `refactor: translate the codebase to English`
2. `feat: serve the catalog as termux-pkg-catalog version 1`
3. `docs: rewrite the README for Termux Package Catalog`

Then `git remote set-url origin https://github.com/GeneralKaos666/termux-pkg-catalog`.

## 10. Out of scope

- Test suite, `pyproject.toml`, console entry point, packaging.
- i18n / locale detection and any Spanish fallback.
- Behavioural changes to AutoSync, Package Runner or validation.
- Rewriting git history or re-licensing.
