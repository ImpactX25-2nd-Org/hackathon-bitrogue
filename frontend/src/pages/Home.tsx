import { Button } from "@/components/ui/button";
import { Sprout, ArrowRight, Globe } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useLanguage, languages } from "@/contexts/LanguageContext";

export default function Home() {
  const navigate = useNavigate();
  const { currentLanguage, setLanguage } = useLanguage();

  const handleGetStarted = () => {
    // Language is already stored via context
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-green-50/50">
      {/* Header */}
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
            
            {/* Language Selector */}
            <div className="flex items-center gap-3">
              <Select value={currentLanguage} onValueChange={setLanguage}>
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
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Logo */}
            <div className="flex justify-center mb-8">
              <div className="h-24 w-24 rounded-full bg-primary/10 flex items-center justify-center">
                <Sprout className="h-16 w-16 text-primary" />
              </div>
            </div>

            {/* Welcome Message */}
            <div className="space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-foreground">
                Welcome to KrishiLok
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Empowering farmers with AI-powered disease detection, community wisdom, 
                and real-time crop guidance in your local language.
              </p>
            </div>

            {/* Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
              <div className="bg-card rounded-lg border border-border p-6 hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-3">🌾</div>
                <h3 className="font-semibold text-foreground mb-2">Disease Detection</h3>
                <p className="text-sm text-muted-foreground">
                  AI-powered crop disease identification and treatment recommendations
                </p>
              </div>
              <div className="bg-card rounded-lg border border-border p-6 hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-3">👥</div>
                <h3 className="font-semibold text-foreground mb-2">Farmer Community</h3>
                <p className="text-sm text-muted-foreground">
                  Connect with experienced farmers and share agricultural knowledge
                </p>
              </div>
              <div className="bg-card rounded-lg border border-border p-6 hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-3">�️</div>
                <h3 className="font-semibold text-foreground mb-2">Multi-Language</h3>
                <p className="text-sm text-muted-foreground">
                  Access information in Tamil, Marathi, Kannada, Hindi, and more
                </p>
              </div>
            </div>

            {/* Get Started Button */}
            <div className="pt-8">
              <Button
                size="lg"
                onClick={handleGetStarted}
                className="h-14 px-10 text-base font-semibold gap-2 transition-transform hover:scale-105"
              >
                Get Started
                <ArrowRight className="h-5 w-5" />
              </Button>
            </div>

            {/* Info Note */}
            <p className="text-sm text-muted-foreground pt-8">
              Join thousands of farmers using KrishiLok to improve their harvest
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
