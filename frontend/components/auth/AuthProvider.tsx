'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: string
  is_verified: boolean
  kyc_status: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken')
    if (token) {
      fetchUser(token)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async (token: string) => {
    try {
      const response = await fetch(`/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        localStorage.removeItem('authToken')
      }
    } catch (error) {
      console.error('Error fetching user:', error)
      localStorage.removeItem('authToken')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('authToken', data.access_token)
        setUser(data.user)
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await fetch(`/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('authToken', data.access_token)
        setUser(data.user)
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('authToken')
    setUser(null)
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
