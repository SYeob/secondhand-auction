-- Add seller_phone column to products table
ALTER TABLE public.products ADD COLUMN seller_phone text;

-- Add check constraint for phone number format (optional but recommended)
ALTER TABLE public.products ADD CONSTRAINT products_seller_phone_format 
CHECK (seller_phone IS NULL OR char_length(seller_phone) BETWEEN 10 AND 15);