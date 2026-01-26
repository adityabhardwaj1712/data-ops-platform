"use client"

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Play,
  Save,
  Eye,
  Code,
  FileText,
  Zap,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

interface ExtractionResult {
  success: boolean
  data: any[]
  confidence: number
  fieldsExtracted: number
  error?: string
}

export default function IntentEditorPage() {
  const [intent, setIntent] = useState('Extract DevOps job listings with company names, locations, salaries, and job descriptions')
  const [schema, setSchema] = useState(`{
  "title": "string",
  "company": "string",
  "location": "string",
  "salary": "string",
  "description": "string",
  "job_type": "string",
  "experience_level": "string"
}`)
  const [extractionMode, setExtractionMode] = useState<'heuristic' | 'ai'>('heuristic')
  const [isExtracting, setIsExtracting] = useState(false)
  const [result, setResult] = useState<ExtractionResult | null>(null)
  const [previewData, setPreviewData] = useState<any>(null)

  // Mock data for live preview
  const mockPreviewData = {
    title: "Senior DevOps Engineer",
    company: "TechCorp Solutions",
    location: "San Francisco, CA",
    salary: "$120,000 - $160,000",
    description: "We are looking for a Senior DevOps Engineer to join our growing team...",
    job_type: "Full-time",
    experience_level: "Senior"
  }

  const handleExtract = async () => {
    setIsExtracting(true)

    // Simulate API call
    setTimeout(() => {
      const mockResult: ExtractionResult = {
        success: true,
        data: [mockPreviewData],
        confidence: 0.87,
        fieldsExtracted: 7
      }
      setResult(mockResult)
      setPreviewData(mockPreviewData)
      setIsExtracting(false)
    }, 2000)
  }

  const handleSchemaChange = (value: string | undefined) => {
    if (value) {
      setSchema(value)
    }
  }

  const formatJson = (jsonString: string) => {
    try {
      return JSON.stringify(JSON.parse(jsonString), null, 2)
    } catch {
      return jsonString
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Intent Editor</h1>
          <p className="text-muted-foreground mt-2">
            Define what data to extract and how it should be structured
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={extractionMode} onValueChange={(value: 'heuristic' | 'ai') => setExtractionMode(value)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="heuristic">Heuristic Mode</SelectItem>
              <SelectItem value="ai">AI-Assisted</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleExtract} disabled={isExtracting}>
            {isExtracting ? (
              <Zap className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {isExtracting ? 'Extracting...' : 'Test Extraction'}
          </Button>
        </div>
      </div>

      {/* Split-screen Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[600px]">
        {/* Left Panel - Intent & Schema */}
        <div className="space-y-6">
          {/* Intent Input */}
          <Card className="premium-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Extraction Intent
              </CardTitle>
              <CardDescription>
                Describe what data you want to extract in natural language
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                placeholder="e.g., Extract job listings with titles, companies, and salaries..."
                className="min-h-[100px] resize-none"
              />
            </CardContent>
          </Card>

          {/* Schema Editor */}
          <Card className="premium-card flex-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center">
                <Code className="h-5 w-5 mr-2" />
                Data Schema
              </CardTitle>
              <CardDescription>
                Define the structure of your extracted data
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="h-80">
                <MonacoEditor
                  height="100%"
                  language="json"
                  theme="vs-dark"
                  value={schema}
                  onChange={handleSchemaChange}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    roundedSelection: false,
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    tabSize: 2,
                    wordWrap: 'on'
                  }}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Panel - Live Preview */}
        <div className="space-y-6">
          {/* Preview Header */}
          <Card className="premium-card">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg flex items-center">
                    <Eye className="h-5 w-5 mr-2" />
                    Live Preview
                  </CardTitle>
                  <CardDescription>
                    See how your intent extracts data from sample content
                  </CardDescription>
                </div>
                {result && (
                  <Badge variant="outline" className={
                    result.success
                      ? "bg-green-500/10 text-green-400 border-green-500/30"
                      : "bg-red-500/10 text-red-400 border-red-500/30"
                  }>
                    {result.success ? (
                      <CheckCircle className="h-3 w-3 mr-1" />
                    ) : (
                      <AlertTriangle className="h-3 w-3 mr-1" />
                    )}
                    {result.confidence.toFixed(2)} confidence
                  </Badge>
                )}
              </div>
            </CardHeader>
          </Card>

          {/* Extracted Data Preview */}
          <Card className="premium-card flex-1">
            <CardContent className="p-6">
              {previewData ? (
                <div className="space-y-4">
                  <div className="text-sm text-muted-foreground mb-4">
                    Extracted {result?.fieldsExtracted || 0} fields with {(result?.confidence || 0 * 100).toFixed(0)}% confidence
                  </div>

                  {Object.entries(previewData).map(([field, value]) => (
                    <div key={field} className="border-b border-border/50 pb-3 last:border-b-0">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium text-primary">
                          {field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </label>
                        <Badge variant="outline" className="text-xs">
                          {typeof value === 'string' ? `${value.length} chars` : typeof value}
                        </Badge>
                      </div>
                      <div className="text-sm text-foreground bg-muted/30 p-3 rounded-md font-mono">
                        {typeof value === 'string' && value.length > 100
                          ? `${value.substring(0, 100)}...`
                          : String(value)
                        }
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                  <div className="text-center">
                    <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Click "Test Extraction" to see live preview</p>
                    <p className="text-sm mt-2">Your schema will be applied to sample data</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Extraction Stats */}
          {result && (
            <Card className="premium-card">
              <CardContent className="p-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-green-400">
                      {result.fieldsExtracted}
                    </div>
                    <div className="text-xs text-muted-foreground">Fields Extracted</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-400">
                      {(result.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Confidence</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-400">
                      {result.data.length}
                    </div>
                    <div className="text-xs text-muted-foreground">Records Found</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Template Library */}
      <Card className="premium-card">
        <CardHeader>
          <CardTitle>Intent Templates</CardTitle>
          <CardDescription>
            Pre-built templates for common extraction tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              className="h-auto p-4 text-left"
              onClick={() => setIntent('Extract job listings with titles, companies, locations, salaries, and descriptions')}
            >
              <div>
                <div className="font-medium">Job Listings</div>
                <div className="text-sm text-muted-foreground mt-1">
                  Extract employment opportunities from career sites
                </div>
              </div>
            </Button>

            <Button
              variant="outline"
              className="h-auto p-4 text-left"
              onClick={() => setIntent('Extract product information including names, prices, descriptions, and specifications')}
            >
              <div>
                <div className="font-medium">Product Catalog</div>
                <div className="text-sm text-muted-foreground mt-1">
                  Extract product details from e-commerce sites
                </div>
              </div>
            </Button>

            <Button
              variant="outline"
              className="h-auto p-4 text-left"
              onClick={() => setIntent('Extract news articles with titles, authors, dates, and content summaries')}
            >
              <div>
                <div className="font-medium">News Articles</div>
                <div className="text-sm text-muted-foreground mt-1">
                  Extract news content from media websites
                </div>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}