import assert from "node:assert/strict";
import { test } from "node:test";
import net from "node:net";
import { mkdtemp, rm } from "node:fs/promises";
import extension, { contextLabel, request } from "../packages/pi/.pi/agent/extensions/herdr-context.ts";

const usage = (tokens, contextWindow = 200_000) => ({
  tokens, contextWindow, percent: tokens === null ? null : tokens / contextWindow * 100,
});

test("current context percentage and unavailable values", () => {
  assert.equal(contextLabel(usage(24_680)), "ctx 12.3%");
  assert.equal(contextLabel(usage(0)), "ctx 0.0%");
  assert.equal(contextLabel(usage(240_000)), "ctx 120.0%");
  for (const value of [undefined, usage(null), usage(NaN), usage(-1), usage(1, 0),
    usage(1, Infinity), { ...usage(1), percent: Infinity }]) {
    assert.equal(contextLabel(value), "ctx ?");
  }
});

test("socket framing, pane ownership, lifecycle, heartbeat and cleanup", async (t) => {
  const directory = await mkdtemp(`${process.cwd()}/.context-test-`);
  const endpoint = `${directory}/api.sock`;
  let foreground = true;
  let failure = false;
  const reports = [];
  const server = net.createServer((socket) => {
    let buffer = "";
    socket.on("data", (data) => {
      buffer += data;
      if (!buffer.includes("\n")) return;
      const message = JSON.parse(buffer);
      assert.equal(message.params.pane_id, "w1:p1");
      if (failure) { socket.end('{"error":{"code":"unavailable"}}\n'); return; }
      let result;
      if (message.method === "pane.process_info") {
        result = { process_info: { foreground_processes: [{ pid: foreground ? process.pid : -1 }] } };
      } else {
        assert.equal(message.method, "pane.report_metadata");
        assert.deepEqual(Object.keys(message.params).sort(), ["pane_id", "source", "tokens", "ttl_ms"]);
        assert.equal(message.params.source, "user:pi-context");
        assert.equal(message.params.ttl_ms, 30_000);
        reports.push(message.params.tokens);
        result = {};
      }
      const encoded = JSON.stringify({ result }) + "\n";
      socket.write(encoded.slice(0, 4));
      setImmediate(() => socket.end(encoded.slice(4)));
    });
  });
  await new Promise((resolve) => server.listen(endpoint, resolve));
  t.after(async () => {
    await new Promise((resolve) => server.close(resolve));
    await rm(directory, { recursive: true });
  });
  for (const [key, value] of Object.entries({ HERDR_ENV: "1", HERDR_SOCKET_PATH: endpoint, HERDR_PANE_ID: "w1:p1" })) {
    const old = process.env[key];
    process.env[key] = value;
    t.after(() => { if (old === undefined) delete process.env[key]; else process.env[key] = old; });
  }
  for (const stream of [process.stdin, process.stdout]) {
    const descriptor = Object.getOwnPropertyDescriptor(stream, "isTTY");
    Object.defineProperty(stream, "isTTY", { value: true, configurable: true });
    t.after(() => { if (descriptor) Object.defineProperty(stream, "isTTY", descriptor); else delete stream.isTTY; });
  }
  let beat;
  let cleared = 0;
  t.mock.method(global, "setInterval", (fn, ms) => {
    assert.equal(ms, 10_000); beat = fn; return { unref() {} };
  });
  t.mock.method(global, "clearInterval", () => { cleared++; });
  function harness(mode = "tui") {
    const handlers = {};
    const ctx = { mode, getContextUsage: () => current };
    extension({ on: (event, handler) => { handlers[event] = handler; } });
    return (event, reason) => handlers[event]?.({ reason }, ctx);
  }
  let current = usage(40_000);
  const emit = harness();
  const value = () => reports.at(-1)?.pi_context;
  await emit("session_start", "startup");
  assert.equal(value(), "ctx 20.0%");
  current = usage(50_000);
  await emit("turn_end");
  assert.equal(value(), "ctx 25.0%");
  current = usage(50_000, 100_000);
  await emit("model_select");
  assert.equal(value(), "ctx 50.0%");
  await emit("session_before_compact");
  assert.equal(value(), "ctx ?");
  await emit("session_compact_failed");
  assert.equal(value(), "ctx 50.0%");
  await emit("session_before_compact");
  current = usage(null);
  await emit("session_compact");
  assert.equal(value(), "ctx ?");
  current = usage(1000);
  await emit("agent_settled");
  assert.equal(value(), "ctx 0.5%");
  current = undefined;
  await emit("session_tree");
  assert.equal(value(), "ctx ?");
  current = usage(10_000);
  beat();
  await emit("turn_end"); // Drain heartbeat then event write.
  assert.equal(value(), "ctx 5.0%");

  for (const mode of ["rpc", "json", "print"]) {
    const before = reports.length;
    const child = harness(mode);
    for (const event of ["session_start", "turn_end", "model_select", "session_shutdown"]) await child(event);
    assert.equal(reports.length, before, `${mode} child must not overwrite parent`);
  }
  foreground = false;
  const before = reports.length;
  await emit("turn_end");
  assert.equal(reports.length, before, "inherited pane env is not ownership");
  foreground = true;
  failure = true;
  await emit("turn_end");
  assert.equal(reports.length, before, "API error fails closed");
  failure = false;
  for (const reason of ["new", "resume", "fork", "reload"]) {
    const pending = emit("turn_end");
    await emit("session_shutdown", reason);
    await pending;
    assert.equal(value(), null, "shutdown clear follows any older write");
    current = usage(0);
    await emit("session_start", reason);
    assert.equal(value(), "ctx 0.0%");
  }
  await emit("session_shutdown", "quit");
  const stopped = reports.length;
  beat();
  await emit("session_shutdown", "quit");
  assert.equal(reports.length, stopped);
  assert.equal(cleared, 5);
  assert.equal(await request(`${directory}/absent.sock`, "pane.get", {}), undefined);
});
