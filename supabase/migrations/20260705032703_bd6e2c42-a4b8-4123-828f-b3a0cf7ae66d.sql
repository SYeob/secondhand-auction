-- === Fix 1: Restrict seller_phone column exposure ===
REVOKE SELECT (seller_phone) ON public.products FROM anon, authenticated;

-- Create SECURITY DEFINER function so product owner can fetch their own product
-- (including seller_phone) during edit
CREATE OR REPLACE FUNCTION public.get_own_product(p_product_id uuid)
RETURNS TABLE(
  id uuid,
  title text,
  description text,
  location text,
  category text,
  starting_price integer,
  current_price integer,
  image_url text,
  end_time timestamptz,
  seller_id uuid,
  seller_phone text,
  created_at timestamptz,
  updated_at timestamptz
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  -- Verify caller is the seller
  IF NOT EXISTS (
    SELECT 1 FROM public.products 
    WHERE public.products.id = p_product_id 
    AND public.products.seller_id = auth.uid()
  ) THEN
    RAISE EXCEPTION 'Access denied: not the seller';
  END IF;
  
  RETURN QUERY 
  SELECT p.id, p.title, p.description, p.location, p.category, 
         p.starting_price, p.current_price, p.image_url, p.end_time,
         p.seller_id, p.seller_phone, p.created_at, p.updated_at
  FROM public.products p
  WHERE p.id = p_product_id;
END;
$$;

REVOKE ALL ON FUNCTION public.get_own_product(uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.get_own_product(uuid) TO authenticated;

-- === Fix 2: Restrict profiles.email column exposure ===
-- Email is redundant with auth.users email; clients can use supabase.auth.getUser() for own email.
REVOKE SELECT (email) ON public.profiles FROM anon, authenticated;

-- === Fix 3: Restrict SECURITY DEFINER functions from public/anon/authenticated execution ===
-- Trigger functions (called only via triggers, not RPC)
REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.update_product_price() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.update_updated_at_column() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.validate_bid() FROM PUBLIC, anon, authenticated;

-- get_seller_contact: winners are logged in, so only authenticated may call it
REVOKE ALL ON FUNCTION public.get_seller_contact(uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.get_seller_contact(uuid) TO authenticated;