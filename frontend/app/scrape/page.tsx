"use client"

import { useState } from "react"
import { api, pollJobStatus } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"

interface ScrapeJob {
  job_id: string
  status: "pending" | "running" | "completed" | "failed"
  result?: any
  error?: string
}

export default function ScrapePage() {
  const [url, setUrl] = useState("")
  const [schema, setSchema] = useState("{}")
  const [job, setJob] = useState<ScrapeJob | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleScrape = async () => {
    try {
      setLoading(true)
      setProgress(10)

      const response = await api.post<ScrapeJob>("/api/scrape", {
        url,
        schema: JSON.parse(schema),
      })

      setJob(response)
      setProgress(30)

      await pollJobStatus(response.job_id, (status) => {
        setJob(status as ScrapeJob)
        if (status.status === "running") setProgress(60)
      })

      setProgress(100)
    } catch (err: any) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Universal Scraper</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <Textarea
          value={schema}
          onChange={(e) => setSchema(e.target.value)}
          rows={6}
        />

        <Button onClick={handleScrape} disabled={loading}>
          {loading ? "Scraping..." : "Start Scrape"}
        </Button>

        {loading && <Progress value={progress} />}

        {job && <pre>{JSON.stringify(job, null, 2)}</pre>}
      </CardContent>
    </Card>
  )
}
