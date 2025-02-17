
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import Sidebar from "@/components/layout/Sidebar";
import Breadcrumbs from "@/components/layout/Breadcrumbs";

import Dashboard from "@/pages/Dashboard";
import StudyActivities from "@/pages/StudyActivities";
import Words from "@/pages/Words";
import WordGroups from "@/pages/WordGroups";
import Sessions from "@/pages/Sessions";
import Settings from "@/pages/Settings";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-8">
            <Breadcrumbs />
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/study-activities" element={<StudyActivities />} />
              <Route path="/words" element={<Words />} />
              <Route path="/groups" element={<WordGroups />} />
              <Route path="/sessions" element={<Sessions />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </div>
        <Toaster />
        <Sonner />
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
