import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { uploadResume } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile?.type === 'application/pdf') {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Please upload a PDF file')
    }
  }, [])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile?.type === 'application/pdf') {
      setFile(selectedFile)
      setError(null)
    } else if (selectedFile) {
      setError('Please upload a PDF file')
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)

    try {
      const data = await uploadResume(file)
      navigate(`/results/${data.resume_id}`, { state: data })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload resume. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  if (uploading) {
    return <LoadingSpinner message="Analyzing your resume..." />
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Resume Job Matcher
        </h1>
        <p className="text-gray-600 text-lg">
          Upload your resume to discover matching roles, get improvement recommendations,
          and find job postings that don't require account creation.
        </p>
      </div>

      <div className="card">
        <div
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
            dragActive
              ? 'border-primary-500 bg-primary-50'
              : file
              ? 'border-emerald-300 bg-emerald-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="flex flex-col items-center">
              <CheckCircle className="text-emerald-500 mb-3" size={48} />
              <p className="text-lg font-medium text-gray-900 mb-1">{file.name}</p>
              <p className="text-sm text-gray-500 mb-4">
                {(file.size / 1024).toFixed(1)} KB
              </p>
              <button
                onClick={() => setFile(null)}
                className="text-sm text-gray-500 hover:text-gray-700 underline"
              >
                Choose a different file
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload className="text-gray-400 mb-3" size={48} />
              <p className="text-lg font-medium text-gray-900 mb-1">
                Drop your resume here
              </p>
              <p className="text-sm text-gray-500 mb-4">or click to browse</p>
              <label className="btn-secondary cursor-pointer">
                Select PDF
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg">
            <AlertCircle size={18} />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {file && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="btn-primary w-full mt-6"
          >
            Analyze Resume
          </button>
        )}
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="bg-primary-100 text-primary-600 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3">
            <FileText size={20} />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">Role Matching</h3>
          <p className="text-sm text-gray-500">
            Identifies roles that match your skills and experience.
          </p>
        </div>
        <div className="card text-center">
          <div className="bg-emerald-100 text-emerald-600 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3">
            <CheckCircle size={20} />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">Resume Optimization</h3>
          <p className="text-sm text-gray-500">
            Suggests improvements and applies them to your PDF.
          </p>
        </div>
        <div className="card text-center">
          <div className="bg-amber-100 text-amber-600 w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Upload size={20} />
          </div>
          <h3 className="font-semibold text-gray-900 mb-1">Job Crawling</h3>
          <p className="text-sm text-gray-500">
            Finds jobs on LinkedIn, Glassdoor, and Indeed with easy-apply.
          </p>
        </div>
      </div>
    </div>
  )
}
