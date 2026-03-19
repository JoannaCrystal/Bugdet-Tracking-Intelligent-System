import { useState } from "react";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Select } from "../ui/select";

interface InvestmentPreferencesFormProps {
  onSubmit: (riskAppetite: "low" | "medium" | "high", horizonMonths: number) => void;
  isLoading?: boolean;
}

const HORIZON_OPTIONS = [
  { value: "12", label: "12 months" },
  { value: "24", label: "24 months" },
  { value: "36", label: "36 months" },
  { value: "60", label: "60 months" },
  { value: "120", label: "120 months" },
];

export function InvestmentPreferencesForm({ onSubmit, isLoading = false }: InvestmentPreferencesFormProps) {
  const [riskAppetite, setRiskAppetite] = useState<"low" | "medium" | "high">("medium");
  const [horizonMonths, setHorizonMonths] = useState("60");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const months = parseInt(horizonMonths, 10);
    if (!isNaN(months) && months > 0 && !isLoading) {
      onSubmit(riskAppetite, months);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 sm:items-end">
      <div>
        <Label htmlFor="risk">Risk Appetite</Label>
        <Select
          id="risk"
          value={riskAppetite}
          onChange={(e) => setRiskAppetite(e.target.value as "low" | "medium" | "high")}
          disabled={isLoading}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </Select>
      </div>
      <div>
        <Label htmlFor="horizon">Investment Horizon (months)</Label>
        <Select
          id="horizon"
          value={horizonMonths}
          onChange={(e) => setHorizonMonths(e.target.value)}
          disabled={isLoading}
        >
          {HORIZON_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      </div>
      <div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Loading..." : "Get Suggestions"}
        </Button>
      </div>
    </form>
  );
}
