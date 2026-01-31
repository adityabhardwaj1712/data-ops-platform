'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
    Card, CardContent, CardHeader, CardTitle, CardDescription
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertCircle, CheckCircle2, RotateCw, Eye, Code, Image as ImageIcon } from 'lucide-react'
import { JsonRenderer } from "@/components/json-renderer"

export default function ReviewPage() {
    const { id } = useParams()
    const router = useRouter()
    const [job, setJob] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [rerunning, setRerunning] = useState(false)
    const [selectors, setSelectors] = useState<any>({})
    const [preflightLoading, setPreflightLoading] = useState(false)
    const [preflightResult, setPreflightResult] = useState<any>(null)
    const [confirmed, setConfirmed] = useState(false)
    const API_BASE_URL = (typeof process !== 'undefined' && process.env ? process.env.NEXT_PUBLIC_API_BASE : '') || "http://localhost:8000"

    useEffect(() => {
        fetchJob()
    }, [id])

    const fetchJob = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/scrape/${id}`)
            const data = await res.json()
            setJob(data)
            if (data.result?.schema?.fields) {
                setSelectors(data.result.schema.fields)
            }
        } catch (err) {
            console.error("Failed to fetch job", err)
        } finally {
            setLoading(false)
        }
    }

    const handlePreflight = async () => {
        setPreflightLoading(true)
        setPreflightResult(null)
        try {
            const res = await fetch(`${API_BASE_URL}/api/scrape/preflight`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: job.config?.url || job.description.replace('Scrape ', ''),
                    schema: {
                        ...job.result.schema,
                        fields: selectors
                    },
                    strategy: job.config?.strategy || 'auto'
                })
            })
            const data = await res.json()
            setPreflightResult(data)
        } catch (err) {
            console.error("Preflight failed", err)
        } finally {
            setPreflightLoading(false)
        }
    }

    const handleRerun = async () => {
        if (!confirmed) return
        setRerunning(true)
        try {
            await fetch(`${API_BASE_URL}/api/scrape/${id}/rerun`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    new_config: {
                        schema: {
                            ...job.result.schema,
                            fields: selectors
                        }
                    }
                })
            })
            router.push(`/jobs`)
        } catch (err) {
            console.error("Rerun failed", err)
        } finally {
            setRerunning(false)
        }
    }

    if (loading) return <div className="p-8 text-center">Loading job data...</div>
    if (!job) return <div className="p-8 text-center text-red-500 font-bold">Job not found</div>

    const result = job.result || {}
    const validation = result.validation_report || { valid: true, errors: [] }

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm border">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Review Job</h1>
                    <p className="text-sm text-muted-foreground font-mono">{id}</p>
                </div>
                <div className="flex gap-3">
                    <Badge variant={validation.valid ? "success" : "destructive"} className="px-3">
                        {validation.valid ? "Self-Validated" : (job.failure_reason || "Issues Detected")}
                    </Badge>
                    <Badge variant="outline" className="px-3 font-mono">
                        Score: {result.confidence?.toFixed(0) || 0}/100
                    </Badge>
                </div>
            </div>

            {/* Confidence Breakdown */}
            {result.confidence_components && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(result.confidence_components).map(([key, val]: [string, any]) => (
                        <Card key={key} className="bg-muted/5 border-none shadow-none ring-1 ring-muted">
                            <CardContent className="pt-4 flex flex-col items-center">
                                <span className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider mb-1">{key.replace('_', ' ')}</span>
                                <span className={`text-2xl font-black ${val > 85 ? 'text-green-600' : val > 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                                    {val}%
                                </span>
                                <div className="w-full h-1 bg-muted mt-2 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-1000 ${val > 80 ? 'bg-green-500' : val > 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                        style={{ width: `${val}%` }}
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {job.failure_message && (
                <Card className="border-orange-200 bg-orange-50/50">
                    <CardContent className="pt-4 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
                        <div>
                            <p className="font-bold text-orange-900 text-sm">Action Required</p>
                            <p className="text-sm text-orange-800 leading-relaxed">{job.failure_message}</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: Artifacts & Data */}
                <div className="lg:col-span-2 space-y-6">
                    <Card className="overflow-hidden border-muted">
                        <Tabs defaultValue="data">
                            <div className="bg-muted/30 border-b px-2">
                                <TabsList className="bg-transparent h-12">
                                    <TabsTrigger value="data" className="data-[state=active]:bg-white"><Code className="w-4 h-4 mr-2" /> Data</TabsTrigger>
                                    <TabsTrigger value="preview" className={`data-[state=active]:bg-white ${preflightResult ? "text-primary font-bold" : ""}`}><Eye className="w-4 h-4 mr-2" /> Preflight</TabsTrigger>
                                    <TabsTrigger value="visual" className="data-[state=active]:bg-white"><ImageIcon className="w-4 h-4 mr-2" /> Screenshot</TabsTrigger>
                                </TabsList>
                            </div>
                            <CardContent className="p-0">
                                <TabsContent value="data" className="m-0">
                                    <div className="p-4 bg-white/5">
                                        <JsonRenderer data={result.data || {}} title="Extracted Data" />
                                    </div>
                                </TabsContent>
                                <TabsContent value="preview" className="m-0">
                                    {preflightResult ? (
                                        <div className="p-4 space-y-4 bg-white/5">
                                            <JsonRenderer data={preflightResult.preview_data || {}} title="Preflight Test Result" />
                                        </div>
                                    ) : (
                                        <div className="p-16 text-center text-muted-foreground">
                                            <Eye className="w-8 h-8 mx-auto mb-2 opacity-20" />
                                            <p className="text-sm italic">Run a Preflight Test to verify your selector changes.</p>
                                        </div>
                                    )}
                                </TabsContent>
                                <TabsContent value="visual" className="m-0 p-4 min-h-[400px] flex items-center justify-center bg-slate-50">
                                    {(result.screenshots && result.screenshots.length > 0) ? (
                                        <div className="relative group">
                                            <img src={`${API_BASE_URL}/${result.screenshots[0]}`} alt="Scrape Artifact" className="max-w-full h-auto rounded shadow-2xl border" />
                                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors pointer-events-none" />
                                        </div>
                                    ) : (
                                        <div className="text-center">
                                            <ImageIcon className="w-10 h-10 mx-auto text-muted-foreground/30 mb-2" />
                                            <p className="text-sm text-muted-foreground">No screenshot artifact available</p>
                                        </div>
                                    )}
                                </TabsContent>
                            </CardContent>
                        </Tabs>
                    </Card>

                    {validation.errors && validation.errors.length > 0 && (
                        <Card className="border-red-200 bg-red-50/30">
                            <CardHeader className="py-4">
                                <CardTitle className="text-sm text-red-700 flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4" /> Detected Issues
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="pb-4">
                                <ul className="space-y-1 text-xs text-red-600 font-medium">
                                    {validation.errors.map((err: string, i: number) => (
                                        <li key={i} className="flex gap-2">
                                            <span className="opacity-50">•</span>
                                            {err}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Right: Controls */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Fix Selectors</CardTitle>
                            <CardDescription className="text-xs">Adjust CSS selectors using the artifacts for reference.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-5">
                            {Object.keys(selectors).map(field => {
                                const hasError = validation.errors && validation.errors.some((e: string) => e.includes(`Field '${field}'`));
                                return (
                                    <div key={field} className="space-y-2">
                                        <div className="flex justify-between items-center px-1">
                                            <Label htmlFor={field} className={`text-xs uppercase font-bold tracking-wider ${hasError ? "text-red-500" : "text-slate-600"}`}>
                                                {field}
                                            </Label>
                                            {hasError && <span className="text-[10px] text-red-500 font-bold uppercase underline">Missing Data</span>}
                                        </div>
                                        <Input
                                            id={field}
                                            value={selectors[field]}
                                            className={`h-9 text-sm transition-all ${hasError ? "border-red-300 bg-red-50/50 focus-visible:ring-red-400" : "bg-white"}`}
                                            onChange={(e) => setSelectors({ ...selectors, [field]: e.target.value })}
                                            placeholder="CSS Selector..."
                                        />
                                    </div>
                                );
                            })}

                            <div className="pt-4 border-t space-y-4">
                                <div className="flex items-start space-x-2 bg-slate-50 p-2 rounded border">
                                    <input
                                        type="checkbox"
                                        id="confirm-fix"
                                        checked={confirmed}
                                        className="mt-0.5 rounded border-slate-300 text-primary focus:ring-primary"
                                        onChange={(e) => setConfirmed(e.target.checked)}
                                    />
                                    <label htmlFor="confirm-fix" className="text-xs text-slate-600 leading-tight cursor-pointer">
                                        I have manually verified these selectors against the page artifacts.
                                    </label>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={handlePreflight}
                                        disabled={preflightLoading || rerunning}
                                        className="h-10"
                                    >
                                        {preflightLoading ? <RotateCw className="w-4 h-4 mr-2 animate-spin" /> : <Eye className="w-4 h-4 mr-2" />}
                                        Preflight
                                    </Button>
                                    <Button
                                        size="sm"
                                        onClick={handleRerun}
                                        disabled={rerunning || !confirmed}
                                        className={`h-10 ${confirmed ? 'shadow-lg shadow-primary/20' : 'opacity-50 cursor-not-allowed'}`}
                                    >
                                        {rerunning ? <RotateCw className="w-4 h-4 mr-2 animate-spin" /> : <RotateCw className="w-4 h-4 mr-2" />}
                                        Full Run
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-slate-900 border-none">
                        <CardHeader className="py-3">
                            <CardTitle className="text-xs text-slate-400 flex items-center gap-2">
                                <CheckCircle2 className="w-3 h-3 text-green-500" /> Best Practices
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pb-4 space-y-3 text-[10px] text-slate-300 leading-normal">
                            <div className="p-2 bg-white/5 rounded">
                                <p className="font-bold text-white mb-1">Selectors</p>
                                <p>Use stable IDs or data attributes instead of long paths like <code>div{">"}div{">"}p</code>.</p>
                            </div>
                            <div className="p-2 bg-white/5 rounded">
                                <p className="font-bold text-white mb-1">Preflight</p>
                                <p>Always test on a single page before a full run to avoid wasting site traffic.</p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
