import { auth, defineMcp } from "@lovable.dev/mcp-js";
import listProductsTool from "./tools/list-products";
import getProductTool from "./tools/get-product";
import listMyBidsTool from "./tools/list-my-bids";
import placeBidTool from "./tools/place-bid";

// Direct supabase.co issuer (never the .lovable.cloud proxy).
const projectRef =
  import.meta.env.VITE_SUPABASE_PROJECT_ID ??
  (import.meta.env.VITE_SUPABASE_URL ?? process.env.SUPABASE_URL)?.match(
    /^https:\/\/([a-z0-9]+)\.supabase\.co(?:\/|$)/,
  )?.[1] ??
  "project-ref-unset";

export default defineMcp({
  name: "pabi-mcp",
  title: "Pa-Bi Auction MCP",
  version: "0.1.0",
  instructions:
    "Tools for the Pa-Bi Korean auction platform. Use list_products / get_product to browse auctions. Authenticated users can call list_my_bids and place_bid.",
  auth: auth.oauth.issuer({
    issuer: `https://${projectRef}.supabase.co/auth/v1`,
    acceptedAudiences: "authenticated",
  }),
  tools: [listProductsTool, getProductTool, listMyBidsTool, placeBidTool],
});
