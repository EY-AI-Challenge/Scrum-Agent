// Mirror of scrum_agent/core/schema.py — keep in sync with the motor contract.

export type ProjectId = 'P1' | 'P2' | 'P3'
export type Domain = 'fintech' | 'retail' | 'healthcare'
export type Priority = 'critical' | 'high' | 'medium' | 'low'
export type ItemType = 'user_story' | 'task'
export type ItemStatus = 'todo' | 'in_progress' | 'done'
export type RiskSeverity = 'critical' | 'high' | 'medium' | 'low'
export type RiskCategory = 'planning' | 'compliance' | 'data' | 'security' | 'capacity' | 'dependency'
export type SourceStatus = 'pdf_loaded' | 'fallback'
export type LLMProviderName = 'null' | 'ollama' | 'openai'
export type LLMMode = 'offline' | 'ollama' | 'openai' | 'auto'
export type ApprovalStatus = 'pending' | 'approved' | 'rejected'
export type ApprovalActionType =
  | 'change_priority'
  | 'reassign_member'
  | 'move_sprint'
  | 'add_risk'
  | 'ask_product_owner'

export interface ProjectState {
  project_id: ProjectId
  name: string
  domain: Domain
  mvp_week: number
  final_week: number
  objective: string
  summary: string
  requirements: string[]
  deadlines: Record<string, string>
  milestones: string[]
  dependencies: string[]
  source_file: string
  source_status: SourceStatus
  raw_text_excerpt: string
}

export interface TeamMemberState {
  member_id: string
  name: string
  role: string
  summary: string
  skills: string[]
  domains: string[]
  experience_years: number
  seniority: number
  capacity_per_sprint: number
}

export interface BacklogItemState {
  item_id: string
  project_id: ProjectId
  epic: string
  title: string
  description: string
  item_type: ItemType
  required_skills: string[]
  priority_score: number
  priority: Priority
  story_points: number
  dependencies: string[]
  acceptance_criteria: string[]
  sprint_hint: number
  phase: string
  status: ItemStatus
  sprint_number: number
  sprint_id: string
}

export interface SprintPlanState {
  sprint_id: string
  project_id: ProjectId
  sprint_number: number
  start_week: number
  end_week: number
  focus: string
  goal: string
  item_ids: string[]
  planned_points: number
  capacity_points: number
}

export interface AllocationState {
  allocation_id: string
  item_id: string
  project_id: ProjectId
  sprint_id: string
  member_id: string
  member_name: string
  role: string
  assigned_points: number
  match_score: number
  matched_skills: string[]
  matched_domains: string[]
  rationale: string
  over_capacity: boolean
}

export interface RiskState {
  risk_id: string
  project_id: ProjectId | null
  severity: RiskSeverity
  category: RiskCategory
  title: string
  description: string
  mitigation: string
  owner_suggestion: string
}

export interface InsightState {
  title: string
  description: string
  impact: string
}

export interface MetadataState {
  engine: 'deterministic'
  capacity_per_member_per_sprint: number
  sprint_length_weeks: number
  source_data_dir: string
}

export interface DemoState {
  projects: ProjectState[]
  team_members: TeamMemberState[]
  backlog_items: BacklogItemState[]
  sprint_plans: SprintPlanState[]
  allocations: AllocationState[]
  risks: RiskState[]
  insights: InsightState[]
  metadata: MetadataState
}

export interface LLMMetadataState {
  provider: LLMProviderName
  model: string
  mode: LLMMode
  fallback_used: boolean
  latency_ms: number
  error: string | null
}

export interface AgentRecommendationState {
  recommendation_id: string
  title: string
  project_id: ProjectId | null
  affected_item_ids: string[]
  affected_member_ids: string[]
  rationale: string
  expected_impact: string
  confidence: number
}

export interface ApprovalActionState {
  action_id: string
  action_type: ApprovalActionType
  project_id: ProjectId | null
  affected_item_ids: string[]
  affected_member_ids: string[]
  before: Record<string, string | number | boolean | null>
  after: Record<string, string | number | boolean | null>
  rationale: string
  status: ApprovalStatus
}

export interface AgentAnalysisState {
  executive_summary: string
  project_assessments: Record<ProjectId, string>
  priority_analysis: string[]
  allocation_analysis: string[]
  risk_analysis: string[]
  product_owner_questions: string[]
}

export interface AgentState extends DemoState {
  agent_analysis: AgentAnalysisState
  recommendations: AgentRecommendationState[]
  approval_queue: ApprovalActionState[]
  llm_metadata: LLMMetadataState
}
