import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MapPin, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import pabiDefault from "@/assets/pabi-default.png";

interface ProductCardProps {
  id: number | string;
  title: string;
  location: string;
  currentPrice: number;
  imageUrl: string;
  endTime?: number; // seconds from epoch OR timestamp
  endTimeStamp?: string; // ISO timestamp for database products
}

const ProductCard = ({ id, title, location, currentPrice, imageUrl, endTime, endTimeStamp }: ProductCardProps) => {
  const navigate = useNavigate();
  const [timeLeft, setTimeLeft] = useState(0);
  const [initialDuration, setInitialDuration] = useState(0);

  useEffect(() => {
    const calculateTimeLeft = () => {
      if (endTimeStamp) {
        // Database product with timestamp
        const endDate = new Date(endTimeStamp).getTime();
        const now = Date.now();
        const diff = Math.max(0, Math.floor((endDate - now) / 1000));
        return diff;
      } else if (endTime !== undefined) {
        // Sample data with seconds - save initial duration
        return endTime;
      }
      return 0;
    };

    const initial = calculateTimeLeft();
    setTimeLeft(initial);
    
    // For sample data, save the initial duration for looping
    if (endTime !== undefined && !endTimeStamp) {
      setInitialDuration(endTime);
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev > 0) return prev - 1;
        
        // Loop for sample data only
        if (endTime !== undefined && !endTimeStamp && initialDuration > 0) {
          return initialDuration;
        }
        
        return 0;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [endTime, endTimeStamp, initialDuration]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Card 
      className="group overflow-hidden hover:shadow-card-hover transition-all duration-300 animate-fade-in cursor-pointer"
      onClick={() => navigate(`/product/${id}`)}
    >
      <div className="relative aspect-square overflow-hidden bg-secondary">
        <img
          src={imageUrl || pabiDefault}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        {timeLeft > 0 && (
          <div className="absolute top-3 right-3 bg-accent text-accent-foreground px-3 py-1.5 rounded-lg flex items-center gap-1.5 shadow-lg animate-pulse-glow">
            <Clock className="h-4 w-4" />
            <span className="text-sm font-bold">{formatTime(timeLeft)}</span>
          </div>
        )}
      </div>
      <CardContent className="p-4 space-y-3">
        <h3 className="font-semibold text-lg line-clamp-1 group-hover:text-primary transition-colors">
          {title}
        </h3>
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <MapPin className="h-4 w-4" />
          <span>{location}</span>
        </div>
        <div className="flex items-end justify-between pt-2 border-t border-border">
          <div>
            <p className="text-xs text-muted-foreground mb-1">현재가</p>
            <p className="text-xl font-bold text-primary">
              {currentPrice.toLocaleString()}
              <span className="text-sm font-normal ml-1">원</span>
            </p>
          </div>
          <Button 
            className="bg-gradient-primary hover:opacity-90 transition-opacity shadow-md"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/product/${id}`);
            }}
          >
            응찰하기
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProductCard;
