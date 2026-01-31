"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Globe, List, Shield, Zap, Search, Activity } from 'lucide-react'
import Link from 'next/link'

export default function Dashboard() {
  return (
    <div className="max-w-5xl mx-auto space-y-12 py-10">
      <div className="space-y-4 text-center animate-in">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold tracking-widest uppercase">
          <Activity className="h-3 w-3" />
          System Active
        </div>
        <h1 className="text-6xl font-bold tracking-tight font-outfit">
          Data<span className="text-gradient">Ops</span> Scraper
        </h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          High-performance, human-verified scraping infrastructure. Powered by smart engine selection and anti-bot evasion.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <DashboardCard
          href="/scrape"
          icon={<Search className="h-6 w-6 text-primary" />}
          title="Engine"
          description="Launch new extraction job"
          delay="stagger-1"
        />
        <DashboardCard
          href="/jobs"
          icon={<List className="h-6 w-6 text-blue-400" />}
          title="Jobs"
          description="Monitor active sessions"
          delay="stagger-2"
        />
        <DashboardCard
          href="/review"
          icon={<Shield className="h-6 w-6 text-purple-400" />}
          title="Review"
          description="Human-in-the-loop audit"
          delay="stagger-3"
        />
      </div>

      <div className="space-y-6 animate-in stagger-2">
        <div className="flex flex-col gap-1">
          <h2 className="text-2xl font-bold font-outfit">Intent <span className="text-primary">Templates</span></h2>
          <p className="text-sm text-muted-foreground">Pre-built templates for common extraction tasks</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <TemplateCard
            title="Job Listings"
            description="Extract employment opportunities from career sites"
            icon={<Activity className="h-5 w-5 text-blue-400" />}
          />
          <TemplateCard
            title="Product Catalog"
            description="Extract product details from e-commerce sites"
            icon={<Globe className="h-5 w-5 text-green-400" />}
          />
          <TemplateCard
            title="News Articles"
            description="Extract news content from media websites"
            icon={<List className="h-5 w-5 text-purple-400" />}
          />
        </div>
      </div>

      <div className="glass-card p-8 animate-in stagger-3">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold font-outfit flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500 fill-yellow-500/20" />
            System Statistics
          </h3>
          <span className="text-xs font-mono text-muted-foreground">v2.5.0-STABLE</span>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          <StatItem label="Jobs Completed" value="1,284" />
          <StatItem label="Success Rate" value="98.2%" />
          <StatItem label="Avg. Latency" value="1.4s" />
          <StatItem label="Proxy Health" value="100%" />
        </div>
      </div>
    </div>
  )
}

function DashboardCard({ href, icon, title, description, delay }: { href: string, icon: any, title: string, description: string, delay: string }) {
  return (
    <Link href={href} className={`animate-in ${delay}`}>
      <div className="glass-card group hover:scale-[1.02] active:scale-[0.98] cursor-pointer">
        <div className="mb-4 h-12 w-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:border-primary/50 transition-colors">
          {icon}
        </div>
        <h3 className="text-xl font-bold mb-1 font-outfit">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </Link>
  )
}

function StatItem({ label, value }: { label: string, value: string }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold font-outfit text-white">{value}</p>
    </div>
  )
}

function TemplateCard({ title, description, icon }: { title: string, description: string, icon: any }) {
  return (
    <div className="glass-card hover:border-primary/50 transition-all cursor-pointer group">
      <div className="h-10 w-10 rounded-lg bg-white/5 flex items-center justify-center border border-white/10 mb-4 group-hover:bg-primary/10 transition-colors">
        {icon}
      </div>
      <h3 className="font-bold font-outfit mb-1">{title}</h3>
      <p className="text-xs text-muted-foreground leading-relaxed">{description}</p>
    </div>
  )
}