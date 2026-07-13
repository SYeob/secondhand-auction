import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { MapPin, Clock, ChevronLeft, Heart, Trash2, Edit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import type { User } from "@supabase/supabase-js";
import Header from "@/components/Header";
import SellerContactInfo from "@/components/SellerContactInfo";

// 임시 상품 데이터 (추후 API나 상태관리로 대체)
const mockProducts = [
  {
    id: 1,
    title: "나이키 에어맥스",
    location: "용인시 기흥구",
    currentPrice: 75000,
    startPrice: 50000,
    imageUrl: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=800&fit=crop",
    endTime: 7200,
    description: "깨끗한 상태의 나이키 에어맥스입니다. 사이즈는 270이며, 착용감이 매우 좋습니다. 정품 보증서 포함되어 있습니다.",
    seller: "판매자123",
    bidCount: 12,
    category: "패션",
  },
  {
    id: 2,
    title: "아이폰 13 Pro",
    location: "경기도 성남시",
    currentPrice: 975000,
    startPrice: 800000,
    imageUrl: "https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=800&h=800&fit=crop",
    endTime: 5400,
    description: "128GB 그래파이트 색상입니다. 외관 상태 좋고 배터리 성능 90% 이상입니다. 박스와 모든 구성품 포함되어 있습니다.",
    seller: "테크셀러",
    bidCount: 25,
    category: "디지털/가전",
  },
  {
    id: 3,
    title: "조던 1 레트로",
    location: "용인시 수지구",
    currentPrice: 105000,
    startPrice: 80000,
    imageUrl: "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=800&h=800&fit=crop",
    endTime: 3600,
    description: "조던 1 레트로 하이 시카고 컬러웨이입니다. 사이즈 265, 미착용 새상품입니다.",
    seller: "스니커즈매니아",
    bidCount: 18,
    category: "패션",
  },
  {
    id: 4,
    title: "MacBook Air M2",
    location: "서울시 강남구",
    currentPrice: 1250000,
    startPrice: 1000000,
    imageUrl: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=800&fit=crop",
    endTime: 10800,
    description: "M2 칩 탑재, 16GB RAM, 512GB SSD입니다. 2024년 초 구매하여 3개월 사용했습니다. 거의 새것 같은 상태입니다.",
    seller: "애플마니아",
    bidCount: 31,
    category: "디지털/가전",
  },
  {
    id: 5,
    title: "갤럭시 Z Flip5",
    location: "서울시 서초구",
    currentPrice: 850000,
    startPrice: 700000,
    imageUrl: "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&h=800&fit=crop",
    endTime: 4500,
    description: "그래파이트 컬러, 256GB 용량입니다. 액정 보호필름 부착되어 있고 케이스도 함께 드립니다.",
    seller: "폰마켓",
    bidCount: 20,
    category: "디지털/가전",
  },
  {
    id: 6,
    title: "소니 WH-1000XM5",
    location: "경기도 수원시",
    currentPrice: 320000,
    startPrice: 250000,
    imageUrl: "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&h=800&fit=crop",
    endTime: 9000,
    description: "최고급 노이즈캔슬링 헤드폰입니다. 2개월 사용했으며 상태 매우 양호합니다. 박스, 케이블 모두 포함입니다.",
    seller: "오디오샵",
    bidCount: 15,
    category: "디지털/가전",
  },
  {
    id: 7,
    title: "캐논 EOS R6",
    location: "서울시 마포구",
    currentPrice: 2850000,
    startPrice: 2500000,
    imageUrl: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&h=800&fit=crop",
    endTime: 1800,
    description: "풀프레임 미러리스 카메라 바디입니다. 셔터 횟수 약 5,000회로 거의 새것입니다. 정품 등록되어 있습니다.",
    seller: "사진작가",
    bidCount: 8,
    category: "디지털/가전",
  },
  {
    id: 8,
    title: "다이슨 V15",
    location: "인천시 연수구",
    currentPrice: 680000,
    startPrice: 500000,
    imageUrl: "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&h=800&fit=crop",
    endTime: 6300,
    description: "최신형 무선 청소기입니다. 1년 사용했으며 필터 등 모든 부속품 깨끗하게 관리되었습니다.",
    seller: "홈케어",
    bidCount: 22,
    category: "디지털/가전",
  },
];

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [timeLeft, setTimeLeft] = useState(0);
  const [bidAmount, setBidAmount] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [user, setUser] = useState<User | null>(null);
  const [sellerId, setSellerId] = useState<string | null>(null);
  const [product, setProduct] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLiked, setIsLiked] = useState(false);
  const [bidHistory, setBidHistory] = useState<any[]>([]);
  const [isAuctionEnded, setIsAuctionEnded] = useState(false);
  const [isWinner, setIsWinner] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);

    // 현재 사용자 확인
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    // 데이터베이스에서 상품 정보, 좋아요 상태, 응찰 내역 가져오기
    const fetchProduct = async () => {
      setIsLoading(true);
      // seller_phone 컬럼은 노출하지 않기 위해 명시적으로 컬럼을 지정합니다.
      const { data } = await supabase
        .from("products")
        .select("id, title, description, location, category, starting_price, current_price, image_url, end_time, seller_id, created_at, updated_at")
        .eq("id", id)
        .maybeSingle();

      if (data) {
        // 데이터베이스 상품 발견
        const auctionEndTime = new Date(data.end_time).getTime();
        const now = Date.now();
        const ended = auctionEndTime <= now;
        
        setProduct({
          id: data.id,
          title: data.title,
          location: data.location,
          currentPrice: data.current_price,
          startPrice: data.starting_price,
          imageUrl: data.image_url,
          description: data.description,
          category: data.category,
          seller: "판매자",
          bidCount: 0, // 이후 응찰 내역 로드 후 업데이트됨
          endTime: Math.max(0, Math.floor((auctionEndTime - now) / 1000)),
        });
        setCurrentPrice(data.current_price);
        setSellerId(data.seller_id);
        setTimeLeft(Math.max(0, Math.floor((auctionEndTime - now) / 1000)));
        setIsAuctionEnded(ended);

        // 좋아요 상태 확인
        if (user) {
          const { data: likeData } = await supabase
            .from("likes")
            .select("*")
            .eq("user_id", user.id)
            .eq("product_id", id)
            .maybeSingle();
          
          setIsLiked(!!likeData);
        }

        // 응찰 내역 가져오기 - bid_amount 기준으로 정렬하여 최고 입찰자 확인
        // profiles.email은 비공개이므로 username만 조회합니다.
        const { data: bidsData } = await supabase
          .from("bids")
          .select(`
            *,
            profiles(username)
          `)
          .eq("product_id", id)
          .order("bid_amount", { ascending: false })
          .order("created_at", { ascending: false });

        if (bidsData) {
          setBidHistory(bidsData);
          
          // 응찰 횟수 업데이트
          setProduct((prev: any) => prev ? { ...prev, bidCount: bidsData.length } : prev);
          
          // 낙찰자 확인 (경매 종료 여부와 관계없이 확인)
          if (bidsData.length > 0 && user) {
            const highestBid = bidsData[0]; // 가장 높은 금액의 응찰
            setIsWinner(highestBid.user_id === user.id);
          }
        }
      } else {
        // mockProducts에서 찾기
        const mockProduct = mockProducts.find((p) => p.id === Number(id));
        if (mockProduct) {
          setProduct(mockProduct);
          setCurrentPrice(mockProduct.currentPrice);
          setTimeLeft(mockProduct.endTime);
        }
      }
      setIsLoading(false);
    };

    if (id) {
      fetchProduct();
    }
  }, [id, user]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev > 0) return prev - 1;
        // 타이머가 0이 되면 경매 종료 및 낙찰자 재확인
        if (prev === 0 && !isAuctionEnded) {
          setIsAuctionEnded(true);
          
          // 경매 종료 시 낙찰자 재확인
          if (bidHistory.length > 0 && user) {
            const highestBid = bidHistory[0];
            const userIsWinner = highestBid.user_id === user.id;
            setIsWinner(userIsWinner);
          }
        }
        return 0;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [isAuctionEnded, bidHistory, user]);

  // 실시간 응찰 업데이트
  useEffect(() => {
    if (!id || !product?.id || typeof product.id === 'number') return;

    const channel = supabase
      .channel(`bids-${id}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'bids',
          filter: `product_id=eq.${id}`,
        },
        async (payload) => {
          // 프로필 정보 가져오기 (username만 노출)
          const { data: profileData } = await supabase
            .from("profiles")
            .select("username")
            .eq("id", payload.new.user_id)
            .single();

          const newBid = {
            ...payload.new,
            profiles: profileData,
          };

          // 응찰 내역을 금액 순으로 정렬하여 업데이트
          setBidHistory((prev) => {
            const updated = [newBid, ...prev];
            const sorted = updated.sort((a, b) => {
              if (b.bid_amount !== a.bid_amount) {
                return b.bid_amount - a.bid_amount;
              }
              return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
            });
            
            // 응찰 횟수 업데이트
            setProduct((prev: any) => prev ? { ...prev, bidCount: sorted.length } : prev);
            
            // 낙찰자 상태 업데이트 (최고 입찰자 확인)
            if (user && sorted.length > 0) {
              const highestBid = sorted[0];
              setIsWinner(highestBid.user_id === user.id);
            }
            
            return sorted;
          });
          setCurrentPrice(payload.new.bid_amount);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [id, product, user]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleBid = async () => {
    // 입력값 검증
    if (!bidAmount || bidAmount.trim() === "") {
      toast({
        title: "입찰 실패",
        description: "응찰 금액을 입력해주세요.",
        variant: "destructive",
      });
      return;
    }

    const amount = Number(bidAmount);
    
    // 숫자 형식 검증
    if (isNaN(amount) || amount < 0) {
      toast({
        title: "입찰 실패",
        description: "올바른 금액을 입력해주세요.",
        variant: "destructive",
      });
      return;
    }

    // 최대 금액 검증 (10억원)
    if (amount > 1000000000) {
      toast({
        title: "입찰 실패",
        description: "응찰 금액은 10억원을 초과할 수 없습니다.",
        variant: "destructive",
      });
      return;
    }
    
    if (amount <= currentPrice) {
      toast({
        title: "입찰 실패",
        description: `현재가(${currentPrice.toLocaleString()}원)보다 높은 금액을 입력해주세요.`,
        variant: "destructive",
      });
      return;
    }

    if (!user) {
      toast({
        title: "로그인 필요",
        description: "응찰하려면 로그인이 필요합니다.",
        variant: "destructive",
      });
      navigate("/auth");
      return;
    }

    // 데이터베이스에 있는 상품인지 확인
    if (!product?.id || typeof product.id === 'number') {
      toast({
        title: "응찰 불가",
        description: "데이터베이스에 등록된 상품만 응찰할 수 있습니다.",
        variant: "destructive",
      });
      return;
    }

    const { error } = await supabase
      .from("bids")
      .insert({
        product_id: product.id,
        user_id: user.id,
        bid_amount: amount,
      });

    if (error) {
      toast({
        title: "응찰 실패",
        description: "응찰 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        variant: "destructive",
      });
      return;
    }

    setCurrentPrice(amount);
    setBidAmount("");
    setIsDialogOpen(false);
    
    toast({
      title: "응찰 완료",
      description: `${amount.toLocaleString()}원에 응찰하셨습니다.`,
    });
  };

  const handleEdit = () => {
    navigate(`/register?edit=${id}`);
  };

  const handleDelete = async () => {
    if (!user) return;

    const { error } = await supabase.from("products").delete().eq("id", id);

    if (error) {
      toast({
        title: "오류",
        description: "삭제에 실패했습니다.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "성공",
      description: "상품이 삭제되었습니다.",
    });
    navigate("/");
  };

  const handleLike = async () => {
    if (!user) {
      toast({
        title: "로그인 필요",
        description: "좋아요를 누르려면 로그인이 필요합니다.",
        variant: "destructive",
      });
      navigate("/auth");
      return;
    }

    if (!product?.id || typeof product.id === 'number') {
      toast({
        title: "좋아요 불가",
        description: "데이터베이스에 등록된 상품만 좋아요할 수 있습니다.",
        variant: "destructive",
      });
      return;
    }

    if (isLiked) {
      // 좋아요 취소
      const { error } = await supabase
        .from("likes")
        .delete()
        .eq("user_id", user.id)
        .eq("product_id", product.id);

      if (error) {
        toast({
          title: "오류",
          description: "좋아요 취소 중 오류가 발생했습니다.",
          variant: "destructive",
        });
        return;
      }

      setIsLiked(false);
      toast({
        title: "좋아요 취소",
        description: "좋아요가 취소되었습니다.",
      });
    } else {
      // 좋아요 추가
      const { error } = await supabase
        .from("likes")
        .insert({
          user_id: user.id,
          product_id: product.id,
        });

      if (error) {
        toast({
          title: "오류",
          description: "좋아요 추가 중 오류가 발생했습니다.",
          variant: "destructive",
        });
        return;
      }

      setIsLiked(true);
      toast({
        title: "좋아요",
        description: "좋아요가 추가되었습니다.",
      });
    }
  };

  const formatBidTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const isOwner = user && sellerId && user.id === sellerId;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-4 py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">로딩 중...</h2>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-4 py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">상품을 찾을 수 없습니다</h2>
          <Button onClick={() => navigate("/")}>홈으로 돌아가기</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-6">
        <Button
          variant="ghost"
          className="mb-6 gap-2"
          onClick={() => navigate("/")}
        >
          <ChevronLeft className="h-4 w-4" />
          목록으로
        </Button>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* 이미지 섹션 */}
          <div className="space-y-4">
            <div className="relative aspect-square overflow-hidden rounded-lg bg-secondary">
              <img
                src={product.imageUrl}
                alt={product.title}
                className="w-full h-full object-cover"
              />
              <button
                onClick={handleLike}
                className="absolute top-4 right-4 p-2 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background transition-colors"
              >
                <Heart
                  className={`h-6 w-6 ${isLiked ? "fill-destructive text-destructive" : "text-muted-foreground"}`}
                />
              </button>
            </div>
          </div>

          {/* 상품 정보 섹션 */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold mb-3">{product.title}</h1>
              <div className="flex items-center gap-2 text-muted-foreground mb-4">
                <MapPin className="h-4 w-4" />
                <span>{product.location}</span>
              </div>
            </div>

            <Separator />

            {/* 가격 정보 */}
            <Card className="border-primary/20 bg-primary/5">
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">시작가</span>
                    <span className="text-lg font-semibold">
                      {product.startPrice.toLocaleString()}원
                    </span>
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">현재가</span>
                    <span className="text-2xl font-bold text-primary">
                      {currentPrice.toLocaleString()}원
                    </span>
                  </div>
                  {timeLeft > 0 && (
                    <>
                      <Separator />
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">남은시간</span>
                        <div className="flex items-center gap-2 bg-accent text-accent-foreground px-3 py-1.5 rounded-lg">
                          <Clock className="h-4 w-4" />
                          <span className="text-lg font-bold">{formatTime(timeLeft)}</span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* 낙찰자 정보 카드 - 항상 접근 가능 */}
            {isAuctionEnded && isWinner && (
              <Dialog>
                <DialogTrigger asChild>
                  <Card 
                    className="border-primary bg-primary/5 cursor-pointer hover:bg-primary/10 transition-colors"
                  >
                    <CardContent className="p-6">
                      <h3 className="text-xl font-bold mb-2 text-primary text-center">
                        🎉 축하드립니다. 낙찰되었습니다! 🎉
                      </h3>
                      <p className="text-center text-sm text-muted-foreground">
                        클릭하여 판매자 연락처 확인
                      </p>
                    </CardContent>
                  </Card>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle className="text-2xl text-center">🎉 축하합니다!</DialogTitle>
                    <DialogDescription className="sr-only">
                      낙찰 축하 및 판매자 연락처 정보
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <p className="text-center text-lg font-semibold">
                      "{product.title}" 경매에서 낙찰받으셨습니다!
                    </p>
                    <p className="text-center text-muted-foreground">
                      낙찰가: <span className="font-bold text-primary">{currentPrice.toLocaleString()}원</span>
                    </p>
                    <Separator />
                    <SellerContactInfo productId={id!} />
                  </div>
                </DialogContent>
              </Dialog>
            )}

            {isAuctionEnded && !isWinner && user && bidHistory.some(bid => bid.user_id === user.id) && (
              <Card className="border-orange-500/50 bg-orange-500/10">
                <CardContent className="p-6">
                  <p className="text-center text-muted-foreground">
                    경매가 종료되었습니다. 아쉽게도 낙찰받지 못하셨습니다.
                  </p>
                </CardContent>
              </Card>
            )}

            {isOwner && (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={handleEdit}
                >
                  <Edit className="h-4 w-4" />
                  수정하기
                </Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" className="flex-1 gap-2">
                      <Trash2 className="h-4 w-4" />
                      삭제하기
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>상품을 삭제하시겠습니까?</AlertDialogTitle>
                      <AlertDialogDescription>
                        이 작업은 되돌릴 수 없습니다. 상품과 관련된 모든 응찰
                        내역이 삭제됩니다.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>취소</AlertDialogCancel>
                      <AlertDialogAction onClick={handleDelete}>
                        삭제
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            )}

            {/* 응찰 버튼 */}
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  className="w-full h-14 text-lg bg-gradient-primary hover:opacity-90 transition-opacity shadow-md"
                  disabled={timeLeft === 0}
                >
                  {timeLeft > 0 ? "응찰하기" : "경매 종료"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>응찰하기</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>현재가</Label>
                    <div className="text-2xl font-bold text-primary">
                      {currentPrice.toLocaleString()}원
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="bid-amount">응찰 금액</Label>
                    <Input
                      id="bid-amount"
                      type="number"
                      placeholder={`${(currentPrice + 1000).toLocaleString()}원 이상 입력`}
                      value={bidAmount}
                      onChange={(e) => setBidAmount(e.target.value)}
                      min={currentPrice + 1}
                    />
                    <p className="text-sm text-muted-foreground">
                      현재가보다 높은 금액을 입력해주세요.
                    </p>
                  </div>
                  <Button
                    className="w-full"
                    onClick={handleBid}
                  >
                    응찰 확인
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* 상품 설명 */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-4">상품 설명</h2>
            <p className="text-muted-foreground leading-relaxed whitespace-pre-line">
              {product.description}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProductDetail;
