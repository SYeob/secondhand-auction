import { useState, useEffect, useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroBanner1 from "@/assets/hero-banner-1.png";
import heroBanner2 from "@/assets/hero-banner-2.png";
import heroBanner3 from "@/assets/hero-banner-3.png";

const banners = [
  {
    title: "프리미엄 경매 플랫폼",
    subtitle: "신뢰할 수 있는 거래의 시작",
    image: heroBanner1,
  },
  {
    title: "실시간 경매",
    subtitle: "최고의 가격으로 낙찰받으세요",
    image: heroBanner2,
  },
  {
    title: "안전한 거래",
    subtitle: "믿을 수 있는 플랫폼",
    image: heroBanner3,
  },
];

const Hero = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [currentX, setCurrentX] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      if (!isDragging) {
        setCurrentSlide((prev) => (prev + 1) % banners.length);
      }
    }, 5000);
    return () => clearInterval(timer);
  }, [isDragging]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % banners.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + banners.length) % banners.length);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setStartX(e.pageX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setCurrentX(e.pageX);
  };

  const handleMouseUp = () => {
    if (!isDragging) return;
    
    const diff = startX - currentX;
    const threshold = 50;

    if (Math.abs(diff) > threshold) {
      if (diff > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
    }

    setIsDragging(false);
    setStartX(0);
    setCurrentX(0);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    setIsDragging(true);
    setStartX(e.touches[0].pageX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    setCurrentX(e.touches[0].pageX);
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    
    const diff = startX - currentX;
    const threshold = 50;

    if (Math.abs(diff) > threshold) {
      if (diff > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
    }

    setIsDragging(false);
    setStartX(0);
    setCurrentX(0);
  };

  return (
    <div 
      ref={containerRef}
      className="relative h-[400px] md:h-[500px] overflow-hidden bg-gradient-hero cursor-grab active:cursor-grabbing select-none"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Slides */}
      {banners.map((banner, index) => (
        <div
          key={index}
          className={`absolute inset-0 transition-all duration-500 ${
            index === currentSlide ? "opacity-100 translate-x-0" : "opacity-0 translate-x-full"
          }`}
          style={{
            transform: isDragging && index === currentSlide 
              ? `translateX(${currentX - startX}px)` 
              : undefined
          }}
        >
          <div className="relative w-full h-full">
            <img 
              src={banner.image} 
              alt={banner.title}
              className="w-full h-full object-cover"
              draggable={false}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-black/40 to-transparent flex items-center justify-center">
              <div className="text-center text-white px-4 animate-fade-in">
                <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-lg">
                  {banner.title}
                </h1>
                <p className="text-xl md:text-2xl opacity-90 drop-shadow-md">
                  {banner.subtitle}
                </p>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Navigation Buttons */}
      <Button
        variant="ghost"
        size="icon"
        onClick={prevSlide}
        className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm z-10"
      >
        <ChevronLeft className="h-6 w-6" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        onClick={nextSlide}
        className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm z-10"
      >
        <ChevronRight className="h-6 w-6" />
      </Button>

      {/* Indicators */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 z-10">
        {banners.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`h-2 rounded-full transition-all ${
              index === currentSlide ? "w-8 bg-white" : "w-2 bg-white/50"
            }`}
          />
        ))}
      </div>
    </div>
  );
};

export default Hero;
