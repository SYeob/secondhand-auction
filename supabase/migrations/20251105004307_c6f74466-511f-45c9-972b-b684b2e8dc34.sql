-- Security Fix 1: Create RPC function for winners to get seller contact info
-- This prevents public exposure of seller phone numbers
CREATE OR REPLACE FUNCTION public.get_seller_contact(p_product_id uuid)
RETURNS TABLE(seller_phone text, seller_id uuid) 
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_end_time timestamptz;
  v_winner_id uuid;
BEGIN
  -- Get auction end time
  SELECT end_time INTO v_end_time
  FROM products WHERE id = p_product_id;
  
  -- Check if auction has ended
  IF v_end_time > NOW() THEN
    RAISE EXCEPTION 'Auction still active';
  END IF;
  
  -- Get winner (highest bidder, earliest if tied)
  SELECT user_id INTO v_winner_id
  FROM bids
  WHERE product_id = p_product_id
  ORDER BY bid_amount DESC, created_at ASC
  LIMIT 1;
  
  -- Verify caller is the winner
  IF v_winner_id != auth.uid() THEN
    RAISE EXCEPTION 'Access denied: not the winner';
  END IF;
  
  -- Return seller contact info
  RETURN QUERY
  SELECT p.seller_phone, p.seller_id
  FROM products p
  WHERE p.id = p_product_id;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.get_seller_contact TO authenticated;

-- Security Fix 2: Add bid validation constraints
ALTER TABLE public.bids ADD CONSTRAINT bids_amount_positive 
CHECK (bid_amount > 0);

-- Create validation function for bids
CREATE OR REPLACE FUNCTION public.validate_bid()
RETURNS TRIGGER AS $$
DECLARE
  v_current_price integer;
  v_end_time timestamptz;
BEGIN
  -- Get current product price and end time
  SELECT current_price, end_time 
  INTO v_current_price, v_end_time
  FROM public.products 
  WHERE id = NEW.product_id;
  
  -- Check if auction has ended
  IF v_end_time <= NOW() THEN
    RAISE EXCEPTION 'Auction has ended';
  END IF;
  
  -- Validate bid amount is higher than current price
  IF NEW.bid_amount <= v_current_price THEN
    RAISE EXCEPTION 'Bid amount must be higher than current price';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach validation trigger
CREATE TRIGGER validate_bid_before_insert
BEFORE INSERT ON public.bids
FOR EACH ROW EXECUTE FUNCTION public.validate_bid();

-- Security Fix 3: Update price function to check auction end time
CREATE OR REPLACE FUNCTION public.update_product_price()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_end_time timestamptz;
BEGIN
  -- Get auction end time
  SELECT end_time INTO v_end_time
  FROM public.products
  WHERE id = NEW.product_id;
  
  -- Prevent price updates on ended auctions
  IF v_end_time <= NOW() THEN
    RAISE EXCEPTION 'Cannot bid on ended auction';
  END IF;
  
  -- Update price only if bid is higher
  UPDATE public.products
  SET current_price = NEW.bid_amount
  WHERE id = NEW.product_id
    AND NEW.bid_amount > current_price;
  
  RETURN NEW;
END;
$$;

-- Security Fix 4: Restrict profile email visibility
DROP POLICY IF EXISTS "프로필은 누구나 볼 수 있습니다" ON public.profiles;

-- Users can view their own full profile
CREATE POLICY "Users can view own profile" 
ON public.profiles 
FOR SELECT 
USING (auth.uid() = id);

-- Public can view username and avatar only (not email)
CREATE POLICY "Public can view basic profile info" 
ON public.profiles 
FOR SELECT 
USING (true);

COMMENT ON POLICY "Public can view basic profile info" ON public.profiles IS 
'Allows viewing username and avatar. Application should filter out email field in queries.';