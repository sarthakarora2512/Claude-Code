import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getResume(resumeId) {
  const response = await api.get(`/resume/${resumeId}`)
  return response.data
}

export async function getRecommendations(resumeId) {
  const response = await api.get(`/recommendations/${resumeId}`)
  return response.data
}

export async function applyRecommendations(resumeId, recommendations) {
  const response = await api.post('/recommendations/apply', {
    resume_id: resumeId,
    recommendations,
  })
  return response.data
}

export async function searchJobsForResume(resumeId) {
  const response = await api.get(`/jobs/search/${resumeId}`)
  return response.data
}

export async function searchJobs(skills, jobTitles, location, remoteOnly) {
  const response = await api.post('/jobs/search', {
    skills,
    job_titles: jobTitles,
    location,
    remote_only: remoteOnly,
  })
  return response.data
}
