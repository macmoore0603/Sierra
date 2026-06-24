import React, { useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSierra } from '../context/SierraContext';
import StatusPill from '../components/StatusPill';
import { colors } from '../theme';

export default function DashboardScreen() {
  const s = useSierra();
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await s.refreshStatus();
    setRefreshing(false);
  }, [s]);

  const voiceTone = s.voiceState === 'running' ? 'green'
    : s.voiceState === 'paused' ? 'gold' : 'red';

  const voiceLabel = s.voiceState === 'running' ? 'LIVE'
    : s.voiceState === 'paused' ? 'PAUSED' : 'OFF';

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.gold} />
      }
    >
      <Text style={styles.title}>SIERRA</Text>
      <Text style={styles.subtitle}>{s.serverUrl}</Text>

      {/* Connection / system pills */}
      <View style={styles.pillRow}>
        <StatusPill label="LINK" value={s.connected ? 'SYNCED' : 'OFFLINE'} tone={s.connected ? 'green' : 'red'} />
        <StatusPill label="API" value={s.reachable === null ? '…' : s.reachable ? 'UP' : 'DOWN'} tone={s.reachable ? 'green' : 'red'} />
        <StatusPill label="HEY SIERRA" value={voiceLabel} tone={voiceTone} />
        <StatusPill label="AUTH" value={s.authenticated ? 'OK' : 'LOCKED'} tone={s.authenticated ? 'green' : 'red'} />
      </View>

      {/* Voice loop control — drives the desktop app remotely */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Voice Loop</Text>
        <Text style={styles.cardBody}>
          Start, pause, or stop the live "Hey Sierra" session on your computer.
        </Text>
        <View style={styles.btnRow}>
          {s.voiceState === 'stopped' ? (
            <ActionButton icon="mic" label="Start" onPress={s.startVoice} disabled={!s.connected} primary />
          ) : (
            <>
              {s.voiceState === 'paused' ? (
                <ActionButton icon="play" label="Resume" onPress={s.resumeVoice} primary />
              ) : (
                <ActionButton icon="pause" label="Pause" onPress={s.pauseVoice} />
              )}
              <ActionButton icon="stop" label="Stop" onPress={s.stopVoice} tone="red" />
            </>
          )}
        </View>
      </View>

      {/* Local router intent hint */}
      {s.lastRoute && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Last Intent</Text>
          <Text style={styles.routeFn}>{s.lastRoute.function || 'unknown'}</Text>
          <Text style={styles.cardBody}>
            confidence {(Number(s.lastRoute.confidence || 0) * 100).toFixed(0)}%
            {s.lastRoute.latency_ms != null ? ` · ${Math.round(s.lastRoute.latency_ms)}ms` : ''}
          </Text>
        </View>
      )}

      {/* Smart home */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Smart Home ({s.devices.length})</Text>
        {s.devices.length === 0 ? (
          <Text style={styles.cardBody}>No Kasa devices reported yet.</Text>
        ) : (
          s.devices.map((d, i) => (
            <View key={i} style={styles.deviceRow}>
              <Ionicons
                name="bulb"
                size={16}
                color={d.is_on || d.state ? colors.gold : colors.muted}
              />
              <Text style={styles.deviceName}>{d.alias || d.name || d.ip}</Text>
              <Text style={[styles.deviceState, { color: d.is_on || d.state ? colors.green : colors.muted }]}>
                {d.is_on || d.state ? 'ON' : 'OFF'}
              </Text>
            </View>
          ))
        )}
      </View>

      {/* 3D printer */}
      {s.printStatus && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>3D Printer</Text>
          <Text style={styles.cardBody}>
            {s.printStatus.state || 'idle'}
            {s.printStatus.progress != null
              ? ` · ${Math.round(Number(s.printStatus.progress) * (s.printStatus.progress <= 1 ? 100 : 1))}%`
              : ''}
          </Text>
        </View>
      )}

      {/* Active project */}
      {s.project && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Active Project</Text>
          <Text style={styles.cardBody}>{s.project}</Text>
        </View>
      )}

      {s.lastError && (
        <View style={[styles.card, { borderColor: colors.red }]}>
          <Text style={[styles.cardTitle, { color: colors.red }]}>Last Error</Text>
          <Text style={styles.cardBody}>{s.lastError}</Text>
        </View>
      )}

      {!s.connected && (
        <Text style={styles.hint}>
          Not synced. Open Settings and set the server address to your computer's LAN IP,
          and make sure the desktop backend runs with --host 0.0.0.0.
        </Text>
      )}
    </ScrollView>
  );
}

function ActionButton({ icon, label, onPress, primary, tone, disabled }) {
  const bg = tone === 'red' ? colors.red : primary ? colors.gold : colors.surfaceAlt;
  const fg = primary || tone === 'red' ? '#000' : colors.text;
  return (
    <TouchableOpacity
      style={[styles.btn, { backgroundColor: bg, opacity: disabled ? 0.4 : 1 }]}
      onPress={onPress}
      disabled={disabled}
    >
      <Ionicons name={icon} size={18} color={fg} />
      <Text style={[styles.btnText, { color: fg }]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  title: { color: colors.gold, fontSize: 34, fontWeight: '800', letterSpacing: 6 },
  subtitle: { color: colors.muted, fontSize: 12, marginTop: 2, marginBottom: 16 },
  pillRow: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 4 },
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 14,
    padding: 16,
    marginTop: 12,
  },
  cardTitle: { color: colors.gold, fontSize: 14, fontWeight: '700', letterSpacing: 1, marginBottom: 6 },
  cardBody: { color: colors.textSecondary, fontSize: 14, lineHeight: 20 },
  routeFn: { color: colors.text, fontSize: 18, fontWeight: '700' },
  btnRow: { flexDirection: 'row', marginTop: 12 },
  btn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    paddingVertical: 10, paddingHorizontal: 18, borderRadius: 10, marginRight: 10,
  },
  btnText: { fontWeight: '700', marginLeft: 8 },
  deviceRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6 },
  deviceName: { color: colors.text, fontSize: 14, marginLeft: 10, flex: 1 },
  deviceState: { fontSize: 12, fontWeight: '700' },
  hint: { color: colors.muted, fontSize: 13, lineHeight: 19, marginTop: 20, fontStyle: 'italic' },
});
