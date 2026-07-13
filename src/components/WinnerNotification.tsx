import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useNavigate } from "react-router-dom";
import SellerContactInfo from "@/components/SellerContactInfo";

interface WinningProduct {
  id: string;
  title: string;
  current_price: number;
}

const WinnerNotification = () => {
  const [showDialog, setShowDialog] = useState(false);
  const [winningProduct, setWinningProduct] = useState<WinningProduct | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const checkForWins = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // localStorage에서 이미 본 낙찰 알림 확인
      const seenWins = JSON.parse(localStorage.getItem('seenWinnerNotifications') || '[]');

      // 종료된 경매 상품 중 내가 낙찰받은 것 확인 (seller_phone은 SellerContactInfo에서 RPC로 조회)
      const { data: products } = await supabase
        .from("products")
        .select("id, title, current_price, end_time")
        .lt("end_time", new Date().toISOString());

      if (!products || products.length === 0) return;

      for (const product of products) {
        // 이미 본 알림은 스킵
        if (seenWins.includes(product.id)) continue;

        // 각 상품의 최고 입찰자 확인
        const { data: bids } = await supabase
          .from("bids")
          .select("user_id, bid_amount")
          .eq("product_id", product.id)
          .order("bid_amount", { ascending: false })
          .order("created_at", { ascending: false })
          .limit(1);

        if (bids && bids.length > 0 && bids[0].user_id === user.id) {
          setWinningProduct(product);
          setShowDialog(true);
          
          // localStorage에 저장
          const updatedSeenWins = [...seenWins, product.id];
          localStorage.setItem('seenWinnerNotifications', JSON.stringify(updatedSeenWins));
          
          break; // 첫 번째 낙찰 상품만 표시
        }
      }
    };

    checkForWins();

    // 30초마다 체크 (실시간성 개선)
    const interval = setInterval(checkForWins, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleClose = () => {
    setShowDialog(false);
    setWinningProduct(null);
  };

  const handleViewProduct = () => {
    if (winningProduct) {
      navigate(`/product/${winningProduct.id}`);
      setShowDialog(false);
      setWinningProduct(null);
    }
  };

  return (
    <Dialog open={showDialog} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-2xl text-center">🎉 축하합니다!</DialogTitle>
          <DialogDescription className="sr-only">
            낙찰 축하 및 판매자 연락처 정보
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <p className="text-center text-lg font-semibold">
            "{winningProduct?.title}" 경매에서 낙찰받으셨습니다!
          </p>
          <p className="text-center text-muted-foreground">
            낙찰가: <span className="font-bold text-primary">{winningProduct?.current_price.toLocaleString()}원</span>
          </p>
          <Separator />
          {winningProduct && <SellerContactInfo productId={winningProduct.id} />}
          <div className="flex gap-2">
            <Button 
              variant="outline"
              className="flex-1" 
              onClick={handleClose}
            >
              나중에 보기
            </Button>
            <Button 
              className="flex-1" 
              onClick={handleViewProduct}
            >
              상품 상세보기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default WinnerNotification;
