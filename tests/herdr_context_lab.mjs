// Run only in a disposable Herdr pane via test_herdr_context_lab.sh.
// Synthetic Pi events exercise the real extension transport and PTY ownership;
// no model requests, private sessions, or managed integrations are loaded.
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import extension from "../packages/pi/.pi/agent/extensions/herdr-context.ts";

assert.match(process.env.HERDR_SESSION ?? "", /^fm-lab-/);
assert.equal(process.stdin.isTTY, true);
const handlers = {};
let usage = { tokens: 50_000, contextWindow: 200_000, percent: 25 };
const ctx = { mode: "tui", getContextUsage: () => usage };
extension({ on: (event, handler) => { handlers[event] = handler; } });
const emit = (event) => handlers[event]({}, ctx);
function lab(...args) {
  const result = spawnSync(process.env.HERDR_LAB_HELPER, [
    "run", process.env.HERDR_SESSION, ...args,
  ], { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
  if (!result.stdout.trim()) return;
  const response = JSON.parse(result.stdout);
  assert.equal(response.error, undefined);
  return response.result;
}
function pane() { return lab("pane", "get", process.env.HERDR_PANE_ID).pane; }
const originalState = pane().agent_status;
lab("pane", "report-metadata", process.env.HERDR_PANE_ID,
  "--source", "user:context-lab", "--token", "unrelated=preserved");
function check(value) {
  const current = pane();
  assert.equal(current.tokens?.pi_context, value);
  assert.equal(current.tokens?.unrelated, "preserved");
  assert.equal(current.agent_status, originalState);
}
try {
  await emit("session_start"); check("ctx 25.0%");
  await emit("session_before_compact"); check("ctx ?");
  usage = { tokens: null, contextWindow: 200_000, percent: null };
  await emit("session_compact"); check("ctx ?");
  usage = { tokens: 50_000, contextWindow: 100_000, percent: 50 };
  await emit("model_select"); check("ctx 50.0%");
  await emit("session_shutdown"); check(undefined);
  usage = { tokens: 0, contextWindow: 100_000, percent: 0 };
  await emit("session_start"); check("ctx 0.0%");
  // Simulate losing the foreground/abrupt exit: no more heartbeat refreshes.
  // Block this driver while the real server expires the token at its actual TTL.
  spawnSync("sleep", ["31"]);
  check(undefined);
  console.log("CONTEXT_LAB_PASS");
} finally {
  await emit("session_shutdown");
}
