import type { Domain } from '../types/demo_state'

const COLORS: Record<Domain, string> = {
  fintech:    'bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/40',
  retail:     'bg-amber-500/20 text-amber-400 ring-1 ring-amber-500/40',
  healthcare: 'bg-teal-500/20 text-teal-400 ring-1 ring-teal-500/40',
}

export default function DomainBadge({ domain }: { domain: Domain }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${COLORS[domain]}`}>
      {domain}
    </span>
  )
}
