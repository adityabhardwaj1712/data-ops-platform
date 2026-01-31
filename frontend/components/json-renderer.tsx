"use client"

import { useState } from "react"
import { Button } from "./ui/button"
import { ChevronDown, ChevronRight, Eye, Code } from "lucide-react"

interface JsonRendererProps {
  data: any
  title?: string
  maxChars?: number
}

export function JsonRenderer({ data, title, maxChars = 2000 }: JsonRendererProps) {
  const [expanded, setExpanded] = useState(false)
  const jsonString = JSON.stringify(data, null, 2)
  const isTooLarge = jsonString.length > maxChars
  
  const displayString = !expanded && isTooLarge 
    ? jsonString.substring(0, maxChars) + "\n\n... (Results truncated for performance. Click Expand to view all)" 
    : jsonString

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        {title && <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">{title}</h3>}
        {isTooLarge && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setExpanded(!expanded)}
            className="text-primary hover:bg-primary/10 h-8 gap-2"
          >
            {expanded ? (
              <>
                <ChevronDown className="h-4 w-4" />
                Show Less
              </>
            ) : (
              <>
                <Eye className="h-4 w-4" />
                Expand Full Results ({Math.round(jsonString.length / 1024)} KB)
              </>
            )}
          </Button>
        )}
      </div>
      <div className="p-4 rounded-xl bg-black/40 border border-white/5 overflow-auto max-h-[500px] text-xs font-mono shadow-inner relative group">
        <pre className={expanded ? "text-green-400/90" : "text-green-400/70"}>
          {displayString}
        </pre>
        {!expanded && isTooLarge && (
          <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-black/80 to-transparent pointer-events-none" />
        )}
      </div>
    </div>
  )
}
