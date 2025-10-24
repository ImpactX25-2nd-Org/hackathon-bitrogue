import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { X, CheckCircle2, ChevronRight } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface Suggestion {
  id: string;
  text: string;
  author: {
    name: string;
    avatar?: string;
  };
  usefulness: number;
  details?: string;
}

interface SolutionPageProps {
  open: boolean;
  onClose: () => void;
  diseaseName: string;
  imageUrl: string;
}

// Mock data - will be populated by backend via fetchSuggestions(scanId)
const mockSuggestions: Suggestion[] = [
  {
    id: "1",
    text: "Apply Mancozeb fungicide twice with 10 days gap",
    author: {
      name: "Suresh Deshmukh",
      avatar: "",
    },
    usefulness: 85,
    details: "I faced this same issue last month. Applied Mancozeb fungicide twice with 10 days gap. Also removed all infected leaves. Crop recovered well in 3 weeks. Make sure to spray in early morning or evening.",
  },
  {
    id: "2",
    text: "Use neem oil mixed with copper fungicide - organic and effective",
    author: {
      name: "Kavita Naik",
      avatar: "",
    },
    usefulness: 92,
    details: "This is an organic solution that worked great for me. Mix 5ml neem oil with 2g copper fungicide per liter of water. Spray every 7 days for 3 weeks. Also maintain good plant spacing of at least 60cm for air circulation.",
  },
];

export const SolutionPage = ({
  open,
  onClose,
  diseaseName,
  imageUrl,
}: SolutionPageProps) => {
  const [suggestions] = useState<Suggestion[]>(mockSuggestions);
  const [selectedSuggestion, setSelectedSuggestion] = useState<string | null>(null);
  const [expandedSuggestion, setExpandedSuggestion] = useState<string | null>(null);

  const handleTriedThis = (suggestionId: string) => {
    setSelectedSuggestion(suggestionId);
    toast({
      title: "Solution marked as tried",
      description: "We'll ask for feedback in 10-15 days",
    });
    
    // Backend integration placeholder: submitTrustScore will be called after follow-up
    console.log(`Suggestion ${suggestionId} marked as tried - backend should schedule follow-up`);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-foreground">Suggested Solutions</DialogTitle>
        </DialogHeader>

        {/* Disease Info Card */}
        <Card className="border-primary/30">
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <img
                src={imageUrl || "/placeholder.svg"}
                alt="Crop scan"
                className="w-24 h-24 rounded-lg object-cover"
              />
              <div>
                <h3 className="font-semibold text-foreground mb-1">{diseaseName}</h3>
                <p className="text-sm text-muted-foreground">
                  Based on community experience
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Suggestions List */}
        <div className="space-y-4">
          <h4 className="font-medium text-foreground">Recommendations from Farmers</h4>
          
          {suggestions.map((suggestion) => (
            <Card
              key={suggestion.id}
              className={`transition-all ${
                selectedSuggestion === suggestion.id
                  ? "border-success bg-success/5"
                  : "hover:border-primary/50"
              }`}
            >
              <CardContent className="pt-6 space-y-4">
                {/* Author Info */}
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={suggestion.author.avatar} />
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {suggestion.author.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <p className="font-medium text-foreground">
                      {suggestion.author.name}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">
                        Usefulness:
                      </span>
                      <Progress value={suggestion.usefulness} className="h-2 w-24" />
                      <span className="text-xs font-medium text-foreground">
                        {suggestion.usefulness}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Suggestion Text */}
                <p className="text-sm text-foreground font-medium">
                  {suggestion.text}
                </p>

                {/* Details Toggle */}
                {suggestion.details && (
                  <div>
                    {expandedSuggestion === suggestion.id ? (
                      <div className="bg-muted/50 rounded-md p-3">
                        <p className="text-sm text-muted-foreground">
                          {suggestion.details}
                        </p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setExpandedSuggestion(null)}
                          className="mt-2 h-auto p-0 text-xs"
                        >
                          Show less
                        </Button>
                      </div>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setExpandedSuggestion(suggestion.id)}
                        className="h-auto p-0 gap-1 text-xs text-primary"
                      >
                        Details <ChevronRight className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                )}

                {/* Action Button */}
                <Button
                  variant={selectedSuggestion === suggestion.id ? "outline" : "secondary"}
                  onClick={() => handleTriedThis(suggestion.id)}
                  disabled={selectedSuggestion === suggestion.id}
                  className="w-full gap-2"
                >
                  {selectedSuggestion === suggestion.id ? (
                    <>
                      <CheckCircle2 className="h-4 w-4" />
                      Marked as Tried
                    </>
                  ) : (
                    "Tried This"
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <p className="text-xs text-muted-foreground text-center mt-4">
          These recommendations will be fetched from backend via fetchSuggestions(scanId)
        </p>
      </DialogContent>
    </Dialog>
  );
};
