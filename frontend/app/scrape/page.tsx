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
      const response = await api.post('/api/scrape', {
        url,
        schema: JSON.parse(schema),
        strategy,
      })

      setJob(response)
      setProgress(30)

      await pollJobStatus(response.job_id, (status) => {
        setJob(status)
        if (status.status === 'running') setProgress(60)
      })

      setProgress(100)
    } catch (error) {
      alert('Scraping failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Universal Scraper</h1>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4">
          <TabsTrigger value="single"><Globe className="w-4 h-4 mr-2" />Single</TabsTrigger>
          <TabsTrigger value="bulk"><Upload className="w-4 h-4 mr-2" />Bulk</TabsTrigger>
          <TabsTrigger value="pipeline"><Sparkles className="w-4 h-4 mr-2" />Pipeline</TabsTrigger>
          <TabsTrigger value="template"><Code2 className="w-4 h-4 mr-2" />Templates</TabsTrigger>
        </TabsList>

        {/* SINGLE */}
        <TabsContent value="single">
          <Card>
            <CardHeader>
              <CardTitle>Single URL Scraping</CardTitle>
              <CardDescription>Extract structured data from a page</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input placeholder="https://example.com" value={url} onChange={e => setUrl(e.target.value)} />
              <Textarea value={schema} onChange={e => setSchema(e.target.value)} rows={6} />
              <Button onClick={handleScrape} disabled={loading}>
                {loading ? <Loader2 className="animate-spin" /> : <Play />}
                Start Scraping
              </Button>
              {loading && <Progress value={progress} />}
            </CardContent>
          </Card>
        </TabsContent>

        {/* BULK */}
        <TabsContent value="bulk">
          <Card>
            <CardHeader>
              <CardTitle>Bulk Import</CardTitle>
              <CardDescription>Scrape multiple URLs</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea value={urls} onChange={e => setUrls(e.target.value)} rows={8} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* PIPELINE */}
        <TabsContent value="pipeline">
          <Card>
            <CardHeader>
              <CardTitle>Pipeline</CardTitle>
              <CardDescription>Coming soon</CardDescription>
            </CardHeader>
          </Card>
        </TabsContent>

        {/* ✅ FIXED TEMPLATE TAB */}
        <TabsContent value="template">
          <Card>
            <CardHeader>
              <CardTitle>Pre-built Templates</CardTitle>
              <CardDescription>
                Use ready-made schemas for common scraping tasks
              </CardDescription>
            </CardHeader>

            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {[
                  ['Job Listings', 'Titles, companies, locations'],
                  ['E-commerce', 'Names, prices, images'],
                  ['News', 'Headlines, authors'],
                  ['Contacts', 'Emails, phones']
                ].map(([title, desc]) => (
                  <Card key={title} className="hover:border-primary cursor-pointer">
                    <CardHeader>
                      <CardTitle className="text-base">{title}</CardTitle>
                      <CardDescription className="text-xs">{desc}</CardDescription>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

