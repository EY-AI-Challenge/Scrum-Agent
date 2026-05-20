import { useDemoStore } from '../store/demoState'
import ProjectCard from '../components/ProjectCard'
import RiskBadge from '../components/RiskBadge'
import CapacityChart from '../components/charts/CapacityChart'

export default function Dashboard() {
  const state = useDemoStore((s) => s.state)
  if (!state) return null

  const criticalRisks = state.risks.filter((r) => r.severity === 'critical' || r.severity === 'high')
  const topRecommendation = state.recommendations[0]

  return (
    <div className="p-6 space-y-8">
      <h2 className="text-2xl font-bold text-white">Portfolio Overview</h2>

      <section className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <h3 className="text-sm font-semibold text-indigo-400">Agent Analysis</h3>
            <p className="text-sm text-gray-300 mt-1 leading-relaxed">
              {state.agent_analysis.executive_summary}
            </p>
          </div>
          <div className="text-right text-xs text-gray-500">
            <div>{state.llm_metadata.provider}</div>
            <div>{state.llm_metadata.model}</div>
            {state.llm_metadata.fallback_used && <div className="text-amber-400">fallback active</div>}
          </div>
        </div>
        {topRecommendation && (
          <div className="mt-4 rounded-lg bg-gray-800/70 p-3 text-xs">
            <span className="text-gray-500">{topRecommendation.recommendation_id}</span>
            <span className="mx-2 text-gray-600">/</span>
            <span className="text-gray-200">{topRecommendation.title}</span>
            <p className="mt-1 text-gray-400">{topRecommendation.expected_impact}</p>
          </div>
        )}
      </section>

      {/* Project cards */}
      <section>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Projects</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {state.projects.map((project) => (
            <ProjectCard
              key={project.project_id}
              project={project}
              backlogItems={state.backlog_items.filter((i) => i.project_id === project.project_id)}
              allocations={state.allocations.filter((a) => a.project_id === project.project_id)}
            />
          ))}
        </div>
      </section>

      {/* Capacity chart */}
      <section>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Sprint Capacity vs Planned
        </h3>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <CapacityChart sprints={state.sprint_plans} />
        </div>
      </section>

      {/* Insights */}
      <section>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Strategic Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {state.insights.map((ins, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-2">
              <h4 className="text-sm font-semibold text-indigo-400">{ins.title}</h4>
              <p className="text-xs text-gray-400 leading-relaxed">{ins.description}</p>
              <p className="text-xs text-gray-500 italic">Impact: {ins.impact}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Critical risks */}
      {criticalRisks.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Active Risks
          </h3>
          <div className="space-y-3">
            {criticalRisks.map((risk) => (
              <div key={risk.risk_id} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-white">{risk.title}</p>
                    <p className="text-xs text-gray-400 mt-1 leading-relaxed">{risk.description}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <RiskBadge level={risk.severity} />
                    {risk.project_id && (
                      <span className="text-xs text-gray-500">{risk.project_id}</span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  <span className="text-gray-400">Mitigation:</span> {risk.mitigation}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
