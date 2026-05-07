const API_URL = import.meta.env.VITE_API_URL

function buildCompilePayload(text, font, fontSize, margins) {
  return {
    text,
    font,
    fontSize,
    top: margins.top,
    bottom: margins.bottom,
    left: margins.left,
    right: margins.right,
  }
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

async function fetchJson(url, options) {
  const response = await fetch(url, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }
  return response.json()
}

async function fetchBlob(url, options) {
  const response = await fetch(url, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }
  return response.blob()
}

export async function ping() {
  const data = await fetchJson(`${API_URL}/api/ping/`)
  return data.message
}

export async function compileText(text, font, fontSize, margins) {
  const payload = buildCompilePayload(text, font, fontSize, margins)
  return fetchBlob(`${API_URL}/api/compile/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function exportPdf(text, font, fontSize, margins) {
  const payload = buildCompilePayload(text, font, fontSize, margins)
  return fetchBlob(`${API_URL}/api/export-pdf/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function exportDocx(text, font, fontSize, margins) {
  return fetchBlob(`${API_URL}/api/export-docx/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, font, fontSize, ...margins }),
  })
}

export async function importFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const data = await fetchJson(`${API_URL}/api/import/`, {
    method: 'POST',
    body: formData,
  })

  if (!data.text) {
    throw new Error('Файл обработан, но текст не получен')
  }
  return data.text
}

export function downloadPdfBlob(blob) {
  downloadBlob(blob, 'document.pdf')
}

export function downloadDocxBlob(blob) {
  downloadBlob(blob, 'document.docx')
}
