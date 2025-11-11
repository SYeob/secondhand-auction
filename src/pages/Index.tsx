import { useState, useEffect, useMemo } from "react";
import Header from "@/components/Header";
import CategoryNav from "@/components/CategoryNav";
import Hero from "@/components/Hero";
import ProductSection from "@/components/ProductSection";
import { supabase } from "@/integrations/supabase/client";

// 상품 타입 정의
interface Product {
  id: number | string;
  title: string;
  location: string;
  currentPrice: number;
  imageUrl: string;
  endTime?: number;
  endTimeStamp?: string;
  category?: string;
}

// 샘플 데이터
// const allProducts: Product[] = [
//   {
//     id: 1,
//     title: "나이키 에어맥스",
//     location: "용인시 기흥구",
//     currentPrice: 75000,
//     imageUrl: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&h=500&fit=crop",
//     endTime: 7200, // 2시간
//     category: "패션",
//   },
//   {
//     id: 2,
//     title: "아이폰 13 Pro",
//     location: "경기도 성남시",
//     currentPrice: 975000,
//     imageUrl: "https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=500&h=500&fit=crop",
//     endTime: 5400, // 1시간 30분
//     category: "디지털/가전",
//   },
//   {
//     id: 3,
//     title: "조던 1 레트로",
//     location: "용인시 수지구",
//     currentPrice: 105000,
//     imageUrl: "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=500&h=500&fit=crop",
//     endTime: 3600, // 1시간
//     category: "패션",
//   },
//   {
//     id: 4,
//     title: "MacBook Air M2",
//     location: "서울시 강남구",
//     currentPrice: 1250000,
//     imageUrl: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&h=500&fit=crop",
//     endTime: 10800, // 3시간
//     category: "디지털/가전",
//   },
// ];

// const popularProducts: Product[] = [
//   {
//     id: 5,
//     title: "갤럭시 Z Flip5",
//     location: "서울시 서초구",
//     currentPrice: 850000,
//     imageUrl: "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500&h=500&fit=crop",
//     endTime: 4500, // 1시간 15분
//     category: "디지털/가전",
//   },
//   {
//     id: 6,
//     title: "소니 WH-1000XM5",
//     location: "경기도 수원시",
//     currentPrice: 320000,
//     imageUrl: "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500&h=500&fit=crop",
//     endTime: 9000, // 2시간 30분
//     category: "디지털/가전",
//   },
//   {
//     id: 7,
//     title: "캐논 EOS R6",
//     location: "서울시 마포구",
//     currentPrice: 2850000,
//     imageUrl: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&h=500&fit=crop",
//     endTime: 1800, // 30분
//     category: "디지털/가전",
//   },
//   {
//     id: 8,
//     title: "다이슨 V15",
//     location: "인천시 연수구",
//     currentPrice: 680000,
//     imageUrl: "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500&h=500&fit=crop",
//     endTime: 6300, // 1시간 45분
//     category: "디지털/가전",
//   },
// ];

const Index = () => {
  const [activeCategory, setActiveCategory] = useState("전체");
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);

  // 카테고리와 검색어에 따른 필터링
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesCategory =
        activeCategory === "전체" || product.category === activeCategory;
      const matchesSearch =
        searchQuery === "" ||
        product.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.location.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [products, activeCategory, searchQuery]);

  useEffect(() => {
    // 페이지 최상단으로 스크롤
    window.scrollTo(0, 0);

    // 데이터베이스에서 상품 가져오기
    const fetchProducts = async () => {
      const { data, error } = await supabase
        .from("products")
        .select("*")
        .order("created_at", { ascending: false });

      if (data && !error) {
        // 데이터베이스 상품을 로컬 형식으로 변환
        const dbProducts = data.map((product) => ({
          id: product.id,
          title: product.title,
          location: product.location,
          currentPrice: product.current_price,
          imageUrl: product.image_url || "",
          category: product.category,
          endTimeStamp: product.end_time, // Pass timestamp for real-time calculation
        }));
        setProducts(dbProducts);
      }
    };

    fetchProducts();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header onSearch={setSearchQuery} />
      <CategoryNav
        activeCategory={activeCategory}
        onCategoryChange={setActiveCategory}
      />
      <Hero />
      <ProductSection
        title={
          activeCategory === "전체"
            ? searchQuery
              ? `검색 결과: "${searchQuery}"`
              : "전체상품"
            : activeCategory
        }
        products={filteredProducts}
      />
    </div>
  );
};

export default Index;
