-- Create likes table for storing user likes on products
CREATE TABLE public.likes (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  product_id UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(user_id, product_id)
);

-- Enable RLS
ALTER TABLE public.likes ENABLE ROW LEVEL SECURITY;

-- Policies for likes table
CREATE POLICY "Users can view all likes"
ON public.likes
FOR SELECT
USING (true);

CREATE POLICY "Users can create their own likes"
ON public.likes
FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own likes"
ON public.likes
FOR DELETE
USING (auth.uid() = user_id);

-- Enable realtime for bids table to show live bidding
ALTER PUBLICATION supabase_realtime ADD TABLE public.bids;