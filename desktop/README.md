# Desktop Application (Electron)

This directory contains a production-oriented Electron desktop application for the Offline Policy Gap Analyzer.

## Highlights

- Hardened Electron process boundaries (`main`, `preload`, renderer)
- Allowlisted typed IPC contracts with schema validation (`zod`)
- Ollama lifecycle management (detect/start/stop/status)
- Local model management (`list`, `pull`, `rm`)
- Offline-first operation with no cloud requirement for inference
- Structured local logging and persistent config/state storage
- Packaging with `electron-builder` for macOS, Windows, Linux
- 2 GiB-per-file release policy tooling with chunking/reassembly scripts

## Workspace Layout

- `src/main` - Electron main process, services, IPC registration
- `src/preload` - Safe bridge API exposed to renderer
- `src/shared` - Cross-process schemas and contracts
- `renderer` - React + Vite UI
- `scripts` - release verification/chunking/assembly tooling
- `resources` - bundled runtime/model resource placeholders

## Development

```bash
cd desktop
npm install
npm --prefix renderer install
npm run dev
```

## Validation

```bash
npm run typecheck
npm run lint
npm run test
npm run build
```

## Packaging

```bash
npm run dist
npm run release:chunk-assets
npm run release:assemble-assets
```

Artifacts are generated in `desktop/release` and optional chunked output in `desktop/release-chunks`.
