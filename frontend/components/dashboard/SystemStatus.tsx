"use client"

import { Card } from "@/components/ui/card"

export function SystemStatus() {
    return (
        <Card className="glass-card w-full p-8 relative overflow-hidden group">
            {/* Background glow effect */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

            <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="space-y-4">
                    <div className="flex items-center gap-4">
                        <h2 className="text-lg font-medium text-muted-foreground">System Status</h2>
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-sm font-medium text-green-500">Optimal</span>
                        </div>
                        <div className="hidden md:flex items-center gap-4 text-sm text-muted-foreground ml-4">
                            <span>[Static: 15]</span>
                            <span>[Playwright: 7]</span>
                            <span>[Stealth: 10]</span>
                        </div>
                    </div>

                    <div>
                        <div className="text-sm text-muted-foreground mb-1">Active Engines:</div>
                        <div className="text-4xl md:text-5xl font-bold font-outfit text-white tracking-tight">
                            99.2% <span className="text-2xl md:text-3xl font-normal text-muted-foreground">Success Rate</span>
                        </div>
                    </div>
                </div>

                <div className="w-full md:w-1/3 h-24">
                    <svg className="w-full h-full" viewBox="0 0 300 60" preserveAspectRatio="none">
                        <path
                            d="M0,30 L20,30 L30,10 L40,50 L50,30 L70,30 L80,20 L90,40 L110,30 L130,30 L140,15 L150,45 L160,30 L180,30 L190,25 L200,35 L220,30 L250,30 L260,20 L270,40 L300,30"
                            fill="none"
                            stroke="hsl(var(--primary))"
                            strokeWidth="2"
                            className="drop-shadow-[0_0_8px_rgba(124,58,237,0.5)]"
                        />
                    </svg>
                </div>
            </div>
        </Card>
    )
}
