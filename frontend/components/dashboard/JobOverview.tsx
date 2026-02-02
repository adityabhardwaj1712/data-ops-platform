"use client"

import { List, CheckCircle, Database, AlertOctagon } from "lucide-react"

export function JobOverview() {
    return (
        <div className="glass-card mb-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold font-outfit">Job Overview</h3>
                <div className="flex gap-2 text-xs">
                    <span className="px-2 py-1 rounded bg-green-500/10 text-green-400 border border-green-500/20">Active</span>
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatBox label="Total Jobs" value="842" icon={List} color="text-white" />
                <StatBox label="Completed" value="810" icon={CheckCircle} color="text-green-400" />
                <StatBox label="Data Points" value="1.2M" icon={Database} color="text-blue-400" />
                <StatBox label="Failed" value="32" icon={AlertOctagon} color="text-red-400" />
            </div>
        </div>
    )
}

function StatBox({ label, value, icon: Icon, color }: any) {
    return (
        <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors group">
            <div className="flex items-center justify-between mb-2">
                <Icon className={`h-4 w-4 ${color} opacity-70 group-hover:opacity-100 transition-opacity`} />
            </div>
            <p className="text-2xl font-bold font-outfit tracking-tight">{value}</p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
        </div>
    )
}
