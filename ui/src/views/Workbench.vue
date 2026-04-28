<template>
  <div
    class="flex flex-col lg:flex-row h-screen overflow-hidden bg-base-100 text-base-content font-sans"
  >
    <aside
      class="hidden lg:flex flex-col w-52 border-r border-subtle bg-base-200/40 shrink-0"
    >
      <div class="px-5 pt-7 pb-5">
        <div class="flex items-center gap-2 mb-3">
          <span
            class="w-4 h-4 rounded-full flex items-center justify-center text-[0.5rem] font-bold bg-primary text-primary-content shrink-0"
          >M</span>
          <span class="text-[0.55rem] uppercase tracking-[0.3em] text-base-content/45">Minerva</span>
        </div>
        <h1 class="font-display italic text-2xl text-base-content leading-tight">
          Workbench
        </h1>
      </div>

      <div class="border-t border-subtle mx-4 mb-2" />

      <nav class="flex-1 px-2 py-2 space-y-px">
        <button
          v-for="item in navItems"
          :key="item.id"
          type="button"
          class="relative w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs transition-all duration-150"
          :class="
            tab === item.id
              ? 'text-primary bg-primary/10'
              : 'text-base-content/50 hover:text-base-content/80 hover:bg-base-200/80'
          "
          @click="tab = item.id"
        >
          <span
            v-if="tab === item.id"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-primary rounded-r-full"
          />
          <span class="text-[0.7rem] w-3 text-center opacity-50 shrink-0">{{ item.sym }}</span>
          <span class="tracking-wide">{{ item.label }}</span>
        </button>
      </nav>

      <div class="px-4 pb-5 pt-4 space-y-4 border-t border-subtle">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span
              class="w-1.5 h-1.5 rounded-full shrink-0 transition-colors duration-700"
              :class="
                apiOk === true
                  ? 'bg-success animate-status-glow'
                  : apiOk === false
                    ? 'bg-error'
                    : 'bg-base-content/20'
              "
            />
            <span class="text-[0.58rem] uppercase tracking-wide text-base-content/40">
              {{ apiOk === null ? "checking" : apiOk ? "connected" : "offline" }}
            </span>
          </div>
          <p class="text-[0.58rem] font-mono text-base-content/40 pl-3.5 truncate" :title="apiHint">
            {{ apiHint }}
          </p>
        </div>
        <button
          type="button"
          class="text-[0.62rem] text-base-content/45 hover:text-primary transition-colors w-full text-left"
          @click="doLogout"
        >
          Disconnect →
        </button>
      </div>
    </aside>

    <div class="flex flex-1 flex-col min-w-0 min-h-0 overflow-hidden">
      <header
        class="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-subtle bg-base-200/50 shrink-0"
      >
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <span
            class="w-4 h-4 rounded-full flex items-center justify-center text-[0.5rem] font-bold bg-primary text-primary-content shrink-0"
          >M</span>
          <span class="font-display italic text-lg text-base-content">Workbench</span>
        </div>
        <div class="flex items-center gap-3">
          <span
            class="w-1.5 h-1.5 rounded-full"
            :class="apiOk === true ? 'bg-success' : apiOk === false ? 'bg-error' : 'bg-base-content/20'"
          />
          <button
            type="button"
            class="text-[0.62rem] text-base-content/45 hover:text-primary transition-colors"
            @click="doLogout"
          >
            Exit
          </button>
        </div>
      </header>

      <div class="lg:hidden flex border-b border-subtle bg-base-200/40 shrink-0">
        <button
          v-for="item in navItems"
          :key="item.id"
          type="button"
          class="flex-1 py-2.5 text-xs transition-all border-b-2"
          :class="
            tab === item.id
              ? 'text-primary border-primary'
              : 'text-base-content/40 border-transparent hover:text-base-content/65'
          "
          @click="tab = item.id"
        >
          {{ item.label }}
        </button>
      </div>

      <main class="flex-1 flex flex-col min-h-0 overflow-hidden">
        <!-- ── SQLite ── -->
        <section
          v-show="tab === 'sqlite'"
          class="flex flex-col flex-1 min-h-0 p-4 sm:p-5 gap-4 overflow-y-auto animate-fade-in"
        >
          <div class="surface overflow-hidden shrink-0">
            <div class="flex flex-wrap items-center gap-2 px-4 py-2.5 border-b border-subtle">
              <span class="text-[0.55rem] uppercase tracking-[0.25em] text-base-content/35">
                Tables
              </span>
              <div class="flex flex-wrap gap-1.5 flex-1 min-w-0">
                <button
                  v-for="t in tables"
                  :key="t"
                  type="button"
                  class="px-2 py-0.5 rounded text-[0.62rem] font-mono bg-primary/8 text-primary/80 border border-primary/20 hover:bg-primary/15 transition-colors"
                  @click="insertTable(t)"
                >
                  {{ t }}
                </button>
                <span v-if="tables.length === 0 && !sqlLoading" class="text-xs font-mono text-base-content/30">
                  no tables found
                </span>
              </div>
              <button
                type="button"
                class="text-[0.58rem] font-mono text-base-content/30 hover:text-base-content/60 transition-colors ml-auto shrink-0"
                @click="loadTables"
              >
                Refresh
              </button>
            </div>

            <div class="p-4 space-y-3">
              <textarea
                v-model="sqlInput"
                class="textarea w-full input-minerva font-mono text-xs leading-[1.7] resize-none"
                style="min-height: 110px"
                placeholder="SELECT name FROM sqlite_master WHERE type='table';"
              />
              <div class="flex items-center gap-3 flex-wrap">
                <button
                  type="button"
                  class="btn-ghost-primary btn-sm font-mono text-xs"
                  :disabled="sqlBusy"
                  @click="runSql"
                >
                  <span v-if="sqlBusy" class="loading loading-spinner loading-xs" />
                  <span v-else>▶ Run</span>
                </button>
                <button
                  type="button"
                  class="text-[0.58rem] font-mono text-base-content/30 hover:text-base-content/60 transition-colors"
                  @click="resetDefaultQuery"
                >
                  Reset query
                </button>
                <span v-if="sqlResult?.truncated" class="text-[0.62rem] font-mono text-warning/70">
                  ⚠ Truncated at 5000 rows
                </span>
                <span v-if="sqlResult" class="text-[0.58rem] font-mono text-base-content/30 ml-auto">
                  {{ sqlResult.rows.length }} row{{ sqlResult.rows.length !== 1 ? "s" : "" }}
                </span>
              </div>
              <p
                v-if="sqlErr"
                class="text-xs font-mono text-error/80 px-3 py-2 rounded-lg bg-error/10 border border-error/20 leading-relaxed"
              >
                ⚠ {{ sqlErr }}
              </p>
            </div>
          </div>

          <div
            v-if="sqlResult && sqlResult.columns.length"
            class="surface overflow-auto"
            style="min-height: 120px"
          >
            <table class="table table-sm table-pin-rows w-full">
              <thead>
                <tr class="bg-base-200/90">
                  <th
                    v-for="c in sqlResult.columns"
                    :key="c"
                    class="font-mono text-[0.62rem] uppercase tracking-wide text-base-content/45 py-2.5 px-3"
                  >
                    {{ c }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, ri) in sqlResult.rows"
                  :key="ri"
                  class="border-base-300/50 hover:bg-base-200/50 transition-colors"
                >
                  <td
                    v-for="c in sqlResult.columns"
                    :key="c"
                    class="font-mono text-[0.68rem] align-top py-2 px-3 text-base-content/75 whitespace-pre-wrap max-w-xs"
                  >
                    {{ formatCell(row[c]) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div
            v-else-if="sqlResult && !sqlResult.columns.length"
            class="surface px-4 py-6 text-center"
          >
            <p class="text-xs font-mono text-base-content/35">Query returned no rows.</p>
          </div>
        </section>

        <!-- ── Files ── -->
        <section
          v-show="tab === 'files'"
          class="flex flex-col flex-1 min-h-0 p-4 sm:p-5 gap-4 animate-fade-in"
        >
          <div class="surface-2 px-3 py-2.5 shrink-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-[0.55rem] uppercase tracking-[0.25em] text-base-content/40">
                Bootstrap
              </span>
              <div class="flex flex-wrap gap-1.5 flex-1 min-w-0">
                <button
                  v-for="b in bootstrap"
                  :key="b.name"
                  type="button"
                  class="px-2 py-0.5 rounded text-[0.62rem] font-mono border transition-colors"
                  :class="
                    b.present
                      ? 'bg-primary/10 text-primary border-primary/25 hover:bg-primary/20'
                      : 'bg-base-300/50 text-base-content/35 border-subtle hover:text-base-content/60'
                  "
                  :title="b.present ? `${b.size} bytes` : 'Missing — click Restore defaults'"
                  @click="openBootstrap(b)"
                >
                  {{ b.present ? "●" : "○" }} {{ b.name }}
                </button>
                <span v-if="bootstrap.length === 0 && !bootstrapLoading" class="text-xs font-mono text-base-content/30">
                  loading…
                </span>
              </div>
              <button
                type="button"
                class="text-[0.6rem] font-mono text-primary/80 hover:text-primary transition-colors px-2 py-1 rounded border border-primary/25 hover:border-primary/50 bg-primary/5 shrink-0"
                :disabled="bootstrapBusy"
                @click="restoreBootstrap"
              >
                {{ bootstrapBusy ? "…" : "Restore defaults" }}
              </button>
            </div>
            <p v-if="bootstrapMsg" class="text-[0.58rem] font-mono text-success/70 mt-1.5">
              {{ bootstrapMsg }}
            </p>
          </div>

          <div class="flex items-center gap-2 shrink-0 pb-3 border-b border-subtle flex-wrap">
            <button
              type="button"
              class="text-[0.62rem] font-mono text-base-content/35 hover:text-primary/70 transition-colors px-2 py-1 rounded border border-subtle hover:border-primary/20"
              :disabled="!filePath"
              @click="goUp"
            >
              ← Up
            </button>
            <span class="font-mono text-xs text-base-content/60 truncate flex-1 min-w-0">
              {{ filePath ? `/ ${filePath}` : "/" }}
            </span>
            <button
              type="button"
              class="text-[0.62rem] font-mono text-base-content/35 hover:text-primary/70 transition-colors px-2 py-1 rounded border border-subtle hover:border-primary/20"
              @click="refreshFiles"
            >
              ↻ Refresh
            </button>
            <button
              type="button"
              class="text-[0.62rem] font-mono text-primary/80 hover:text-primary transition-colors px-2 py-1 rounded border border-primary/25 hover:border-primary/50 bg-primary/5"
              @click="newFile"
            >
              + File
            </button>
            <button
              type="button"
              class="text-[0.62rem] font-mono text-primary/80 hover:text-primary transition-colors px-2 py-1 rounded border border-primary/25 hover:border-primary/50 bg-primary/5"
              @click="newFolder"
            >
              + Folder
            </button>
          </div>

          <div class="flex-1 flex flex-col lg:flex-row gap-4 min-h-0">
            <div class="surface w-full lg:w-64 lg:min-w-[14rem] shrink-0 overflow-auto flex flex-col min-h-0">
              <div v-if="fileEntries.length === 0 && !draftPath" class="p-5 text-xs font-mono text-base-content/30 text-center">
                Empty directory
              </div>
              <ul class="p-1.5 space-y-px flex-1">
                <li
                  v-if="draftPath"
                  class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-mono text-primary bg-primary/10 border border-primary/20"
                >
                  <span class="opacity-60 shrink-0 text-[0.58rem]">·</span>
                  <span class="truncate flex-1">{{ draftName }}</span>
                  <span class="text-[0.5rem] opacity-60 shrink-0">new</span>
                  <button
                    type="button"
                    class="text-[0.62rem] opacity-50 hover:opacity-100 hover:text-error shrink-0"
                    title="Discard draft"
                    @click.stop="discardDraft"
                  >
                    ×
                  </button>
                </li>
                <li
                  v-for="e in fileEntries"
                  :key="e.path"
                  class="group flex items-center rounded-lg text-xs font-mono transition-all hover:bg-base-200/60"
                  :class="editorPath === e.path ? 'bg-primary/8' : ''"
                >
                  <button
                    type="button"
                    class="flex-1 min-w-0 flex items-center gap-2 px-2.5 py-1.5 text-left"
                    :class="editorPath === e.path ? 'text-primary' : 'text-base-content/70'"
                    @click="openEntry(e)"
                  >
                    <span class="opacity-40 shrink-0 text-[0.58rem]">{{ e.isDir ? "▸" : "·" }}</span>
                    <span class="truncate">{{ e.name }}</span>
                    <span v-if="e.isDir" class="ml-auto text-[0.5rem] opacity-25 shrink-0">dir</span>
                  </button>
                  <button
                    type="button"
                    class="shrink-0 px-2 py-1.5 text-[0.7rem] opacity-0 group-hover:opacity-60 hover:!opacity-100 hover:text-error transition-opacity"
                    title="Delete"
                    @click.stop="deleteEntry(e)"
                  >
                    ×
                  </button>
                </li>
              </ul>
            </div>

            <div class="flex-1 flex flex-col gap-3 min-h-0 min-w-0">
              <div class="flex items-center gap-3 shrink-0 flex-wrap">
                <span class="text-[0.6rem] font-mono text-base-content/50 truncate max-w-[50%]">
                  {{ editorPath || draftPath || "—" }}
                </span>
                <button
                  type="button"
                  class="btn-ghost-primary btn-sm font-mono text-xs"
                  :disabled="(!editorPath && !draftPath) || editorBinary"
                  @click="saveFile"
                >
                  Save
                </button>
                <span v-if="editorBinary" class="text-[0.62rem] font-mono text-warning/60">
                  Binary — view only
                </span>
                <span
                  v-if="fileSaved"
                  class="text-[0.62rem] font-mono text-success/70 animate-fade-in"
                >
                  Saved ✓
                </span>
                <span
                  v-if="(editorPath || draftPath) && !editorBinary && !fileSaved"
                  class="text-[0.58rem] font-mono text-base-content/25"
                >
                  Shift+S to save
                </span>
              </div>
              <textarea
                v-model="editorContent"
                class="flex-1 textarea surface input-minerva font-mono text-xs leading-[1.7] resize-none"
                style="min-height: 280px"
                :disabled="(!editorPath && !draftPath) || editorBinary"
                placeholder="Open a file from the list, or click + File to create one…"
                @keydown="handleEditorKey"
              />
            </div>
          </div>
          <p
            v-if="fileErr"
            class="text-xs font-mono text-error/80 px-3 py-2 rounded-lg bg-error/10 border border-error/20 shrink-0"
          >
            ⚠ {{ fileErr }}
          </p>
        </section>

        <section
          v-show="!isLg && tab === 'chat'"
          class="lg:hidden flex flex-col flex-1 min-h-0 overflow-hidden animate-fade-in"
        >
          <ChatPanel />
        </section>
      </main>
    </div>

    <aside
      class="hidden lg:flex flex-col w-[380px] xl:w-[400px] shrink-0 border-l border-subtle bg-base-100 min-h-0"
    >
      <div class="px-4 pt-4 pb-2 border-b border-subtle shrink-0">
        <p class="text-[0.55rem] uppercase tracking-[0.2em] text-base-content/45">Agent</p>
        <p class="font-display text-lg text-base-content leading-tight">Chat</p>
      </div>
      <div class="flex-1 min-h-0 overflow-hidden min-w-0">
        <ChatPanel compact />
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import ChatPanel from "../components/ChatPanel.vue";
import {
  deletePath,
  getBootstrapStatus,
  getResolvedApiOrigin,
  listFiles,
  logout,
  mkdir,
  pingHealth,
  readFile,
  seedBootstrap,
  sqliteQuery,
  sqliteTables,
  writeFile,
} from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const tab = ref<"chat" | "sqlite" | "files">("sqlite");
const apiOk = ref<boolean | null>(null);
const apiHint = ref("…");
let healthTimer: ReturnType<typeof setInterval> | undefined;
const isLg = ref(false);
let mqRemove: (() => void) | undefined;

const navItemsAll = [
  { id: "chat" as const, sym: "›", label: "Chat" },
  { id: "sqlite" as const, sym: "≡", label: "SQLite" },
  { id: "files" as const, sym: "⊞", label: "Files" },
];
const navItems = computed(() =>
  isLg.value ? navItemsAll.filter((i) => i.id !== "chat") : navItemsAll,
);

async function refreshHealth() {
  apiOk.value = await pingHealth();
}

// ── SQLite ──
const DEFAULT_SQL =
  "SELECT name AS table_name\nFROM sqlite_master\nWHERE type = 'table'\n  AND name NOT LIKE 'sqlite_%'\nORDER BY name;";

const tables = ref<string[]>([]);
const sqlInput = ref(DEFAULT_SQL);
const sqlResult = ref<{ columns: string[]; rows: Record<string, unknown>[]; truncated: boolean } | null>(null);
const sqlErr = ref("");
const sqlBusy = ref(false);
const sqlLoading = ref(false);

function resetDefaultQuery() {
  sqlInput.value = DEFAULT_SQL;
}

async function loadTables() {
  sqlLoading.value = true;
  try {
    tables.value = await sqliteTables();
    sqlErr.value = "";
    if (sqlResult.value === null) {
      await runSql();
    }
  } catch (e) {
    sqlErr.value = e instanceof Error ? e.message : "Error";
  } finally {
    sqlLoading.value = false;
  }
}

function insertTable(name: string) {
  sqlInput.value = `SELECT *\nFROM ${name}\nLIMIT 50;`;
}

async function runSql() {
  const query = sqlInput.value.trim();
  if (!query) return;
  sqlErr.value = "";
  sqlResult.value = null;
  sqlBusy.value = true;
  try {
    sqlResult.value = await sqliteQuery(query);
  } catch (e) {
    sqlErr.value = e instanceof Error ? e.message : "Error";
  } finally {
    sqlBusy.value = false;
  }
}

function formatCell(v: unknown) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  const s = String(v);
  return s.length > 300 ? s.slice(0, 300) + "…" : s;
}

// ── Files ──
const filePath = ref("");
const fileEntries = ref<{ name: string; path: string; isDir: boolean }[]>([]);
const editorPath = ref("");
const editorContent = ref("");
const editorBinary = ref(false);
const fileErr = ref("");
const fileSaved = ref(false);
const draftPath = ref("");

const bootstrap = ref<{ name: string; present: boolean; size: number; mtime: number }[]>([]);
const bootstrapLoading = ref(false);
const bootstrapBusy = ref(false);
const bootstrapMsg = ref("");

async function refreshBootstrap() {
  bootstrapLoading.value = true;
  try {
    const res = await getBootstrapStatus();
    bootstrap.value = res.files;
  } catch (e) {
    fileErr.value = e instanceof Error ? e.message : "Error";
  } finally {
    bootstrapLoading.value = false;
  }
}

async function restoreBootstrap() {
  bootstrapBusy.value = true;
  bootstrapMsg.value = "";
  fileErr.value = "";
  try {
    const added = await seedBootstrap();
    bootstrapMsg.value = added.length
      ? `Restored ${added.length} file${added.length === 1 ? "" : "s"}: ${added.join(", ")}`
      : "All bootstrap files already present.";
    setTimeout(() => (bootstrapMsg.value = ""), 4000);
    await refreshBootstrap();
    await refreshFiles();
  } catch (e) {
    fileErr.value = e instanceof Error ? e.message : "Error";
  } finally {
    bootstrapBusy.value = false;
  }
}

async function openBootstrap(b: { name: string; present: boolean }) {
  if (!b.present) return;
  filePath.value = "";
  draftPath.value = "";
  await refreshFiles();
  await openEntry({ path: b.name, isDir: false });
}

const draftName = computed(() => draftPath.value.split("/").pop() || "");

function joinPath(dir: string, name: string) {
  return dir ? `${dir}/${name}` : name;
}

function newFile() {
  const name = window.prompt("New file name (relative to current folder):", "untitled.txt");
  if (!name) return;
  const trimmed = name.trim();
  if (!trimmed) return;
  draftPath.value = joinPath(filePath.value, trimmed);
  editorPath.value = "";
  editorBinary.value = false;
  editorContent.value = "";
  fileErr.value = "";
}

function discardDraft() {
  draftPath.value = "";
  editorContent.value = "";
}

async function newFolder() {
  const name = window.prompt("New folder name:", "new-folder");
  if (!name) return;
  const trimmed = name.trim();
  if (!trimmed) return;
  fileErr.value = "";
  try {
    await mkdir(joinPath(filePath.value, trimmed));
    await refreshFiles();
  } catch (e) {
    fileErr.value = e instanceof Error ? e.message : "Error";
  }
}

async function deleteEntry(e: { name: string; path: string; isDir: boolean }) {
  const label = e.isDir ? `folder '${e.name}' and everything inside it` : `file '${e.name}'`;
  if (!window.confirm(`Delete ${label}? This cannot be undone.`)) return;
  fileErr.value = "";
  try {
    await deletePath(e.path);
    if (editorPath.value === e.path) {
      editorPath.value = "";
      editorContent.value = "";
    }
    await refreshFiles();
  } catch (err) {
    fileErr.value = err instanceof Error ? err.message : "Error";
  }
}

async function refreshFiles() {
  fileErr.value = "";
  try {
    const res = await listFiles(filePath.value);
    if (res.type === "directory") fileEntries.value = res.entries;
  } catch (e) {
    fileErr.value = e instanceof Error ? e.message : "Error";
  }
}

async function openEntry(e: { path: string; isDir: boolean }) {
  fileErr.value = "";
  draftPath.value = "";
  if (e.isDir) {
    filePath.value = e.path;
    editorPath.value = "";
    editorContent.value = "";
    return;
  }
  try {
    const r = await readFile(e.path);
    editorPath.value = r.path;
    editorBinary.value = r.binary;
    editorContent.value = r.text;
  } catch (e) {
    fileErr.value = e instanceof Error ? e.message : "Error";
  }
}

async function goUp() {
  if (!filePath.value) return;
  const parts = filePath.value.replace(/\\/g, "/").split("/").filter(Boolean);
  parts.pop();
  filePath.value = parts.join("/");
  editorPath.value = "";
  editorContent.value = "";
  draftPath.value = "";
}

async function saveFile() {
  if (editorBinary.value) return;
  const target = editorPath.value || draftPath.value;
  if (!target) return;
  fileErr.value = "";
  try {
    await writeFile(target, editorContent.value);
    if (draftPath.value) {
      editorPath.value = draftPath.value;
      draftPath.value = "";
      await refreshFiles();
    }
    fileSaved.value = true;
    setTimeout(() => (fileSaved.value = false), 2000);
  } catch (e) {
    fileErr.value = e instanceof Error ? e.message : "Error";
  }
}

function handleEditorKey(e: KeyboardEvent) {
  if (e.key === "s" && e.shiftKey && !e.ctrlKey && !e.metaKey) {
    e.preventDefault();
    saveFile();
  }
}

watch(filePath, () => {
  void refreshFiles();
});

onMounted(async () => {
  const mq = window.matchMedia("(min-width: 1024px)");
  isLg.value = mq.matches;
  if (mq.matches && tab.value === "chat") tab.value = "sqlite";
  const onMq = () => {
    isLg.value = mq.matches;
    if (mq.matches && tab.value === "chat") tab.value = "sqlite";
  };
  mq.addEventListener("change", onMq);
  mqRemove = () => mq.removeEventListener("change", onMq);

  apiHint.value = getResolvedApiOrigin();
  await refreshHealth();
  healthTimer = setInterval(refreshHealth, 20000);
  await loadTables();
  await refreshFiles();
  await refreshBootstrap();
});

onUnmounted(() => {
  mqRemove?.();
  if (healthTimer) clearInterval(healthTimer);
});

async function doLogout() {
  await logout();
  await router.push("/login");
}
</script>