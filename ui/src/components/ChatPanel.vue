<template>
  <div class="flex flex-col h-full min-h-0" :class="compact ? 'p-3 gap-2' : 'p-4 sm:p-5 gap-3'">
    <div class="flex items-end gap-2 shrink-0 flex-wrap">
      <div>
        <label class="text-[0.55rem] uppercase tracking-[0.2em] text-base-content/45 block mb-1">
          Session
        </label>
        <input
          v-model="chatStore.session"
          type="text"
          class="input input-sm w-[min(100%,11rem)] input-minerva font-mono text-xs"
          placeholder="default"
        />
      </div>
      <button
        v-if="chatStore.messages.length > 0"
        type="button"
        class="text-[0.6rem] font-mono text-base-content/35 hover:text-error/70 transition-colors mb-1"
        @click="chatStore.messages = []"
      >
        Clear
      </button>
    </div>

    <div
      ref="chatScrollRef"
      class="flex-1 min-h-0 overflow-y-auto surface-2 p-3 space-y-3"
    >
      <div
        v-if="chatStore.messages.length === 0"
        class="flex flex-col items-center justify-center text-center py-8 space-y-2"
      >
        <span class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold bg-primary text-primary-content shadow-sm">
          M
        </span>
        <p class="text-xs text-base-content/50">Send a message to run the agent.</p>
        <p class="text-[0.58rem] font-mono text-base-content/35">
          Enter to send · Shift+Enter for newline
        </p>
      </div>

      <TransitionGroup name="msg">
        <div v-for="(m, i) in chatStore.messages" :key="i" class="msg-enter-active">
          <div
            class="flex items-start gap-2"
            :class="m.role === 'user' ? 'flex-row-reverse' : ''"
          >
            <div
              class="w-5 h-5 rounded-full shrink-0 flex items-center justify-center text-[0.5rem] font-bold mt-0.5"
              :class="
                m.role === 'user'
                  ? 'bg-primary text-primary-content'
                  : m.role === 'error'
                    ? 'bg-error/15 text-error'
                    : 'bg-base-300/80 text-base-content/55'
              "
            >
              {{ m.role === "user" ? "U" : m.role === "error" ? "!" : "A" }}
            </div>
            <div
              class="max-w-[min(92%,36rem)] rounded-xl px-3 py-2 text-sm"
              :class="
                m.role === 'user'
                  ? 'bg-primary/10 text-base-content rounded-tr-sm border border-primary/20'
                  : m.role === 'error'
                    ? 'bg-error/10 text-error/90 rounded-tl-sm border border-error/25'
                    : 'bg-base-100 text-base-content/90 rounded-tl-sm border border-base-300/80'
              "
            >
              <pre class="whitespace-pre-wrap font-mono text-[0.7rem] leading-relaxed">{{ m.text }}</pre>
            </div>
          </div>
        </div>
      </TransitionGroup>

      <div v-if="chatStore.busy" class="flex items-start gap-2">
        <div
          class="w-5 h-5 rounded-full shrink-0 flex items-center justify-center text-[0.5rem] mt-0.5 bg-base-300/80 text-base-content/50"
        >
          A
        </div>
        <div
          class="rounded-xl rounded-tl-sm px-3 py-2.5 bg-base-100 border border-base-300/80 flex items-center gap-1.5"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-base-content/35 animate-dot-1" />
          <span class="w-1.5 h-1.5 rounded-full bg-base-content/35 animate-dot-2" />
          <span class="w-1.5 h-1.5 rounded-full bg-base-content/35 animate-dot-3" />
        </div>
      </div>
    </div>

    <form class="flex gap-2 items-end shrink-0 pt-1" @submit.prevent="onSubmit">
      <textarea
        v-model="chatStore.input"
        class="textarea flex-1 input-minerva text-sm leading-relaxed resize-none font-sans"
        :style="{ minHeight: compact ? '56px' : '72px', maxHeight: '200px' }"
        placeholder="Message the agent… (Enter to send)"
        @keydown="handleChatKey"
      />
      <button
        type="submit"
        class="btn-ghost-primary shrink-0 font-mono text-xs px-4"
        :class="compact ? 'h-14' : 'h-[72px]'"
        :disabled="chatStore.busy"
      >
        <span v-if="chatStore.busy" class="loading loading-spinner loading-xs" />
        <span v-else class="leading-tight">Send<br />→</span>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { chatStore, sendChatMessage } from "../chatStore";

defineProps<{ compact?: boolean }>();

const chatScrollRef = ref<HTMLElement | null>(null);

function handleChatKey(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    void sendChatMessage(chatScrollRef);
  }
}

function onSubmit() {
  void sendChatMessage(chatScrollRef);
}
</script>
