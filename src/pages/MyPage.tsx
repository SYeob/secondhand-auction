import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { User } from "@supabase/supabase-js";
import Header from "@/components/Header";
import ProductCard from "@/components/ProductCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const MyPage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [myBids, setMyBids] = useState<any[]>([]);
  const [myLikes, setMyLikes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    window.scrollTo(0, 0);

    // 사용자 인증 확인
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        navigate("/auth");
        return;
      }
      setUser(user);
      await fetchMyData(user.id);
    };

    checkUser();

    // 인증 상태 변경 감지
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        navigate("/auth");
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const fetchMyData = async (userId: string) => {
    setIsLoading(true);

    try {
      // 내가 응찰한 상품들 가져오기
      const { data: bidsData, error: bidsError } = await supabase
        .from("bids")
        .select("product_id, products(*)")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (bidsError) {
        console.error("응찰 데이터 로딩 오류:", bidsError);
      } else if (bidsData) {
        // 중복 제거 (같은 상품에 여러 번 응찰한 경우) 및 null 제거
        const uniqueProducts = Array.from(
          new Map(
            bidsData
              .filter(bid => bid.products !== null)
              .map(bid => [bid.product_id, bid.products])
          ).values()
        );
        setMyBids(uniqueProducts);
      }

      // 내가 좋아요한 상품들 가져오기
      const { data: likesData, error: likesError } = await supabase
        .from("likes")
        .select("product_id")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (likesError) {
        console.error("좋아요 데이터 로딩 오류:", likesError);
      } else if (likesData && likesData.length > 0) {
        // 좋아요한 상품의 ID 목록 추출
        const productIds = likesData.map(like => like.product_id);
        
        // 상품 정보 가져오기
        const { data: productsData, error: productsError } = await supabase
          .from("products")
          .select("id, title, location, current_price, image_url, end_time")
          .in("id", productIds);

        if (productsError) {
          console.error("상품 데이터 로딩 오류:", productsError);
        } else if (productsData) {
          setMyLikes(productsData);
        }
      } else {
        setMyLikes([]);
      }
    } catch (error) {
      console.error("데이터 로딩 중 예외 발생:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-2xl">마이페이지</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              <span className="font-semibold text-foreground">{user?.email}</span>님의 활동 내역
            </p>
          </CardContent>
        </Card>

        <Tabs defaultValue="bids" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-8">
            <TabsTrigger value="bids">응찰한 상품</TabsTrigger>
            <TabsTrigger value="likes">좋아요한 상품</TabsTrigger>
          </TabsList>

          <TabsContent value="bids">
            {isLoading ? (
              <p className="text-center py-12 text-muted-foreground">로딩 중...</p>
            ) : myBids.length === 0 ? (
              <p className="text-center py-12 text-muted-foreground">응찰한 상품이 없습니다.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {myBids.map((product: any) => (
                  <ProductCard
                    key={product.id}
                    id={product.id}
                    title={product.title}
                    location={product.location}
                    currentPrice={product.current_price}
                    imageUrl={product.image_url}
                    endTime={Math.max(0, Math.floor((new Date(product.end_time).getTime() - Date.now()) / 1000))}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="likes">
            {isLoading ? (
              <p className="text-center py-12 text-muted-foreground">로딩 중...</p>
            ) : myLikes.length === 0 ? (
              <p className="text-center py-12 text-muted-foreground">좋아요한 상품이 없습니다.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {myLikes.map((product: any) => (
                  <ProductCard
                    key={product.id}
                    id={product.id}
                    title={product.title}
                    location={product.location}
                    currentPrice={product.current_price}
                    imageUrl={product.image_url}
                    endTime={Math.max(0, Math.floor((new Date(product.end_time).getTime() - Date.now()) / 1000))}
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MyPage;
