<template>
  <div class="relative min-h-screen flex items-center justify-center p-5 overflow-hidden bg-base-100">
    <div class="bg-dots absolute inset-0 pointer-events-none" />

    <div
      class="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] rounded-full pointer-events-none"
      style="background: radial-gradient(circle, rgba(212, 84, 44, 0.06) 0%, transparent 70%)"
    />

    <div class="relative w-full max-w-[360px] animate-slide-up">
      <div class="text-center mb-10 space-y-2.5">
        <div class="inline-flex items-center gap-2 mb-1">
          <span class="w-5 h-5 rounded-full flex items-center justify-center text-[0.55rem] font-bold bg-primary text-primary-content">
            M
          </span>
          <span class="text-[0.6rem] uppercase tracking-[0.3em] text-base-content/45">Minerva</span>
        </div>
        <h1 class="font-display italic text-[3.2rem] text-base-content leading-none text-glow">
          Workbench
        </h1>
        <p class="text-xs text-base-content/45 tracking-wide">
          Agent runtime console
        </p>
      </div>

      <div class="surface overflow-hidden bg-base-100/90 backdrop-blur-md">
        <div class="px-5 py-3 border-b border-subtle flex items-center justify-between">
          <span class="text-[0.58rem] uppercase tracking-[0.2em] text-base-content/40">
            API status
          </span>
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
            <span class="text-[0.62rem] font-mono text-base-content/55 truncate max-w-[230px]">
              {{ apiOk === null ? "checking…" : apiOk ? "reachable" : "unreachable" }}
              <span class="text-base-content/35 mx-1">·</span>
              {{ apiHint }}
            </span>
          </div>
        </div>

        <form class="p-5 space-y-4" @submit.prevent="submit">
          <div class="space-y-1.5">
            <label class="text-[0.58rem] uppercase tracking-[0.2em] text-base-content/40">
              Username
            </label>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              class="input input-bordered w-full text-sm input-minerva"
              placeholder="admin"
              required
            />
          </div>

          <div class="space-y-1.5">
            <label class="text-[0.58rem] uppercase tracking-[0.2em] text-base-content/40">
              Password
            </label>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              class="input input-bordered w-full text-sm input-minerva"
              required
            />
          </div>

          <div
            v-if="err"
            class="text-xs font-mono text-error py-2 px-3 rounded-lg bg-error/10 border border-error/25 leading-relaxed"
          >
            ⚠ {{ err }}
          </div>

          <button
            type="submit"
            class="btn-ghost-primary w-full mt-1 text-sm font-medium tracking-wide"
            :disabled="loading"
          >
            <span v-if="loading" class="loading loading-spinner loading-sm" />
            <span v-else>Continue →</span>
          </button>
        </form>
      </div>

      <p class="mt-6 text-center text-[0.58rem] text-base-content/40 leading-relaxed">
        Use the same hostname for UI &amp; API<br />
        (both <span class="text-base-content/55">localhost</span> or both
        <span class="text-base-content/55">127.0.0.1</span>) for session cookies.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getResolvedApiOrigin, login, pingHealth } from "../api";

const router = useRouter();
const route = useRoute();
const username = ref("");
const password = ref("");
const err = ref("");
const loading = ref(false);
const apiOk = ref<boolean | null>(null);
const apiHint = ref("…");

onMounted(async () => {
  apiHint.value = getResolvedApiOrigin();
  apiOk.value = await pingHealth();
});

async function submit() {
  err.value = "";
  loading.value = true;
  try {
    await login(username.value, password.value);
    const next = typeof route.query.next === "string" ? route.query.next : "/app";
    await router.replace(next);
  } catch (e) {
    err.value = e instanceof Error ? e.message : "Login failed";
  } finally {
    loading.value = false;
  }
}
</script>
