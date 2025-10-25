import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DiseaseDetectionResult } from "@/components/DiseaseDetectionResult";
import { CommunityDashboard } from "@/components/CommunityDashboard";
import { SolutionPage } from "@/components/SolutionPage";
import { Button } from "@/components/ui/button";
import { Sprout, Users, Lightbulb, Camera, HelpCircle, LogOut, Globe, ArrowLeft } from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";
import { useLanguage, languages } from "@/contexts/LanguageContext";
import { getUserScans, getScanById } from "@/lib/api";

const Index = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isSolutionPageOpen, setIsSolutionPageOpen] = useState(false);
  const [currentTab, setCurrentTab] = useState("detection");
  const { currentLanguage, setLanguage } = useLanguage();
  const [diseaseData, setDiseaseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load scan data from backend
  useEffect(() => {
    const loadScanData = async () => {
      const scanId = searchParams.get('scanId');
      
      console.log('🔍 URL:', window.location.href);
      console.log('🔍 Search Params:', window.location.search);
      console.log('🔍 ScanId from params:', scanId);
      
      try {
        setIsLoading(true);
        console.log('📊 Loading scan data from backend...');
        
        if (scanId) {
          // Load specific scan
          console.log('📍 Loading scan by ID:', scanId);
          const response = await getScanById(scanId);
          
          if (response.success && response.data) {
            setDiseaseData({
              diseaseName: response.data.diseaseName || "Unknown Disease",
              reliability: response.data.reliability || 0,
              timestamp: response.data.timestamp,
              nextSteps: response.data.nextSteps || [],
              communityAdvice: response.data.communityAdvice || [],
              isCommon: response.data.isCommon || true,
            });
            console.log('✅ Loaded scan data:', response.data.diseaseName);
          }
        } else {
          // Load user's latest scan
          console.log('📍 Loading user\'s latest scan');
          const response = await getUserScans(0, 1);
          
          if (response.success && response.data.scans.length > 0) {
            const latestScan = response.data.scans[0];
            setDiseaseData({
              diseaseName: latestScan.disease_name || "Unknown Disease",
              reliability: latestScan.reliability || 0,
              timestamp: latestScan.created_at,
              nextSteps: latestScan.next_steps || [],
              communityAdvice: [],
              isCommon: latestScan.is_common || true,
            });
            console.log('✅ Loaded latest scan:', latestScan.disease_name);
          } else {
            // No scans yet, show mock data
            console.log('📝 No scans found, using mock data');
            setDiseaseData(mockDiseaseData);
          }
        }
      } catch (error: any) {
        console.error('❌ Error loading scan data:', error);
        toast({
          title: "Failed to load scan data",
          description: error.message || "Using demo data",
          variant: "destructive",
        });
        setDiseaseData(mockDiseaseData);
      } finally {
        setIsLoading(false);
      }
    };

    loadScanData();
  }, [searchParams]); // Reload when URL params change


  const handleLanguageChange = (language: string) => {
    setLanguage(language);
    toast({
      title: "Language updated",
      description: `Switched to ${languages.find(l => l.code === language)?.name}`,
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userData");
    toast({
      title: "Logged out",
      description: "You have been successfully logged out",
    });
    navigate("/");
  };
  
  // Mock community advice data
  const mockCommunityAdvice = [
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
  ];
  
  // Fallback mock data for disease detection
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
    communityAdvice: mockCommunityAdvice,
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
                <h1 className="text-3xl font-bold text-foreground">KrishiLok</h1>
                <p className="text-sm text-muted-foreground">Agricultural Community Support Platform</p>
              </div>
            </div>
            
            {/* Language Selector, Back to Login, and Logout */}
            <div className="flex items-center gap-3">
              <Select value={currentLanguage} onValueChange={handleLanguageChange}>
                <SelectTrigger className="w-[160px]">
                  <Globe className="h-4 w-4 mr-2 text-primary" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      <span className="font-medium">{lang.nativeName}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/login")}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Login
              </Button>
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleLogout}
                    className="rounded-full"
                  >
                    <LogOut className="h-5 w-5 text-muted-foreground" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Logout</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="detection" className="w-full" onValueChange={setCurrentTab}>
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
              {/* Know More Icon - Top Left */}
              <div className="flex items-center justify-between mb-4">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-16 w-16 rounded-full hover:bg-primary/10"
                      onClick={() => navigate("/documentation")}
                    >
                      <HelpCircle className="h-12 w-12 text-primary stroke-[3]" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Know More</p>
                  </TooltipContent>
                </Tooltip>
                <div className="flex-1"></div>
              </div>

              {/* Scan new crop button */}
              <div className="flex items-center justify-between mb-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate("/crop-scan")}
                  className="gap-2"
                >
                  <Camera className="h-4 w-4" />
                  Scan New Crop
                </Button>
                {diseaseData?.timestamp && (
                  <p className="text-xs text-muted-foreground">
                    Last scan: {new Date(diseaseData.timestamp).toLocaleString()}
                  </p>
                )}
              </div>
              
              {isLoading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="mt-4 text-muted-foreground">Loading scan data...</p>
                  </div>
                </div>
              ) : (
                <DiseaseDetectionResult {...(diseaseData || mockDiseaseData)} />
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="community" className="mt-0">
            <div className="max-w-5xl mx-auto">
              {/* Know More Icon - Top Left */}
              <div className="flex items-center justify-between mb-4">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-16 w-16 rounded-full hover:bg-primary/10"
                      onClick={() => navigate("/documentation")}
                    >
                      <HelpCircle className="h-12 w-12 text-primary stroke-[3]" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Know More</p>
                  </TooltipContent>
                </Tooltip>
                <div className="flex-1"></div>
              </div>
              
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

      {/* Floating Action Buttons */}
      
      {/* Solve This FAB - Hidden on Community Dashboard */}
      {currentTab !== "community" && (
        <Button
          size="lg"
          className="fixed bottom-8 left-1/2 -translate-x-1/2 h-16 px-8 rounded-full shadow-lg gap-2 z-50 transition-transform active:scale-110 duration-120"
          onClick={() => setIsSolutionPageOpen(true)}
        >
          <Lightbulb className="h-6 w-6" />
          Solve this
        </Button>
      )}

      {/* Scan Crop FAB */}
      <Button
        size="lg"
        className="fixed bottom-8 right-8 h-16 px-8 rounded-full shadow-lg gap-2 z-50 transition-transform active:scale-110 duration-120"
        onClick={() => navigate("/crop-scan")}
      >
        <Camera className="h-6 w-6" />
        Scan Crop
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
