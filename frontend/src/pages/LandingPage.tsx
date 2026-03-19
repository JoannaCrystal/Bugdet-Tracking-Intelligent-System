import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { TrendingUp, Upload, Sparkles } from "lucide-react";

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
        <div className="text-center mb-12 sm:mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 tracking-tight mb-4">
            Personal Finance
            <span className="text-teal-600"> AI</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-2">
            AI-powered insights for your spending, savings, and goals.
          </p>
          <p className="text-slate-500 mb-10">
            Connect your data and get clear, trustworthy financial analysis.
          </p>
          <div className="flex flex-wrap justify-center gap-4 mb-4">
            <Button
              size="lg"
              onClick={() => navigate("/data-sources")}
              className="bg-teal-600 hover:bg-teal-700"
            >
              <TrendingUp className="mr-2 h-5 w-5" />
              Use Plaid Sample Data
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate("/data-sources")}
              className="border-teal-200 text-teal-700 hover:bg-teal-50"
            >
              <Upload className="mr-2 h-5 w-5" />
              Upload Statement
            </Button>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/data-sources")}
            className="text-slate-500 hover:text-slate-700"
          >
            <Sparkles className="mr-2 h-4 w-4" />
            Generate Demo Data
          </Button>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-16 sm:mb-20">
          {[
            {
              title: "Spending Insights",
              desc: "Understand where your money goes with clear category breakdowns.",
              icon: "📊",
            },
            {
              title: "Savings Planning",
              desc: "Set goals and get realistic monthly targets with cutback suggestions.",
              icon: "🎯",
            },
            {
              title: "Subscription Review",
              desc: "Detect recurring charges and find easy wins.",
              icon: "🔄",
            },
            {
              title: "Ask Natural Questions",
              desc: "Get answers in plain language powered by AI agents.",
              icon: "💬",
            },
          ].map((f) => (
            <div
              key={f.title}
              className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <span className="text-2xl mb-3 block">{f.icon}</span>
              <h3 className="font-semibold text-slate-800 mb-2">{f.title}</h3>
              <p className="text-sm text-slate-600">{f.desc}</p>
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50/80 p-8 max-w-2xl mx-auto">
          <h3 className="font-semibold text-slate-800 mb-3">Trust & Transparency</h3>
          <p className="text-sm text-slate-600 mb-2">
            Insights are based on your uploaded or sandbox data. We never see your bank credentials.
          </p>
          <p className="text-sm text-slate-600">
            Investment suggestions are educational only—not financial advice. Always consult a qualified professional.
          </p>
        </div>
      </div>
    </div>
  );
}
