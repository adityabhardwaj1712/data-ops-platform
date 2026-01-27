"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Globe, Zap, Shield, Code2, Upload, Sparkles, Play, Loader2 } from 'lucide-react'
import { api, pollJobStatus } from '@/lib/api'

interface ScrapeJob {
    job_id: string
    status: string
    result?: any
    error?: string
}

export default function ScrapePage() {
    const [activeTab, setActiveTab] = useState('single')
    const [url, setUrl] = useState('')
    const [urls, setUrls] = useState('')
    const [schema, setSchema] = useState('{\n  "title": "string",\n  "description": "string"\n}')
    const [strategy, setStrategy] = useState('auto')
    const [loading, setLoading] = useState(false)
    const [job, setJob] = useState<ScrapeJob | null>(null)
    const [progress, setProgress] = useState(0)

    const handleScrape = async () => {
        setLoading(true)
        setProgress(10)

        try {
            const schemaObj = JSON.parse(schema)

            const response = await api.post('/api/scrape', {
                url,
                schema: schemaObj,
                strategy,
            })

            setJob(response)
            setProgress(30)

            // Poll for status
            await pollJobStatus(
                response.job_id,
                (status) => {
                    setJob(status)
                    if (status.status === 'running') {
                        setProgress(60)
                    }
                }
            )

            setProgress(100)
        } catch (error) {
            console.error('Scraping failed:', error)
            alert('Scraping failed: ' + (error as Error).message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Universal Scraper</h1>
                <p className="text-muted-foreground mt-2">
                    Extract data from any website with intelligent strategies
                </p>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="single">
                        <Globe className="w-4 h-4 mr-2" />
                        Single URL
                    </TabsTrigger>
                    <TabsTrigger value="bulk">
                        <Upload className="w-4 h-4 mr-2" />
                        Bulk Import
                    </TabsTrigger>
                    <TabsTrigger value="pipeline">
                        <Sparkles className="w-4 h-4 mr-2" />
                        Pipeline
                    </TabsTrigger>
                    <TabsTrigger value="template">
                        <Code2 className="w-4 h-4 mr-2" />
                        Templates
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="single" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Single URL Scraping</CardTitle>
                            <CardDescription>
                                Extract data from a single webpage with customizable schema
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="url">Target URL</Label>
                                <Input
                                    id="url"
                                    placeholder="https://example.com"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="strategy">Scraping Strategy</Label>
                                <Select value={strategy} onValueChange={setStrategy}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="auto">
                                            <div className="flex items-center">
                                                <Sparkles className="w-4 h-4 mr-2" />
                                                Auto-Detect (Recommended)
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="static">
                                            <div className="flex items-center">
                                                <Zap className="w-4 h-4 mr-2" />
                                                Static (Fast, simple pages)
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="browser">
                                            <div className="flex items-center">
                                                <Globe className="w-4 h-4 mr-2" />
                                                Browser (JavaScript-heavy sites)
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="stealth">
                                            <div className="flex items-center">
                                                <Shield className="w-4 h-4 mr-2" />
                                                Stealth (Anti-bot evasion)
                                            </div>
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="schema">Data Schema (JSON)</Label>
                                <Textarea
                                    id="schema"
                                    placeholder='{"title": "string", "price": "string"}'
                                    value={schema}
                                    onChange={(e) => setSchema(e.target.value)}
                                    className="font-mono text-sm"
                                    rows={8}
                                />
                                <p className="text-xs text-muted-foreground">
                                    Define the structure of data you want to extract
                                </p>
                            </div>

                            <Button
                                onClick={handleScrape}
                                disabled={loading || !url}
                                className="w-full"
                                size="lg"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Scraping...
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-4 h-4 mr-2" />
                                        Start Scraping
                                    </>
                                )}
                            </Button>

                            {loading && (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>Progress</span>
                                        <span>{progress}%</span>
                                    </div>
                                    <Progress value={progress} />
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {job && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center justify-between">
                                    <span>Scraping Result</span>
                                    <Badge variant={job.status === 'completed' ? 'default' : 'secondary'}>
                                        {job.status}
                                    </Badge>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {job.status === 'completed' && job.result && (
                                    <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-96 text-sm">
                                        {JSON.stringify(job.result, null, 2)}
                                    </pre>
                                )}
                                {job.status === 'failed' && (
                                    <div className="text-destructive">
                                        Error: {job.error || 'Unknown error'}
                                    </div>
                                )}
                                {job.status === 'running' && (
                                    <div className="flex items-center text-muted-foreground">
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Processing...
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="bulk">
                    <Card>
                        <CardHeader>
                            <CardTitle>Bulk URL Import</CardTitle>
                            <CardDescription>
                                Upload a CSV file or paste multiple URLs to scrape in batch
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="urls">URLs (one per line)</Label>
                                <Textarea
                                    id="urls"
                                    placeholder="https://example.com/page1&#10;https://example.com/page2&#10;https://example.com/page3"
                                    value={urls}
                                    onChange={(e) => setUrls(e.target.value)}
                                    rows={10}
                                />
                            </div>
                            <Button className="w-full" size="lg">
                                <Upload className="w-4 h-4 mr-2" />
                                Import & Scrape
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="pipeline">
                    <Card>
                        <CardHeader>
                            <CardTitle>Multi-Source Pipeline</CardTitle>
                            <CardDescription>
                                Run the full 6-layer pipeline across multiple sources
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">
                                Pipeline interface coming soon...
                            </p>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="template">
                    <Card>
                        <CardHeader>
                            <CardTitle>Pre-built Templates</CardTitle>
                            <CardDescription>
                                Use ready-made schemas for common scraping tasks
                            </CardDescription>
                        </CardContent>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <Card className="cursor-pointer hover:border-primary transition-colors">
                                    <CardHeader>
                                        <CardTitle className="text-base">Job Listings</CardTitle>
                                        <CardDescription className="text-xs">
                                            Extract job titles, companies, locations, salaries
                                        </CardDescription>
                                    </CardHeader>
                                </Card>
                                <Card className="cursor-pointer hover:border-primary transition-colors">
                                    <CardHeader>
                                        <CardTitle className="text-base">E-commerce Products</CardTitle>
                                        <CardDescription className="text-xs">
                                            Extract product names, prices, descriptions, images
                                        </CardDescription>
                                    </CardHeader>
                                </Card>
                                <Card className="cursor-pointer hover:border-primary transition-colors">
                                    <CardHeader>
                                        <CardTitle className="text-base">News Articles</CardTitle>
                                        <CardDescription className="text-xs">
                                            Extract headlines, authors, dates, content
                                        </CardDescription>
                                    </CardHeader>
                                </Card>
                                <Card className="cursor-pointer hover:border-primary transition-colors">
                                    <CardHeader>
                                        <CardTitle className="text-base">Contact Information</CardTitle>
                                        <CardDescription className="text-xs">
                                            Extract emails, phones, addresses, social links
                                        </CardDescription>
                                    </CardHeader>
                                </Card>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
