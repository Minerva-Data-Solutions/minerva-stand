import { getApiBase } from "./lib/apiBase";

function apiUrl(path: string): string {
  const base = getApiBase();
  if (!path.startsWith("/")) {
    return `${base}/${path}`;
  }
  return `${base}${path}`;
}

async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const url = apiUrl(path);
  const headers = new Headers(init.headers);
  if (
    init.body &&
    typeof init.body === "string" &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(url, {
    ...init,
    headers,
    credentials: "include",
  });
}

function apiErrorMessage(j: unknown, fallback: string): string {
  if (j && typeof j === "object" && "error" in j) {
    const err = (j as { error?: { message?: string } }).error;
    if (err?.message) return err.message;
  }
  return fallback;
}

export async function pingHealth(): Promise<boolean> {
  try {
    const r = await fetch(apiUrl("/health"), { method: "GET", credentials: "omit" });
    return r.ok;
  } catch {
    return false;
  }
}

export function getResolvedApiOrigin(): string {
  const b = getApiBase();
  return b || "(same origin as UI — dev proxy)";
}

export async function login(username: string, password: string) {
  let r: Response;
  try {
    r = await apiFetch("/api/workbench/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new Error(
      "Cannot reach the API. In dev, run `nanobot serve` on port 8900 and keep Vite’s default proxy. In Docker, open the UI and API on the same hostname (e.g. both localhost or both 127.0.0.1).",
    );
  }
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    throw new Error(apiErrorMessage(j, "Login failed"));
  }
}

export async function logout() {
  try {
    await apiFetch("/api/workbench/auth/logout", { method: "POST" });
  } catch {
    /* ignore */
  }
}

export async function session(): Promise<boolean> {
  try {
    const r = await apiFetch("/api/workbench/auth/session");
    return r.ok;
  } catch {
    return false;
  }
}

export async function chat(message: string, sessionId?: string) {
  let r: Response;
  try {
    r = await apiFetch("/api/workbench/chat", {
      method: "POST",
      body: JSON.stringify({ message, sessionId }),
    });
  } catch {
    throw new Error("Network error — API unreachable.");
  }
  const j = await r.json();
  if (!r.ok) {
    throw new Error(apiErrorMessage(j, "Chat failed"));
  }
  return (j as { reply: string }).reply;
}

export async function listFiles(path: string) {
  const q = new URLSearchParams({ path });
  let r: Response;
  try {
    r = await apiFetch(`/api/workbench/files?${q}`);
  } catch {
    throw new Error("Network error — API unreachable.");
  }
  const j = await r.json();
  if (!r.ok) {
    throw new Error(apiErrorMessage(j, "List failed"));
  }
  return j as
    | {
        type: "directory";
        path: string;
        entries: { name: string; path: string; isDir: boolean; size: number | null }[];
      }
    | {
        type: "file";
        name: string;
        path: string;
        size: number;
      };
}

export async function readFile(path: string) {
  const q = new URLSearchParams({ path });
  let r: Response;
  try {
    r = await apiFetch(`/api/workbench/files/content?${q}`);
  } catch {
    throw new Error("Network error — API unreachable.");
  }
  const j = await r.json();
  if (!r.ok) {
    throw new Error(apiErrorMessage(j, "Read failed"));
  }
  return j as { path: string; text: string; binary: boolean };
}

export async function writeFile(path: string, content: string) {
  let r: Response;
  try {
    r = await apiFetch("/api/workbench/files/content", {
      method: "PUT",
      body: JSON.stringify({ path, content }),
    });
  } catch {
    throw new Error("Network error — API unreachable.");
  }
  const j = await r.json();
  if (!r.ok) {
    throw new Error(apiErrorMessage(j, "Save failed"));
  }
}

export async function sqliteTables() {
  let r: Response;
  try {
    r = await apiFetch("/api/workbench/sqlite/tables");
  } catch {
    throw new Error("Network error — API unreachable.");
  }
  const j = await r.json();
  if (!r.ok) {
    throw new Error(apiErrorMessage(j, "Tables failed"));
  }
  return (j as { tables: string[] }).tables;
}

export async function sqliteQuery(sql: string) {
  let r: Response;
  try {
    r = await apiFetch("/api/workbench/sqlite/query", {
      method: "POST",
      body: JSON.stringify({ sql }),
    });
  } catch {
    throw new Error("Network error — API unreachable.");
  }
  const j = await r.json();
  if (!r.ok) {
    throw new Error(apiErrorMessage(j, "Query failed"));
  }
  return j as {
    columns: string[];
    rows: Record<string, unknown>[];
    truncated: boolean;
  };
}
