declare const process: { env: Record<string, string | undefined> };
import { createClient } from "@supabase/supabase-js";
import { defineTool, type ToolContext } from "@lovable.dev/mcp-js";
import { z } from "zod";

export default defineTool({
  name: "place_bid",
  title: "Place a bid",
  description:
    "Place a bid on a Pa-Bi auction product as the signed-in user. Amount must exceed the current price.",
  inputSchema: {
    product_id: z.string().uuid().describe("Product UUID to bid on."),
    amount: z.number().int().positive().describe("Bid amount in KRW."),
  },
  annotations: { readOnlyHint: false, destructiveHint: false, openWorldHint: false },
  handler: async ({ product_id, amount }, ctx: ToolContext) => {
    if (!ctx.isAuthenticated()) {
      return { content: [{ type: "text", text: "Not authenticated." }], isError: true };
    }
    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_PUBLISHABLE_KEY!,
      {
        global: { headers: { Authorization: `Bearer ${ctx.getToken()}` } },
        auth: { persistSession: false, autoRefreshToken: false },
      },
    );
    const { data, error } = await supabase
      .from("bids")
      .insert({ product_id, user_id: ctx.getUserId(), bid_amount: amount })
      .select()
      .maybeSingle();
    if (error) {
      return { content: [{ type: "text", text: error.message }], isError: true };
    }
    return {
      content: [{ type: "text", text: `Bid placed: ${JSON.stringify(data)}` }],
      structuredContent: { bid: data },
    };
  },
});
