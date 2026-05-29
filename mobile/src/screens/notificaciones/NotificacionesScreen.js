import { useEffect, useState } from 'react'
import {
  View, Text, FlatList, StyleSheet,
  ActivityIndicator, TouchableOpacity, RefreshControl,
} from 'react-native'
import api from '../../services/api'

const TIPO_ICON = {
  pago_confirmado:    '✅',
  pago_rechazado:     '❌',
  pago_revertido:     '↩️',
  mora:               '⚠️',
  distribucion:       '💰',
  invitacion:         '📬',
  default:            '🔔',
}

function NotificacionItem({ item }) {
  const icon = TIPO_ICON[item.tipo] ?? TIPO_ICON.default
  const date = new Date(item.created_at).toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
  return (
    <View style={[styles.item, !item.leida && styles.itemUnread]}>
      <Text style={styles.icon}>{icon}</Text>
      <View style={styles.itemBody}>
        <Text style={styles.itemTitle}>{item.titulo}</Text>
        <Text style={styles.itemMsg} numberOfLines={2}>{item.mensaje}</Text>
        <Text style={styles.itemDate}>{date}</Text>
      </View>
      {!item.leida && <View style={styles.dot} />}
    </View>
  )
}

export default function NotificacionesScreen() {
  const [items, setItems]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError]       = useState(null)

  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true); else setLoading(true)
    try {
      // Backend endpoint: GET /usuarios/me/notificaciones (not yet in current router,
      // placeholder call — will be wired when ISSUE-40 endpoint is added)
      const { data } = await api.get('/usuarios/me/notificaciones')
      setItems(data)
      setError(null)
    } catch {
      setError('No se pudieron cargar las notificaciones')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const markAllRead = async () => {
    try {
      await api.post('/usuarios/me/notificaciones/leer-todas')
      setItems((prev) => prev.map((n) => ({ ...n, leida: true })))
    } catch { /* silent */ }
  }

  if (loading) return <ActivityIndicator style={{ flex: 1 }} size="large" color="#4f46e5" />

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Notificaciones</Text>
        {items.some((n) => !n.leida) && (
          <TouchableOpacity onPress={markAllRead}>
            <Text style={styles.markAll}>Marcar todas leídas</Text>
          </TouchableOpacity>
        )}
      </View>

      {error && <Text style={styles.errorText}>{error}</Text>}

      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => <NotificacionItem item={item} />}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => fetchData(true)} />}
        ListEmptyComponent={<Text style={styles.empty}>Sin notificaciones por ahora.</Text>}
        contentContainerStyle={{ paddingBottom: 40 }}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: '#f9fafb', paddingHorizontal: 16, paddingTop: 48 },
  header:     { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  title:      { fontSize: 22, fontWeight: 'bold', color: '#111827' },
  markAll:    { fontSize: 12, color: '#4f46e5', fontWeight: '600' },
  item:       { flexDirection: 'row', backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 10, alignItems: 'flex-start', shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 4, elevation: 1 },
  itemUnread: { borderLeftWidth: 3, borderLeftColor: '#4f46e5' },
  icon:       { fontSize: 22, marginRight: 12, marginTop: 2 },
  itemBody:   { flex: 1 },
  itemTitle:  { fontSize: 14, fontWeight: '600', color: '#111827', marginBottom: 2 },
  itemMsg:    { fontSize: 13, color: '#6b7280', marginBottom: 4 },
  itemDate:   { fontSize: 11, color: '#9ca3af' },
  dot:        { width: 8, height: 8, borderRadius: 4, backgroundColor: '#4f46e5', marginTop: 6 },
  empty:      { textAlign: 'center', color: '#9ca3af', marginTop: 40 },
  errorText:  { color: '#dc2626', marginBottom: 8 },
})
