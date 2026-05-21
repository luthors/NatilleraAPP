import { useEffect, useState } from 'react'
import {
  View, Text, FlatList, TouchableOpacity,
  StyleSheet, ActivityIndicator, RefreshControl,
} from 'react-native'
import api from '../../services/api'

const ESTADO_COLOR = {
  ACTIVA:   '#16a34a',
  PENDIENTE:'#d97706',
  CERRADA:  '#6b7280',
  ARCHIVADA:'#9ca3af',
}

function NatilleraItem({ item, onPress }) {
  const color = ESTADO_COLOR[item.estado] ?? '#6b7280'
  return (
    <TouchableOpacity style={styles.card} onPress={() => onPress(item)}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardName}>{item.nombre}</Text>
        <View style={[styles.badge, { backgroundColor: color }]}>
          <Text style={styles.badgeText}>{item.estado}</Text>
        </View>
      </View>
      <Text style={styles.cardMonto}>
        {new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(item.monto_por_periodo)}
        <Text style={styles.cardPeriodo}> / {item.periodicidad.toLowerCase()}</Text>
      </Text>
    </TouchableOpacity>
  )
}

export default function NatillerasScreen({ navigation }) {
  const [natilleras, setNatilleras] = useState([])
  const [loading, setLoading]       = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError]           = useState(null)

  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true); else setLoading(true)
    try {
      const { data } = await api.get('/natilleras')
      setNatilleras(data)
      setError(null)
    } catch (e) {
      setError(e.response?.data?.detail ?? 'Error al cargar natilleras')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  if (loading) return <ActivityIndicator style={{ flex: 1 }} size="large" color="#4f46e5" />

  if (error) return (
    <View style={styles.center}>
      <Text style={styles.errorText}>{error}</Text>
      <TouchableOpacity onPress={() => fetchData()}><Text style={styles.link}>Reintentar</Text></TouchableOpacity>
    </View>
  )

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mis Natilleras</Text>
      <FlatList
        data={natilleras}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <NatilleraItem item={item} onPress={(n) => navigation.navigate('NatilleraDetail', { natilleraId: n.id })} />
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchData(true)} />}
        ListEmptyComponent={<Text style={styles.empty}>No tienes natilleras aún.</Text>}
        contentContainerStyle={{ paddingBottom: 40 }}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb', paddingHorizontal: 16, paddingTop: 48 },
  title:     { fontSize: 22, fontWeight: 'bold', color: '#111827', marginBottom: 16 },
  card:      { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  cardHeader:{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  cardName:  { fontSize: 16, fontWeight: '600', color: '#111827', flex: 1 },
  badge:     { borderRadius: 999, paddingHorizontal: 8, paddingVertical: 2 },
  badgeText: { color: '#fff', fontSize: 11, fontWeight: '600' },
  cardMonto: { fontSize: 18, fontWeight: 'bold', color: '#4f46e5' },
  cardPeriodo:{ fontSize: 13, fontWeight: 'normal', color: '#6b7280' },
  empty:     { textAlign: 'center', color: '#9ca3af', marginTop: 40 },
  center:    { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorText: { color: '#dc2626', marginBottom: 12 },
  link:      { color: '#4f46e5', fontWeight: '600' },
})
