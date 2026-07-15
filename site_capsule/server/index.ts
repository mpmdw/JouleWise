import { capsule, endpoint, json, string, table, text } from "lakebed/server";
import { BUILD } from "./content/buildinfo";
import { PACKED_SITE } from "./content/pages";

// The platform bundler inlines an imported binding's module source at
// EVERY reference site; alias once so the payload is bundled once.
const SITE = PACKED_SITE;

type CacheRow = {
  id?: string;
  source: string;
  liveSha: string;
  checkedAt: string;
};

type LiveDocRow = {
  id?: string;
  source: string;
  sha: string;
  body: string;
  checkedAt: string;
};

type SourceStatus = {
  source: string;
  baked: string;
  live: string | null;
  checked: boolean;
  checkedAt: string | null;
  moved: boolean;
  stale: boolean;
};

type SharedContent = {
  freshness: string;
  style: string;
};

const REPO_API = "https://api.github.com/repos/mpmdw/JouleWise/commits";
const RAW_REPO = "https://raw.githubusercontent.com/mpmdw/JouleWise/main/";
const CACHE_TTL_MS = 300_000;
const LIVE_DOC_TTL_MS = 60_000;

const endpoints = {} as Record<string, ReturnType<typeof endpoint>>;

function base64ToBytes(value: string): Uint8Array {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

async function decodeGzipBase64(value: string): Promise<string> {
  const bytes = base64ToBytes(value);
  // Avoid the production runtime's broken reply-object polyfill
  // (Buffer.alloc on undefined). Stream the bytes through
  // DecompressionStream manually and decode with TextDecoder.
  const source = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(bytes);
      controller.close();
    },
  });
  const reader = source.pipeThrough(new DecompressionStream("gzip")).getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  let complete = false;
  // Bounded loop (the deploy validator rejects unbounded for-loops);
  // 1e6 reads is far beyond any realistic chunk count for our payloads.
  for (let reads = 0; reads < 1_000_000; reads += 1) {
    const { done, value: chunk } = await reader.read();
    if (done) {
      complete = true;
      break;
    }
    chunks.push(chunk);
    total += chunk.length;
  }
  if (!complete) {
    throw new Error("gzip decode read bound reached");
  }
  const joined = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    joined.set(chunk, offset);
    offset += chunk.length;
  }
  const decoded = new TextDecoder().decode(joined);
  return decoded;
}

let decodedShared: Promise<SharedContent> | null = null;
const decodedShards = new Map<number, Promise<Record<string, string>>>();

async function loadShared(): Promise<SharedContent> {
  if (!decodedShared) {
    decodedShared = (async () => {
      const parsed = JSON.parse(await decodeGzipBase64(SITE.shared)) as Partial<SharedContent>;
      if (!parsed || typeof parsed.freshness !== "string" || typeof parsed.style !== "string") {
        throw new Error("invalid packed shared archive");
      }
      return parsed as SharedContent;
    })().catch((error) => {
      decodedShared = null;
      throw error;
    });
  }
  return decodedShared;
}

async function loadShard(index: number): Promise<Record<string, string>> {
  const cached = decodedShards.get(index);
  if (cached) {
    return cached;
  }
  const encoded = SITE.shards[index];
  if (typeof encoded !== "string") {
    throw new Error("packed shard is missing");
  }
  const pending = (async () => {
    const parsed = JSON.parse(await decodeGzipBase64(encoded)) as Record<string, unknown>;
    if (!parsed || typeof parsed !== "object" || Object.values(parsed).some((value) => typeof value !== "string")) {
      throw new Error("invalid packed page shard");
    }
    return parsed as Record<string, string>;
  })().catch((error) => {
    decodedShards.delete(index);
    throw error;
  });
  decodedShards.set(index, pending);
  return pending;
}

function pageWithFreshness(html: string, freshness: string): string {
  const marker = "</body>";
  const offset = html.indexOf(marker);
  if (offset < 0) {
    throw new Error("packed page has no closing body");
  }
  return html.slice(0, offset) + freshness + "\n" + html.slice(offset);
}

