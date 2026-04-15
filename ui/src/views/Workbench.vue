<template>
  <div class="flex h-screen overflow-hidden bg-base-300 font-mono text-base-content">
    <aside
      class="hidden lg:flex flex-col w-52 border-r border-subtle bg-base-200 shrink-0"
    >
      <div class="px-5 pt-7 pb-5">
        <div class="flex items-center gap-2 mb-3">
          <span
            class="w-4 h-4 rounded-full flex items-center justify-center text-[0.5rem] font-bold text-primary-content shrink-0"
            style="background: #E24D27"
          >M</span>
          <span class="text-[0.55rem] uppercase tracking-[0.3em] text-base-content/40">Minerva</span>
        </div>
        <h1 class="font-display italic text-2xl font-black text-base-content leading-tight">
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
              : 'text-base-content/50 hover:text-base-content/80 hover:bg-white/[0.04]'
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
            <span class="text-[0.58rem] uppercase tracking-wide text-base-content/35">
              {{ apiOk === null ? "checking" : apiOk ? "connected" : "offline" }}
            </span>
          </div>
          <p class="text-[0.58rem] font-mono text-base-content/30 pl-3.5 truncate" :title="apiHint">
            {{ apiHint }}
          </p>
        </div>
        <button
          type="button"
          class="text-[0.62rem] font-mono text-base-content/30 hover:text-primary/70 transition-colors w-full text-left"
          @click="doLogout"
        >
          Disconnect →
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <header
        class="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-subtle bg-base-200 shrink-0"
      >
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <span
            class="w-4 h-4 rounded-full flex items-center justify-center text-[0.5rem] font-bold text-primary-content shrink-0"
            style="background: #E24D27"
          >M</span>
          <span class="font-display italic text-lg font-black text-base-content">Workbench</span>
        </div>
        <div class="flex items-center gap-3">
          <span
            class="w-1.5 h-1.5 rounded-full"
            :class="apiOk === true ? 'bg-success' : apiOk === false ? 'bg-error' : 'bg-base-content/20'"
          />
          <button
            type="button"
            class="text-[0.62rem] font-mono text-base-content/35 hover:text-primary/70 transition-colors"
            @click="doLogout"
          >
            Exit
          </button>
        </div>
      </header>

      <div class="lg:hidden flex border-b border-subtle bg-base-200/60 shrink-0">
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
        <!-- ── Chat ── -->
        <section
          v-show="tab === 'chat'"
          class="flex flex-col flex-1 min-h-0 p-4 sm:p-5 gap-4 animate-fade-in"
        >
          <div class="flex items-end gap-3 shrink-0">
            <div>
              <label class="text-[0.55rem] uppercase tracking-[0.2em] text-base-content/35 block mb-1">
                Session
              </label>
              <input
                v-model="chatSession"
                type="text"
                class="input input-sm w-[200px] input-minerva font-mono text-xs"
                placeholder="default"
              />
            </div>
            <button
              v-if="messages.length > 0"
              type="button"
              class="text-[0.6rem] font-mono text-base-content/25 hover:text-error/60 transition-colors mb-1"
              @click="messages = []"
            >
              Clear
            </button>
          </div>

          <div
            ref="chatScrollRef"
            class="flex-1 min-h-0 overflow-y-auto surface-2 p-4 space-y-4"
          >
            <div
              v-if="messages.length === 0"
              class="flex flex-col items-center justify-center h-full text-center py-16 space-y-3"
            >
              <span
                class="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold text-primary-content opacity-15"
                style="background: #E24D27"
              >M</span>
              <p class="text-xs font-mono text-base-content/35">Send a message to run the agent.</p>
              <p class="text-[0.58rem] font-mono text-base-content/25">
                Enter to send · Shift+Enter for newline
              </p>
            </div>

            <TransitionGroup name="msg">
              <div v-for="(m, i) in messages" :key="i" class="msg-enter-active">
                <div
                  class="flex items-start gap-2.5"
                  :class="m.role === 'user' ? 'flex-row-reverse' : ''"
                >
                  <div
                    class="w-5 h-5 rounded-full shrink-0 flex items-center justify-center text-[0.5rem] font-bold mt-0.5"
                    :class="
                      m.role === 'user'
                        ? 'text-primary-content'
                        : m.role === 'error'
                          ? 'bg-error/20 text-error'
                          : 'bg-white/[0.07] text-base-content/50'
                    "
                    :style="m.role === 'user' ? 'background: #E24D27' : ''"
                  >
                    {{ m.role === "user" ? "U" : m.role === "error" ? "!" : "A" }}
                  </div>
                  <div
                    class="max-w-[min(84%,44rem)] rounded-xl px-3.5 py-2.5 text-sm"
                    :class="
                      m.role === 'user'
                        ? 'bg-primary/10 text-base-content rounded-tr-sm border border-primary/15'
                        : m.role === 'error'
                          ? 'bg-error/10 text-error/85 rounded-tl-sm border border-error/20'
                          : 'bg-white/[0.05] text-base-content/90 rounded-tl-sm border border-white/[0.04]'
                    "
                  >
                    <pre class="whitespace-pre-wrap font-mono text-xs leading-[1.75]">{{ m.text }}</pre>
                  </div>
                </div>
              </div>
            </TransitionGroup>

            <div v-if="chatBusy" class="flex items-start gap-2.5">
              <div class="w-5 h-5 rounded-full shrink-0 flex items-center justify-center text-[0.5rem] mt-0.5 bg-white/[0.07] text-base-content/50">
                A
              </div>
              <div class="rounded-xl rounded-tl-sm px-4 py-3 bg-white/[0.05] border border-white/[0.04] flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-base-content/40 animate-dot-1" />
                <span class="w-1.5 h-1.5 rounded-full bg-base-content/40 animate-dot-2" />
                <span class="w-1.5 h-1.5 rounded-full bg-base-content/40 animate-dot-3" />
              </div>
            </div>
          </div>

          <form class="flex gap-2 items-end shrink-0" @submit.prevent="sendChat">
            <textarea
              v-model="chatInput"
              class="textarea flex-1 input-minerva text-sm leading-relaxed resize-none"
              style="min-height: 72px; max-height: 200px"
              placeholder="Message the agent… (Enter to send)"
              @keydown="handleChatKey"
            />
            <button
              type="submit"
              class="btn-ghost-primary shrink-0 h-[72px] px-5 font-mono text-xs"
              :disabled="chatBusy"
            >
              <span v-if="chatBusy" class="loading loading-spinner loading-xs" />
              <span v-else class="leading-tight">Send<br />→</span>
            </button>
          </form>
        </section>

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
                <tr class="bg-base-300/80">
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
                  class="border-white/[0.025] hover:bg-white/[0.02] transition-colors"
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
          <div class="flex items-center gap-2 shrink-0 pb-3 border-b border-subtle">
            <button
              type="button"
              class="text-[0.62rem] font-mono text-base-content/35 hover:text-primary/70 transition-colors px-2 py-1 rounded border border-subtle hover:border-primary/20"
              :disabled="!filePath"
              @click="goUp"
            >
              ← Up
            </button>
            <span class="font-mono text-xs text-base-content/50 truncate flex-1 min-w-0">
              {{ filePath ? `/ ${filePath}` : "/" }}
            </span>
            <span v-if="editorPath" class="text-[0.58rem] font-mono text-base-content/30 shrink-0 truncate max-w-[160px]">
              {{ editorPath.split("/").pop() }}
            </span>
          </div>

          <div class="flex-1 flex flex-col lg:flex-row gap-4 min-h-0">
            <div class="surface w-full lg:w-52 lg:min-w-[12rem] shrink-0 overflow-auto" style="max-height: 280px">
              <div v-if="fileEntries.length === 0" class="p-5 text-xs font-mono text-base-content/30 text-center">
                Empty directory
              </div>
              <ul class="p-1.5 space-y-px">
                <li v-for="e in fileEntries" :key="e.path">
                  <button
                    type="button"
                    class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-mono text-left transition-all hover:bg-white/[0.04]"
                    :class="editorPath === e.path ? 'text-primary' : 'text-base-content/60'"
                    @click="openEntry(e)"
                  >
                    <span class="opacity-40 shrink-0 text-[0.58rem]">{{ e.isDir ? "▸" : "·" }}</span>
                    <span class="truncate">{{ e.name }}</span>
                    <span v-if="e.isDir" class="ml-auto text-[0.5rem] opacity-25 shrink-0">dir</span>
                  </button>
                </li>
              </ul>
            </div>

            <div class="flex-1 flex flex-col gap-3 min-h-0 min-w-0">
              <div class="flex items-center gap-3 shrink-0 flex-wrap">
                <button
                  type="button"
                  class="btn-ghost-primary btn-sm font-mono text-xs"
                  :disabled="!editorPath || editorBinary"
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
                  v-if="editorPath && !editorBinary && !fileSaved"
                  class="text-[0.58rem] font-mono text-base-content/25"
                >
                  Shift+S to save
                </span>
              </div>
              <textarea
                v-model="editorContent"
                class="flex-1 textarea surface input-minerva font-mono text-xs leading-[1.7] resize-none"
                style="min-height: 280px"
                :disabled="!editorPath || editorBinary"
                placeholder="Open a file from the list…"
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
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import {
  chat,
  getResolvedApiOrigin,
  listFiles,
  logout,
  pingHealth,
  readFile,
  sqliteQuery,
  sqliteTables,
  writeFile,
} from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const tab = ref<"chat" | "sqlite" | "files">("chat");
const apiOk = ref<boolean | null>(null);
const apiHint = ref("…");
let healthTimer: ReturnType<typeof setInterval> | undefined;

