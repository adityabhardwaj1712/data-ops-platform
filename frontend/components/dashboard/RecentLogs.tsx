"use client"

import { Activity, Bell, CheckCircle, XCircle, AlertTriangle } from "lucide-react"

const LOGS = [
    { id: 1, type: "success", msg: "Task #2489 completed successfully", time: "2m ago" },
    { id: 2, type: "info", msg: "Selector auto-learned: .product-price", time: "5m ago" },
    { id: 3, type: "error", msg: "Domain blocked: example.com (Circuit Open)", time: "12m ago" },
    { id: 4, type: "warn", msg: "High latency detected on proxy node 4", time: "15m ago" },
]

export function RecentLogs() {
    return (
        <div className="glass-card h-full">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold font-outfit flex items-center gap-2">
                    <Activity className="h-5 w-5 text-blue-400" />
                    Recent Activity
                </h3>
                <button className="text-xs text-primary hover:text-primary/80 transition-colors">
                    View All
                </button>
            </div>

            <div className="space-y-4">
                {LOGS.map((log) => (
                    <div key={log.id} className="flex gap-3 items-start pb-4 border-b border-white/5 last:border-0 last:pb-0">
                        <div className="mt-0.5">
                            {log.type === "success" && <CheckCircle className="h-4 w-4 text-green-400" />}
                            {log.type === "info" && <Bell className="h-4 w-4 text-blue-400" />}
                            {log.type === "error" && <XCircle className="h-4 w-4 text-red-400" />}
                            {log.type === "warn" && <AlertTriangle className="h-4 w-4 text-yellow-400" />}
                        </div>
                        <div className="flex-1">
                            <p className="text-sm font-medium leading-tight">{log.msg}</p>
                            <p className="text-[10px] text-muted-foreground mt-1">{log.time}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
