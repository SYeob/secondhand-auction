import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Loader2 } from "lucide-react";

interface SellerContactInfoProps {
  productId: string;
}

const SellerContactInfo = ({ productId }: SellerContactInfoProps) => {
  const [sellerPhone, setSellerPhone] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSellerContact = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const { data, error: rpcError } = await supabase.rpc('get_seller_contact', {
          p_product_id: productId
        });

        if (rpcError) {
          console.error("판매자 연락처 조회 오류:", rpcError);
          setError("판매자 연락처를 불러올 수 없습니다.");
          return;
        }

        if (data && data.length > 0) {
          setSellerPhone(data[0].seller_phone);
        }
      } catch (err) {
        console.error("Unexpected error:", err);
        setError("오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchSellerContact();
  }, [productId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 p-4 rounded-lg">
        <p className="text-sm text-destructive text-center">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-primary/5 p-4 rounded-lg">
      <p className="text-sm text-muted-foreground mb-2">판매자 연락처</p>
      <p className="text-2xl font-bold text-center">
        {sellerPhone || '연락처 정보 없음'}
      </p>
    </div>
  );
};

export default SellerContactInfo;
