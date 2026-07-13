-- Add foreign key from bids.user_id to profiles.id
ALTER TABLE public.bids
ADD CONSTRAINT bids_user_id_fkey 
FOREIGN KEY (user_id) 
REFERENCES public.profiles(id) 
ON DELETE CASCADE;