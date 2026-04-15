import { createRouter, createWebHistory } from "vue-router";
import { session as checkSession } from "./api";
import Login from "./views/Login.vue";
import Workbench from "./views/Workbench.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/app" },
    { path: "/login", component: Login, meta: { public: true } },
    { path: "/app", component: Workbench },
  ],
});

router.beforeEach(async (to) => {
  if (to.meta.public) return true;
  const ok = await checkSession();
  if (!ok) return { path: "/login", query: { next: to.fullPath } };
  return true;
});
