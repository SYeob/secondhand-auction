-- Fix search_path for security functions
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER
SET search_path = public;