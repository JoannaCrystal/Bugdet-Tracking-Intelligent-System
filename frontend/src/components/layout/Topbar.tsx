import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

interface TopbarProps {
  onAsk?: (question: string) => void;
}

export function Topbar({ onAsk }: TopbarProps) {
  const [question, setQuestion] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (q) {
      if (onAsk) {
        onAsk(q);
      } else {
        navigate("/ask", { state: { question: q } });
      }
      setQuestion("");
    }
  };

  return (
    <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur flex items-center px-4 gap-3 sm:gap-4 shrink-0">
      <Link to="/dashboard" className="flex items-center gap-2 shrink-0 hover:opacity-80 transition-opacity">
        <span className="text-lg font-semibold text-slate-800">Finance</span>
        <span className="text-xs text-slate-500 font-medium">AI</span>
      </Link>
      <form onSubmit={handleSubmit} className="flex-1 flex gap-2 min-w-0 max-w-xl">
        <Input
          type="text"
          placeholder="Ask a finance question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" size="sm">
          Ask
        </Button>
      </form>
      <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-sm font-medium">
        ?
      </div>
    </header>
  );
}
