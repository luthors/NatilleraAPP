import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const response = await api.get('/users/me')
          setUser(response.data)
        } catch (err) {
          console.error('Failed to fetch user:', err)
          localStorage.removeItem('access_token')
        }
      }
      setLoading(false)
    }
    checkAuth()
  }, [])

  const login = async (email, password) => {
    try {
      setError(null)
      const response = await api.post('/auth/login', { email, password })
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      setUser(response.data.user)
      return response.data
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
      throw err
    }
  }

  const register = async (email, password, full_name) => {
    try {
      setError(null)
      const response = await api.post('/auth/register', {
        email,
        password,
        full_name,
      })
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      setUser(response.data.user)
      return response.data
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
      throw err
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
