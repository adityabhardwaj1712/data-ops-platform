"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Globe, List, Shield, Zap, Search, Activity, ArrowUpRight } from 'lucide-react'
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

      <div className="glass-card p-10 animate-in stagger-3 relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
          <Zap className="h-32 w-32 text-primary" />
        </div>
        <div className="flex items-center justify-between mb-10 relative z-10">
          <div>
            <h3 className="text-2xl font-bold font-outfit flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <Activity className="h-5 w-5 text-primary" />
              </div>
              Platform Intelligence
            </h3>
            <p className="text-sm text-muted-foreground mt-1">Real-time infrastructure health and performance metrics</p>
          </div>
          <Badge variant="outline" className="px-3 py-1 border-white/10 bg-white/5 font-mono text-[10px] uppercase tracking-tighter">
            System: Stable
          </Badge>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-12 relative z-10">
          <StatItem label="Entities Extracted" value="284,912" trend="+12.5%" />
          <StatItem label="Extraction Quality" value="99.4%" trend="Optimal" />
          <StatItem label="Engine Latency" value="0.84s" trend="-0.2s" />
          <StatItem label="Success Rate" value="98.2%" trend="Stable" />
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

function StatItem({ label, value, trend }: { label: string, value: string, trend?: string }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{label}</p>
        {trend && (
          <div className="flex items-center gap-1 text-[8px] font-bold text-green-400 bg-green-400/10 px-1.5 py-0.5 rounded-full">
            <ArrowUpRight className="h-2 w-2" />
            {trend}
          </div>
        )}
      </div>
      <p className="text-3xl font-bold font-outfit text-white tracking-tighter">{value}</p>
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