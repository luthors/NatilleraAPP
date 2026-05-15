import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, Alert, KeyboardAvoidingView, Platform,
} from 'react-native'
import * as SecureStore from 'expo-secure-store'
import api from '../../services/api'

export default function LoginScreen({ navigation }) {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]   = useState(false)

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Por favor completa todos los campos.')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      await SecureStore.setItemAsync('access_token', data.access_token)
      await SecureStore.setItemAsync('refresh_token', data.refresh_token)
      // RootNavigator listens to this via re-mount / context — for now, hard reload
      navigation.reset({ index: 0, routes: [{ name: 'Main' }] })
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Error al iniciar sesión'
      Alert.alert('Error', msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <Text style={styles.logo}>🏦 Natillera App</Text>
      <Text style={styles.subtitle}>Inicia sesión</Text>

      <TextInput
        style={styles.input}
        placeholder="Correo electrónico"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={styles.input}
        placeholder="Contraseña"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleLogin}
        disabled={loading}
      >
        <Text style={styles.buttonText}>{loading ? 'Entrando...' : 'Iniciar sesión'}</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => navigation.navigate('Register')}>
        <Text style={styles.link}>¿No tienes cuenta? Regístrate</Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container:      { flex: 1, justifyContent: 'center', paddingHorizontal: 24, backgroundColor: '#f9fafb' },
  logo:           { fontSize: 28, fontWeight: 'bold', color: '#4f46e5', textAlign: 'center', marginBottom: 4 },
  subtitle:       { fontSize: 14, color: '#6b7280', textAlign: 'center', marginBottom: 32 },
  input:          { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, marginBottom: 12, fontSize: 15 },
  button:         { backgroundColor: '#4f46e5', borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginTop: 4 },
  buttonDisabled: { opacity: 0.5 },
  buttonText:     { color: '#fff', fontWeight: '600', fontSize: 15 },
  link:           { textAlign: 'center', marginTop: 20, color: '#4f46e5', fontSize: 14 },
})
