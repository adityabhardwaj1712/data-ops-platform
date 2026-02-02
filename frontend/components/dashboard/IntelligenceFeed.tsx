"use client"

import { Card } from "@/components/ui/card"
import { Search, ShieldCheck, Cpu, AlertTriangle } from "lucide-react"

export function IntelligenceFeed() {
    const events = [
        {
            icon: ShieldCheck,
            color: "text-green-400",
            title: "HEALED:",
            desc: "Target: EBay - Selector div.price replaced.",
            time: "51m ago"
        },
        {
            icon: Cpu,
            color: "text-green-400",
            title: "OPTIMIZED:",
            desc: "Engine switched to Stealth for Linkedin.",
            time: "18m ago"
        },
        {
            icon: AlertTriangle,
            color: "text-yellow-400",
            title: "DRIFT:",
            desc: "Schema deviation detected on Target-B",
            time: "Just now"
        }
    ]

    return (
        <Card className="glass-card p-6 h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Search className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">Intelligence Feed</h3>
                </div>
            </div>

            <div className="space-y-6 relative">
                {/* Timeline line */}
                <div className="absolute left-[11px] top-2 bottom-2 w-[1px] bg-white/10" />

                {events.map((event, i) => (
                    <div key={i} className="flex gap-4 relative">
                        <div className={`mt-1 bg-background z-10`}>
                            <event.icon className={`w-6 h-6 ${event.color}`} />
                        </div>

                        <div>
                            <div className={`text-xs font-bold mb-1 ${event.color}`}>{event.title}</div>
                            <p className="text-sm text-muted-foreground leading-snug mb-1">
                                {event.desc}
                            </p>
                            <span className="text-xs text-muted-foreground/50">{event.time}</span>
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    )
}
