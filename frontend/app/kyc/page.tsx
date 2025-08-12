'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Upload, FileText, CheckCircle, XCircle, Clock } from 'lucide-react'

interface KYCStatus {
  id: number
  status: 'pending' | 'approved' | 'rejected' | 'under_review'
  document_type: string
  document_number: string
  admin_notes?: string
  created_at: string
  reviewed_at?: string
}

export default function KYCPage() {
  const { user } = useAuth()
  const [kycStatus, setKycStatus] = useState<KYCStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [formData, setFormData] = useState({
    document_type: 'national_id',
    document_number: '',
    document_file: null as File | null,
    selfie_file: null as File | null,
    business_registration: null as File | null,
    business_address: ''
  })

  useEffect(() => {
    if (user) {
      fetchKYCStatus()
    }
  }, [user])

  const fetchKYCStatus = async () => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`/api/v1/kyc/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setKycStatus(data)
      } else if (response.status === 404) {
        setKycStatus(null)
      } else {
        setError('Failed to fetch KYC status')
      }
    } catch (error) {
      setError('Error fetching KYC status')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, field: string) => {
    const file = e.target.files?.[0]
    if (file) {
      setFormData(prev => ({
        ...prev,
        [field]: file
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setUploading(true)

    try {
      const token = localStorage.getItem('authToken')
      const formDataToSend = new FormData()
      
      formDataToSend.append('document_type', formData.document_type)
      formDataToSend.append('document_number', formData.document_number)
      
      if (formData.document_file) {
        formDataToSend.append('document_file', formData.document_file)
      }
      
      if (formData.selfie_file) {
        formDataToSend.append('selfie_file', formData.selfie_file)
      }
      
      if (formData.business_registration) {
        formDataToSend.append('business_registration', formData.business_registration)
      }
      
      if (formData.business_address) {
        formDataToSend.append('business_address', formData.business_address)
      }

      const response = await fetch(`/api/v1/kyc/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      })

      if (response.ok) {
        setSuccess('KYC documents uploaded successfully! Your application is under review.')
        fetchKYCStatus()
        // Reset form
        setFormData({
          document_type: 'national_id',
          document_number: '',
          document_file: null,
          selfie_file: null,
          business_registration: null,
          business_address: ''
        })
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to upload KYC documents')
      }
    } catch (error) {
      setError('Error uploading KYC documents')
    } finally {
      setUploading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-6 h-6 text-green-600" />
      case 'rejected':
        return <XCircle className="w-6 h-6 text-red-600" />
      case 'under_review':
        return <Clock className="w-6 h-6 text-yellow-600" />
      default:
        return <Clock className="w-6 h-6 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'text-green-600'
      case 'rejected':
        return 'text-red-600'
      case 'under_review':
        return 'text-yellow-600'
      default:
        return 'text-gray-600'
    }
  }

  if (!user) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">Please log in to access KYC verification.</p>
      </div>
    )
  }

  if (user.role !== 'farmer') {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">KYC verification is only available for farmers.</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          KYC Verification
        </h1>
        <p className="text-xl text-gray-600">
          Complete your verification to start listing produce on AgriLink
        </p>
      </div>

      {/* Current Status */}
      {kycStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {getStatusIcon(kycStatus.status)}
              <span>Verification Status: {kycStatus.status.replace('_', ' ').toUpperCase()}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Document Type:</span> {kycStatus.document_type.replace('_', ' ').toUpperCase()}
              </div>
              <div>
                <span className="font-medium">Document Number:</span> {kycStatus.document_number}
              </div>
              <div>
                <span className="font-medium">Submitted:</span> {new Date(kycStatus.created_at).toLocaleDateString()}
              </div>
              {kycStatus.reviewed_at && (
                <div>
                  <span className="font-medium">Reviewed:</span> {new Date(kycStatus.reviewed_at).toLocaleDateString()}
                </div>
              )}
            </div>
            
            {kycStatus.admin_notes && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <span className="font-medium">Admin Notes:</span>
                <p className="mt-2 text-gray-700">{kycStatus.admin_notes}</p>
              </div>
            )}

            {kycStatus.status === 'rejected' && (
              <div className="text-center">
                <Button onClick={() => setKycStatus(null)}>
                  Submit New Application
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Upload Form */}
      {!kycStatus || kycStatus.status === 'rejected' ? (
        <Card>
          <CardHeader>
            <CardTitle>Upload Verification Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg mb-4">
                {success}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type *
                  </label>
                  <select
                    value={formData.document_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, document_type: e.target.value }))}
                    className="input-field"
                    required
                  >
                    <option value="national_id">National ID</option>
                    <option value="drivers_license">Driver's License</option>
                    <option value="passport">Passport</option>
                    <option value="cac_certificate">CAC Certificate</option>
                    <option value="utility_bill">Utility Bill</option>
                    <option value="bank_statement">Bank Statement</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Number *
                  </label>
                  <input
                    type="text"
                    value={formData.document_number}
                    onChange={(e) => setFormData(prev => ({ ...prev, document_number: e.target.value }))}
                    className="input-field"
                    placeholder="Enter document number"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document File *
                </label>
                <input
                  type="file"
                  onChange={(e) => handleFileChange(e, 'document_file')}
                  className="input-field"
                  accept=".pdf,.jpg,.jpeg,.png"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Accepted formats: PDF, JPG, JPEG, PNG (Max 5MB)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selfie Photo
                </label>
                <input
                  type="file"
                  onChange={(e) => handleFileChange(e, 'selfie_file')}
                  className="input-field"
                  accept=".jpg,.jpeg,.png"
                />
                <p className="text-sm text-gray-500 mt-1">
                  A clear photo of yourself holding the document
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Address
                </label>
                <input
                  type="text"
                  value={formData.business_address}
                  onChange={(e) => setFormData(prev => ({ ...prev, business_address: e.target.value }))}
                  className="input-field"
                  placeholder="Enter your business address"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Registration Document
                </label>
                <input
                  type="file"
                  onChange={(e) => handleFileChange(e, 'business_registration')}
                  className="input-field"
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Business registration certificate or similar document
                </p>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={uploading}
              >
                {uploading ? (
                  <>
                    <Upload className="w-4 h-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Submit KYC Application
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : null}

      {/* Information */}
      <Card>
        <CardHeader>
          <CardTitle>About KYC Verification</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            KYC (Know Your Customer) verification is required for all farmers to ensure the safety 
            and trustworthiness of our platform. This process helps us verify your identity and 
            business legitimacy.
          </p>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">What happens after submission?</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Your documents will be reviewed by our admin team</li>
              <li>• Review typically takes 1-3 business days</li>
              <li>• You'll receive email notifications about status changes</li>
              <li>• Once approved, you can start listing your produce</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
