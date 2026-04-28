import { nextTick, reactive } from "vue";
import { chat as chatApi } from "./api";

export const chatStore = reactive({
  session: "",
  input: "",
  busy: false,
  messages: [] as { role: string; text: string }[],
});

async function scrollEl(el: HTMLElement | null) {
  await nextTick();
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

export async function sendChatMessage(scrollRef: { value: HTMLElement | null }) {
  const t = chatStore.input.trim();
  if (!t || chatStore.busy) return;
  chatStore.busy = true;
  chatStore.messages.push({ role: "user", text: t });
  chatStore.input = "";
  await scrollEl(scrollRef.value);
  try {
    const sid = chatStore.session.trim() || undefined;
    const reply = await chatApi(t, sid);
    chatStore.messages.push({ role: "assistant", text: reply });
  } catch (e) {
    chatStore.messages.push({
      role: "error",
      text: e instanceof Error ? e.message : "Error",
    });
  } finally {
    chatStore.busy = false;
    await scrollEl(scrollRef.value);
  }
}
