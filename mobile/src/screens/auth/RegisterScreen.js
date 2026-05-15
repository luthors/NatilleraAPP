import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, Alert, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native'
import * as SecureStore from 'expo-secure-store'
import api from '../../services/api'

export default function RegisterScreen({ navigation }) {
  const [form, setForm] = useState({ nombre: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const set = (key) => (val) => setForm((f) => ({ ...f, [key]: val }))

  const handleRegister = async () => {
    if (!form.nombre || !form.email || !form.password) {
      Alert.alert('Error', 'Por favor completa todos los campos.')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/registro', form)
      await SecureStore.setItemAsync('access_token', data.access_token)
      await SecureStore.setItemAsync('refresh_token', data.refresh_token)
      navigation.reset({ index: 0, routes: [{ name: 'Main' }] })
    } catch (err) {
      Alert.alert('Error', err.response?.data?.detail ?? 'Error al registrarse')
    } finally {
      setLoading(false)
    }
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.logo}>🏦 Natillera App</Text>
        <Text style={styles.subtitle}>Crea tu cuenta</Text>

        {[
          { key: 'nombre',   label: 'Nombre completo',    type: 'default' },
          { key: 'email',    label: 'Correo electrónico', type: 'email-address' },
          { key: 'password', label: 'Contraseña',         secure: true },
        ].map(({ key, label, type, secure }) => (
          <TextInput
            key={key}
            style={styles.input}
            placeholder={label}
            autoCapitalize={key === 'email' ? 'none' : 'words'}
            keyboardType={type ?? 'default'}
            secureTextEntry={secure}
            value={form[key]}
            onChangeText={set(key)}
          />
        ))}

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleRegister}
          disabled={loading}
        >
          <Text style={styles.buttonText}>{loading ? 'Creando...' : 'Registrarme'}</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Login')}>
          <Text style={styles.link}>¿Ya tienes cuenta? Inicia sesión</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container:      { flexGrow: 1, justifyContent: 'center', paddingHorizontal: 24, backgroundColor: '#f9fafb', paddingVertical: 40 },
  logo:           { fontSize: 28, fontWeight: 'bold', color: '#4f46e5', textAlign: 'center', marginBottom: 4 },
  subtitle:       { fontSize: 14, color: '#6b7280', textAlign: 'center', marginBottom: 32 },
  input:          { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, marginBottom: 12, fontSize: 15 },
  button:         { backgroundColor: '#4f46e5', borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginTop: 4 },
  buttonDisabled: { opacity: 0.5 },
  buttonText:     { color: '#fff', fontWeight: '600', fontSize: 15 },
  link:           { textAlign: 'center', marginTop: 20, color: '#4f46e5', fontSize: 14 },
})
