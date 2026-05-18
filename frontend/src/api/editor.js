const API_URL = import.meta.env.VITE_API_URL || ''
const EXPERT_TOKEN_KEY = 'expert_token'

function buildCompilePayload(text, font, fontSize, margins) {
  return { text, font, fontSize, top: margins.top, bottom: margins.bottom, left: margins.left, right: margins.right }
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

async function checkResponse(response) {
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }
  return response
}

async function fetchJson(url, options) {
  return (await checkResponse(await fetch(url, options))).json()
}

async function fetchBlob(url, options) {
  return (await checkResponse(await fetch(url, options))).blob()
}

// -- text compilation & export --

export async function compileText(text, font, fontSize, margins) {
  return fetchBlob(`${API_URL}/api/compile/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildCompilePayload(text, font, fontSize, margins)),
  })
}

export async function exportPdf(text, font, fontSize, margins) {
  return fetchBlob(`${API_URL}/api/export/pdf/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildCompilePayload(text, font, fontSize, margins)),
  })
}

export async function exportDocx(text, font, fontSize, margins) {
  return fetchBlob(`${API_URL}/api/export/docx/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildCompilePayload(text, font, fontSize, margins)),
  })
}

export async function importFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const data = await fetchJson(`${API_URL}/api/import/`, {
    method: 'POST',
    body: formData,
  })
  if (!data.text) throw new Error('Файл обработан, но текст не получен')
  return data.text
}

// -- fonts --

export async function fetchFonts() {
  const data = await fetchJson(`${API_URL}/api/fonts/`)
  return data.map(f => f.name)
}

export async function uploadFont(file, name, token) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  const data = await fetchJson(`${API_URL}/api/fonts/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })
  return data.name
}

export function createFontFace(name, url) {
  const style = document.createElement('style')
  style.textContent = `@font-face { font-family: '${name}'; src: url('${url}'); }`
  document.head.appendChild(style)
}

export function getFontUrl(name) {
  return `${API_URL}/api/fonts/${encodeURIComponent(name)}/`
}

// -- auth --

export function loadToken() {
  return localStorage.getItem(EXPERT_TOKEN_KEY) || ''
}

export function saveToken(token) {
  localStorage.setItem(EXPERT_TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(EXPERT_TOKEN_KEY)
}

export async function loginExpert(password) {
  const data = await fetchJson(`${API_URL}/api/auth/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'expert', password }),
  })
  return data.token
}

export async function verifyToken(token) {
  const res = await fetch(`${API_URL}/api/auth/verify/`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.ok
}

export function downloadPdfBlob(blob) {
  downloadBlob(blob, 'document.pdf')
}

export function downloadDocxBlob(blob) {
  downloadBlob(blob, 'document.docx')
}
