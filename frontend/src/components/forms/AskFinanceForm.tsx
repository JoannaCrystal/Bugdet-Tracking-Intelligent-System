import { useState, useEffect } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Search } from "lucide-react";

const DEFAULT_PROMPTS = [
  "What are my subscriptions?",
  "Where am I overspending?",
  "Can I save $20,000 in 12 months?",
  "What should I cut down?",
  "What investment options fit a medium risk appetite?",
];

interface AskFinanceFormProps {
  onSubmit: (question: string) => void;
  isLoading?: boolean;
  compact?: boolean;
  initialQuestion?: string;
  suggestedPrompts?: string[];
}

export function AskFinanceForm({
  onSubmit,
  isLoading = false,
  compact = false,
  initialQuestion = "",
  suggestedPrompts = DEFAULT_PROMPTS,
}: AskFinanceFormProps) {
  const [question, setQuestion] = useState(initialQuestion);

  useEffect(() => {
    if (initialQuestion) setQuestion(initialQuestion);
  }, [initialQuestion]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (q && !isLoading) {
      onSubmit(q);
    }
  };

  const handleChipClick = (prompt: string) => {
    setQuestion(prompt);
    onSubmit(prompt);
  };

  if (compact) {
    return (
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          placeholder="Ask about your finances..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
          className="max-w-sm"
        />
        <Button type="submit" disabled={isLoading || !question.trim()} size="sm">
          {isLoading ? "..." : "Ask"}
        </Button>
      </form>
    );
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <Input
          placeholder="e.g. What are my subscriptions? How can I save more?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
          className="flex-1 min-w-0"
        />
        <Button type="submit" disabled={isLoading || !question.trim()} className="shrink-0">
          <Search className="h-4 w-4 mr-2" />
          {isLoading ? "Analyzing..." : "Ask"}
        </Button>
      </form>
      <div className="flex flex-wrap gap-2">
        {suggestedPrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => handleChipClick(prompt)}
            disabled={isLoading}
            className="px-3 py-1.5 text-sm rounded-full bg-slate-100 hover:bg-teal-50 hover:text-teal-700 text-slate-600 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
