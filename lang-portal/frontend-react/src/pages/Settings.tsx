import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

const Settings = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);
  const [resetConfirmation, setResetConfirmation] = useState("");

  useEffect(() => {
    const theme = localStorage.getItem("theme");
    if (theme === "dark") {
      setIsDarkMode(true);
      document.documentElement.classList.add("dark");
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const handleThemeChange = (checked: boolean) => {
    setIsDarkMode(checked);
    if (checked) {
      localStorage.setItem("theme", "dark");
      document.documentElement.classList.add("dark");
    } else {
      localStorage.setItem("theme", "light");
      document.documentElement.classList.remove("dark");
    }
  };

  const handleReset = () => {
    if (resetConfirmation.toLowerCase() === "reset me") {
      console.log("Resetting database...");
      setIsResetDialogOpen(false);
      setResetConfirmation("");
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Settings</h1>
      
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="dark-mode">Dark Mode</Label>
            <p className="text-sm text-gray-500">
              Enable dark mode for a better night time experience
            </p>
          </div>
          <Switch
            id="dark-mode"
            checked={isDarkMode}
            onCheckedChange={handleThemeChange}
          />
        </div>

        <div className="border-t pt-6">
          <div className="space-y-0.5">
            <h2 className="text-lg font-medium">Danger Zone</h2>
            <p className="text-sm text-gray-500">
              Careful! These actions cannot be undone.
            </p>
          </div>
          <div className="mt-4">
            <Button
              variant="destructive"
              onClick={() => setIsResetDialogOpen(true)}
            >
              Reset History
            </Button>
          </div>
        </div>
      </div>

      <Dialog open={isResetDialogOpen} onOpenChange={setIsResetDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Are you sure?</DialogTitle>
            <DialogDescription>
              This action cannot be undone. Type "reset me" to confirm.
            </DialogDescription>
          </DialogHeader>
          <Input
            value={resetConfirmation}
            onChange={(e) => setResetConfirmation(e.target.value)}
            placeholder="Type 'reset me' to confirm"
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsResetDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleReset}
              disabled={resetConfirmation.toLowerCase() !== "reset me"}
            >
              Reset
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Settings;
