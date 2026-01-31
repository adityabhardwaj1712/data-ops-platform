import Link from "next/link"
import { Shield, LayoutDashboard, Globe, Search } from "lucide-react"

export function Navigation() {
  return (
    <nav className="sticky top-0 z-50 w-full glass border-b border-white/10 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center ring-2 ring-primary/20 group-hover:rotate-12 transition-transform">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold font-outfit tracking-tight">
            Data<span className="text-primary">Ops</span>
          </span>
        </Link>

        <div className="flex items-center gap-8">
          <NavLink href="/" icon={<LayoutDashboard className="h-4 w-4" />} label="Dashboard" />
          <NavLink href="/scrape" icon={<Search className="h-4 w-4" />} label="Scraper" />
          <NavLink href="/review" icon={<Globe className="h-4 w-4" />} label="Review" />

          <div className="h-8 w-[1px] bg-white/10 mx-2" />

          <button className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 transition-colors text-sm font-medium">
            System Beta
          </button>
        </div>
      </div>
    </nav>
  )
}

function NavLink({ href, icon, label }: { href: string, icon: any, label: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-white transition-colors"
    >
      {icon}
      {label}
    </Link>
  )
}
