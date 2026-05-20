import type { AgentState } from '../types/demo_state'

const BASE = '/api'

export async function fetchAgentState(): Promise<AgentState> {
  const res = await fetch(`${BASE}/agent-state`)
  if (!res.ok) throw new Error(`Failed to fetch agent state: ${res.statusText}`)
  return res.json()
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
): Promise<string> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  if (!res.ok) throw new Error(`Chat request failed: ${res.statusText}`)
  const data = await res.json()
  return data.response as string
}
