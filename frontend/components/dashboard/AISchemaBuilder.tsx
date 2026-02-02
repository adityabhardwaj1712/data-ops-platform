"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Search, Brain } from "lucide-react"

export function AISchemaBuilder() {
    return (
        <Card className="glass-card p-6 h-full flex flex-col relative overflow-hidden">

            <div className="flex items-center gap-3 mb-6">
                <Brain className="w-5 h-5 text-primary" />
                <h3 className="font-semibold text-lg">AI Schema Builder</h3>
            </div>

            <div className="flex-1 space-y-4">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <input
                        type="text"
                        className="w-full bg-black/20 border border-white/5 rounded-xl py-3 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-colors"
                        placeholder='questich-icon": "s-result-item"'
                    />
                </div>

                <div className="p-4 rounded-xl bg-white/5 border border-white/5 h-32 text-muted-foreground text-sm leading-relaxed">
                    e.g. "Extract all product names, and stock counts from Etsy wedding listings..."
                </div>
            </div>

            <div className="flex justify-end mt-6">
                <Button className="bg-cyan-400 hover:bg-cyan-500 text-black font-semibold rounded-lg px-6">
                    Generate Schema
                </Button>
            </div>
        </Card>
    )
}