const navItems = [
  { id: "chat" as const, sym: "›", label: "Chat" },
  { id: "sqlite" as const, sym: "≡", label: "SQLite" },
  { id: "files" as const, sym: "⊞", label: "Files" },
];

async function refreshHealth() {
  apiOk.value = await pingHealth();
}

// ── Chat ──
const chatSession = ref("");
const chatInput = ref("");
const chatBusy = ref(false);
const messages = ref<{ role: string; text: string }[]>([]);
const chatScrollRef = ref<HTMLElement | null>(null);

function handleChatKey(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChat();
  }
}

async function sendChat() {
  const t = chatInput.value.trim();
  if (!t || chatBusy.value) return;
  chatBusy.value = true;
  messages.value.push({ role: "user", text: t });
  chatInput.value = "";
  await scrollChat();
  try {
    const sid = chatSession.value.trim() || undefined;
    const reply = await chat(t, sid);
    messages.value.push({ role: "assistant", text: reply });
  } catch (e) {
    messages.value.push({ role: "error", text: e instanceof Error ? e.message : "Error" });
  } finally {
    chatBusy.value = false;
    await scrollChat();
  }
}

async function scrollChat() {
  await nextTick();
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight;
  }
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
}

async function saveFile() {
  if (!editorPath.value || editorBinary.value) return;
  fileErr.value = "";
  try {
    await writeFile(editorPath.value, editorContent.value);
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
  apiHint.value = getResolvedApiOrigin();
  await refreshHealth();
  healthTimer = setInterval(refreshHealth, 20000);
  await loadTables();
  await refreshFiles();
});

onUnmounted(() => {
  if (healthTimer) clearInterval(healthTimer);
});

async function doLogout() {
  await logout();
  await router.push("/login");
}
</script>
