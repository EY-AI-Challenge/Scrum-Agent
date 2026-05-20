import { Fragment, useState, useMemo, type ReactNode } from 'react'
import { useDemoStore } from '../store/demoState'
import RiskBadge from '../components/RiskBadge'
import DomainBadge from '../components/DomainBadge'
import type { ProjectId, Priority, ItemStatus } from '../types/demo_state'

const STATUS_COLORS: Record<ItemStatus, string> = {
  todo:        'text-gray-400',
  in_progress: 'text-yellow-400',
  done:        'text-green-400',
}

export default function Backlog() {
  const state = useDemoStore((s) => s.state)
  const [projectFilter, setProjectFilter] = useState<ProjectId | ''>('')
  const [priorityFilter, setPriorityFilter] = useState<Priority | ''>('')
  const [statusFilter, setStatusFilter] = useState<ItemStatus | ''>('')
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  const items = useMemo(() => {
    if (!state) return []
    return state.backlog_items.filter((item) => {
      if (projectFilter && item.project_id !== projectFilter) return false
      if (priorityFilter && item.priority !== priorityFilter) return false
      if (statusFilter && item.status !== statusFilter) return false
      if (search && !item.title.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [state, projectFilter, priorityFilter, statusFilter, search])

  if (!state) return null

  return (
    <div className="p-6 space-y-5">
      <h2 className="text-2xl font-bold text-white">Backlog</h2>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-800 text-sm text-gray-200 placeholder-gray-500 rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-indigo-500 w-48"
        />
        <Select value={projectFilter} onChange={(v) => setProjectFilter(v as ProjectId | '')}>
          <option value="">All projects</option>
          {state.projects.map((p) => <option key={p.project_id} value={p.project_id}>{p.project_id} – {p.name}</option>)}
        </Select>
        <Select value={priorityFilter} onChange={(v) => setPriorityFilter(v as Priority | '')}>
          <option value="">All priorities</option>
          {(['critical','high','medium','low'] as Priority[]).map((p) => <option key={p} value={p}>{p}</option>)}
        </Select>
        <Select value={statusFilter} onChange={(v) => setStatusFilter(v as ItemStatus | '')}>
          <option value="">All statuses</option>
          {(['todo','in_progress','done'] as ItemStatus[]).map((s) => <option key={s} value={s}>{s}</option>)}
        </Select>
        <span className="ml-auto text-xs text-gray-500 self-center">{items.length} items</span>
      </div>

      {/* Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wider">
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Project</th>
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Sprint</th>
              <th className="px-4 py-3">Points</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {items.map((item) => {
              const project = state.projects.find((p) => p.project_id === item.project_id)
              const isExpanded = expanded === item.item_id
              const allocation = state.allocations.find((a) => a.item_id === item.item_id)
              return (
                <Fragment key={item.item_id}>
                  <tr
                    onClick={() => setExpanded(isExpanded ? null : item.item_id)}
                    className="hover:bg-gray-800/50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{item.item_id}</td>
                    <td className="px-4 py-3 text-gray-200 max-w-xs">
                      <div className="truncate">{item.title}</div>
                      <div className="text-xs text-gray-500">{item.epic}</div>
                    </td>
                    <td className="px-4 py-3">
                      {project && <DomainBadge domain={project.domain} />}
                    </td>
                    <td className="px-4 py-3"><RiskBadge level={item.priority} /></td>
                    <td className={`px-4 py-3 text-xs font-medium ${STATUS_COLORS[item.status]}`}>{item.status}</td>
                    <td className="px-4 py-3 text-xs text-gray-400">{item.sprint_id}</td>
                    <td className="px-4 py-3 text-xs text-gray-400">{item.story_points}</td>
                  </tr>
                  {isExpanded && (
                    <tr key={`${item.item_id}-detail`} className="bg-gray-800/30">
                      <td colSpan={7} className="px-4 py-4 space-y-3">
                        <p className="text-sm text-gray-300">{item.description}</p>
                        {allocation && (
                          <div className="bg-gray-900 rounded-lg p-3 text-xs space-y-1">
                            <p className="text-indigo-400 font-medium">Assigned to {allocation.member_name}</p>
                            <p className="text-gray-400">{allocation.rationale}</p>
                            <div className="flex gap-3 text-gray-500">
                              <span>Score: {allocation.match_score.toFixed(1)}</span>
                              <span>Skills: {allocation.matched_skills.join(', ') || '—'}</span>
                              {allocation.over_capacity && (
                                <span className="text-red-400 font-medium">Over capacity</span>
                              )}
                            </div>
                          </div>
                        )}
                        {item.dependencies.length > 0 && (
                          <p className="text-xs text-gray-500">
                            Depends on: {item.dependencies.join(', ')}
                          </p>
                        )}
                      </td>
                    </tr>
                  )}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Select({ value, onChange, children }: {
  value: string
  onChange: (v: string) => void
  children: ReactNode
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-800 text-sm text-gray-200 rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-indigo-500"
    >
      {children}
    </select>
  )
}
