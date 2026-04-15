export function getApiBase(): string {
  if (import.meta.env.DEV) {
    return "";
  }
  const explicit = import.meta.env.VITE_API_BASE_URL;
  if (typeof explicit === "string" && explicit.trim()) {
    return explicit.trim().replace(/\/$/, "");
  }
  if (typeof window === "undefined") {
    return "";
  }
  const port = import.meta.env.VITE_API_PORT || "8900";
  return `${window.location.protocol}//${window.location.hostname}:${port}`;
}
