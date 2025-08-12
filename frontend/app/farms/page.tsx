'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { MapPin, Ruler, Leaf, Plus, Edit, Eye } from 'lucide-react'

interface Farm {
  id: number
  name: string
  description: string
  location: string
  size_hectares: number
  soil_type: string
  irrigation_type: string
  is_active: boolean
  created_at: string
}

export default function FarmsPage() {
  const { user } = useAuth()
  const [farms, setFarms] = useState<Farm[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user) {
      fetchFarms()
    }
  }, [user])

  const fetchFarms = async () => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`/api/v1/farms/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setFarms(data)
      } else {
        setError('Failed to fetch farms')
      }
    } catch (error) {
      setError('Error fetching farms')
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">Please log in to access your farms.</p>
      </div>
    )
  }

  if (user.role !== 'farmer') {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600">Farm management is only available for farmers.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="text-center">
          <Leaf className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Loading farms...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <div className="text-red-600 mb-4">{error}</div>
        <Button onClick={fetchFarms}>Try Again</Button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          My Farms
        </h1>
        <p className="text-xl text-gray-600">
          Manage your agricultural properties and land
        </p>
      </div>

      {/* Create Farm Button */}
      <div className="text-center">
        <Button size="lg" className="mb-8">
          <Plus className="w-5 h-5 mr-2" />
          Add New Farm
        </Button>
      </div>

      {/* Farms Grid */}
      {farms.length === 0 ? (
        <div className="text-center py-20">
          <Leaf className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No Farms Yet</h3>
          <p className="text-gray-500 mb-6">Start by adding your first farm to begin listing produce</p>
          <Button size="lg">
            <Plus className="w-5 h-5 mr-2" />
            Add Your First Farm
          </Button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {farms.map((farm) => (
            <Card key={farm.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">{farm.name}</CardTitle>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{farm.description}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Location */}
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-gray-500" />
                  <span className="text-sm">{farm.location}</span>
                </div>

                {/* Size */}
                <div className="flex items-center space-x-2">
                  <Ruler className="w-4 h-4 text-gray-500" />
                  <span className="text-sm">{farm.size_hectares} hectares</span>
                </div>

                {/* Soil Type */}
                {farm.soil_type && (
                  <div className="flex items-center space-x-2">
                    <Leaf className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">Soil: {farm.soil_type}</span>
                  </div>
                )}

                {/* Irrigation */}
                {farm.irrigation_type && (
                  <div className="flex items-center space-x-2">
                    <Leaf className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">Irrigation: {farm.irrigation_type}</span>
                  </div>
                )}

                {/* Status */}
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    farm.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {farm.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="text-xs text-gray-500">
                    Added {new Date(farm.created_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Create Listing
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    View Listings
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Information Card */}
      <Card>
        <CardHeader>
          <CardTitle>About Farm Management</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            Managing your farms on AgriLink allows you to organize your agricultural properties 
            and create detailed produce listings for each location.
          </p>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Benefits of Farm Management:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Organize produce by farm location</li>
              <li>• Track soil types and irrigation methods</li>
              <li>• Create detailed listings for each farm</li>
              <li>• Monitor farm-specific performance</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
