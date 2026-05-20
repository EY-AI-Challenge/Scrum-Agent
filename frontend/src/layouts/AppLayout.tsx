import { NavLink, Outlet } from 'react-router-dom'
import {
  HomeIcon,
  ListBulletIcon,
  CalendarDaysIcon,
  UsersIcon,
  ShieldExclamationIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline'
import { useDemoStore } from '../store/demoState'

const NAV = [
  { to: '/dashboard', label: 'Dashboard',  Icon: HomeIcon },
  { to: '/backlog',   label: 'Backlog',    Icon: ListBulletIcon },
  { to: '/sprints',   label: 'Sprints',    Icon: CalendarDaysIcon },
  { to: '/team',      label: 'Team',       Icon: UsersIcon },
  { to: '/risks',     label: 'Risks',      Icon: ShieldExclamationIcon },
  { to: '/agent',     label: 'Agent',      Icon: SparklesIcon },
  { to: '/chat',      label: 'Agent Chat', Icon: ChatBubbleLeftRightIcon },
]

export default function AppLayout() {
  const { state, loading, error } = useDemoStore()
  const llm = state?.llm_metadata

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="px-5 py-5 border-b border-gray-800">
          <span className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Scrum</span>
          <h1 className="text-xl font-bold text-white leading-tight">Agent</h1>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-3 border-t border-gray-800 text-xs text-gray-500">
          <div>Engine: {state?.metadata.engine ?? 'loading'}</div>
          <div>LLM: {llm ? `${llm.provider}${llm.fallback_used ? ' fallback' : ''}` : 'loading'}</div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center h-full text-gray-400">
            Loading portfolio data…
          </div>
        )}
        {error && (
          <div className="m-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}
        {!loading && !error && <Outlet />}
      </main>
    </div>
  )
}
