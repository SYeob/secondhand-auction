import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Search, User, LogIn, LogOut, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import type { User as SupabaseUser } from "@supabase/supabase-js";

interface HeaderProps {
  onSearch?: (query: string) => void;
}

const Header = ({ onSearch }: HeaderProps) => {
  const navigate = useNavigate();
  const [user, setUser] = useState<SupabaseUser | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    // 현재 세션 확인
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    // 인증 상태 변경 감지
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    toast.success("로그아웃되었습니다.");
    navigate("/");
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchQuery);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 border-b border-border">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Link to="/">
              <div className="bg-gradient-primary text-primary-foreground font-bold text-2xl px-4 py-2 rounded-xl shadow-glow cursor-pointer hover:opacity-90 transition-opacity">
                Pa-Bi
              </div>
            </Link>
          </div>

          {/* Search Bar */}
          {onSearch && (
            <div className="flex-1 max-w-2xl hidden md:flex">
              <form onSubmit={handleSearch} className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="검색어를 입력해 주세요"
                  className="pl-10 bg-secondary/50 border-border focus:border-primary transition-colors"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </form>
            </div>
          )}

          {/* Auth Buttons */}
          <div className="flex items-center gap-2">
            {user ? (
              <>
                <Button
                  size="sm"
                  className="gap-2 bg-gradient-primary hover:opacity-90 transition-opacity"
                  onClick={() => navigate("/register")}
                >
                  <Plus className="h-4 w-4" />
                  <span className="hidden sm:inline">상품등록</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-sm hidden md:inline-flex"
                  onClick={() => navigate("/mypage")}
                >
                  {user.email}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="gap-2"
                  onClick={handleSignOut}
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">로그아웃</span>
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  className="gap-2"
                  onClick={() => navigate("/auth")}
                >
                  <LogIn className="h-4 w-4" />
                  <span className="hidden sm:inline">로그인</span>
                </Button>
                <Button
                  size="sm"
                  className="gap-2 bg-gradient-primary hover:opacity-90 transition-opacity"
                  onClick={() => navigate("/auth")}
                >
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">회원가입</span>
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Mobile Search */}
        {onSearch && (
          <div className="md:hidden mt-3">
            <form onSubmit={handleSearch} className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                type="search"
                placeholder="검색어를 입력해 주세요"
                className="pl-10 bg-secondary/50"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
