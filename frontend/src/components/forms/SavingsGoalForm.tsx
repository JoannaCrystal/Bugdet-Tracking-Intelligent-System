import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

interface SavingsGoalFormProps {
  onSubmit: (goalAmount: number, goalMonths: number) => void;
  isLoading?: boolean;
}

export function SavingsGoalForm({ onSubmit, isLoading = false }: SavingsGoalFormProps) {
  const [goalAmount, setGoalAmount] = useState("");
  const [goalMonths, setGoalMonths] = useState("12");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const amount = parseFloat(goalAmount);
    const months = parseInt(goalMonths, 10);
    if (!isNaN(amount) && amount > 0 && !isNaN(months) && months > 0 && !isLoading) {
      onSubmit(amount, months);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 sm:items-end">
      <div>
        <Label htmlFor="goal-amount">Goal Amount ($)</Label>
        <Input
          id="goal-amount"
          type="number"
          min="1"
          step="100"
          placeholder="e.g. 20000"
          value={goalAmount}
          onChange={(e) => setGoalAmount(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div>
        <Label htmlFor="goal-months">Timeframe (months)</Label>
        <Input
          id="goal-months"
          type="number"
          min="1"
          max="600"
          placeholder="e.g. 12"
          value={goalMonths}
          onChange={(e) => setGoalMonths(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div>
        <Button type="submit" disabled={isLoading || !goalAmount}>
          {isLoading ? "Analyzing..." : "Analyze Goal"}
        </Button>
      </div>
    </form>
  );
}
