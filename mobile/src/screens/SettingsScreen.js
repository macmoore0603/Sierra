import React, { useState } from 'react';
import {
  View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator, Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSierra } from '../context/SierraContext';
import { colors } from '../theme';

export default function SettingsScreen() {
  const s = useSierra();
  const [url, setUrl] = useState(s.serverUrl);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const save = async () => {
    setSaving(true);
    try {
      const clean = await s.updateServerUrl(url);
      setUrl(clean);
      Alert.alert('Saved', `Connecting to ${clean}`);
    } finally {
      setSaving(false);
    }
  };

  const test = async () => {
    setTesting(true);
    try {
      await s.updateServerUrl(url);
      const ok = await s.refreshStatus();
      Alert.alert(
        ok ? 'Connected ✓' : 'Could not reach Sierra',
        ok
          ? `${s.serviceName || 'Sierra Backend'} is up at ${s.serverUrl}.`
          : `No response from ${s.serverUrl}.\n\nCheck:\n• Phone and computer on the same Wi-Fi\n• Desktop app running\n• Backend started with --host 0.0.0.0\n• Address is the computer's LAN IP:8000`
      );
    } finally {
      setTesting(false);
    }
  };

  const autoDetect = async () => {
    const found = await s.discover();
    if (found) {
      setUrl(found.url);
      Alert.alert('Found Sierra ✓', `Connected to ${found.name || 'Sierra'} at ${found.url}.`);
    } else {
      Alert.alert(
        'No Sierra found',
        'Scanned your Wi-Fi network but found no Sierra backend.\n\nMake sure the desktop app is running with --host 0.0.0.0 and that this phone is on the same Wi-Fi, then try again or enter the address manually.'
      );
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16, paddingBottom: 48 }}>
      <Text style={styles.section}>CONNECTION</Text>

      <TouchableOpacity
        style={[styles.btn, styles.autoBtn]}
        onPress={autoDetect}
        disabled={s.discovering}
      >
        {s.discovering ? (
          <>
            <ActivityIndicator color="#000" />
            <Text style={styles.autoBtnText}>
              {'  '}Scanning… {Math.round((s.discoveryProgress || 0) * 100)}%
            </Text>
          </>
        ) : (
          <>
            <Ionicons name="search" size={18} color="#000" />
            <Text style={styles.autoBtnText}>{'  '}Auto-detect Sierra on Wi-Fi</Text>
          </>
        )}
      </TouchableOpacity>

      <Text style={[styles.help, { marginTop: 8, marginBottom: 16 }]}>
        Finds your computer automatically — no IP needed. Or enter it manually below.
      </Text>

      <Text style={styles.label}>Sierra desktop server address</Text>
      <TextInput
        style={styles.input}
        value={url}
        onChangeText={setUrl}
        placeholder="http://192.168.1.100:8000"
        placeholderTextColor={colors.muted}
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
      />
      <Text style={styles.help}>
        Your computer's LAN IP and port 8000. Find the IP in macOS System Settings → Wi-Fi → Details,
        or run <Text style={styles.code}>ipconfig getifaddr en0</Text>.
      </Text>

      <View style={styles.btnRow}>
        <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={save} disabled={saving}>
          {saving ? <ActivityIndicator color="#000" /> : <Text style={styles.btnPrimaryText}>Save & Connect</Text>}
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.btnGhost]} onPress={test} disabled={testing}>
          {testing ? <ActivityIndicator color={colors.gold} /> : <Text style={styles.btnGhostText}>Test</Text>}
        </TouchableOpacity>
      </View>

      <Text style={[styles.section, { marginTop: 28 }]}>STATUS</Text>
      <Row label="Realtime link" value={s.connected ? 'Synced' : 'Offline'} ok={s.connected} />
      <Row label="REST /status" value={s.reachable === null ? 'Unknown' : s.reachable ? 'Up' : 'Down'} ok={s.reachable} />
      <Row label="Service" value={s.serviceName || '—'} />
      <Row label="Voice loop" value={s.voiceState} ok={s.voiceState === 'running'} />
      <Row label="Face auth" value={s.authenticated ? 'Authenticated' : 'Locked'} ok={s.authenticated} />

      <Text style={[styles.section, { marginTop: 28 }]}>ENABLE LAN ACCESS</Text>
      <View style={styles.infoCard}>
        <Ionicons name="information-circle" size={18} color={colors.gold} />
        <Text style={styles.infoText}>
          The desktop backend defaults to localhost-only. To let this phone connect, start it on the LAN:
          {'\n\n'}
          <Text style={styles.code}>cd backend{'\n'}python -m uvicorn server:app_socketio --host 0.0.0.0 --port 8000</Text>
          {'\n\n'}
          Both devices must be on the same Wi-Fi network.
        </Text>
      </View>

      <Text style={styles.footer}>Sierra Mobile · companion for the Sierra desktop app</Text>
    </ScrollView>
  );
}

function Row({ label, value, ok }) {
  const color = ok === undefined ? colors.textSecondary : ok ? colors.green : colors.red;
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={[styles.rowValue, { color }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  section: { color: colors.gold, fontSize: 13, fontWeight: '700', letterSpacing: 2, marginBottom: 12 },
  label: { color: colors.textSecondary, fontSize: 13, marginBottom: 6 },
  input: {
    backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1,
    borderRadius: 10, padding: 12, color: colors.text, fontSize: 15,
  },
  help: { color: colors.muted, fontSize: 12, marginTop: 8, lineHeight: 18 },
  code: { color: colors.gold, fontFamily: 'monospace', fontSize: 12 },
  btnRow: { flexDirection: 'row', marginTop: 16 },
  btn: { flex: 1, paddingVertical: 13, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  autoBtn: { flexDirection: 'row', backgroundColor: colors.gold, marginBottom: 4 },
  autoBtnText: { color: '#000', fontWeight: '700', fontSize: 15 },
  btnPrimary: { backgroundColor: colors.gold, marginRight: 10 },
  btnPrimaryText: { color: '#000', fontWeight: '700' },
  btnGhost: { borderColor: colors.gold, borderWidth: 1 },
  btnGhostText: { color: colors.gold, fontWeight: '700' },
  row: {
    flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 11,
    borderBottomColor: colors.border, borderBottomWidth: 1,
  },
  rowLabel: { color: colors.textSecondary, fontSize: 14 },
  rowValue: { fontSize: 14, fontWeight: '600' },
  infoCard: {
    flexDirection: 'row', backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1,
    borderRadius: 12, padding: 14,
  },
  infoText: { color: colors.textSecondary, fontSize: 13, lineHeight: 19, marginLeft: 10, flex: 1 },
  footer: { color: colors.muted, fontSize: 12, textAlign: 'center', marginTop: 30 },
});
