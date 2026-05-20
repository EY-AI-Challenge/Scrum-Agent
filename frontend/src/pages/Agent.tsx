import {
  ClipboardDocumentCheckIcon,
  SparklesIcon,
  QuestionMarkCircleIcon,
} from '@heroicons/react/24/outline'
import type { ReactNode } from 'react'
import { useDemoStore } from '../store/demoState'
import type {
  AgentRecommendationState,
  ApprovalActionState,
  ProjectId,
} from '../types/demo_state'

export default function Agent() {
  const state = useDemoStore((s) => s.state)
  if (!state) return null

  const analysis = state.agent_analysis
  const llm = state.llm_metadata

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-white">Agent Workspace</h2>
          <p className="text-sm text-gray-500 mt-1">{analysis.executive_summary}</p>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-gray-800 bg-gray-900 px-3 py-2 text-xs">
          <span className="text-gray-500">LLM</span>
          <span className="font-medium text-gray-200">{llm.provider}</span>
          <span className="text-gray-600">{llm.model}</span>
          {llm.fallback_used && <span className="text-amber-400">fallback</span>}
        </div>
      </div>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {(Object.entries(analysis.project_assessments) as [ProjectId, string][]).map(([projectId, text]) => (
          <div key={projectId} className="rounded-xl border border-gray-800 bg-gray-900 p-4 space-y-2">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold text-white">{projectName(projectId, state.projects)}</h3>
              <span className="font-mono text-xs text-gray-500">{projectId}</span>
            </div>
            <p className="text-xs leading-relaxed text-gray-400">{text}</p>
          </div>
        ))}
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <Panel
          icon={<SparklesIcon className="h-5 w-5" />}
          title="Recommendations"
          count={state.recommendations.length}
        >
          <div className="space-y-3">
            {state.recommendations.map((recommendation) => (
              <RecommendationCard
                key={recommendation.recommendation_id}
                recommendation={recommendation}
              />
            ))}
          </div>
        </Panel>

        <Panel
          icon={<ClipboardDocumentCheckIcon className="h-5 w-5" />}
          title="Approval Queue"
          count={state.approval_queue.length}
        >
          <div className="space-y-3">
            {state.approval_queue.map((action) => (
              <ApprovalCard key={action.action_id} action={action} />
            ))}
          </div>
        </Panel>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <AnalysisList title="Priority" items={analysis.priority_analysis} />
        <AnalysisList title="Allocation" items={analysis.allocation_analysis} />
        <AnalysisList title="Risk" items={analysis.risk_analysis} />
      </section>

      {analysis.product_owner_questions.length > 0 && (
        <section className="rounded-xl border border-gray-800 bg-gray-900 p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
            <QuestionMarkCircleIcon className="h-5 w-5 text-indigo-400" />
            Product Owner Questions
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {analysis.product_owner_questions.map((question) => (
              <p key={question} className="rounded-lg bg-gray-800/70 p-3 text-xs leading-relaxed text-gray-300">
                {question}
              </p>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

function Panel({
  icon,
  title,
  count,
  children,
}: {
  icon: ReactNode
  title: string
  count: number
  children: ReactNode
}) {
  return (
    <section className="rounded-xl border border-gray-800 bg-gray-900 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <span className="text-indigo-400">{icon}</span>
          {title}
        </div>
        <span className="rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-400">{count}</span>
      </div>
      {children}
    </section>
  )
}

function RecommendationCard({ recommendation }: { recommendation: AgentRecommendationState }) {
  return (
    <article className="rounded-lg bg-gray-800/70 p-3 space-y-2">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-white">{recommendation.title}</p>
          <p className="text-xs text-gray-500">
            {recommendation.recommendation_id}
            {recommendation.project_id ? ` - ${recommendation.project_id}` : ' - portfolio'}
          </p>
        </div>
        <span className="text-xs font-medium text-indigo-300">
          {Math.round(recommendation.confidence * 100)}%
        </span>
      </div>
      <p className="text-xs leading-relaxed text-gray-400">{recommendation.rationale}</p>
      <p className="text-xs leading-relaxed text-gray-300">{recommendation.expected_impact}</p>
      <EntityList label="Items" values={recommendation.affected_item_ids} />
      <EntityList label="Members" values={recommendation.affected_member_ids} />
    </article>
  )
}

function ApprovalCard({ action }: { action: ApprovalActionState }) {
  return (
    <article className="rounded-lg bg-gray-800/70 p-3 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-white">{formatAction(action.action_type)}</p>
          <p className="text-xs text-gray-500">
            {action.action_id}
            {action.project_id ? ` - ${action.project_id}` : ' - portfolio'}
          </p>
        </div>
        <span className="rounded bg-amber-500/20 px-2 py-0.5 text-xs font-medium text-amber-300">
          {action.status}
        </span>
      </div>
      <p className="text-xs leading-relaxed text-gray-400">{action.rationale}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <KeyValueBlock title="Before" values={action.before} />
        <KeyValueBlock title="After" values={action.after} />
      </div>
      <EntityList label="Items" values={action.affected_item_ids} />
      <EntityList label="Members" values={action.affected_member_ids} />
    </article>
  )
}

function AnalysisList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-xl border border-gray-800 bg-gray-900 p-4">
      <h3 className="mb-3 text-sm font-semibold text-white">{title}</h3>
      <div className="space-y-2">
        {items.map((item) => (
          <p key={item} className="text-xs leading-relaxed text-gray-400">
            {item}
          </p>
        ))}
      </div>
    </section>
  )
}

function EntityList({ label, values }: { label: string; values: string[] }) {
  if (values.length === 0) return null
  return (
    <div className="flex flex-wrap items-center gap-1.5 text-xs">
      <span className="text-gray-500">{label}</span>
      {values.map((value) => (
        <span key={value} className="rounded bg-gray-900 px-1.5 py-0.5 font-mono text-gray-400">
          {value}
        </span>
      ))}
    </div>
  )
}

function KeyValueBlock({
  title,
  values,
}: {
  title: string
  values: Record<string, string | number | boolean | null>
}) {
  return (
    <div className="rounded bg-gray-900 p-2">
      <p className="mb-1 text-xs font-medium text-gray-500">{title}</p>
      {Object.keys(values).length === 0 ? (
        <p className="text-xs text-gray-600">none</p>
      ) : (
        <div className="space-y-1">
          {Object.entries(values).map(([key, value]) => (
            <p key={key} className="text-xs text-gray-400">
              <span className="text-gray-500">{key}:</span> {String(value)}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}

function projectName(projectId: ProjectId, projects: { project_id: ProjectId; name: string }[]) {
  return projects.find((project) => project.project_id === projectId)?.name ?? projectId
}

function formatAction(actionType: string) {
  return actionType
    .split('_')
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(' ')
}
