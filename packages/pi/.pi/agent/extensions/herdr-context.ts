import net from "node:net";
import type { ContextUsage, ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const TOKEN = "pi_context";
const SOURCE = "user:pi-context";
const TTL_MS = 30_000;

// Use Pi's current-window estimate, never cumulative session token totals.
export function contextLabel(usage: ContextUsage | undefined): string {
  if (!usage || usage.tokens === null || usage.percent === null ||
      !Number.isFinite(usage.tokens) || usage.tokens < 0 ||
      !Number.isFinite(usage.contextWindow) || usage.contextWindow <= 0 ||
      !Number.isFinite(usage.percent) || usage.percent < 0) return "ctx ?";
  return `ctx ${usage.percent.toFixed(1)}%`;
}

// Bounded, newline-delimited Herdr socket API; no command, path or transcript logging.
export function request(endpoint: string, method: string, params: object): Promise<any> {
  return new Promise((resolve) => {
    let buffer = "";
    const socket = net.createConnection(endpoint);
    const timer = setTimeout(() => finish(undefined), 750);
    function finish(value: unknown) {
      clearTimeout(timer);
      socket.destroy();
      resolve(value);
    }
    socket.on("error", () => finish(undefined));
    socket.on("end", () => finish(undefined));
    socket.on("connect", () => socket.write(`${JSON.stringify({ id: SOURCE, method, params })}\n`));
    socket.on("data", (data) => {
      buffer += data.toString();
      if (buffer.length > 256_000) return finish(undefined);
      const newline = buffer.indexOf("\n");
      if (newline < 0) return;
      try { finish(JSON.parse(buffer.slice(0, newline)).result); }
      catch { finish(undefined); }
    });
  });
}

export default function (pi: ExtensionAPI) {
  const env = process.env;
  if (env.HERDR_ENV !== "1" || !env.HERDR_SOCKET_PATH || !env.HERDR_PANE_ID) return;
  const endpoint = process.platform === "win32"
    ? `\\\\.\\pipe\\${env.HERDR_SOCKET_PATH}` : env.HERDR_SOCKET_PATH;
  const pane_id = env.HERDR_PANE_ID;
  let active = false;
  let compacting = false;
  let context: ExtensionContext | undefined;
  let heartbeat: ReturnType<typeof setInterval> | undefined;
  let queue = Promise.resolve();

  function publish(value: string | null) {
    // Serialize writes, including shutdown clear, so an old value cannot land last.
    queue = queue.then(async () => {
      const result = await request(endpoint, "pane.process_info", { pane_id });
      // Env vars are inherited by children. Only the Pi process actually controlling
      // this pane's PTY may write (not another TUI in a child PTY or a background Pi).
      if (!result?.process_info?.foreground_processes?.some(
        (p: { pid: number }) => p.pid === process.pid,
      )) return;
      await request(endpoint, "pane.report_metadata", {
        pane_id, source: SOURCE, tokens: { [TOKEN]: value }, ttl_ms: TTL_MS,
      });
    }).catch(() => { /* Display-only: unavailable Herdr must not break Pi. */ });
    return queue;
  }

  function refresh(ctx: ExtensionContext) {
    if (!active || ctx.mode !== "tui") return;
    context = ctx;
    let label = "ctx ?";
    try { if (!compacting) label = contextLabel(ctx.getContextUsage()); } catch { /* unknown */ }
    return publish(label);
  }

  pi.on("session_start", (_event, ctx) => {
    if (ctx.mode !== "tui" || !process.stdin.isTTY || !process.stdout.isTTY) return;
    active = true;
    compacting = false;
    if (heartbeat) clearInterval(heartbeat);
    heartbeat = setInterval(() => { if (context) void refresh(context); }, 10_000);
    heartbeat.unref();
    return refresh(ctx);
  });
  for (const event of ["turn_end", "agent_settled", "model_select", "session_tree"] as const) {
    pi.on(event, (_event, ctx) => refresh(ctx));
  }
  pi.on("session_before_compact", (_event, ctx) => {
    compacting = true;
    return refresh(ctx);
  });
  for (const event of ["session_compact", "session_compact_failed"] as const) {
    pi.on(event, (_event, ctx) => {
      compacting = false;
      return refresh(ctx);
    });
  }
  pi.on("session_shutdown", () => {
    if (heartbeat) clearInterval(heartbeat);
    heartbeat = undefined;
    context = undefined;
    if (!active) return;
    active = false;
    return publish(null);
  });
}
