import { useState, type KeyboardEvent } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/solid'

interface Props {
  onSend: (message: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('')

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex items-end gap-3 bg-gray-900 border border-gray-700 rounded-2xl px-4 py-3">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Ask the Scrum Agent anything…"
        disabled={disabled}
        rows={1}
        className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 resize-none outline-none max-h-40 overflow-y-auto"
      />
      <button
        onClick={submit}
        disabled={disabled || !value.trim()}
        className="w-8 h-8 rounded-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors flex-shrink-0"
      >
        <PaperAirplaneIcon className="w-4 h-4 text-white" />
      </button>
    </div>
  )
}
