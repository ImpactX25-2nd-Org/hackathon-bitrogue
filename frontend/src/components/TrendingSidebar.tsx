import { TrendingUp, MessageCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface TrendingTopic {
  id: string;
  title: string;
  replies: number;
  trending: boolean;
}

const trendingTopics: TrendingTopic[] = [
  { id: "1", title: "Organic pest control for tomatoes", replies: 24, trending: true },
  { id: "2", title: "Best time to plant wheat in winter", replies: 18, trending: true },
  { id: "3", title: "Drip irrigation setup guide", replies: 31, trending: true },
  { id: "4", title: "Dealing with fungal infections", replies: 15, trending: false },
  { id: "5", title: "Soil pH testing methods", replies: 22, trending: false },
  { id: "6", title: "Crop rotation strategies", replies: 19, trending: false },
  { id: "7", title: "Fertilizer recommendations", replies: 27, trending: false },
];

export function TrendingSidebar() {
  return (
    <Card className="h-fit sticky top-6">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5 text-primary" />
          Trending Discussions
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[calc(100vh-12rem)]">
          <div className="space-y-1 p-4 pt-0">
            {trendingTopics.map((topic) => (
              <button
                key={topic.id}
                className="w-full text-left p-3 rounded-lg hover:bg-muted/50 transition-colors group"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors line-clamp-2">
                    {topic.title}
                  </p>
                  {topic.trending && (
                    <span className="flex-shrink-0 w-2 h-2 rounded-full bg-secondary animate-pulse" />
                  )}
                </div>
                <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                  <MessageCircle className="h-3 w-3" />
                  <span>{topic.replies} replies</span>
                </div>
              </button>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
