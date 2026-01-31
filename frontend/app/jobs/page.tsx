"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { List, RotateCcw, CheckCircle2, AlertCircle, Clock, ExternalLink } from "lucide-react"
import Link from "next/link"

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchJobs()
    const interval = setInterval(fetchJobs, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchJobs = async () => {
    try {
      const data = await api.get("/api/jobs")
      setJobs(data)
    } catch (err) {
      console.error("Failed to fetch jobs", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      <div className="flex items-center justify-between animate-in">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold font-outfit">Active <span className="text-gradient">Sessions</span></h1>
          <p className="text-muted-foreground">Monitor and manage your scraping infrastructure</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchJobs} className="gap-2 glass">
          <RotateCcw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 animate-in stagger-1">
        {jobs.length === 0 && !loading ? (
          <div className="glass-card text-center py-20 space-y-4">
            <div className="h-16 w-16 bg-white/5 rounded-full flex items-center justify-center mx-auto border border-white/10 text-muted-foreground">
              <List className="h-8 w-8" />
            </div>
            <p className="text-lg font-medium text-muted-foreground">No active jobs found</p>
            <Link href="/scrape">
              <Button className="bg-primary hover:bg-primary/90">Launch New Job</Button>
            </Link>
          </div>
        ) : (
          jobs.map((job, idx) => (
            <div key={job.job_id} className={`glass-card flex items-center justify-between animate-in`} style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="flex items-center gap-6">
                <div className={`h-12 w-12 rounded-xl flex items-center justify-center border border-white/10 ${getStatusColor(job.status)}`}>
                  {getStatusIcon(job.status)}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-muted-foreground tracking-tighter">{job.job_id}</span>
                    <Badge variant="outline" className="text-[10px] uppercase">{job.strategy || 'auto'}</Badge>
                  </div>
                  <h3 className="font-bold text-lg font-outfit truncate max-w-[300px]">{job.url}</h3>
                </div>
              </div>
              <div className="flex items-center gap-8">
                <div className="text-right space-y-1">
                  <p className="text-xs text-muted-foreground uppercase font-bold tracking-widest">Status</p>
                  <p className={`text-sm font-bold ${getStatusTextColor(job.status)}`}>{job.status}</p>
                </div>
                <div className="text-right space-y-1">
                  <p className="text-xs text-muted-foreground uppercase font-bold tracking-widest">Confidence</p>
                  <p className="text-sm font-bold text-white">{job.confidence ? `${job.confidence}%` : '-'}</p>
                </div>
                <Link href={`/scrape?jobId=${job.job_id}`}>
                  <Button variant="ghost" size="icon" className="hover:bg-primary/20 hover:text-primary">
                    <ExternalLink className="h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'COMPLETED': return <CheckCircle2 className="h-6 w-6" />
    case 'FAILED_FINAL': return <AlertCircle className="h-6 w-6" />
    case 'RUNNING': return <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
    default: return <Clock className="h-6 w-6" />
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'COMPLETED': return 'bg-green-500/10 text-green-400 border-green-500/20'
    case 'FAILED_FINAL': return 'bg-red-500/10 text-red-400 border-red-500/20'
    case 'RUNNING': return 'bg-primary/10 text-primary border-primary/20'
    default: return 'bg-white/5 text-muted-foreground border-white/10'
  }
}

function getStatusTextColor(status: string) {
  switch (status) {
    case 'COMPLETED': return 'text-green-400'
    case 'FAILED_FINAL': return 'text-red-400'
    case 'RUNNING': return 'text-primary'
    default: return 'text-muted-foreground'
  }
}
