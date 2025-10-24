import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Sprout, ArrowLeft, Globe, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";
import { Label } from "@/components/ui/label";
import { useLanguage, languages } from "@/contexts/LanguageContext";
import { registerUser } from "@/lib/api";

export default function Signup() {
  const navigate = useNavigate();
  const { currentLanguage, setLanguage } = useLanguage();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [passwordError, setPasswordError] = useState("");

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (value.length > 0 && value.length < 6) {
      setPasswordError("Password must be at least 6 characters long");
    } else {
      setPasswordError("");
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!name || !email || !password) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    // Trim password to remove accidental spaces
    const trimmedPassword = password.trim();
    
    if (trimmedPassword.length < 6) {
      toast({
        title: "Invalid password",
        description: `Password must be at least 6 characters long (current: ${trimmedPassword.length})`,
        variant: "destructive",
      });
      return;
    }

    if (trimmedPassword !== confirmPassword.trim()) {
      toast({
        title: "Password mismatch",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast({
        title: "Invalid email",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const result = await registerUser({
        email,
        password: trimmedPassword,
        name,
        phone: phone || undefined,
        language: currentLanguage,
      });

      if (result.success) {
        toast({
          title: "Registration successful!",
          description: "You can now sign in with your credentials",
        });

        // Navigate to login page
        setTimeout(() => {
          navigate("/login");
        }, 1500);
      } else {
        toast({
          title: "Registration failed",
          description: result.message || "Please try again",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      toast({
        title: "Registration failed",
        description: error.message || "An error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToHome = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-green-50/50">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleBackToHome}
                className="mr-2"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <Sprout className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold text-foreground">KrishiLok</h1>
                <p className="text-sm text-muted-foreground">Create your account</p>
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
        <div className="max-w-md mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Signup Card */}
          <Card className="border-2">
            <CardHeader className="space-y-1">
              <div className="flex justify-center mb-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <Sprout className="h-10 w-10 text-primary" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold text-center text-foreground">
                Join KrishiLok
              </CardTitle>
              <CardDescription className="text-center">
                Connect with farmers and get expert advice
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSignup} className="space-y-4">
                {/* Name Input */}
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm font-medium">
                    Full Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="h-11"
                    disabled={isLoading}
                    required
                  />
                </div>

                {/* Email Input */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium">
                    Email Address <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11"
                    disabled={isLoading}
                    required
                  />
                </div>

                {/* Phone Input (Optional) */}
                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-sm font-medium">
                    Phone Number <span className="text-muted-foreground text-xs">(Optional)</span>
                  </Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="Enter your phone number"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="h-11"
                    disabled={isLoading}
                  />
                </div>

                {/* Password Input */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium">
                    Password <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Create a password (min 6 characters)"
                    value={password}
                    onChange={(e) => handlePasswordChange(e.target.value)}
                    className={`h-11 ${passwordError ? 'border-destructive' : ''}`}
                    disabled={isLoading}
                    required
                    minLength={6}
                  />
                  {passwordError && (
                    <p className="text-xs text-destructive">{passwordError}</p>
                  )}
                  {password.length >= 6 && (
                    <p className="text-xs text-green-600">✓ Password length is valid</p>
                  )}
                </div>

                {/* Confirm Password Input */}
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-sm font-medium">
                    Confirm Password <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`h-11 ${confirmPassword && password !== confirmPassword ? 'border-destructive' : ''}`}
                    disabled={isLoading}
                    required
                  />
                  {confirmPassword && password !== confirmPassword && (
                    <p className="text-xs text-destructive">Passwords do not match</p>
                  )}
                  {confirmPassword && password === confirmPassword && password.length >= 6 && (
                    <p className="text-xs text-green-600">✓ Passwords match</p>
                  )}
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full h-11 font-semibold"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Creating account...
                    </>
                  ) : (
                    "Sign Up"
                  )}
                </Button>

                {/* Divider */}
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">Or</span>
                  </div>
                </div>

                {/* Sign In Link */}
                <div className="text-center">
                  <span className="text-sm text-muted-foreground">
                    Already have an account?{" "}
                  </span>
                  <Button
                    type="button"
                    variant="link"
                    className="px-1 text-primary hover:text-primary/80 font-semibold text-sm"
                    onClick={() => navigate("/login")}
                    disabled={isLoading}
                  >
                    Sign in
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Terms Note */}
          <div className="mt-6 text-center">
            <p className="text-xs text-muted-foreground">
              By signing up, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
