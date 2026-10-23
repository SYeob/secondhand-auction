// Ambient declaration for the Deno runtime `process` shim used by the
// emitted MCP edge function. These tool files are bundled into a Deno
// function at build time and never run in the browser.
declare const process: { env: Record<string, string | undefined> };
