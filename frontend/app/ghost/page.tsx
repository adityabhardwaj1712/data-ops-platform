"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Shield,
  Globe,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MapPin,
  Activity,
  Zap,
  Eye,
  EyeOff
} from 'lucide-react'

interface ProxyLocation {
  id: string
  country: string
  city: string
  lat: number
  lng: number
  status: 'active' | 'warning' | 'banned'
  successRate: number
  responseTime: number
  requests: number
}

interface StealthMetrics {
  overallStealth: number
  banRate: number
  successRate: number
  averageResponseTime: number
  activeProxies: number
  totalRequests: number
}

export default function GhostMonitorPage() {
  const [metrics, setMetrics] = useState<StealthMetrics>({
    overallStealth: 0.87,
    banRate: 0.03,
    successRate: 0.94,
    averageResponseTime: 1250,
    activeProxies: 45,
    totalRequests: 15420
  })

  const [proxies] = useState<ProxyLocation[]>([
    { id: '1', country: 'US', city: 'New York', lat: 40.7128, lng: -74.0060, status: 'active', successRate: 0.96, responseTime: 1100, requests: 2340 },
    { id: '2', country: 'DE', city: 'Frankfurt', lat: 50.1109, lng: 8.6821, status: 'active', successRate: 0.92, responseTime: 1400, requests: 1890 },
    { id: '3', country: 'JP', city: 'Tokyo', lat: 35.6762, lng: 139.6503, status: 'warning', successRate: 0.78, responseTime: 2800, requests: 1560 },
    { id: '4', country: 'GB', city: 'London', lat: 51.5074, lng: -0.1278, status: 'active', successRate: 0.94, responseTime: 1200, requests: 2130 },
    { id: '5', country: 'CA', city: 'Toronto', lat: 43.6532, lng: -79.3832, status: 'active', successRate: 0.89, responseTime: 1600, requests: 1780 },
    { id: '6', country: 'AU', city: 'Sydney', lat: -33.8688, lng: 151.2093, status: 'banned', successRate: 0.45, responseTime: 0, requests: 890 },
    { id: '7', country: 'FR', city: 'Paris', lat: 48.8566, lng: 2.3522, status: 'active', successRate: 0.91, responseTime: 1300, requests: 2010 },
    { id: '8', country: 'IN', city: 'Mumbai', lat: 19.0760, lng: 72.8777, status: 'warning', successRate: 0.82, responseTime: 2200, requests: 1340 }
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 10),
        successRate: Math.max(0.85, Math.min(0.98, prev.successRate + (Math.random() - 0.5) * 0.02))
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getProxyStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-500'
      case 'warning':
        return 'text-yellow-500'
      case 'banned':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getProxyStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-3 w-3" />
      case 'warning':
        return <AlertTriangle className="h-3 w-3" />
      case 'banned':
        return <XCircle className="h-3 w-3" />
      default:
        return <Activity className="h-3 w-3" />
    }
  }

  const getStealthColor = (stealth: number) => {
    if (stealth >= 0.9) return '#10b981'
    if (stealth >= 0.8) return '#f59e0b'
    if (stealth >= 0.7) return '#f97316'
    return '#ef4444'
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ghost Monitor</h1>
          <p className="text-muted-foreground mt-2">
            Stealth operations dashboard - monitor your invisible scraping infrastructure
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
            <Eye className="h-3 w-3 mr-1" />
            Stealth Active
          </Badge>
          <Button variant="outline">
            <Shield className="h-4 w-4 mr-2" />
            Stealth Settings
          </Button>
        </div>
      </div>

      {/* Stealth Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="premium-card glow-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overall Stealth</p>
                <p className="text-2xl font-bold">{(metrics.overallStealth * 100).toFixed(0)}%</p>
              </div>
              <div className="h-12 w-12 rounded-full flex items-center justify-center bg-primary/10">
                <Eye className="h-6 w-6 text-primary" />
              </div>
            </div>
            <Progress value={metrics.overallStealth * 100} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">{(metrics.successRate * 100).toFixed(1)}%</p>
              </div>
              <div className="h-12 w-12 rounded-full flex items-center justify-center bg-green-500/10">
                <CheckCircle className="h-6 w-6 text-green-500" />
              </div>
            </div>
            <Progress value={metrics.successRate * 100} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ban Rate</p>
                <p className="text-2xl font-bold">{(metrics.banRate * 100).toFixed(1)}%</p>
              </div>
              <div className="h-12 w-12 rounded-full flex items-center justify-center bg-red-500/10">
                <XCircle className="h-6 w-6 text-red-500" />
              </div>
            </div>
            <Progress value={metrics.banRate * 100} className="mt-3" />
          </CardContent>
        </Card>

        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Proxies</p>
                <p className="text-2xl font-bold">{metrics.activeProxies}</p>
              </div>
              <div className="h-12 w-12 rounded-full flex items-center justify-center bg-blue-500/10">
                <Globe className="h-6 w-6 text-blue-500" />
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              {metrics.totalRequests.toLocaleString()} total requests
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Proxy Map Visualization */}
      <Card className="premium-card glow-border">
        <CardHeader>
          <CardTitle>Proxy Distribution Map</CardTitle>
          <CardDescription>
            Global proxy network status and performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative h-96 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg overflow-hidden">
            {/* Simplified world map background */}
            <div className="absolute inset-0 opacity-20">
              <svg viewBox="0 0 1000 500" className="w-full h-full">
                <path d="M200,150 Q300,100 400,150 T600,150 Q700,200 800,150" stroke="currentColor" fill="none" strokeWidth="2"/>
                <path d="M150,200 Q250,180 350,200 T550,200 Q650,220 750,200" stroke="currentColor" fill="none" strokeWidth="2"/>
                <path d="M100,250 Q200,230 300,250 T500,250 Q600,270 700,250" stroke="currentColor" fill="none" strokeWidth="2"/>
              </svg>
            </div>

            {/* Proxy locations */}
            {proxies.map((proxy) => (
              <div
                key={proxy.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2"
                style={{
                  left: `${((proxy.lng + 180) / 360) * 100}%`,
                  top: `${((90 - proxy.lat) / 180) * 100}%`
                }}
              >
                <div className={`relative group cursor-pointer`}>
                  <div className={`w-3 h-3 rounded-full border-2 border-white shadow-lg ${getProxyStatusColor(proxy.status)}`} />
                  <div className={`absolute -top-1 -right-1 w-2 h-2 rounded-full bg-white border border-gray-400 ${getProxyStatusColor(proxy.status)}`} />

                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-black/80 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                    <div className="font-medium">{proxy.city}, {proxy.country}</div>
                    <div className="text-gray-300">
                      {(proxy.successRate * 100).toFixed(0)}% success • {proxy.responseTime}ms
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-sm rounded-lg p-3">
              <div className="text-xs text-white space-y-1">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span>Active</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                  <span>Warning</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-red-500"></div>
                  <span>Banned</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Proxy Details Table */}
      <Card className="premium-card">
        <CardHeader>
          <CardTitle>Proxy Performance Details</CardTitle>
          <CardDescription>
            Real-time statistics for each proxy location
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {proxies.map((proxy) => (
              <div key={proxy.id} className="flex items-center justify-between p-4 rounded-md bg-muted/30">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {getProxyStatusIcon(proxy.status)}
                    <div>
                      <div className="font-medium">{proxy.city}, {proxy.country}</div>
                      <div className="text-sm text-muted-foreground">
                        {proxy.requests.toLocaleString()} requests
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <div className="text-sm font-medium">{(proxy.successRate * 100).toFixed(0)}%</div>
                    <div className="text-xs text-muted-foreground">Success Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-medium">
                      {proxy.responseTime > 0 ? `${proxy.responseTime}ms` : 'N/A'}
                    </div>
                    <div className="text-xs text-muted-foreground">Response Time</div>
                  </div>
                  <div className="w-20">
                    <Progress value={proxy.successRate * 100} className="h-2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}