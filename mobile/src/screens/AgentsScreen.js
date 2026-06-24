import React from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSierra } from '../context/SierraContext';
import { colors } from '../theme';

// Capabilities Sierra's orchestrator can route to (backend/agents + integrations
// + tools). Live runs stream into the activity feed via the tool_execution event.
const CAPABILITIES = [
  { key: 'web', icon: 'globe', name: 'Web Agent', desc: 'Browse & act on the web (Playwright)' },
  { key: 'cad', icon: 'cube', name: 'CAD Agent', desc: 'Generate 3D / CAD models' },
  { key: 'printer', icon: 'print', name: '3D Printer', desc: 'Monitor & control prints (Moonraker)' },
  { key: 'kasa', icon: 'bulb', name: 'Smart Home', desc: 'TP-Link Kasa lights & plugs' },
  { key: 'calendar', icon: 'calendar', name: 'Calendar', desc: 'Schedule & reminders' },
  { key: 'github', icon: 'logo-github', name: 'GitHub', desc: 'Repos, issues, code assist' },
];

function timeAgo(ts) {
  const sec = Math.floor((Date.now() - ts) / 1000);
  if (sec < 60) return `${sec}s ago`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  return `${Math.floor(min / 60)}h ago`;
}

export default function AgentsScreen() {
  const s = useSierra();

  return (
    <View style={styles.container}>
      <FlatList
        data={s.activity}
        keyExtractor={(item, i) => `${item.ts}-${i}`}
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        ListHeaderComponent={
          <View>
            <Text style={styles.section}>CAPABILITIES</Text>
            <View style={styles.grid}>
              {CAPABILITIES.map((c) => (
                <View key={c.key} style={styles.capCard}>
                  <Ionicons name={c.icon} size={22} color={colors.gold} />
                  <Text style={styles.capName}>{c.name}</Text>
                  <Text style={styles.capDesc}>{c.desc}</Text>
                </View>
              ))}
            </View>

            <Text style={[styles.section, { marginTop: 22 }]}>
              LIVE ACTIVITY {s.activity.length > 0 ? `(${s.activity.length})` : ''}
            </Text>
            {!s.connected && (
              <Text style={styles.note}>Not synced — connect in Settings to see live tool runs.</Text>
            )}
          </View>
        }
        ListEmptyComponent={
          s.connected ? (
            <Text style={styles.note}>
              No tool runs yet. When Sierra executes an action on your computer it appears here in real time.
            </Text>
          ) : null
        }
        renderItem={({ item }) => (
          <View style={styles.activityRow}>
            <Ionicons
              name={item.status === 'executing' ? 'flash' : 'checkmark-circle'}
              size={18}
              color={item.realtime ? colors.gold : colors.green}
            />
            <View style={{ flex: 1, marginLeft: 10 }}>
              <Text style={styles.toolName}>{item.tool || 'tool'}</Text>
              {item.args && (
                <Text style={styles.toolArgs} numberOfLines={2}>
                  {typeof item.args === 'string' ? item.args : JSON.stringify(item.args)}
                </Text>
              )}
            </View>
            <Text style={styles.toolTime}>{timeAgo(item.ts)}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  section: { color: colors.gold, fontSize: 13, fontWeight: '700', letterSpacing: 2, marginBottom: 12 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  capCard: {
    width: '48%', backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1,
    borderRadius: 12, padding: 14, marginBottom: 12,
  },
  capName: { color: colors.text, fontSize: 15, fontWeight: '700', marginTop: 8 },
  capDesc: { color: colors.muted, fontSize: 12, marginTop: 4, lineHeight: 16 },
  note: { color: colors.muted, fontSize: 13, fontStyle: 'italic', lineHeight: 19 },
  activityRow: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1,
    borderRadius: 10, padding: 12, marginBottom: 8,
  },
  toolName: { color: colors.text, fontSize: 14, fontWeight: '700' },
  toolArgs: { color: colors.muted, fontSize: 12, marginTop: 2 },
  toolTime: { color: colors.muted, fontSize: 11, marginLeft: 8 },
});
