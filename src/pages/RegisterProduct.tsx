import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import Header from "@/components/Header";
import { z } from "zod";

const productSchema = z.object({
  title: z.string().trim().min(1, "상품명을 입력해주세요").max(100, "상품명은 100자 이하여야 합니다"),
  description: z.string().trim().max(2000, "상품 설명은 2000자 이하여야 합니다").optional(),
  location: z.string().trim().min(1, "위치를 입력해주세요").max(100, "위치는 100자 이하여야 합니다"),
  category: z.string().min(1, "카테고리를 선택해주세요"),
  startingPrice: z.string().refine((val) => {
    const num = Number(val);
    return !isNaN(num) && num >= 0 && num <= 1000000000;
  }, "시작가는 0원 이상 10억원 이하여야 합니다"),
  imageUrl: z.string().trim().url("올바른 URL 형식이 아닙니다").optional().or(z.literal("")),
  sellerPhone: z.string().trim().regex(/^(01[0-9]-?[0-9]{3,4}-?[0-9]{4})?$/, "올바른 전화번호 형식이 아닙니다 (예: 010-1234-5678)").optional().or(z.literal("")),
  endTime: z.string().min(1, "경매 종료 시간을 선택해주세요"),
});

const RegisterProduct = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get("edit");
  const [isLoading, setIsLoading] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    location: "",
    category: "전체",
    startingPrice: "",
    imageUrl: "",
    endTime: "",
    sellerPhone: "",
  });

  useEffect(() => {
    // 페이지 최상단으로 스크롤
    window.scrollTo(0, 0);

    // 수정 모드일 경우 기존 데이터 불러오기
    const loadProductData = async () => {
      if (editId) {
        setIsEditMode(true);
        const { data } = await supabase
          .from("products")
          .select("*")
          .eq("id", editId)
          .single();

        if (data) {
          setFormData({
            title: data.title,
            description: data.description || "",
            location: data.location,
            category: data.category,
            startingPrice: data.starting_price.toString(),
            imageUrl: data.image_url || "",
            endTime: new Date(data.end_time).toISOString().slice(0, 16),
            sellerPhone: data.seller_phone || "",
          });
        }
      }
    };

    loadProductData();
  }, [editId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // 입력값 검증
    try {
      productSchema.parse(formData);
    } catch (error) {
      if (error instanceof z.ZodError) {
        toast({
          title: "입력값 오류",
          description: error.errors[0].message,
          variant: "destructive",
        });
        setIsLoading(false);
        return;
      }
    }

    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      toast({
        title: "로그인 필요",
        description: "상품을 등록하려면 로그인이 필요합니다.",
        variant: "destructive",
      });
      navigate("/auth");
      setIsLoading(false);
      return;
    }

    const endTime = new Date(formData.endTime);
    if (endTime <= new Date()) {
      toast({
        title: isEditMode ? "수정 실패" : "등록 실패",
        description: "종료 시간은 현재 시간보다 이후여야 합니다.",
        variant: "destructive",
      });
      setIsLoading(false);
      return;
    }

    const productData = {
      title: formData.title,
      description: formData.description,
      location: formData.location,
      category: formData.category,
      starting_price: Number(formData.startingPrice),
      image_url: formData.imageUrl.trim() || null,
      end_time: endTime.toISOString(),
      seller_phone: formData.sellerPhone.trim() || null,
    };

    let error;
    if (isEditMode && editId) {
      // 수정 모드
      const result = await supabase
        .from("products")
        .update(productData)
        .eq("id", editId);
      error = result.error;
    } else {
      // 등록 모드
      const result = await supabase
        .from("products")
        .insert({
          ...productData,
          current_price: Number(formData.startingPrice),
          seller_id: user.id,
        });
      error = result.error;
    }

    if (error) {
      toast({
        title: isEditMode ? "수정 실패" : "등록 실패",
        description: isEditMode ? "상품 수정 중 오류가 발생했습니다." : "상품 등록 중 오류가 발생했습니다.",
        variant: "destructive",
      });
      setIsLoading(false);
      return;
    }

    toast({
      title: isEditMode ? "수정 완료" : "등록 완료",
      description: isEditMode ? "상품이 성공적으로 수정되었습니다." : "상품이 성공적으로 등록되었습니다.",
    });

    navigate("/");
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">{isEditMode ? "경매 물품 수정" : "경매 물품 등록"}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title">상품명 *</Label>
                <Input
                  id="title"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="상품명을 입력하세요"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">상품 설명</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="상품에 대한 자세한 설명을 입력하세요"
                  rows={5}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">위치 *</Label>
                <Input
                  id="location"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="예: 서울시 강남구"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">카테고리 *</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="전체">전체</SelectItem>
                    <SelectItem value="패션">패션</SelectItem>
                    <SelectItem value="디지털">디지털</SelectItem>
                    <SelectItem value="가전">가전</SelectItem>
                    <SelectItem value="생활">생활</SelectItem>
                    <SelectItem value="기타">기타</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="startingPrice">시작가 (원) *</Label>
                <Input
                  id="startingPrice"
                  type="number"
                  required
                  min="0"
                  value={formData.startingPrice}
                  onChange={(e) => setFormData({ ...formData, startingPrice: e.target.value })}
                  placeholder="100000"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="imageUrl">이미지 URL</Label>
                <Input
                  id="imageUrl"
                  type="url"
                  value={formData.imageUrl}
                  onChange={(e) => setFormData({ ...formData, imageUrl: e.target.value })}
                  placeholder="https://example.com/image.jpg (비워두면 기본 이미지 사용)"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sellerPhone">판매자 연락처</Label>
                <Input
                  id="sellerPhone"
                  type="tel"
                  value={formData.sellerPhone}
                  onChange={(e) => setFormData({ ...formData, sellerPhone: e.target.value })}
                  placeholder="010-1234-5678 (낙찰자에게만 공개됩니다)"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endTime">경매 종료 시간 *</Label>
                <Input
                  id="endTime"
                  type="datetime-local"
                  required
                  value={formData.endTime}
                  onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                />
              </div>

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => navigate("/")}
                  disabled={isLoading}
                >
                  취소
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-gradient-primary"
                  disabled={isLoading}
                >
                  {isLoading ? (isEditMode ? "수정 중..." : "등록 중...") : (isEditMode ? "상품 수정하기" : "상품 등록하기")}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RegisterProduct;
