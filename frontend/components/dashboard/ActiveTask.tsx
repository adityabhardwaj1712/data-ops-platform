"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Loader2, Shield, Globe, Clock } from "lucide-react"

export function ActiveTaskMonitor() {
    return (
        <div className="glass-card mb-6 group relative overflow-hidden">
            <div className="absolute top-0 right-0 p-32 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
                <Loader2 className="h-64 w-64 text-primary animate-spin-slow" />
            </div>

            <div className="flex items-start justify-between mb-6 relative z-10">
                <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center ring-2 ring-primary/20">
                        <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold font-outfit text-white">Task #2489</h3>
                        <p className="text-muted-foreground text-sm flex items-center gap-2">
                            <Globe className="h-3 w-3" />
                            linkedin.com/jobs/search
                        </p>
                    </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                    <Badge variant="outline" className="bg-primary/10 border-primary/20 text-primary animate-pulse">
                        Processing
                    </Badge>
                    <span className="text-xs text-muted-foreground font-mono">ID: 8f92a...1b9</span>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-8 mb-6 relative z-10">
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Selectors Found</span>
                        <span className="text-white font-bold">12/14</span>
                    </div>
                    <Progress value={85} className="h-1.5" />
                </div>
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Data Learner</span>
                        <span className="text-white font-bold">Active</span>
                    </div>
                    <Progress value={100} className="h-1.5 animate-pulse" />
                </div>
            </div>

            <div className="flex items-center gap-4 text-xs text-muted-foreground bg-black/20 p-3 rounded-lg border border-white/5 relative z-10">
                <Shield className="h-4 w-4 text-green-400" />
                <span>Mode: <span className="text-white font-bold">Stealth Browser v2</span></span>
                <div className="h-3 w-[1px] bg-white/10" />
                <Clock className="h-4 w-4 text-blue-400" />
                <span>Est. Time: <span className="text-white font-bold">45s</span></span>
            </div>
        </div>
    )
}
