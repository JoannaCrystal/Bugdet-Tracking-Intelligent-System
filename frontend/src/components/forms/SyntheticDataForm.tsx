import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

interface SyntheticDataFormProps {
  onSubmit: (count: number, daysBack: number) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function SyntheticDataForm({ onSubmit, isLoading = false, disabled = false }: SyntheticDataFormProps) {
  const [count, setCount] = useState("50");
  const [daysBack, setDaysBack] = useState("90");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const c = parseInt(count, 10);
    const d = parseInt(daysBack, 10);
    if (!isNaN(c) && c >= 1 && c <= 1000 && !isNaN(d) && d >= 1 && d <= 365 && !isLoading && !disabled) {
      onSubmit(c, d);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 sm:items-end">
      <div>
        <Label htmlFor="count">Number of transactions</Label>
        <Input
          id="count"
          type="number"
          min="1"
          max="1000"
          value={count}
          onChange={(e) => setCount(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div>
        <Label htmlFor="days">Days back</Label>
        <Input
          id="days"
          type="number"
          min="1"
          max="365"
          value={daysBack}
          onChange={(e) => setDaysBack(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div>
        <Button type="submit" disabled={isLoading || disabled}>
          {isLoading ? "Generating..." : "Generate Demo Data"}
        </Button>
      </div>
    </form>
  );
}
