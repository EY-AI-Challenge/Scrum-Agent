import { useDemoStore } from '../store/demoState'
import SprintCard from '../components/SprintCard'
import DomainBadge from '../components/DomainBadge'

export default function Sprints() {
  const state = useDemoStore((s) => s.state)
  if (!state) return null

  return (
    <div className="p-6 space-y-8">
      <h2 className="text-2xl font-bold text-white">Sprint Plans</h2>

      {state.projects.map((project) => {
        const sprints = state.sprint_plans
          .filter((s) => s.project_id === project.project_id)
          .sort((a, b) => a.sprint_number - b.sprint_number)

        return (
          <section key={project.project_id} className="space-y-3">
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-semibold text-white">{project.name}</h3>
              <DomainBadge domain={project.domain} />
              <span className="text-xs text-gray-500">MVP W{project.mvp_week} · Final W{project.final_week}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {sprints.map((sprint) => (
                <SprintCard key={sprint.sprint_id} sprint={sprint} />
              ))}
            </div>
          </section>
        )
      })}
    </div>
  )
}
