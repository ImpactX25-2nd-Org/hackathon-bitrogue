import { useState } from "react";
import { MessageCirclePlus, Sprout } from "lucide-react";
import { Button } from "@/components/ui/button";
import { QuestionCard } from "@/components/QuestionCard";
import { TrendingSidebar } from "@/components/TrendingSidebar";
import { TopFarmersCard } from "@/components/TopFarmersCard";
import { AskQuestionModal } from "@/components/AskQuestionModal";

const mockQuestions = [
  {
    id: "1",
    author: "Ramesh Yadav",
    authorLevel: "beginner" as const,
    authorScore: 120,
    question: "Which pesticide should I use for whiteflies on tomato?",
    description: "My tomato plants are heavily infested with whiteflies. Looking for effective and safe pesticide recommendations.",
    timestamp: "2 hours ago",
    tags: ["tomato", "pest-control", "whiteflies"],
    answers: [
      {
        id: "a1",
        author: "Priya Singh",
        authorLevel: "expert" as const,
        authorScore: 1180,
        content: "Use Imidacloprid 17.8% SL at 0.3ml per litre of water. Spray during early morning or evening. Repeat after 10-12 days if needed. Also maintain proper plant spacing for better air circulation.",
        isVerified: true,
        verificationReason: "This recommendation matches agricultural guidelines for whitefly control on tomatoes. Imidacloprid is approved by CIBRC and the dosage is scientifically validated.",
        helpful: 15,
        timestamp: "1 hour ago",
      },
      {
        id: "a2",
        author: "Suresh Kumar",
        authorLevel: "reliable" as const,
        authorScore: 650,
        content: "Try neem oil spray - 5ml per litre water. It's organic and safe. I've been using it for 3 years with good results.",
        isVerified: true,
        verificationReason: "Neem-based pesticides are recognized as effective organic alternatives for whitefly management. The concentration mentioned is within safe and effective limits.",
        helpful: 8,
        timestamp: "45 minutes ago",
      },
    ],
  },
  {
    id: "2",
    author: "Meena Devi",
    authorLevel: "reliable" as const,
    authorScore: 540,
    question: "Best time to plant wheat in North India?",
    description: "Planning to plant wheat this season. What's the optimal sowing time for maximum yield in Punjab region?",
    timestamp: "5 hours ago",
    tags: ["wheat", "sowing", "timing", "north-india"],
    answers: [
      {
        id: "a3",
        author: "Rajesh Kumar",
        authorLevel: "expert" as const,
        authorScore: 1250,
        content: "For Punjab, ideal sowing window is 1st November to 25th November. Late sowing reduces yield by 1% per day after 25th Nov. Ensure soil temperature is 20-25°C for best germination.",
        isVerified: true,
        verificationReason: "This aligns with Punjab Agricultural University recommendations and ICAR guidelines for wheat cultivation in North-Western plains.",
        helpful: 22,
        timestamp: "3 hours ago",
      },
    ],
  },
  {
    id: "3",
    author: "Anil Sharma",
    authorLevel: "beginner" as const,
    authorScore: 85,
    question: "How to increase soil fertility naturally?",
    description: "My soil test shows low nitrogen. Looking for organic methods to improve soil health without chemical fertilizers.",
    timestamp: "1 day ago",
    tags: ["soil-health", "organic-farming", "fertility"],
    answers: [
      {
        id: "a4",
        author: "Amit Patel",
        authorLevel: "reliable" as const,
        authorScore: 890,
        content: "Grow green manure crops like Dhaincha or Sunnhemp before main crop. Incorporate after 45-50 days. Also add well-decomposed FYM @ 10 tons per hectare. Practice crop rotation with legumes.",
        isVerified: true,
        verificationReason: "Green manuring and FYM application are scientifically proven methods to increase soil nitrogen and organic matter content, as per ICAR-IARI research.",
        helpful: 18,
        timestamp: "20 hours ago",
      },
      {
        id: "a5",
        author: "Kavita Singh",
        authorLevel: "expert" as const,
        authorScore: 1050,
        content: "Use vermicompost @ 5 tons/hectare. Also apply biofertilizers like Rhizobium for legumes and Azotobacter for cereals. These fix atmospheric nitrogen naturally.",
        isVerified: true,
        verificationReason: "Vermicompost and biofertilizers are validated by agricultural research institutions for sustainable soil fertility management.",
        helpful: 14,
        timestamp: "18 hours ago",
      },
    ],
  },
];

const Index = () => {
  const [showAskQuestion, setShowAskQuestion] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-primary-light flex items-center justify-center">
              <Sprout className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-primary">KrishiAI</h1>
              <p className="text-xs text-muted-foreground">Farmer Community</p>
            </div>
          </div>
          <Button onClick={() => setShowAskQuestion(true)} className="gap-2">
            <MessageCirclePlus className="h-4 w-4" />
            Ask Question
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[1fr_350px] gap-6">
          {/* Left Column - Questions & Top Farmers */}
          <div className="space-y-6">
            {/* Welcome Banner */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-primary via-primary-light to-success text-primary-foreground">
              <h2 className="text-2xl font-bold mb-2">Welcome to KrishiAI Community! 🌾</h2>
              <p className="text-sm opacity-90">
                Ask questions, share knowledge, and get AI-verified answers from fellow farmers
              </p>
            </div>

            {/* Top Farmers */}
            <TopFarmersCard />

            {/* Questions Feed */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-foreground">Recent Discussions</h2>
                <Button variant="outline" size="sm">Latest</Button>
              </div>
              <div className="space-y-4">
                {mockQuestions.map((question) => (
                  <QuestionCard key={question.id} {...question} />
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Trending Sidebar */}
          <div className="hidden lg:block">
            <TrendingSidebar />
          </div>
        </div>
      </main>

      {/* Ask Question Modal */}
      <AskQuestionModal
        isOpen={showAskQuestion}
        onClose={() => setShowAskQuestion(false)}
      />
    </div>
  );
};

export default Index;
