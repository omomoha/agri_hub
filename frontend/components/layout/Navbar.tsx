'use client'

import Link from 'next/link'
import { useAuth } from '@/components/auth/AuthProvider'
import { Button } from '@/components/ui/Button'
import { Leaf, User, LogOut } from 'lucide-react'

export function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <Leaf className="w-8 h-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">AgriLink</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/listings" className="text-gray-600 hover:text-primary-600">
              Browse Listings
            </Link>
            {user?.role === 'farmer' && (
              <Link href="/farms" className="text-gray-600 hover:text-primary-600">
                My Farms
              </Link>
            )}
            {user?.role === 'admin' && (
              <Link href="/admin/kyc" className="text-gray-600 hover:text-primary-600">
                Admin Panel
              </Link>
            )}
          </div>

          {/* Auth Section */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <User className="w-5 h-5 text-gray-600" />
                  <span className="text-sm text-gray-700">{user.full_name}</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                  className="flex items-center space-x-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link href="/auth/login">
                  <Button variant="outline" size="sm">Login</Button>
                </Link>
                <Link href="/auth/register">
                  <Button size="sm">Register</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
