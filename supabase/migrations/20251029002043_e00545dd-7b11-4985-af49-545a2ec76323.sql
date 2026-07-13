-- 사용자 프로필 테이블 생성
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- RLS 활성화
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 프로필 정책: 누구나 프로필 조회 가능
CREATE POLICY "프로필은 누구나 볼 수 있습니다"
ON public.profiles
FOR SELECT
USING (true);

-- 프로필 정책: 본인만 프로필 생성 가능
CREATE POLICY "사용자는 자신의 프로필을 생성할 수 있습니다"
ON public.profiles
FOR INSERT
WITH CHECK (auth.uid() = id);

-- 프로필 정책: 본인만 프로필 수정 가능
CREATE POLICY "사용자는 자신의 프로필을 수정할 수 있습니다"
ON public.profiles
FOR UPDATE
USING (auth.uid() = id);

-- 새 사용자 가입 시 자동으로 프로필 생성하는 함수
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, username)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1))
  );
  RETURN NEW;
END;
$$;

-- 사용자 생성 시 트리거
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();

-- 업데이트 시간 자동 갱신 함수
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

-- 프로필 업데이트 시 트리거
CREATE TRIGGER update_profiles_updated_at
BEFORE UPDATE ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- 상품 테이블 생성
CREATE TABLE public.products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  location TEXT NOT NULL,
  starting_price INTEGER NOT NULL,
  current_price INTEGER NOT NULL,
  image_url TEXT NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE NOT NULL,
  seller_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  category TEXT NOT NULL DEFAULT '전체',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- RLS 활성화
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

-- 상품 정책: 누구나 조회 가능
CREATE POLICY "상품은 누구나 볼 수 있습니다"
ON public.products
FOR SELECT
USING (true);

-- 상품 정책: 로그인한 사용자만 상품 등록 가능
CREATE POLICY "로그인한 사용자는 상품을 등록할 수 있습니다"
ON public.products
FOR INSERT
WITH CHECK (auth.uid() = seller_id);

-- 상품 정책: 판매자만 자신의 상품 수정 가능
CREATE POLICY "판매자는 자신의 상품을 수정할 수 있습니다"
ON public.products
FOR UPDATE
USING (auth.uid() = seller_id);

-- 상품 정책: 판매자만 자신의 상품 삭제 가능
CREATE POLICY "판매자는 자신의 상품을 삭제할 수 있습니다"
ON public.products
FOR DELETE
USING (auth.uid() = seller_id);

-- 상품 업데이트 시 트리거
CREATE TRIGGER update_products_updated_at
BEFORE UPDATE ON public.products
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();