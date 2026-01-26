"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { CheckCircle, AlertCircle, Loader2, ExternalLink } from 'lucide-react'

interface ExtractionEvent {
  id: string
  timestamp: Date
  type: 'success' | 'warning' | 'error' | 'info'
  message: string
  source: string
  confidence: number
  url?: string
}

export function LiveExtractionFeed() {
  const [events, setEvents] = useState<ExtractionEvent[]>([])

  // Simulate real-time events
  useEffect(() => {
    const mockEvents: ExtractionEvent[] = [
      {
        id: '1',
        timestamp: new Date(Date.now() - 1000 * 30),
        type: 'success',
        message: 'Extracted 12 job listings from linkedin.com',
        source: 'linkedin.com',
        confidence: 0.89,
        url: 'https://linkedin.com/jobs/search'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 1000 * 60),
        type: 'warning',
        message: 'Low confidence match: "senior engineer" → 0.65',
        source: 'indeed.com',
        confidence: 0.65
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 1000 * 90),
        type: 'success',
        message: 'Found 8 DevOps positions matching intent',
        source: 'glassdoor.com',
        confidence: 0.92
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 1000 * 120),
        type: 'error',
        message: 'CAPTCHA detected on monster.com',
        source: 'monster.com',
        confidence: 0
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 1000 * 150),
        type: 'success',
        message: 'Schema validation passed for 15 records',
        source: 'dice.com',
        confidence: 0.97
      }
    ]

    setEvents(mockEvents)

    // Simulate new events every 30 seconds
    const interval = setInterval(() => {
      const newEvent: ExtractionEvent = {
        id: Date.now().toString(),
        timestamp: new Date(),
        type: Math.random() > 0.8 ? 'warning' : 'success',
        message: `Extracted ${Math.floor(Math.random() * 20) + 5} records from ${['linkedin.com', 'indeed.com', 'glassdoor.com'][Math.floor(Math.random() * 3)]}`,
        source: 'system',
        confidence: Math.random() * 0.4 + 0.6
      }

      setEvents(prev => [newEvent, ...prev.slice(0, 9)]) // Keep last 10
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-3 w-3 text-green-500" />
      case 'warning':
        return <AlertCircle className="h-3 w-3 text-yellow-500" />
      case 'error':
        return <AlertCircle className="h-3 w-3 text-red-500" />
      default:
        return <Loader2 className="h-3 w-3 text-blue-500 animate-spin" />
    }
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / (1000 * 60))

    if (minutes < 1) return 'now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ago`
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400'
    if (confidence >= 0.6) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <Card className="premium-card glow-border row-span-2">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Live Extraction Feed</CardTitle>
            <CardDescription>
              Real-time extraction events and matches
            </CardDescription>
          </div>
          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
            LIVE
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-80">
          <div className="space-y-1 p-6">
            {events.map((event) => (
              <div
                key={event.id}
                className="flex items-start space-x-3 p-3 rounded-md bg-muted/30 hover:bg-muted/50 transition-colors terminal-text"
              >
                <div className="mt-0.5">
                  {getEventIcon(event.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-foreground">
                    {event.message}
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-muted-foreground">
                      {event.source}
                    </span>
                    {event.confidence > 0 && (
                      <span className={`text-xs font-mono ${getConfidenceColor(event.confidence)}`}>
                        {event.confidence.toFixed(2)}
                      </span>
                    )}
                    {event.url && (
                      <ExternalLink className="h-3 w-3 text-muted-foreground cursor-pointer hover:text-foreground" />
                    )}
                    <span className="text-xs text-muted-foreground">
                      {formatTime(event.timestamp)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}