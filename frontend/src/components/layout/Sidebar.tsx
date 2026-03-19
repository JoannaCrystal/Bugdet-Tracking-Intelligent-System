import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageCircle,
  Receipt,
  RefreshCw,
  PiggyBank,
  TrendingUp,
  Database,
  FileSearch,
} from "lucide-react";
import { cn } from "../../lib/utils";

const navItems = [
  { to: "/dashboard", label: "Overview", Icon: LayoutDashboard },
  { to: "/ask", label: "Ask Finance", Icon: MessageCircle },
  { to: "/transactions", label: "Transactions", Icon: Receipt },
  { to: "/subscriptions", label: "Subscriptions", Icon: RefreshCw },
  { to: "/savings-goal", label: "Savings Goal", Icon: PiggyBank },
  { to: "/investments", label: "Investments", Icon: TrendingUp },
  { to: "/data-sources", label: "Data Sources", Icon: Database },
  { to: "/data-review", label: "Data Review", Icon: FileSearch },
];

// For end link matching so /ask doesn't match /dashboard
function pathMatch(to: string, path: string) {
  if (to === "/dashboard") return path === "/dashboard" || path === "/dashboard/";
  return path === to || path.startsWith(to + "/");
}

export function Sidebar({ collapsed = false }: { collapsed?: boolean }) {
  return (
    <aside
      className={cn(
        "flex flex-col bg-slate-50/80 border-r border-slate-200 transition-all",
        collapsed ? "w-16" : "w-56"
      )}
    >
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-teal-50 text-teal-700 border border-teal-100"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )
            }
          >
            <Icon className="h-5 w-5 shrink-0 opacity-70" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
