import React, { useState } from 'react'
import axios from 'axios'

export const App: React.FC = () => {
	const [sessionId] = useState(() => `web:${Math.random().toString(36).slice(2)}`)
	const [input, setInput] = useState("")
	const [messages, setMessages] = useState<{role:'user'|'assistant', content:string}[]>([])
	const [loading, setLoading] = useState(false)

	const send = async () => {
		if (!input.trim()) return
		const userMsg = { role: 'user' as const, content: input }
		setMessages(m => [...m, userMsg])
		setInput("")
		setLoading(true)
		try {
			const resp = await axios.post('http://localhost:8000/api/chat', {
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
		<div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'system-ui' }}>
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
	)
}