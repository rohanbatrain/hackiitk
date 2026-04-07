# Production Desktop Application Architecture

## 1. Scope and Support Matrix

### Platforms and Architectures
- **Windows**: 10/11 (x64)
- **macOS**: 13+ (x64, arm64)
- **Linux**: modern glibc distributions (x64)

### Runtime Requirements
- Local Ollama runtime (detected and optionally managed by app)
- Sufficient RAM and disk based on installed model size
- Offline execution supported after installation

### Enterprise Constraints
- No external inference APIs required
- Local logging and diagnostics bundle support
- Update channel control (`stable`, `beta`)

## 2. Application Architecture

### Process Model
- **Main process**
  - Window lifecycle
  - IPC registration and allowlist
  - Runtime/model/updater services
  - Config/state persistence
- **Preload process**
  - Narrow bridge (`window.desktopApi`)
  - No Node.js exposure to renderer
- **Renderer process**
  - React UI for onboarding/runtime/models/tasks/settings

### Security Controls
- `contextIsolation: true`
- `sandbox: true`
- `nodeIntegration: false`
- external URL opening denied by default and routed through system shell
- all IPC payloads validated via `zod`

## 3. Reliability and Recovery

- Persistent JSON state for onboarding and task history
- Persistent JSON settings for runtime/config behavior
- Structured log sink in user data directory
- Runtime watchdog checks via periodic status polling
- Explicit start/stop control for Ollama process

## 4. Model and Runtime Management

- Runtime checks:
  - command availability (`ollama --version`)
  - daemon health (`/api/tags`)
- Model flows:
  - list installed models
  - pull model by tag
  - remove model
- Task execution:
  - local text generation through `/api/generate`

## 5. Packaging, Installers, and Update Strategy

### Build Tooling
- `electron-builder` with cross-platform targets:
  - Windows: NSIS + portable
  - macOS: DMG + ZIP
  - Linux: AppImage + DEB

### Update Strategy
- GitHub releases as update feed
- update checks through `electron-updater`
- stable/beta channels configured via settings

### Release Asset Policy (< 2 GiB per file)
- `scripts/verify-release-assets.mjs` enforces hard per-file limit
- `scripts/chunk-release-assets.mjs` splits oversized artifacts into <2 GiB parts
- `scripts/assemble-release-assets.mjs` reconstructs and verifies checksums

## 6. Release Flow

1. Build desktop app (`npm run dist`)
2. Verify per-file size policy (`verify-release-assets`)
3. Chunk oversized assets (`release:chunk-assets`)
4. Publish installers + chunked model/runtime packs + manifest
5. Client/installer assembles chunked assets and verifies checksums

## 7. Operations and Troubleshooting

### Common Diagnostics
- App status and runtime checks from **Runtime** screen
- Model inventory and management from **Models** screen
- Local prompt execution from **Tasks** screen
- Settings for host/command/update controls from **Settings** screen

### Troubleshooting
- If Ollama is unavailable: verify command path and host in settings
- If model pull fails: check disk/RAM and local network policy
- If update check fails: validate release metadata and connectivity
- For incident triage: collect logs from user data `logs/` directory

## 8. QA and Production Readiness

Desktop workspace validation commands:
- `npm run typecheck`
- `npm run lint`
- `npm run test`
- `npm run build`

Repository-level Python CI remains unchanged and continues validating the core backend pipeline.
