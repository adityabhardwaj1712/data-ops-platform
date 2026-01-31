"use client"

import { useState, useEffect } from "react"
import { api, pollJobStatus } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sparkles, Settings2, Play, AlertCircle, CheckCircle2, Download, History, Database, Shield, Zap, Info, RotateCcw, Bug } from "lucide-react"

interface ScrapeJob {
  job_id: string
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED_FINAL" | "RERUNNING"
  result?: any
  confidence?: number
  confidence_components?: Record<string, number>
  strategy_used?: string
  error?: string
  debug_data?: any
}

const DEFAULT_SCHEMA = JSON.stringify({
  title: "h1",
  price: ".a-price-whole",
  description: "meta[name='description']"
}, null, 2)

export default function ScrapePage() {
  const [url, setUrl] = useState("")
  const [strategy, setStrategy] = useState("auto")
  const [schema, setSchema] = useState(DEFAULT_SCHEMA)
  const [job, setJob] = useState<ScrapeJob | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [history, setHistory] = useState<ScrapeJob[]>([])
  const [debug, setDebug] = useState(false)
  const [useAutoDetect, setUseAutoDetect] = useState(false)
  const [aiPrompt, setAiPrompt] = useState("")
  const [previewData, setPreviewData] = useState<any>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  // Load history from local storage
  useEffect(() => {
    const saved = localStorage.getItem("scrape_history")
    if (saved) setHistory(JSON.parse(saved))
  }, [])

  const saveToHistory = (newJob: ScrapeJob) => {
    const updated = [newJob, ...history.slice(0, 9)]
    setHistory(updated)
    localStorage.setItem("scrape_history", JSON.stringify(updated))
  }

  const handleScrape = async () => {
    try {
      setLoading(true)
      setProgress(10)
      setJob(null)

      const response = await api.post<ScrapeJob>("/api/scrape", {
        url,
        strategy,
        schema: useAutoDetect ? {} : JSON.parse(schema),
        debug,
        auto_detect: useAutoDetect
      })

      setJob(response)
      setProgress(30)

      const finalStatus = await pollJobStatus(response.job_id, (status) => {
        setJob(prev => ({ ...prev, ...status }))
        if (status.status === "running") setProgress(60)
      })

      setProgress(100)
      saveToHistory(finalStatus)
    } catch (err: any) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  const downloadResults = () => {
    if (!job?.result) return
    const blob = new Blob([JSON.stringify(job.result, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `scrape_results_${job.job_id}.json`
    a.click()
  }

  const handleReplay = async (jobId: string) => {
    try {
      setLoading(true)
      const response = await api.post<{ job_id: string }>(`/api/scrape/${jobId}/replay`)
      setJob({ job_id: response.job_id, status: "PENDING" })

      const finalStatus = await pollJobStatus(response.job_id, (status) => {
        setJob(prev => ({ ...prev, ...status }))
      })
      saveToHistory(finalStatus)
    } catch (err: any) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateSchema = async () => {
    if (!aiPrompt) return
    try {
      setLoading(true)
      const response = await api.post<{ prompt: string, generated_schema: any }>(`/api/scrape/ai-schema?prompt=${encodeURIComponent(aiPrompt)}`)
      setSchema(JSON.stringify(response.generated_schema, null, 2))
      alert("Schema generated successfully!")
    } catch (err: any) {
      alert("Failed to generate schema: " + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async () => {
    try {
      setPreviewLoading(true)
      setPreviewData(null)
      const response = await api.post<any>("/api/scrape/preview", {
        url,
        schema: JSON.parse(schema),
        strategy: "static"
      })
      setPreviewData(response)
    } catch (err: any) {
      alert("Preview failed: " + err.message)
    } finally {
      setPreviewLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold font-outfit">Enterprise <span className="text-gradient">Scraper</span></h1>
          <p className="text-muted-foreground">Pro-grade extraction with smart engine selection</p>
        </div>
        <Badge variant="outline" className="px-4 py-1 border-primary/20 bg-primary/5 text-primary">
          v2.5.0 STABLE
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card shadow-2xl space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground ml-1">Target URL</label>
                <Input
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="bg-white/5 border-white/10 h-11 focus:ring-primary"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-sm font-medium text-muted-foreground">Scraping Strategy</label>
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <span className={`text-[10px] uppercase font-bold tracking-tighter transition-colors ${debug ? 'text-primary' : 'text-muted-foreground'}`}>
                      Debug Mode
                    </span>
                    <div
                      onClick={() => setDebug(!debug)}
                      className={`h-4 w-8 rounded-full border border-white/10 transition-colors p-0.5 flex ${debug ? 'bg-primary border-primary justify-end' : 'bg-white/5 justify-start'}`}
                    >
                      <div className="h-2.5 w-2.5 rounded-full bg-white shadow-sm" />
                    </div>
                  </label>
                </div>
                <Select value={strategy} onValueChange={setStrategy}>
                  <SelectTrigger className="bg-white/5 border-white/10 h-11">
                    <SelectValue placeholder="Select Strategy" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0f1115] border-white/10 text-white">
                    <SelectItem value="auto" className="hover:bg-primary/20">Auto (Smart Ladder)</SelectItem>
                    <SelectItem value="static" className="hover:bg-primary/20">Static (Fast HTTP)</SelectItem>
                    <SelectItem value="browser" className="hover:bg-primary/20">Browser (Playwright)</SelectItem>
                    <SelectItem value="stealth" className="hover:bg-primary/20">Stealth (Anti-Bot)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Tabs defaultValue="simple" className="w-full">
              <div className="flex items-center justify-between mb-4">
                <TabsList className="bg-white/5 border border-white/10 p-1">
                  <TabsTrigger value="simple" className="flex items-center gap-2 data-[state=active]:bg-primary">
                    <Sparkles className="h-4 w-4" />
                    Simple Mode
                  </TabsTrigger>
                  <TabsTrigger value="advanced" className="flex items-center gap-2 data-[state=active]:bg-primary">
                    <Settings2 className="h-4 w-4" />
                    Advanced (JSON)
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="simple" className="mt-0 space-y-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground ml-1">What do you want to extract?</label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="e.g., product name, price, and primary image"
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                        className="bg-white/5 border-white/10"
                      />
                      <Button
                        variant="secondary"
                        onClick={handleGenerateSchema}
                        disabled={loading || !aiPrompt}
                        className="gap-2"
                      >
                        <Sparkles className="h-4 w-4" />
                        Generate
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-xl border border-primary/20 bg-primary/5">
                    <div className="space-y-1">
                      <p className="text-sm font-bold text-primary">Auto Field Detection</p>
                      <p className="text-xs text-muted-foreground">AI-powered extraction without manual selectors</p>
                    </div>
                    <Button
                      variant={useAutoDetect ? "default" : "outline"}
                      size="sm"
                      onClick={() => setUseAutoDetect(!useAutoDetect)}
                      className="h-8"
                    >
                      {useAutoDetect ? "Enabled" : "Enable"}
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="advanced" className="mt-0 space-y-2">
                <div className="space-y-4">
                  <Textarea
                    value={schema}
                    onChange={(e) => setSchema(e.target.value)}
                    rows={6}
                    className="font-mono text-xs bg-white/5 border-white/10 focus:ring-primary"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full gap-2 border-primary/20 text-primary hover:bg-primary/5"
                    onClick={handlePreview}
                    disabled={previewLoading || !url}
                  >
                    <Zap className="h-4 w-4" />
                    {previewLoading ? "Running Preview..." : "Run Preview (Dry Run)"}
                  </Button>
                </div>
              </TabsContent>
            </Tabs>

            <Button
              onClick={handleScrape}
              className="w-full h-12 text-md font-bold bg-primary hover:bg-primary/90 shadow-lg shadow-primary/20 transition-all active:scale-[0.98]"
              disabled={loading || !url}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Engine Running...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Play className="h-4 w-4 fill-current" />
                  Launch Engine
                </span>
              )}
            </Button>
          </div>

          {loading && (
            <div className="glass-card animate-in fade-in slide-in-from-bottom-2 space-y-4">
              <div className="flex justify-between text-sm font-medium">
                <span className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                  Execution Progress
                </span>
                <span className="text-primary">{progress}%</span>
              </div>
              <Progress value={progress} className="h-1.5 bg-white/5 shadow-inner" />
            </div>
          )}

          {job && job.status === "COMPLETED" && (
            <div className="space-y-6 animate-in zoom-in-95">
              <div className="glass-card border-green-500/20">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold font-outfit flex items-center gap-2 text-green-400">
                    <CheckCircle2 className="h-5 w-5" />
                    Results
                  </h3>
                  <Button variant="ghost" size="sm" onClick={downloadResults} className="text-primary hover:bg-primary/10">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
                <div className="p-4 rounded-xl bg-black/40 border border-white/5 overflow-auto max-h-[400px] text-xs font-mono text-green-400/90 shadow-inner">
                  {JSON.stringify(job.result || {}, null, 2)}
                </div>
              </div>

              {job.debug_data && (
                <div className="glass-card border-primary/20 bg-primary/5">
                  <h3 className="text-lg font-bold font-outfit flex items-center gap-2 mb-4">
                    <Bug className="h-5 w-5 text-primary" />
                    Debug Intelligence
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Escalation Path</p>
                      <div className="space-y-2">
                        {job.debug_data.escalation_path?.map((step: any, idx: number) => (
                          <div key={idx} className="flex items-center gap-3 text-xs p-2 rounded bg-black/20 border border-white/5">
                            <Badge variant={step.status === 'success' ? 'success' : 'destructive'} className="h-4 text-[8px]">
                              {step.status}
                            </Badge>
                            <span className="font-mono">{step.strategy}</span>
                            {step.error && <span className="text-red-400/60 truncate italic max-w-[100px]">{step.error}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Engine Metrics</p>
                      <div className="space-y-2">
                        {Object.entries(job.debug_data.engine_metrics || {}).map(([engine, time]: any) => (
                          <div key={engine} className="flex items-center justify-between text-xs p-2 rounded bg-black/20 border border-white/5">
                            <span className="font-mono uppercase">{engine}</span>
                            <span className="text-primary font-bold">{Number(time).toFixed(2)}s</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {previewData && (
            <div className="glass-card border-yellow-500/20 bg-yellow-500/5 space-y-4 animate-in fade-in zoom-in-95">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold font-outfit flex items-center gap-2 text-yellow-500">
                  <Zap className="h-5 w-5" />
                  Preview Results
                </h3>
                <Badge variant={previewData.status === 'success' ? 'success' : 'destructive'}>
                  {previewData.success_rate}% Success
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase text-muted-foreground">Found</p>
                  <div className="space-y-1">
                    {Object.entries(previewData.found).map(([field, value]: any) => (
                      <div key={field} className="text-xs p-2 rounded bg-black/20 border border-white/5 flex justify-between">
                        <span className="font-bold text-green-400">{field}</span>
                        <span className="text-muted-foreground truncate max-w-[150px]">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase text-muted-foreground">Missing</p>
                  <div className="space-y-1">
                    {previewData.missing.map((field: string) => (
                      <div key={field} className="text-xs p-2 rounded bg-black/20 border border-red-500/20 text-red-400 flex items-center gap-2">
                        <AlertCircle className="h-3 w-3" />
                        {field}
                      </div>
                    ))}
                    {previewData.missing.length === 0 && <p className="text-xs text-muted-foreground italic">None</p>}
                  </div>
                </div>
              </div>
            </div>
          )}

          {job && job.status === "FAILED_FINAL" && (
            <div className="glass-card border-red-500/20 bg-red-500/5 space-y-3">
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="h-5 w-5" />
                <h3 className="font-bold">Extraction Failed</h3>
              </div>
              <p className="text-sm text-red-300/80 font-mono p-3 bg-black/20 rounded-lg">{job.error || "Unknown error occurred"}</p>
            </div>
          )}
        </div>

        <div className="space-y-8">
          <div className="glass-card space-y-6">
            <h3 className="text-xl font-bold font-outfit border-b border-white/5 pb-2">Execution Metrics</h3>
            <div className="space-y-4">
              <MetricItem icon={<Database className="h-4 w-4" />} label="Active Engine" value={job?.strategy_used || "Idle"} />
              <MetricItem icon={<Shield className="h-4 w-4" />} label="Anti-Bot" value={job?.strategy_used === 'stealth' ? 'Active' : 'Off'} />
              <MetricItem icon={<Zap className="h-4 w-4" />} label="Confidence" value={job?.confidence ? `${job.confidence}%` : "0%"} color={job?.confidence && job.confidence > 80 ? 'text-green-400' : 'text-primary'} />
            </div>
          </div>

          <div className="glass-card space-y-6">
            <h3 className="text-xl font-bold font-outfit flex items-center gap-2 border-b border-white/5 pb-2">
              <History className="h-5 w-5" />
              Recent Jobs
            </h3>
            <div className="space-y-3">
              {history.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">No jobs in session</p>
              ) : (
                history.map((h, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                    <div className="space-y-0.5">
                      <p className="text-[10px] text-muted-foreground font-mono truncate max-w-[120px]">{h.job_id}</p>
                      <p className="text-xs font-medium uppercase text-primary">{h.status}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 rounded-full hover:bg-primary/20 hover:text-primary"
                        onClick={() => handleReplay(h.job_id)}
                        disabled={loading}
                      >
                        <RotateCcw className="h-3.5 w-3.5" />
                      </Button>
                      <Badge className={h.status === 'COMPLETED' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}>
                        {h.confidence ? `${h.confidence}%` : '-'}
                      </Badge>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricItem({ icon, label, value, color = "text-primary" }: { icon: any, label: string, value: string, color?: string }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-sm font-medium">{label}</span>
      </div>
      <span className={`text-sm font-bold uppercase tracking-wider ${color}`}>{value}</span>
    </div>
  )
}
