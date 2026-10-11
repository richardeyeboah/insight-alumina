type RouteContext = { params: Promise<{ path: string[] }> };

async function forward(request: Request, context: RouteContext) {
  const { path } = await context.params;
  const endpoint = path.join("/");
  const reads = new Set(["session", "metrics", "bookings", "jobs", "summary"]);
  const writes = new Set(["login", "logout", "summary"]);
  const allowed = request.method === "GET" ? reads.has(endpoint) : writes.has(endpoint) || /^jobs\/\d+\/retry$/.test(endpoint);
  if (!allowed) return Response.json({ detail: "Not found" }, { status: 404 });
  const base = process.env.API_BASE_URL;
  if (!base) return Response.json({ detail: "Administration is not connected yet. Start the backend and set API_BASE_URL." }, { status: 503 });
  const headers = new Headers({ "Accept": "application/json" });
  headers.set("Cookie", request.headers.get("cookie") || "");
  headers.set("Origin", request.headers.get("origin") || "");
  let body: string | undefined;
  if (request.method === "POST") {
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = []; let size = 0;
    if (reader) { while (true) { const { done, value } = await reader.read(); if (done) break; size += value.length; if (size > 8192) { await reader.cancel(); return Response.json({ detail: "Request too large" }, { status: 413 }); } chunks.push(value); } }
    const bytes = new Uint8Array(size); let offset = 0; for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
    body = new TextDecoder().decode(bytes);
    headers.set("Content-Type", "application/json");
  }
  try {
    const upstream = await fetch(`${base.replace(/\/$/, "")}/v1/admin/${endpoint}`, { method: request.method, headers, body, cache: "no-store", redirect: "error", signal: AbortSignal.timeout(15000) });
    const resultHeaders = new Headers({ "Content-Type": "application/json", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
    const cookie = upstream.headers.get("set-cookie"); if (cookie) resultHeaders.set("Set-Cookie", cookie);
    return new Response(await upstream.text(), { status: upstream.status, headers: resultHeaders });
  } catch { return Response.json({ detail: "Administration service is unavailable. Please try again later." }, { status: 503 }); }
}
export const GET = forward;
export const POST = forward;
