import { ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import ProductCard from "./ProductCard";

interface ProductSectionProps {
  title: string;
  products: Array<{
    id: number | string;
    title: string;
    location: string;
    currentPrice: number;
    imageUrl: string;
    endTime?: number;
    endTimeStamp?: string;
  }>;
}

const ProductSection = ({ title, products }: ProductSectionProps) => {
  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl md:text-3xl font-bold">{title}</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} {...product} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProductSection;
