'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { CheckCircle, XCircle, Clock, Eye, FileText } from 'lucide-react'

interface KYCApplication {
  id: number
  user_id: number
  document_type: string
  document_number: string
  document_file_path: string
  selfie_file_path?: string
  business_registration?: string
  business_address?: string
  status: 'pending' | 'approved' | 'rejected' | 'under_review'
  admin_notes?: string
  created_at: string
  user: {
    full_name: string
    email: string
    role: string
  }
}

export default function AdminKYCPage() {
  const { user } = useAuth()
  const [applications, setApplications] = useState<KYCApplication[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedApp, setSelectedApp] = useState<KYCApplication | null>(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const [reviewing, setReviewing] = useState(false)

  useEffect(() => {
    if (user && user.role === 'admin') {
      fetchKYCQueue()
    }
  }, [user])

  const fetchKYCQueue = async () => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`/api/v1/kyc/admin/queue`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setApplications(data)
      } else {
        setError('Failed to fetch KYC applications')
      }
    } catch (error) {
      setError('Error fetching KYC applications')
    } finally {
      setLoading(false)
    }
  }

  const handleReview = async (status: 'approved' | 'rejected') => {
    if (!selectedApp) return

    setReviewing(true)
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`/api/v1/kyc/admin/${selectedApp.id}/review`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status,
          admin_notes: reviewNotes
        })
      })

      if (response.ok) {
        // Refresh the queue
        fetchKYCQueue()
        setSelectedApp(null)
        setReviewNotes('')
        setError('')
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to update KYC status')
      }
    } catch (error) {
      setError('Error updating KYC status')
    } finally {
      setReviewing(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'under_review':
        return <Clock className="w-5 h-5 text-yellow-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'under_review':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (!user) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">Please log in to access the admin panel.</p>
      </div>
    )
  }

  if (user.role !== 'admin') {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">Access denied. Admin privileges required.</p>
      </div>
      )
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="text-center">
          <Clock className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Loading KYC applications...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          KYC Review Panel
        </h1>
        <p className="text-xl text-gray-600">
          Review and approve farmer verification applications
        </p>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="text-center py-6">
            <div className="text-2xl font-bold text-blue-600">
              {applications.filter(app => app.status === 'pending').length}
            </div>
            <div className="text-sm text-gray-600">Pending Review</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-6">
            <div className="text-2xl font-bold text-yellow-600">
              {applications.filter(app => app.status === 'under_review').length}
            </div>
            <div className="text-sm text-gray-600">Under Review</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-6">
            <div className="text-2xl font-bold text-green-600">
              {applications.filter(app => app.status === 'approved').length}
            </div>
            <div className="text-sm text-gray-600">Approved</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-6">
            <div className="text-2xl font-bold text-red-600">
              {applications.filter(app => app.status === 'rejected').length}
            </div>
            <div className="text-sm text-gray-600">Rejected</div>
          </CardContent>
        </Card>
      </div>

      {/* Applications List */}
      <Card>
        <CardHeader>
          <CardTitle>KYC Applications</CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {applications.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No Applications</h3>
              <p className="text-gray-500">All KYC applications have been processed</p>
            </div>
          ) : (
            <div className="space-y-4">
              {applications.map((app) => (
                <div key={app.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(app.status)}`}>
                          {app.status.replace('_', ' ').toUpperCase()}
                        </div>
                        <div>
                          <h4 className="font-medium">{app.user.full_name}</h4>
                          <p className="text-sm text-gray-600">{app.user.email}</p>
                        </div>
                      </div>
                      
                      <div className="mt-2 grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Document:</span> {app.document_type.replace('_', ' ').toUpperCase()}
                        </div>
                        <div>
                          <span className="font-medium">Number:</span> {app.document_number}
                        </div>
                        <div>
                          <span className="font-medium">Submitted:</span> {new Date(app.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedApp(app)}
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Review
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Review Modal */}
      {selectedApp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">Review KYC Application</h3>
              
              <div className="space-y-4 mb-6">
                <div>
                  <span className="font-medium">Applicant:</span> {selectedApp.user.full_name}
                </div>
                <div>
                  <span className="font-medium">Email:</span> {selectedApp.user.email}
                </div>
                <div>
                  <span className="font-medium">Document Type:</span> {selectedApp.document_type.replace('_', ' ').toUpperCase()}
                </div>
                <div>
                  <span className="font-medium">Document Number:</span> {selectedApp.document_number}
                </div>
                {selectedApp.business_address && (
                  <div>
                    <span className="font-medium">Business Address:</span> {selectedApp.business_address}
                  </div>
                )}
                <div>
                  <span className="font-medium">Submitted:</span> {new Date(selectedApp.created_at).toLocaleDateString()}
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Notes
                </label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  className="input-field"
                  rows={4}
                  placeholder="Add notes about your decision..."
                />
              </div>

              <div className="flex space-x-4">
                <Button
                  onClick={() => handleReview('approved')}
                  disabled={reviewing}
                  className="flex-1"
                >
                  {reviewing ? 'Processing...' : 'Approve'}
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => handleReview('rejected')}
                  disabled={reviewing}
                  className="flex-1"
                >
                  {reviewing ? 'Processing...' : 'Reject'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedApp(null)
                    setReviewNotes('')
                  }}
                  disabled={reviewing}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
