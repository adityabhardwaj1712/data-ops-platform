"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Shield, Search, AlertTriangle, CheckCircle2, ArrowRight } from "lucide-react"
import Link from "next/link"

export default function ReviewPage() {
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const data = await api.get("/api/hitl")
      setTasks(data)
    } catch (err) {
      console.error("Failed to fetch HITL tasks", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      <div className="flex items-center justify-between animate-in">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold font-outfit">Quality <span className="text-gradient">Audit</span></h1>
          <p className="text-muted-foreground">Human-in-the-loop verification for low-confidence results</p>
        </div>
        <div className="flex gap-4">
          <Badge variant="outline" className="px-4 py-1 border-yellow-500/20 bg-yellow-500/5 text-yellow-500 gap-2">
            <AlertTriangle className="h-3 w-3" />
            {tasks.length} Pending
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 animate-in stagger-1">
        {tasks.length === 0 && !loading ? (
          <div className="glass-card text-center py-24 space-y-6">
            <div className="h-20 w-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto border border-green-500/20 text-green-400">
              <CheckCircle2 className="h-10 w-10" />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-bold font-outfit">All Clear!</h3>
              <p className="text-muted-foreground max-w-sm mx-auto">No results currently require human verification. Your engines are performing with high confidence.</p>
            </div>
          </div>
        ) : (
          tasks.map((task, idx) => (
            <div key={task.id} className="glass-card group hover:border-primary/30 transition-all animate-in" style={{ animationDelay: `${idx * 0.1}s` }}>
              <div className="flex items-start justify-between">
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Badge className="bg-yellow-500/20 text-yellow-500 border-yellow-500/20">Needs Audit</Badge>
                    <span className="text-xs font-mono text-muted-foreground">Job ID: {task.job_id}</span>
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-xl font-bold font-outfit group-hover:text-primary transition-colors">{task.target_url}</h3>
                    <p className="text-sm text-muted-foreground">Low confidence on fields: <span className="text-red-400">{task.low_confidence_fields?.join(", ")}</span></p>
                  </div>
                </div>
                <Link href={`/review/${task.id}`}>
                  <Button className="gap-2 bg-primary hover:bg-primary/90 shadow-lg shadow-primary/20">
                    Verify Now
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="glass-card p-8 animate-in stagger-2 border-primary/20 bg-primary/5">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-xl bg-primary/20 flex items-center justify-center text-primary shrink-0">
            <Shield className="h-6 w-6" />
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-bold font-outfit">Why am I seeing this?</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              When our AI engines identify data but have low confidence (below 80%), they flag it for a human audit. This ensures 100% data integrity before export. Once you verify a result, the system learns from your correction to improve future extraction.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
