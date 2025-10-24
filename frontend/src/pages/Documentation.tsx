import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Sprout, ArrowLeft, Globe } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useLanguage, languages } from "@/contexts/LanguageContext";

interface CropInfo {
  name: string;
  season: string;
  infoGap: string;
  color: string;
}

const cropsData: CropInfo[] = [
  {
    name: "Ragi (Finger Millet)",
    season: "June–September (Kharif)",
    infoGap: "Farmers don't track rainfall onset accurately → late sowing reduces yield; lack info on improved high-protein varieties.",
    color: "bg-amber-50 border-amber-200",
  },
  {
    name: "Sunflower",
    season: "January–April",
    infoGap: "Missing data on how cloudy weather lowers oil content; limited knowledge of bee pollination role.",
    color: "bg-yellow-50 border-yellow-200",
  },
  {
    name: "Groundnut",
    season: "June–October",
    infoGap: "Unawareness about calcium and sulfur micronutrient importance for better pod formation.",
    color: "bg-orange-50 border-orange-200",
  },
  {
    name: "Cotton",
    season: "June–September",
    infoGap: "Farmers lack access to pest surveillance data (bollworm outbreaks) and don't rotate crops properly.",
    color: "bg-blue-50 border-blue-200",
  },
  {
    name: "Sugarcane",
    season: "Jan–Mar & Oct–Dec",
    infoGap: "Lack guidance on ratoon management and water-efficient irrigation (subsurface drip).",
    color: "bg-green-50 border-green-200",
  },
  {
    name: "Turmeric",
    season: "May–August",
    infoGap: "No real-time disease alert systems (leaf blotch, rhizome rot); improper drying methods reduce market value.",
    color: "bg-yellow-50 border-yellow-300",
  },
  {
    name: "Pulses (Black gram, Green gram)",
    season: "October–December",
    infoGap: "Missing info on temperature-sensitive flowering and suitable intercrops.",
    color: "bg-lime-50 border-lime-200",
  },
  {
    name: "Grapes",
    season: "August–April",
    infoGap: "Poor awareness of pruning schedules and fungal disease cycles.",
    color: "bg-purple-50 border-purple-200",
  },
  {
    name: "Chilli",
    season: "June–September (Kharif), October–February (Rabi)",
    infoGap: "Lack knowledge of pest management (thrips, leaf curl virus) and fertilizer balance.",
    color: "bg-red-50 border-red-200",
  },
  {
    name: "Rice (Paddy)",
    season: "Samba (Aug–Jan), Kuruvai (Jun–Sep)",
    infoGap: "Unawareness about rainfall changes causing transplant delays and poor drainage in deltas.",
    color: "bg-emerald-50 border-emerald-200",
  },
];

const CropCard = ({ crop }: { crop: CropInfo }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card className={`${crop.color} border-2 transition-all duration-300 hover:shadow-lg`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-xl font-bold text-foreground mb-1">
              {crop.name}
            </CardTitle>
            <p className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Sprout className="h-4 w-4" />
              Best Season: {crop.season}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="gap-2 shrink-0"
          >
            {isExpanded ? (
              <>
                Hide Details <ChevronUp className="h-4 w-4" />
              </>
            ) : (
              <>
                View Details <ChevronDown className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      
      {/* Expandable Info Gap Section */}
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <CardContent className="pt-0">
          <div className="bg-background/60 rounded-lg p-4 border border-border">
            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
              📊 Information Gap
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {crop.infoGap}
            </p>
          </div>
        </CardContent>
      </div>
    </Card>
  );
};

export default function Documentation() {
  const navigate = useNavigate();
  const { currentLanguage, setLanguage } = useLanguage();

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-amber-50">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(-1)}
              className="shrink-0"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-3 flex-1">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Sprout className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-foreground">Crop Knowledge Center</h1>
                <p className="text-sm text-muted-foreground">Learn about crops, seasons, and knowledge gaps</p>
              </div>
            </div>
            
            {/* Language Selector */}
            <div className="shrink-0">
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
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          {/* Introduction Card */}
          <Card className="mb-8 bg-gradient-to-r from-green-100 to-yellow-100 border-2 border-green-300">
            <CardContent className="pt-6">
              <h2 className="text-xl font-bold text-foreground mb-2">
                🌾 Why This Matters
              </h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Understanding crop seasons and knowledge gaps helps farmers make better decisions. 
                This guide highlights common information challenges farmers face and opportunities 
                for improved agricultural practices.
              </p>
            </CardContent>
          </Card>

          {/* Crop Cards Grid */}
          <div className="space-y-4">
            {cropsData.map((crop, index) => (
              <div
                key={index}
                className="animate-in fade-in slide-in-from-bottom-4"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <CropCard crop={crop} />
              </div>
            ))}
          </div>

          {/* Footer Note */}
          <div className="mt-8 text-center">
            <p className="text-sm text-muted-foreground italic">
              💡 This information is curated to help bridge knowledge gaps in modern farming practices.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
