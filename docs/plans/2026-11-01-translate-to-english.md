# Termux Package Catalog — English Translation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-publish Vlsy46 as `termux-pkg-catalog` 1.0.0, with every identifier, string, file name, catalog key and README line in English, and no behaviour change.

**Architecture:** Three Python modules keep their current responsibilities — `autosync.py` (fetch/validate/cache), `catalog.py` (local fallback data + cache load), `termux_pkg_catalog.py` (TUI, search, Package Runner). The catalog data moves from `catalogo.json` to `catalog.json` under English category keys. Translation is mechanical: no function gains or loses behaviour except the two version numbers and the fallback default noted in the spec.

**Tech Stack:** Python 3 standard library only (`json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `pathlib`, `urllib`). No dependencies, no test framework.

**Spec:** `docs/specs/2026-11-01-translate-to-english-design.md` (read §4, §5, §6 for the exact names and copy; this plan does not repeat them)

## Global Constraints

- English only. No Spanish word, identifier or accented character survives in `*.py`, `*.json` or `README.md`.
- `VERSION = "1.0.0"`; `catalog_version = 1`; `schema_version = 1`; local fallback `CATALOG_VERSION = 0` when no cache exists.
- `CATALOG_URL = "https://raw.githubusercontent.com/GeneralKaos666/termux-pkg-catalog/main/catalog.json"`.
- Preserve exactly: 250 package → command pairs, the `(pkg|pip) install <name>` regex, argument-list execution (never a shell), the 200/1000/120/500/2 MiB/8 s validation limits, atomic cache write, `ensure_ascii=False`, `NO_COLOR` and TTY checks, `SystemExit(0)` on EOF/Ctrl+C.
- Confirmation words are exactly `("y", "yes")`; Spanish `s`/`si`/`sí` are not accepted.
- Canonical residue check, used by every task (define once per shell):

```bash
ES='[áéíóúñÁÉÍÓÚÑ¿¡]|catalogo|\bpaquetes?\b|\bcomando\b|\bgestor\b|\barchivo\b|\bpausar\b|estilo\(|limpiar\(|ErrorCatalogo|COLORES|mostrar_|buscar_|guardar_|cargar_|descargar_|validar_|sincronizar_|ejecutar_|analizar_'
```

- **Single commit.** The repo is fresh with no history (spec §9). Tasks verify but do not commit; Task 6 makes the one initial release commit. Before starting, snapshot the originals so every task can diff against them and any step is recoverable:

```bash
mkdir -p "$HOME/.tmp/opencode/vlsy46-original"
cp -a Vlsy46.py catalogo.py autosync.py catalogo.json README.md LICENSE "$HOME/.tmp/opencode/vlsy46-original/"
```

- Commits are GPG-signed: run `sh "$HOME/.config/opencode/skills/gpg-commit/scripts/unlock-gpg.sh"` before committing and verify with `git verify-commit HEAD`.

## Review Focus

- **Spanish confirmation habit:** typing `s` or `si` at `Run the installation? [y/N]` must mean *no* — it silently cancels. Covered by Task 3 (exact tuple assertion) and Task 6 (manual pass).
- **First-run sync never fires:** remote catalog `1` against a fallback of `1` reports "already latest" and downloads nothing. Covered by Task 2 (`CATALOG_VERSION == 0`) and Task 4 (`1 > 0` assertion).
- **Banner overflow:** the longer product name and attribution must not break the 46-character box frame. Covered by Task 3 (equal-line-width test).
- **Public catalog keys:** any consumer reading `catalog.json` sees a completely different key set. Covered by Task 4 (exact 34-key set assertion, old keys absent).
- **Stale cache file:** an old `catalogo_cache.json` is ignored and never cleaned up. Covered by Task 2 (`CACHE_FILE` name + `.gitignore` update).

---

### Task 1: Translate `autosync.py`

**Files:**
- Modify: `autosync.py` (whole file, name unchanged)
- Test: none added; the checks below are the test cycle

**Interfaces:**
- Consumes: nothing from other modules.
- Produces: `CatalogError`, `validate_catalog(data) -> dict`, `load_cache() -> dict | None`, `download_catalog() -> dict`, `save_cache(data) -> None`, `CATALOG_URL`, `CACHE_FILE: Path`, `MAX_BYTES`, `TIMEOUT`.

- [ ] **Step 1: Show the Spanish residue fails**

Run:
```bash
ES='[áéíóúñÁÉÍÓÚÑ¿¡]|catalogo|\bpaquetes?\b|\bcomando\b|\bgestor\b|\barchivo\b|\bpausar\b|estilo\(|limpiar\(|ErrorCatalogo|COLORES|mostrar_|buscar_|guardar_|cargar_|descargar_|validar_|sincronizar_|ejecutar_|analizar_'
grep -nP "$ES" autosync.py
```
Expected: FAIL — many hits (`ErrorCatalogo`, `URL_CATALOGO`, `validar_catalogo`, `cargar_cache`, `descargar_catalogo`, `guardar_cache`, Spanish docstrings and messages).

- [ ] **Step 2: Translate the module**

Apply spec §4 (`autosync.py` table), §6 (AutoSync validation errors) and Global Constraints. Rename the module docstring to `"""Safe synchronization of the remote catalog."""`. Set `CATALOG_URL` to the new repository path. Keep the validation order, limit values, exception chaining (`from error`) and the temp-file-then-`os.replace` write exactly as they are.

- [ ] **Step 3: Run the residue check to verify it passes**

Run the Step 1 command.
Expected: PASS — no output, `grep` exit status 1.

- [ ] **Step 4: Verify validation still accepts the real catalog and rejects bad ones**

Run:
```bash
python3 - <<'EOF'
import json, copy
from autosync import validate_catalog, CatalogError

data = json.load(open("catalogo.json"))
validate_catalog(data); print("accepts real catalog")

def rejects(mutate, expected):
    bad = copy.deepcopy(data); mutate(bad)
    try: validate_catalog(bad)
    except CatalogError as e:
        assert expected in str(e), (expected, str(e)); print("rejects:", str(e))
    else: raise SystemExit("not rejected: " + expected)

rejects(lambda d: d.update(schema_version=2), "Unsupported catalog format version")
rejects(lambda d: d.update(catalog_version=0), "The catalog version is invalid")
rejects(lambda d: d.update(packages={}), "The catalog contains no valid categories")
EOF
```
Expected: `accepts real catalog` then three `rejects: …` lines, exit 0.

- [ ] **Step 5: Compile**

Run: `python3 -m py_compile autosync.py`
Expected: exit 0, no output.

---

### Task 2: Translate `catalog.py`, rename it, fix the fallback default

**Files:**
- Rename + modify: `catalogo.py` → `catalog.py`
- Modify: `.gitignore:221-222`
- Test: none added; the checks below are the test cycle

**Interfaces:**
- Consumes: `load_cache()` from Task 1.
- Produces: `packages: dict[str, dict[str, str]]` (the 22 fallback categories, English keys), `CATALOG_VERSION: int` (`0` when no cache exists).

- [ ] **Step 1: Show the residue fails**

Run: `ES=...` from Global Constraints, then `grep -nP "$ES" catalogo.py`.
Expected: FAIL — `paquetes`, `VERSION_CATALOGO`, Spanish docstring.

- [ ] **Step 2: Rename and translate**

```bash
mv catalogo.py catalog.py
```
Translate the docstring, `paquetes` → `packages`, `VERSION_CATALOGO` → `CATALOG_VERSION`, and translate the 22 category keys per spec §5 (values untouched). Change the no-cache default:

```python
CATALOG_VERSION = _cache["catalog_version"] if _cache else 0
```

- [ ] **Step 3: Update the ignored cache names**

In `.gitignore`, replace `catalogo_cache.json` with `catalog_cache.json` and `catalogo.json.tmp` with `catalog.json.tmp`. Do not add `catalog.json` itself.

- [ ] **Step 4: Verify the module loads with the right defaults**

Run:
```bash
python3 - <<'EOF'
import pathlib, catalog
assert catalog.CATALOG_VERSION == 0, catalog.CATALOG_VERSION
assert len(catalog.packages) == 22, len(catalog.packages)
assert "system" in catalog.packages and "sistema" not in catalog.packages
print("catalog ok:", catalog.CATALOG_VERSION, len(catalog.packages))
EOF
git check-ignore -q catalog_cache.json && echo "cache ignored"
git check-ignore -q catalog.json && echo "ERROR: catalog.json ignored" || echo "catalog.json tracked"
```
Expected: `catalog ok: 0 22`, `cache ignored`, `catalog.json tracked`.

- [ ] **Step 5: Residue check and compile**

Run the Step 1 grep on `catalog.py` (expect no output), then `python3 -m py_compile catalog.py` (expect exit 0).

---

### Task 3: Translate the entry point, rename it to `termux_pkg_catalog.py`

**Files:**
- Rename + modify: `Vlsy46.py` → `termux_pkg_catalog.py`
- Test: none added; the checks below are the test cycle

**Interfaces:**
- Consumes: `packages`, `CATALOG_VERSION` from Task 2; `CatalogError`, `download_catalog`, `save_cache` from Task 1.
- Produces: `style`, `clear_screen`, `read_input`, `pause`, `show_header`, `search_packages(query) -> list[tuple[str, str, str]]`, `show_search`, `show_menu() -> list[str]`, `parse_install_command(command) -> tuple[str, str] | None`, `run_install(command)`, `show_category(category)`, `sync_catalog(origin)`, `main()`, `VERSION = "1.0.0"`, `COLORS`, `COLORS_ENABLED`.

- [ ] **Step 1: Show the residue fails**

Run: `grep -nP "$ES" Vlsy46.py` with `ES` from Global Constraints.
Expected: FAIL — Spanish identifiers and all UI strings.

- [ ] **Step 2: Rename and translate**

```bash
mv Vlsy46.py termux_pkg_catalog.py
```
Apply spec §4 (`termux_pkg_catalog.py` table) and every string in spec §6 (header, menu, search, category, Package Runner, AutoSync, cancellation). Update the import line to `from catalog import packages, CATALOG_VERSION` and `from autosync import CatalogError, download_catalog, save_cache`. Set `VERSION = "1.0.0"`. Confirmation check becomes:

```python
if answer.casefold() not in ("y", "yes"):
```

Rewrite the banner so `"Termux Package Catalog"`, `f"version {VERSION}"` and `"Based on Vlsy46 by Lucas Sogaray"` all fit the frame: widen the box to at least 48 characters and pad each line to the same width. Keep `colorama`-free plain ANSI, the `NO_COLOR` gate and the `cls`/`clear` logic untouched.

- [ ] **Step 3: Residue check, compile, clean run**

Run:
```bash
grep -nP "$ES" termux_pkg_catalog.py
python3 -m py_compile termux_pkg_catalog.py
python3 termux_pkg_catalog.py </dev/null; echo "exit=$?"
```
Expected: no grep output; compile exit 0; the run prints the English banner and menu and `exit=0` via the EOF path.

- [ ] **Step 4: Verify the banner frame and the confirmation words**

Run:
```bash
python3 - <<'EOF'
import io, contextlib, termux_pkg_catalog as t
buf = io.StringIO()
with contextlib.redirect_stdout(buf): t.show_header()
lines = buf.getvalue().splitlines()
assert len({len(l) for l in lines}) == 1, [(len(l), l) for l in lines]
assert "Termux Package Catalog" in lines[1]
print("banner ok, width", len(lines[0]))
EOF
grep -n '("y", "yes")' termux_pkg_catalog.py
```
Expected: `banner ok, width <n>` and one matching line for the confirmation tuple.

- [ ] **Step 5: Confirm no module still imports the old names**

Run: `grep -rn "catalogo\|ErrorCatalogo\|VERSION_CATALOGO" --include="*.py" .`
Expected: no output.

---

### Task 4: Translate `catalog.json`

**Files:**
- Rename + modify: `catalogo.json` → `catalog.json`
- Reference: snapshot at `$HOME/.tmp/opencode/vlsy46-original/catalogo.json`

**Interfaces:**
- Produces: `catalog.json` with `schema_version: 1`, `catalog_version: 1`, `updated_at: "2026-11-01"`, 34 English category keys, 250 identical package → command pairs.

- [ ] **Step 1: Show the keys are still Spanish**

Run: `python3 -c "import json;print(sorted(json.load(open('catalogo.json'))['packages']))"`
Expected: the 34 Spanish keys, including `sistema`, `red`, `lenguaje`, `bases de datos`.

- [ ] **Step 2: Rename and rewrite the keys**

```bash
mv catalogo.json catalog.json
python3 - <<'EOF'
import json
MAP = {
    "sistema": "system", "red": "network", "lenguaje": "language",
    "bases de datos": "databases", "servidores": "servers",
    "multimedia": "multimedia", "formatos": "formats", "diversion": "fun",
    "datos": "data", "web": "web", "machine learning": "machine learning",
    "utilidades": "utilities", "seguridad": "security", "testing": "testing",
    "automatizacion": "automation", "publicacion": "publishing", "GUI": "GUI",
    "juegos": "games", "CLI": "CLI", "ciencia": "science", "Cloud": "Cloud",
    "fechas": "dates", "desarrollo": "development", "archivos": "files",
    "compilacion": "compilation", "documentacion": "documentation",
    "configuracion": "configuration", "texto y web": "text and web",
    "red y protocolos": "network and protocols",
    "validacion y datos": "validation and data",
    "terminal y logs": "terminal and logs",
    "archivos y multimedia": "files and multimedia",
    "fechas y observabilidad": "dates and observability",
    "desarrollo y testing": "development and testing",
}
path = "catalog.json"
doc = json.load(open(path, encoding="utf-8"))
assert set(doc["packages"]) == set(MAP), set(doc["packages"]) ^ set(MAP)
doc["catalog_version"] = 1
doc["updated_at"] = "2026-11-01"
doc["packages"] = {MAP[k]: v for k, v in doc["packages"].items()}
with open(path, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2); f.write("\n")
print("rewritten")
EOF
```

- [ ] **Step 3: Verify the pairs are byte-identical and the numbers are right**

Run:
```bash
python3 - <<'EOF'
import json, os
ORIG = json.load(open(os.path.expanduser("~/.tmp/opencode/vlsy46-original/catalogo.json")))
NEW = json.load(open("catalog.json"))
PAIRS = sorted(p for cat in ORIG["packages"].values() for p in cat.items())
NEWPAIRS = sorted(p for cat in NEW["packages"].values() for p in cat.items())
assert NEWPAIRS == PAIRS, "package/command pairs changed"
assert NEW["schema_version"] == 1 and NEW["catalog_version"] == 1
assert NEW["updated_at"] == "2026-11-01"
assert len(NEW["packages"]) == 34, len(NEW["packages"])
assert sum(len(v) for v in NEW["packages"].values()) == 250
import catalog
assert catalog.CATALOG_VERSION == 0
assert NEW["catalog_version"] > catalog.CATALOG_VERSION
print("data ok: 34 categories, 250 pairs, catalog_version 1")
EOF
```

- [ ] **Step 4: Verify AutoSync accepts the new file**

Run:
```bash
python3 -c "import json; from autosync import validate_catalog; validate_catalog(json.load(open('catalog.json'))); print('validates')"
grep -nP '[áéíóúñÁÉÍÓÚÑ¿¡]' catalog.json; echo "ascii-check-exit=$?"
```
Expected: `validates`, and `ascii-check-exit=1` (no non-ASCII bytes).

---

### Task 5: Translate `README.md`, keep attribution

**Files:**
- Modify: `README.md`
- Unchanged: `LICENSE` (already English; `Copyright (c) 2026 lucassogarayDA` must stay)

**Interfaces:**
- Produces: English README whose commands and paths match Tasks 2–4.

- [ ] **Step 1: Show the Spanish residue fails**

Run: `grep -nP "$ES" README.md`
Expected: FAIL — the whole document.

- [ ] **Step 2: Rewrite in English**

Required exact values: title `# Termux Package Catalog`, `- **Version:** 1.0.0`, `- **Maintained by:** GeneralKaos666`, `- **Based on:** Vlsy46 by Lucas Sogaray (MIT)`, run command `python3 termux_pkg_catalog.py`, clone URL `https://github.com/GeneralKaos666/termux-pkg-catalog.git`. Keep every section of the original (features, AutoSync, Package Runner, install/use, menu keys, project structure, adding packages, security/compatibility, license) with the file names from spec §3 and the strings from spec §6. State that only `y`/`yes` confirms an install. Mark it explicitly as an independent project based on Vlsy46.

- [ ] **Step 3: Verify residue and references**

Run:
```bash
grep -nP "$ES" README.md
grep -n "catalogo\|Vlsy46\.py\|2\.0\.0" README.md
python3 - <<'EOF'
import re, pathlib
text = pathlib.Path("README.md").read_text()
for f in ("termux_pkg_catalog.py", "catalog.py", "catalog.json", "autosync.py"):
    assert f in text, f
assert "Lucas Sogaray" in text
print("readme ok")
EOF
```
Expected: first two greps print nothing (attribution uses `Vlsy46 by Lucas Sogaray`, not the path); `readme ok`.

- [ ] **Step 4: Confirm no stray old files remain**

Run: `ls; git status --short`
Expected: `autosync.py catalog.json catalog.py docs LICENSE README.md termux_pkg_catalog.py` and no `catalogo.*` or `Vlsy46.py`.

---

### Task 6: Full verification, release commit, new remote

**Files:**
- Commit: all project files
- Modify: `.git/config` (add `origin`)

- [ ] **Step 1: Run the complete gate**

```bash
ES='[áéíóúñÁÉÍÓÚÑ¿¡]|catalogo|\bpaquetes?\b|\bcomando\b|\bgestor\b|\barchivo\b|\bpausar\b|estilo\(|limpiar\(|ErrorCatalogo|COLORES|mostrar_|buscar_|guardar_|cargar_|descargar_|validar_|sincronizar_|ejecutar_|analizar_'
python3 -m py_compile termux_pkg_catalog.py catalog.py autosync.py
python3 termux_pkg_catalog.py </dev/null >"$HOME/.tmp/opencode/tpc-run.txt"; echo "run-exit=$?"
grep -nP "$ES" *.py *.json README.md; echo "residue-exit=$?"
grep -c "Termux Package Catalog" "$HOME/.tmp/opencode/tpc-run.txt"
```
Expected: compile silent, `run-exit=0`, `residue-exit=1`, and at least `1` banner hit.

- [ ] **Step 2: Manual TUI pass**

Run `python3 termux_pkg_catalog.py`, then, in order: open category `1`, select package `1`, answer `n` at the install prompt (expect `Installation cancelled.`), return to the menu with `0`, run `B` and search `git` (expect matches), run `U` with the network off (expect `Check failed: …` and return to the menu), exit with `0` (expect `Goodbye!`). Then delete any generated `catalog_cache.json` before committing.

- [ ] **Step 3: Commit the release**

```bash
sh "$HOME/.config/opencode/skills/gpg-commit/scripts/unlock-gpg.sh"
git add -A
git commit -S -m "feat: initial English release of Termux Package Catalog"
git verify-commit HEAD
git log -1 --show-signature --format='%h %G?'
```
Expected: one commit, `verify-commit` exit 0, `%G?` prints `G`.

- [ ] **Step 4: Point the repo at the new GitHub location**

```bash
git remote add origin https://github.com/GeneralKaos666/termux-pkg-catalog
git remote -v
```
Expected: `origin` fetch and push both show the new URL. Do not push — the repository is created by the user.

- [ ] **Step 5: Confirm the tree is clean**

Run: `git status --short` and `git ls-files`
Expected: no output from status; `ls-files` lists eight tracked paths (four modules, `catalog.json`, `README.md`, `LICENSE`, the spec and this plan) — note `catalog_cache.json` must not appear.
