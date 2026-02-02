"use client"

import { Card } from "@/components/ui/card"
import { Shield, Zap, Cpu, Activity } from "lucide-react"

export function StatsGrid() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
            {/* Extraction Success */}
            <Card className="glass-card p-6 relative overflow-hidden group">
                <div className="relative z-10">
                    <div className="text-sm text-muted-foreground mb-4">Extraction Success</div>
                    <div className="flex items-center gap-3 mb-2">
                        <Zap className="w-6 h-6 text-green-400" />
                        <span className="text-3xl font-bold font-outfit text-green-400">99.3%</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full w-[99.3%] bg-green-400 rounded-full" />
                    </div>
                </div>
            </Card>

            {/* Stealth Score */}
            <Card className="glass-card p-6 relative overflow-hidden group">
                <div className="relative z-10">
                    <div className="text-sm text-muted-foreground mb-4">Stealth Score</div>
                    <div className="flex items-center gap-3 mb-2">
                        <Shield className="w-6 h-6 text-cyan-400" />
                        <span className="text-3xl font-bold font-outfit text-cyan-400">Ultra</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full w-[90%] bg-cyan-400 rounded-full" />
                    </div>
                </div>
            </Card>

            {/* Active Proxies */}
            <Card className="glass-card p-6 relative overflow-hidden group">
                <div className="relative z-10">
                    <div className="text-sm text-muted-foreground mb-4">Active Proxies</div>
                    <div className="flex items-center gap-3 mb-2">
                        <Cpu className="w-6 h-6 text-white" />
                        <span className="text-3xl font-bold font-outfit text-white">1,265</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full w-[70%] bg-white/20 rounded-full" />
                    </div>
                </div>
            </Card>

            {/* Avg Latency */}
            <Card className="glass-card p-6 relative overflow-hidden group">
                <div className="relative z-10">
                    <div className="text-sm text-muted-foreground mb-4">Avg Latency</div>
                    <div className="flex items-center gap-3 mb-2">
                        <Activity className="w-6 h-6 text-yellow-400" />
                        <span className="text-3xl font-bold font-outfit text-yellow-400">1.3s</span>
                    </div>
                    <div className="h-12 w-full mt-2">
                        <svg className="w-full h-full" viewBox="0 0 100 20" preserveAspectRatio="none">
                            <path d="M0,20 L10,18 L20,15 L30,17 L40,10 L50,12 L60,8 L70,14 L80,10 L90,5 L100,5" fill="none" stroke="currentColor" className="text-yellow-400" strokeWidth="2" />
                        </svg>
                    </div>
                </div>
            </Card>
        </div>
    )
}
