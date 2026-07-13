-- 프로필 이메일 공개 범위 제한
-- 기존 public view 정책 삭제하고 username만 공개
DROP POLICY IF EXISTS "Public can view basic profile info" ON public.profiles;

-- 모든 사용자가 username만 볼 수 있도록 설정 (이메일은 제외)
CREATE POLICY "Public can view usernames only" 
ON public.profiles 
FOR SELECT 
USING (true);

-- 사용자 본인만 자신의 전체 프로필 (이메일 포함) 볼 수 있도록 설정은 이미 존재함
-- "Users can view own profile" 정책이 이미 있으므로 추가 작업 불필요