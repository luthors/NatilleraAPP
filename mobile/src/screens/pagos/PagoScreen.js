import { useState, useEffect } from 'react'
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, Alert, ScrollView, ActivityIndicator, Platform,
} from 'react-native'
import { Picker } from '@react-native-picker/picker'
import api from '../../services/api'

const METODOS = ['TRANSFERENCIA', 'EFECTIVO', 'PSE']

export default function PagoScreen({ route, navigation }) {
  const { natilleraId } = route.params ?? {}
  const [periodos, setPeriodos]   = useState([])
  const [loadingP, setLoadingP]   = useState(true)
  const [form, setForm]           = useState({ periodo_id: null, metodo: 'TRANSFERENCIA', referencia: '' })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get(`/natilleras/${natilleraId}/periodos`)
      .then(({ data }) => {
        const abiertos = data.filter((p) => p.estado !== 'CERRADO')
        setPeriodos(abiertos)
        if (abiertos.length) setForm((f) => ({ ...f, periodo_id: abiertos[0].id }))
      })
      .catch(() => Alert.alert('Error', 'No se pudieron cargar los períodos'))
      .finally(() => setLoadingP(false))
  }, [natilleraId])

  const handleSubmit = async () => {
    if (!form.periodo_id) {
      Alert.alert('Error', 'Selecciona un período')
      return
    }
    setSubmitting(true)
    try {
      await api.post(`/natilleras/${natilleraId}/mis-pagos`, {
        periodo_id: form.periodo_id,
        metodo:     form.metodo,
        referencia: form.referencia || undefined,
      })
      Alert.alert('Éxito', 'Pago registrado. Queda pendiente de confirmación por el administrador.', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ])
    } catch (err) {
      Alert.alert('Error', err.response?.data?.detail ?? 'Error al registrar pago')
    } finally {
      setSubmitting(false)
    }
  }

  if (loadingP) return <ActivityIndicator style={{ flex: 1 }} size="large" color="#4f46e5" />

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Registrar pago</Text>

      <Text style={styles.label}>Período</Text>
      <View style={styles.pickerWrapper}>
        <Picker
          selectedValue={form.periodo_id}
          onValueChange={(v) => setForm((f) => ({ ...f, periodo_id: v }))}
          style={styles.picker}
        >
          {periodos.map((p) => (
            <Picker.Item key={p.id} label={p.nombre} value={p.id} />
          ))}
        </Picker>
      </View>

      <Text style={styles.label}>Método de pago</Text>
      <View style={styles.pickerWrapper}>
        <Picker
          selectedValue={form.metodo}
          onValueChange={(v) => setForm((f) => ({ ...f, metodo: v }))}
          style={styles.picker}
        >
          {METODOS.map((m) => <Picker.Item key={m} label={m} value={m} />)}
        </Picker>
      </View>

      <Text style={styles.label}>Referencia (opcional)</Text>
      <TextInput
        style={styles.input}
        placeholder="Ej. TRX-20260526-001"
        value={form.referencia}
        onChangeText={(v) => setForm((f) => ({ ...f, referencia: v }))}
      />

      <TouchableOpacity
        style={[styles.button, submitting && styles.buttonDisabled]}
        onPress={handleSubmit}
        disabled={submitting}
      >
        <Text style={styles.buttonText}>{submitting ? 'Registrando...' : 'Registrar pago'}</Text>
      </TouchableOpacity>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container:     { flexGrow: 1, padding: 24, backgroundColor: '#f9fafb' },
  title:         { fontSize: 22, fontWeight: 'bold', color: '#111827', marginBottom: 24 },
  label:         { fontSize: 13, fontWeight: '600', color: '#374151', marginBottom: 4, marginTop: 12 },
  pickerWrapper: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, marginBottom: 4, overflow: 'hidden' },
  picker:        { height: Platform.OS === 'ios' ? 180 : 52 },
  input:         { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, fontSize: 15 },
  button:        { backgroundColor: '#4f46e5', borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginTop: 28 },
  buttonDisabled:{ opacity: 0.5 },
  buttonText:    { color: '#fff', fontWeight: '600', fontSize: 15 },
})
