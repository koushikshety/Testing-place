export default {
  async fetch(request) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS" }
      });
    }
    const { searchParams } = new URL(request.url);
    const target = searchParams.get("url");
    const referer = searchParams.get("ref") || "";
    if (!target) return new Response("Missing ?url=", { status: 400 });

    const upstream = await fetch(target, {
      headers: {
        "User-Agent": "Mozilla/5.0",
        ...(referer ? { "Referer": referer, "Origin": new URL(referer).origin } : {})
      }
    });

    const headers = new Headers(upstream.headers);
    headers.set("Access-Control-Allow-Origin", "*");
    return new Response(upstream.body, { status: upstream.status, headers });
  }
};
