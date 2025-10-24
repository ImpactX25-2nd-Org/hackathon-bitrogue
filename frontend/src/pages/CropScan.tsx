import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sprout, Camera, Upload, Mic, Play, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { onSendForDetection } from "@/lib/api-placeholders";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";

export default function CropScan() {
  const navigate = useNavigate();
  const { currentLanguage } = useLanguage();
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>("");
  const [description, setDescription] = useState("");
  const [cropName, setCropName] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceFile, setVoiceFile] = useState<Blob | null>(null);
  const [transcription, setTranscription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  // Reset form to allow new scan
  const resetForm = () => {
    setImageFile(null);
    setImagePreview("");
    setDescription("");
    setCropName("");
    setVoiceFile(null);
    setTranscription("");
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (cameraInputRef.current) cameraInputRef.current.value = "";
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleVoiceRecord = () => {
    if (isRecording) {
      setIsRecording(false);
      // Simulate voice recording completion (frontend only)
      const mockBlob = new Blob(["mock audio data"], { type: "audio/webm" });
      setVoiceFile(mockBlob);
      setTranscription("Mock transcription: My tomato plants have brown spots on leaves");
      toast({
        title: "Recording completed",
        description: "Voice will be auto-translated to English (backend)",
      });
    } else {
      setIsRecording(true);
      toast({
        title: "Recording started",
        description: "Hold to record your message",
      });
    }
  };

  const handlePlayVoice = () => {
    if (voiceFile) {
      toast({
        title: "Playing recording",
        description: "Audio playback (frontend only)",
      });
    }
  };

  const handleSubmit = async () => {
    if (!imageFile || !cropName || !description) {
      toast({
        title: "Missing information",
        description: "Please add an image, crop name, and description",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    
    try {
      console.log('📤 Sending image for detection:', {
        cropName,
        imageSize: imageFile.size,
        imageType: imageFile.type
      });
      
      const result = await onSendForDetection({
        image: imageFile,
        cropName,
        description,
        voiceFile,
        language: currentLanguage,
      });
      
      console.log('✅ Detection result received:', result);
      
      toast({
        title: "Analysis complete!",
        description: `Disease detected: ${result.diseaseName}`,
      });
      
      // Navigate to dashboard to show results (scanId will be in URL)
      setTimeout(() => {
        setIsSubmitting(false);
        navigate(`/dashboard?scanId=${result.scanId}`);
      }, 1000);
      
    } catch (error: any) {
      setIsSubmitting(false);
      toast({
        title: "Analysis failed",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <Sprout className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-3xl font-bold text-foreground">Crop Scan</h1>
              <p className="text-sm text-muted-foreground">Upload and analyze your crop</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">Scan Your Crop</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Image Upload Area */}
              <div
                className="border-2 border-dashed border-border rounded-lg p-8 text-center transition-colors hover:border-primary"
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
              >
                {imagePreview ? (
                  <div className="space-y-4">
                    <img
                      src={imagePreview}
                      alt="Crop preview"
                      className="max-h-64 mx-auto rounded-lg"
                    />
                    <p className="text-sm text-muted-foreground">Image selected</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex justify-center gap-4">
                      <Upload className="h-12 w-12 text-muted-foreground" />
                    </div>
                    <p className="text-foreground font-medium">
                      Drag and drop your image here
                    </p>
                    <p className="text-sm text-muted-foreground">or</p>
                  </div>
                )}

                <div className="flex gap-4 justify-center mt-4">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    className="gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Add Photo
                  </Button>

                  <input
                    ref={cameraInputRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    variant="outline"
                    onClick={() => cameraInputRef.current?.click()}
                    className="gap-2"
                  >
                    <Camera className="h-4 w-4" />
                    Scan Photo
                  </Button>
                </div>
              </div>

              {/* Description Input */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Brief Description
                </label>
                <Input
                  placeholder="Describe the problem in one line..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              {/* Crop Name Input */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Crop Name
                </label>
                <Input
                  placeholder="e.g., Groundnut / Cotton / Mango"
                  value={cropName}
                  onChange={(e) => setCropName(e.target.value)}
                />
              </div>

              {/* Voice Recording */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-foreground">
                  Voice Recording (Optional)
                </label>
                <div className="flex gap-2">
                  <Button
                    variant={isRecording ? "destructive" : "secondary"}
                    onClick={handleVoiceRecord}
                    className={`gap-2 flex-1 ${isRecording ? 'animate-pulse' : ''}`}
                  >
                    <Mic className="h-4 w-4" />
                    {isRecording ? "Stop Recording" : "Record voice (your language)"}
                  </Button>
                  {voiceFile && (
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handlePlayVoice}
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                <p className="text-xs text-muted-foreground italic">
                  Voice will be auto-translated to English (backend)
                </p>

                {transcription && (
                  <div className="bg-muted rounded-md p-3">
                    <p className="text-sm text-foreground font-medium mb-1">
                      Transcription:
                    </p>
                    <p className="text-sm text-muted-foreground">{transcription}</p>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={resetForm}
                  disabled={!imageFile && !cropName && !description}
                >
                  Clear Form
                </Button>
                <Button
                  className="flex-1 gap-2"
                  onClick={handleSubmit}
                  disabled={!imageFile || !cropName || !description || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Send for Detection"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
