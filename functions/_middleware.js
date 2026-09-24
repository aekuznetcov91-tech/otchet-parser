/**
 * Cloudflare Pages Edge Middleware
 * Enforces RFC 7617 HTTP Basic Authentication across the entire site perimeter.
 */

async function timingSafeEqual(a, b) {
  const enc = new TextEncoder();
  const hashA = await crypto.subtle.digest("SHA-256", enc.encode(a || ""));
  const hashB = await crypto.subtle.digest("SHA-256", enc.encode(b || ""));
  const bufA = new Uint8Array(hashA);
  const bufB = new Uint8Array(hashB);
  if (bufA.length !== bufB.length) return false;
  let diff = 0;
  for (let i = 0; i < bufA.length; i++) {
    diff |= bufA[i] ^ bufB[i];
  }
  return diff === 0;
}

export async function onRequest(context) {
  const { request, env } = context;

  // Allow CORS preflight requests without authentication
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  }

  const authHeader = request.headers.get("Authorization");
  if (!authHeader) {
    return new Response("Доступ защищен. Требуется авторизация.", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="B2C Analytics Dashboard", charset="UTF-8"',
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  }

  const [scheme, encoded] = authHeader.split(" ");
  if (scheme !== "Basic" || !encoded) {
    return new Response("Неверный формат заголовка авторизации.", {
      status: 400,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  let decoded = "";
  try {
    decoded = atob(encoded);
  } catch (e) {
    return new Response("Неверная кодировка base64.", {
      status: 400,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  const colonIdx = decoded.indexOf(":");
  const user = colonIdx !== -1 ? decoded.slice(0, colonIdx) : decoded;
  const pass = colonIdx !== -1 ? decoded.slice(colonIdx + 1) : "";

  // Sourced from Cloudflare Environment Variables or default configured fallback
  const expectedUser = env.AUTH_USER || "director";
  const expectedPass = env.AUTH_PASS || "password";

  const userMatches = await timingSafeEqual(user, expectedUser);
  const passMatches = await timingSafeEqual(pass, expectedPass);

  if (!userMatches || !passMatches) {
    return new Response("Доступ закрыт. Неверный логин или пароль.", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="B2C Analytics Dashboard", charset="UTF-8"',
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  }

  // Credentials are valid; proceed to requested page/asset
  const response = await context.next();

  // Add security headers to the downstream response
  const newHeaders = new Headers(response.headers);
  newHeaders.set("X-Content-Type-Options", "nosniff");
  newHeaders.set("X-Frame-Options", "DENY");
  newHeaders.set("Referrer-Policy", "strict-origin-when-cross-origin");

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders,
  });
}
