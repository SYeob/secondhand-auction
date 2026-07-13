-- 응찰 테이블 생성
CREATE TABLE public.bids (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  bid_amount INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- RLS 활성화
ALTER TABLE public.bids ENABLE ROW LEVEL SECURITY;

-- RLS 정책
CREATE POLICY "응찰 내역은 누구나 볼 수 있습니다"
ON public.bids
FOR SELECT
USING (true);

CREATE POLICY "로그인한 사용자는 응찰할 수 있습니다"
ON public.bids
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- 인덱스 추가
CREATE INDEX idx_bids_product_id ON public.bids(product_id);
CREATE INDEX idx_bids_user_id ON public.bids(user_id);

-- 최고가 응찰 시 제품 가격 자동 업데이트 함수
CREATE OR REPLACE FUNCTION public.update_product_price()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  UPDATE public.products
  SET current_price = NEW.bid_amount
  WHERE id = NEW.product_id
    AND NEW.bid_amount > current_price;
  RETURN NEW;
END;
$$;

-- 트리거 생성
CREATE TRIGGER on_bid_inserted
  AFTER INSERT ON public.bids
  FOR EACH ROW
  EXECUTE FUNCTION public.update_product_price();