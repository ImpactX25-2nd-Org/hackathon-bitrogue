import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DiseaseDetectionResult } from "@/components/DiseaseDetectionResult";
import { CommunityDashboard } from "@/components/CommunityDashboard";
import { SolutionPage } from "@/components/SolutionPage";
import { Button } from "@/components/ui/button";
import { Sprout, Users, Lightbulb, Camera } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();
  const [isSolutionPageOpen, setIsSolutionPageOpen] = useState(false);
  
  // Mock data for disease detection
  const mockDiseaseData = {
    diseaseName: "Early Blight (Alternaria solani)",
    reliability: 92,
    nextSteps: [
      "Remove and destroy infected leaves immediately to prevent spread",
      "Apply copper-based fungicide every 7-10 days",
      "Ensure proper spacing between plants for air circulation",
      "Water at soil level, avoid wetting leaves",
      "Apply mulch to prevent soil splash onto lower leaves",
    ],
    communityAdvice: [
      {
        farmerName: "Suresh Deshmukh",
        trustScore: 88,
        advice: "I faced this same issue last month. Applied Mancozeb fungicide twice with 10 days gap. Also removed all infected leaves. Crop recovered well in 3 weeks.",
        helpfulCount: 24,
        responseCount: 8,
        timestamp: "2 days ago",
      },
      {
        farmerName: "Kavita Naik",
        trustScore: 95,
        advice: "Early blight spreads fast in humid weather. I use neem oil mixed with copper fungicide - it's organic and very effective. Also maintain good plant spacing of at least 60cm.",
        helpfulCount: 31,
        responseCount: 12,
        timestamp: "5 days ago",
      },
    ],
    isCommon: true,
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sprout className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold text-foreground">FarmConnect</h1>
                <p className="text-sm text-muted-foreground">Agricultural Community Support Platform</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              className="gap-2"
              onClick={() => navigate("/crop-scan")}
            >
              <Camera className="h-4 w-4" />
              Scan Crop
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="detection" className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-md mx-auto mb-8">
            <TabsTrigger value="detection" className="gap-2">
              <Sprout className="h-4 w-4" />
              Disease Detection
            </TabsTrigger>
            <TabsTrigger value="community" className="gap-2">
              <Users className="h-4 w-4" />
              Community Dashboard
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="detection" className="mt-0">
            <div className="max-w-4xl mx-auto">
              <DiseaseDetectionResult {...mockDiseaseData} />
            </div>
          </TabsContent>
          
          <TabsContent value="community" className="mt-0">
            <div className="max-w-5xl mx-auto">
              <CommunityDashboard />
            </div>
          </TabsContent>
        </Tabs>
      </main>

      <div className="mt-16 border-t border-border bg-muted/30">
        <div className="container mx-auto px-4 py-12">
          <h2 className="text-2xl font-bold text-foreground mb-8 text-center">Community Workflow</h2>
          <div className="prose prose-sm max-w-none">
            <div className="bg-card rounded-lg p-6 border border-border">
              <h3 className="text-lg font-semibold text-foreground mb-4">How the System Works:</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-primary mb-2">1. Disease Detection & Analysis</h4>
                  <p className="text-muted-foreground text-sm">
                    Farmer uploads crop image → ML model analyzes → Provides diagnosis with reliability score
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-primary mb-2">2. Common Disease Flow</h4>
                  <p className="text-muted-foreground text-sm">
                    If disease is common → Display AI suggestions with color-coded reliability + Community advice from farmers with proven trust scores
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-primary mb-2">3. Rare Disease Flow</h4>
                  <p className="text-muted-foreground text-sm">
                    If disease is rare/new → Farmer posts to Community Dashboard → Community members respond → Government extension workers verify solution
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-primary mb-2">4. Trust Score System</h4>
                  <p className="text-muted-foreground text-sm">
                    Each community member has a trust score that increases with positive feedback and decreases with negative feedback. This ensures reliable advice surfaces to the top.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Action Button - Solve This */}
      <Button
        size="lg"
        className="fixed bottom-8 right-8 h-14 px-6 rounded-full shadow-lg gap-2 z-50"
        onClick={() => setIsSolutionPageOpen(true)}
      >
        <Lightbulb className="h-5 w-5" />
        Solve this
      </Button>

      {/* Solution Page Modal */}
      <SolutionPage
        open={isSolutionPageOpen}
        onClose={() => setIsSolutionPageOpen(false)}
        diseaseName={mockDiseaseData.diseaseName}
        imageUrl="/placeholder.svg"
      />
    </div>
  );
};

export default Index;
