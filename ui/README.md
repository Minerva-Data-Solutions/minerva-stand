# Minerva Stand UI

## Development

1. Install dependencies: `bun install`
2. Run the API locally on port **8900** (`nanobot serve` in the project root, or Docker `stand-api`).
3. Start Vite: `bun run dev` (default **http://127.0.0.1:5174**).

Vite proxies `/api`, `/health`, and `/v1` to `VITE_PROXY_TARGET` (default `http://127.0.0.1:8900`). Override in `.env` if your API runs elsewhere.

Open the UI and API on the **same hostname** (both `localhost` or both `127.0.0.1`) so session cookies work.

## Production build

`bun run build` outputs to `dist/` for `serve-ui` or static hosting.