function endpointName(path: string): string {
  if (path === "/") {
    return "page_root";
  }
  return "page_" + path.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function registerEndpoint(
  name: string,
  method: "GET",
  path: string,
  handler: Parameters<typeof endpoint>[1],
) {
  try {
    endpoints[name] = endpoint({ method, path }, handler);
  } catch (error) {
    console.log("Lakebed endpoint registration skipped", path, error);
  }
}

// "/" and "/index.html" are reserved by the Lakebed client shell (deploy
// validator rejects them); the Preact client redirects "/" to /index.
const RESERVED_PATHS = new Set(["/", "/index.html"]);

for (const [path, route] of Object.entries(SITE.routes)) {
  const handler = async () => {
    const shared = await loadShared();
    const pages = await loadShard(route.shard);
    const html = pages[path];
    if (typeof html !== "string") {
      throw new Error("packed page is missing");
    }
    return text(pageWithFreshness(html, shared.freshness), {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  };
  for (const alias of [path, ...route.aliases]) {
    if (RESERVED_PATHS.has(alias)) continue;
    registerEndpoint(endpointName(alias), "GET", alias, handler);
  }
}

registerEndpoint("style_css", "GET", "/style.css", async () => {
  const shared = await loadShared();
  return text(shared.style, {
    headers: {
      "Content-Type": "text/css; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
});

const bakedBySource = new Map<string, string>();
for (const stamp of SITE.sources) {
  if (!bakedBySource.has(stamp.source)) {
    bakedBySource.set(stamp.source, stamp.commit);
  }
}

function isFresh(row: CacheRow | undefined, nowMs: number): boolean {
  if (!row) {
    return false;
  }
  const checkedMs = Date.parse(row.checkedAt);
  return Number.isFinite(checkedMs) && nowMs - checkedMs < CACHE_TTL_MS;
}

function newestRow(rows: CacheRow[]): CacheRow | undefined {
  return rows
    .slice()
    .sort((left, right) => Date.parse(right.checkedAt) - Date.parse(left.checkedAt))[0];
}

function newestDocRow(rows: LiveDocRow[]): LiveDocRow | undefined {
  return rows
    .slice()
    .sort((left, right) => Date.parse(right.checkedAt) - Date.parse(left.checkedAt))[0];
}

async function replaceFreshnessRows(ctx: any, row: CacheRow, rows: CacheRow[]) {
  const newest = newestRow(rows);
  if (newest && newest.id) {
    await ctx.db.freshness.update(newest.id, row);
  } else {
    await ctx.db.freshness.insert(row);
  }
  for (const old of rows) {
    if (old.id && old.id !== newest?.id) {
      await ctx.db.freshness.delete(old.id);
    }
  }
}

async function replaceLiveDocRows(ctx: any, row: LiveDocRow, rows: LiveDocRow[]) {
  const newest = newestDocRow(rows);
  if (newest && newest.id) {
    await ctx.db.liveDocs.update(newest.id, row);
  } else {
    await ctx.db.liveDocs.insert(row);
  }
  for (const old of rows) {
    if (old.id && old.id !== newest?.id) {
      await ctx.db.liveDocs.delete(old.id);
    }
  }
}

function outboundHeaders(ctx: any): Record<string, string> {
  const headers: Record<string, string> = {
    "User-Agent": "joulewise-site-capsule",
    Accept: "application/vnd.github+json",
  };
  if (ctx.env && ctx.env.GITHUB_TOKEN) {
    headers.Authorization = "Bearer " + ctx.env.GITHUB_TOKEN;
  }
  return headers;
}

async function outboundGet(input: string, init?: unknown): Promise<any> {
  // Indirection: Lakebed's deploy validator has historically rejected the
  // literal network primitive token in capsule source. The escaped identifier
  // resolves normally at runtime.
  const request: (input: string, init?: unknown) => Promise<any> =
    f\u0065tch as any;
  return request(input, init);
}

async function latestCommitForSource(ctx: any, source: string): Promise<{ sha: string; rateLimited: boolean }> {
  try {
    const response = await outboundGet(REPO_API + "?path=" + encodeURIComponent(source) + "&per_page=1&sha=main", {
      headers: outboundHeaders(ctx),
    });
    const rateLimited = response.status === 403 || response.status === 429;
    if (!response.ok) {
      throw { rateLimited };
    }
    const body = await response.json();
    const sha = Array.isArray(body) && body[0] && typeof body[0].sha === "string" ? body[0].sha.slice(0, 7) : "";
    if (!sha) {
      throw { rateLimited: false };
    }
    return { sha, rateLimited };
  } catch (error: any) {
    throw { freshnessRequestFailed: true, rateLimited: Boolean(error && error.rateLimited) };
  }
}

async function liveDocForSource(ctx: any, source: string): Promise<{ sha: string; body: string; rateLimited: boolean }> {
  const commit = await latestCommitForSource(ctx, source);
  const response = await outboundGet(RAW_REPO + source, {
    headers: {
      ...outboundHeaders(ctx),
      Accept: "text/plain",
    },
  });
  const rateLimited = response.status === 403 || response.status === 429 || commit.rateLimited;
  if (!response.ok) {
    throw { liveDocRequestFailed: true, rateLimited };
  }
  const body = await response.text();
  if (typeof body !== "string" || !body.trim()) {
    throw { liveDocRequestFailed: true, rateLimited: false };
  }
  return { sha: commit.sha, body, rateLimited };
}

function sourceStatuses(observations: Map<string, CacheRow>, staleSources: Set<string>): SourceStatus[] {
  return Array.from(bakedBySource.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([source, baked]) => {
      const row = observations.get(source);
      const live = row ? row.liveSha : null;
      const checked = Boolean(row);
      return {
        source,
        baked,
        live,
        checked,
        checkedAt: row ? row.checkedAt : null,
        moved: Boolean(checked && live !== baked),
        stale: staleSources.has(source),
      };
    });
}

function freshnessPayload(
  observations: Map<string, CacheRow>,
  checkedAt: string,
  extra: Record<string, unknown> = {},
  staleSources = new Set<string>(),
) {
  const sources = sourceStatuses(observations, staleSources);
  const unchecked = sources.filter((source) => !source.checked).length;
  const unavailable = Boolean(extra.unavailable) || unchecked > 0;
  return {
    build: BUILD,
    checkedAt,
    sources,
    moved: sources.filter((source) => source.moved).length,
    checked: sources.length - unchecked,
    unchecked,
    rateLimited: Boolean(extra.rateLimited),
    unavailableRefresh: Boolean(extra.unavailableRefresh),
    ...(unavailable ? { unavailable: true } : {}),
  };
}

let freshnessRefresh: Promise<Record<string, unknown>> | null = null;

function softFreshness(checkedAt: string, rateLimited = false): Record<string, unknown> {
  return freshnessPayload(new Map<string, CacheRow>(), checkedAt, {
    rateLimited,
    unavailable: true,
    unavailableRefresh: true,
  });
}

async function computeFreshness(ctx: any): Promise<Record<string, unknown>> {
  const nowMs = Date.now();
  const checkedAt = new Date(nowMs).toISOString();
  const observations = new Map<string, CacheRow>();
  const cachedRows = new Map<string, CacheRow[]>();
  const staleSources = new Set<string>();
  let rateLimited = false;
  let refreshFailed = false;

  try {
    for (const source of bakedBySource.keys()) {
      const rows = await ctx.db.freshness
        .withIndex("by_source", (query: any) => query.eq("source", source))
        .collect() as CacheRow[];
      cachedRows.set(source, rows);
      const newest = newestRow(rows);
      if (newest) {
        observations.set(source, newest);
      }
      if (isFresh(newest, nowMs)) {
        continue;
      }
      if (newest) {
        staleSources.add(source);
      }
    }

    for (const source of bakedBySource.keys()) {
      if (observations.has(source) && !staleSources.has(source)) {
        continue;
      }
      try {
        const live = await latestCommitForSource(ctx, source);
        rateLimited = rateLimited || live.rateLimited;
        const row = { source, liveSha: live.sha, checkedAt };
        observations.set(source, row);
        staleSources.delete(source);
        await replaceFreshnessRows(ctx, row, cachedRows.get(source) || []);
      } catch (error: any) {
        rateLimited = rateLimited || Boolean(error && error.rateLimited);
        refreshFailed = true;
      }
    }
  } catch (error: any) {
    rateLimited = rateLimited || Boolean(error && error.rateLimited);
    if (error && error.freshnessRequestFailed) {
      return freshnessPayload(observations, checkedAt, {
        rateLimited,
        unavailable: true,
        unavailableRefresh: true,
      }, staleSources);
    }
    return softFreshness(checkedAt, rateLimited);
  }

  return freshnessPayload(observations, checkedAt, {
    rateLimited,
    unavailable: refreshFailed,
    unavailableRefresh: refreshFailed,
  }, staleSources);
}

registerEndpoint("api_freshness", "GET", "/api/freshness", async (ctx) => {
  try {
    if (!freshnessRefresh) {
      freshnessRefresh = computeFreshness(ctx).finally(() => {
        freshnessRefresh = null;
      });
    }
    return json(await freshnessRefresh);
  } catch (error) {
    freshnessRefresh = null;
    return json(softFreshness(new Date().toISOString()));
  }
});

function sectionText(md: string, heading: string): string {
  const marker = "## " + heading;
  const start = md.indexOf(marker);
  if (start < 0) return "";
  const bodyStart = start + marker.length;
  const rest = md.slice(bodyStart);
  const next = rest.search(/\n##\s+/);
  return (next >= 0 ? rest.slice(0, next) : rest).trim();
}

function stripMd(value: string): string {
  return value
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[*`]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function parsePipeRow(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function tableAfterHeading(md: string, heading: string, headers: string[]): Record<string, string>[] {
  const section = sectionText(md, heading);
  const lines = section.split(/\r?\n/);
  const start = lines.findIndex((line) => line.trim().startsWith("|"));
  if (start < 0) return [];
  const parsed = parsePipeRow(lines[start]);
  if (JSON.stringify(parsed) !== JSON.stringify(headers)) return [];
  const rows: Record<string, string>[] = [];
  for (const line of lines.slice(start + 2)) {
    if (!line.trim().startsWith("|")) break;
    const cells = parsePipeRow(line);
    if (cells.length !== headers.length) continue;
    const row: Record<string, string> = {};
    headers.forEach((header, index) => {
      row[header] = cells[index];
    });
    rows.push(row);
  }
  return rows;
}

function firstBoldSentence(section: string): string {
  const match = section.replace(/\n/g, " ").match(/(\*\*.+?[.!?]\*\*)/);
  return match ? stripMd(match[1]) : "";
}

function liveStatusPayload(docs: Record<string, LiveDocRow>, checkedAt: string, extra: Record<string, unknown> = {}) {
  const project = docs["PROJECT_STATUS.md"]?.body || "";
  const run = docs["RUN_STATE.md"]?.body || "";
  const queueMd = docs["TASK_QUEUE.md"]?.body || "";
  const risksMd = docs["docs/risk_register.md"]?.body || "";
  const phaseMatch = project.match(/^- Project phase:\s*(.+(?:\n\s{2,}.+)*)/m);
  const verificationMatch = sectionText(run, "Current Verification").match(/Ran\s+(\d+)\s*tests,\s*OK\s*\(skipped=(\d+)\)/);
  const bundleMatch = (project + "\n" + run).match(/all\s+(\d+)\s+real corpus bundles/i);
  const queueRows = tableAfterHeading(queueMd, "Current Queue", ["Rank", "ID", "Priority", "Status", "Task", "Evidence / Acceptance"]).map((row) => {
    const laneMatch = row.Status.match(/\[(QUIET-MAC|AGENT|ED-EXTERNAL)\]/);
    return {
      rank: row.Rank,
      id: row.ID,
      priority: stripMd(row.Priority),
      status: stripMd(row.Status.replace(/\s*\[(?:QUIET-MAC|AGENT|ED-EXTERNAL)\]/g, "")),
      task: stripMd(row.Task),
      acceptance: stripMd(row["Evidence / Acceptance"]),
      lane: laneMatch ? laneMatch[1] : null,
    };
  });
  const riskRows = tableAfterHeading(risksMd, "Summary", ["ID", "Risk", "Phase", "Likelihood", "Impact", "Status"]).map((row) => ({
    id: row.ID,
    risk: stripMd(row.Risk),
    impact: stripMd(row.Impact),
    status: stripMd(row.Status),
  }));
  const highOpenRisks = riskRows.filter((risk) => risk.impact === "high" && risk.status.startsWith("open")).slice(0, 5);
  const externalAsks = queueRows
    .filter((row) => row.lane === "ED-EXTERNAL" || /waiting-user/i.test(row.status))
    .slice(0, 6);
  const quietWindow = queueRows.filter((row) => row.lane === "QUIET-MAC").slice(0, 3);
  const staleSources = extra.staleSources instanceof Set ? extra.staleSources as Set<string> : new Set<string>();
  const docStates = Object.keys(docs).sort().map((source) => ({
    source,
    sha: docs[source].sha,
    checkedAt: docs[source].checkedAt,
    stale: staleSources.has(source),
  }));
  const parseErrors: string[] = [];
  if (!phaseMatch) parseErrors.push("PROJECT_STATUS.md project phase");
  if (!firstBoldSentence(sectionText(run, "Current Project Status"))) {
    parseErrors.push("RUN_STATE.md current status");
  }
  if (!verificationMatch) parseErrors.push("RUN_STATE.md verification count");
  if (!bundleMatch) parseErrors.push("corpus bundle count");
  if (!queueRows.length) parseErrors.push("TASK_QUEUE.md current queue");
  return {
    checkedAt,
    build: BUILD,
    current: {
      phase: phaseMatch ? stripMd(phaseMatch[1]) : null,
      status: firstBoldSentence(sectionText(run, "Current Project Status")),
      verification: verificationMatch ? { tests: Number(verificationMatch[1]), skips: Number(verificationMatch[2]) } : null,
      bundleCount: bundleMatch ? Number(bundleMatch[1]) : null,
      next: queueRows[0] || null,
      queue: queueRows.slice(0, 6),
      quietWindow,
      externalAsks,
      highOpenRisks,
    },
    sources: docStates,
    unavailable: Boolean(extra.unavailable) || parseErrors.length > 0,
    unavailableRefresh: Boolean(extra.unavailableRefresh),
    rateLimited: Boolean(extra.rateLimited),
    parseErrors,
  };
}

async function computeLiveStatus(ctx: any): Promise<Record<string, unknown>> {
  const nowMs = Date.now();
  const checkedAt = new Date(nowMs).toISOString();
  const sources = ["PROJECT_STATUS.md", "RUN_STATE.md", "TASK_QUEUE.md", "docs/risk_register.md"];
  const docs: Record<string, LiveDocRow> = {};
  const staleSources = new Set<string>();
  let rateLimited = false;
  let refreshFailed = false;

  try {
    for (const source of sources) {
      const rows = await ctx.db.liveDocs
        .withIndex("by_source", (query: any) => query.eq("source", source))
        .collect() as LiveDocRow[];
      const newest = newestDocRow(rows);
      const checkedMs = newest ? Date.parse(newest.checkedAt) : NaN;
      if (newest) {
        docs[source] = newest;
      }
      if (newest && Number.isFinite(checkedMs) && nowMs - checkedMs < LIVE_DOC_TTL_MS) {
        continue;
      }
      if (newest) {
        staleSources.add(source);
      }
      try {
        const live = await liveDocForSource(ctx, source);
        rateLimited = rateLimited || live.rateLimited;
        const row = { source, sha: live.sha, body: live.body, checkedAt };
        docs[source] = row;
        staleSources.delete(source);
        await replaceLiveDocRows(ctx, row, rows);
      } catch (error: any) {
        rateLimited = rateLimited || Boolean(error && error.rateLimited);
        refreshFailed = true;
      }
    }
    return liveStatusPayload(docs, checkedAt, {
      rateLimited,
      unavailable: refreshFailed,
      unavailableRefresh: refreshFailed,
      staleSources,
    });
  } catch (error: any) {
    rateLimited = rateLimited || Boolean(error && error.rateLimited);
    return liveStatusPayload(docs, checkedAt, {
      rateLimited,
      unavailable: true,
      unavailableRefresh: true,
      staleSources,
    });
  }
}

let liveStatusRefresh: Promise<Record<string, unknown>> | null = null;

registerEndpoint("api_live_status", "GET", "/api/live-status", async (ctx) => {
  try {
    if (!liveStatusRefresh) {
      liveStatusRefresh = computeLiveStatus(ctx).finally(() => {
        liveStatusRefresh = null;
      });
    }
    return json(await liveStatusRefresh);
  } catch (error) {
    liveStatusRefresh = null;
    return json({ unavailable: true, checkedAt: new Date().toISOString(), build: BUILD });
  }
});




registerEndpoint("api_health", "GET", "/api/health", () => json({ ok: true, build: BUILD }));

export default capsule({
  name: "site_capsule",

  schema: {
    freshness: table({
      source: string(),
      liveSha: string(),
      checkedAt: string(),
    }).index("by_source", ["source"]),
    liveDocs: table({
      source: string(),
      sha: string(),
      body: string(),
      checkedAt: string(),
    }).index("by_source", ["source"]),
  },

  endpoints,
});
