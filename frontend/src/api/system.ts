/**
 * Avvia update.py sul backend e chiama onLine per ogni riga di output.
 * Risolve quando il processo termina (ricevuto [DONE]) o la connessione si chiude.
 */
export async function streamUpdate(onLine: (line: string) => void): Promise<void> {
  const res = await fetch('/api/system/update')
  if (!res.ok || !res.body) {
    throw new Error(`HTTP ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const line = part.trim()
      if (line.startsWith('data: ')) {
        const text = line.slice(6)
        if (text === '[DONE]') return
        onLine(text)
      }
    }
  }
}
