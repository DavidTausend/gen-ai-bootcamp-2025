import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Volume2 } from "lucide-react";

// Function to fetch words from the API
const fetchWords = async (page: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/words?page=${page}`);
    if (!response.ok) {
      throw new Error("Failed to fetch words");
    }
    return response.json();
  } catch (error) {
    console.error("Error fetching words:", error);
    return { items: [], pagination: { current_page: 1, total_pages: 1 } };
  }
};

const Words = () => {
  const [words, setWords] = useState<{ id: number; german: string; english: string; correct?: number; wrong?: number }[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Fetch words when the component loads or when the page changes
  useEffect(() => {
    const loadWords = async () => {
      setLoading(true);
      const data = await fetchWords(currentPage);
      setWords(data.items);
      setTotalPages(data.pagination.total_pages);
      setLoading(false);
    };
    loadWords();
  }, [currentPage]);

  const playSound = (word: string) => {
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = "de-DE"; // German pronunciation
    speechSynthesis.speak(utterance);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Words</h1>
      {loading ? (
        <p className="text-center text-gray-500">Loading words...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>German</TableHead>
                <TableHead>English</TableHead>
                <TableHead>Correct</TableHead>
                <TableHead>Wrong</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {words.length > 0 ? (
                words.map((word) => (
                  <TableRow key={word.id}>
                    <TableCell className="flex items-center space-x-2">
                      <span>{word.german}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => playSound(word.german)}
                      >
                        <Volume2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                    <TableCell>{word.english}</TableCell>
                    <TableCell className="text-green-600">{word.correct || 0}</TableCell>
                    <TableCell className="text-red-600">{word.wrong || 0}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-gray-500">
                    No words found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">
          Page {currentPage} of {totalPages}
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Words;
