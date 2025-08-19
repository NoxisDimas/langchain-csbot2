import React, { useState } from 'react'
import axios from 'axios'
import { RAGUpload } from './RAGUpload'

export const App: React.FC = () => {
	const [sessionId] = useState(() => `web:${Math.random().toString(36).slice(2)}`)
	const [input, setInput] = useState("")
	const [messages, setMessages] = useState<{role:'user'|'assistant', content:string}[]>([])
	const [loading, setLoading] = useState(false)
	const [activeView, setActiveView] = useState<'chat' | 'rag'>('chat')

	const send = async () => {
		if (!input.trim()) return
		const userMsg = { role: 'user' as const, content: input }
		setMessages(m => [...m, userMsg])
		setInput("")
		setLoading(true)
		try {
			const base = (import.meta as any).env?.VITE_API_URL || ''
			const resp = await axios.post(`${base}/api/chat`, {
				session_id: sessionId,
				message: userMsg.content,
				channel: 'web',
			})
			const aiMsg = { role: 'assistant' as const, content: resp.data.answer }
			setMessages(m => [...m, aiMsg])
		} catch (e:any) {
			setMessages(m => [...m, { role: 'assistant', content: 'Error: ' + (e?.message || 'unknown') }])
		} finally {
			setLoading(false)
		}
	}

	return (
		<div style={{ maxWidth: 1200, margin: '40px auto', fontFamily: 'system-ui' }}>
			{/* Navigation */}
			<div style={{ display: 'flex', justifyContent: 'center', marginBottom: '30px' }}>
				<button
					onClick={() => setActiveView('chat')}
					style={{
						padding: '12px 24px',
						margin: '0 10px',
						border: 'none',
						background: activeView === 'chat' ? '#007bff' : '#f8f9fa',
						color: activeView === 'chat' ? 'white' : '#333',
						borderRadius: '4px',
						cursor: 'pointer',
						fontSize: '16px'
					}}
				>
					Chat
				</button>
				<button
					onClick={() => setActiveView('rag')}
					style={{
						padding: '12px 24px',
						margin: '0 10px',
						border: 'none',
						background: activeView === 'rag' ? '#007bff' : '#f8f9fa',
						color: activeView === 'rag' ? 'white' : '#333',
						borderRadius: '4px',
						cursor: 'pointer',
						fontSize: '16px'
					}}
				>
					RAG System
				</button>
			</div>

			{/* Chat View */}
			{activeView === 'chat' && (
				<div style={{ maxWidth: 600, margin: '0 auto' }}>
					<h2>AI Customer Service</h2>
					<div style={{ border: '1px solid #ccc', padding: 12, borderRadius: 8, minHeight: 240 }}>
						{messages.map((m, i) => (
							<div key={i} style={{ margin: '8px 0', textAlign: m.role === 'user' ? 'right' : 'left' }}>
								<span style={{ display: 'inline-block', background: m.role==='user'?'#e6f7ff':'#f6ffed', padding: '8px 12px', borderRadius: 8 }}>
									{m.content}
								</span>
							</div>
						))}
					</div>
					<div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
						<input value={input} onChange={e=>setInput(e.target.value)} placeholder="Tulis pesan..." style={{ flex: 1, padding: 8 }} />
						<button disabled={loading} onClick={send}>{loading? 'Mengirim...' : 'Kirim'}</button>
					</div>
				</div>
			)}

			{/* RAG View */}
			{activeView === 'rag' && <RAGUpload />}
		</div>
	)
}