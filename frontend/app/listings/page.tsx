'use client'

import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/components/auth/AuthProvider'
import { Leaf, MapPin, Calendar, Scale, DollarSign } from 'lucide-react'

interface Listing {
  id: number
  title: string
  description: string
  produce_type: string
  quantity_kg: number
  unit_price_ngn: number
  total_price_ngn: number
  harvest_date: string
  expiry_date: string
  is_organic: boolean
  quality_grade: string
  farmer_id: number
  farm_id: number
  created_at: string
}

export default function ListingsPage() {
  const { user } = useAuth()
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchListings()
  }, [])

  const fetchListings = async () => {
    try {
      const token = localStorage.getItem('authToken')
      const response = await fetch(`/api/v1/listings`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        redirect: 'follow'
      })

      if (response.ok) {
        const data = await response.json()
        setListings(data)
      } else {
        setError('Failed to fetch listings')
      }
    } catch (error) {
      setError('Error fetching listings')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN'
    }).format(price)
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="text-center">
          <Leaf className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Loading listings...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <div className="text-red-600 mb-4">{error}</div>
        <Button onClick={fetchListings}>Try Again</Button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Browse Produce Listings
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Discover fresh, high-quality produce from verified farmers across Nigeria
        </p>
      </div>

      {/* Create Listing Button for Farmers */}
      {user?.role === 'farmer' && user?.is_verified && (
        <div className="text-center">
          <Button size="lg" className="mb-8">
            Create New Listing
          </Button>
        </div>
      )}

      {/* Listings Grid */}
      {listings.length === 0 ? (
        <div className="text-center py-20">
          <Leaf className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No Listings Available</h3>
          <p className="text-gray-500">Check back later for fresh produce listings</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {listings.map((listing) => (
            <Card key={listing.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">{listing.title}</CardTitle>
                  {listing.is_organic && (
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                      Organic
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">{listing.description}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Produce Type */}
                <div className="flex items-center space-x-2">
                  <Leaf className="w-4 h-4 text-primary-600" />
                  <span className="text-sm font-medium capitalize">{listing.produce_type}</span>
                </div>

                {/* Quantity and Price */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Scale className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">{listing.quantity_kg} kg</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <DollarSign className="w-4 h-4 text-gray-500" />
                    <span className="text-sm font-medium">{formatPrice(listing.unit_price_ngn)}/kg</span>
                  </div>
                </div>

                {/* Total Price */}
                <div className="text-lg font-bold text-primary-600">
                  Total: {formatPrice(listing.total_price_ngn)}
                </div>

                {/* Dates */}
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4" />
                    <span>Harvested: {formatDate(listing.harvest_date)}</span>
                  </div>
                  {listing.expiry_date && (
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4" />
                      <span>Expires: {formatDate(listing.expiry_date)}</span>
                    </div>
                  )}
                </div>

                {/* Quality Grade */}
                {listing.quality_grade && (
                  <div className="text-sm">
                    <span className="font-medium">Quality:</span> {listing.quality_grade}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  {user?.role !== 'farmer' && (
                    <Button className="flex-1" size="sm">
                      Make Offer
                    </Button>
                  )}
                  <Button variant="outline" size="sm" className="flex-1">
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
