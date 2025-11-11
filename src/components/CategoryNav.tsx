import { cn } from "@/lib/utils";

const categories = ["전체", "패션", "디지털", "가전", "생활", "기타"];

interface CategoryNavProps {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

const CategoryNav = ({ activeCategory, onCategoryChange }: CategoryNavProps) => {
  return (
    <nav className="bg-background border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-2 overflow-x-auto py-3 scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => onCategoryChange(category)}
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all",
                activeCategory === category
                  ? "bg-gradient-primary text-primary-foreground shadow-card"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary"
              )}
            >
              {category}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default CategoryNav;
