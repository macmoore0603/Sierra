import React, { useState, useRef, useEffect } from 'react';
import {
  View, TextInput, FlatList, Text, StyleSheet, TouchableOpacity,
  KeyboardAvoidingView, Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSierra } from '../context/SierraContext';
import { colors } from '../theme';

export default function ChatScreen() {
  const s = useSierra();
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const listRef = useRef(null);

  useEffect(() => {
    if (s.messages.length > 0) {
      setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 80);
    }
  }, [s.messages.length]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput('');
    setSending(true);
    try {
      await s.sendChat(text);
    } catch (e) {
      setInput(text); // restore the message so a failed send isn't lost
    } finally {
      setSending(false);
    }
  };

  const liveBadge = s.voiceState !== 'stopped';

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View style={styles.statusBar}>
        <View style={[styles.dot, { backgroundColor: s.connected ? colors.green : colors.red }]} />
        <Text style={styles.statusText}>
          {s.connected ? (liveBadge ? 'Synced · voice live' : 'Synced') : 'Offline'}
        </Text>
        {s.messages.length > 0 && (
          <TouchableOpacity onPress={s.clearMessages} style={styles.clearBtn}>
            <Text style={styles.clearText}>Clear</Text>
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        ref={listRef}
        data={s.messages}
        keyExtractor={(_, i) => i.toString()}
        contentContainerStyle={{ padding: 12, flexGrow: 1 }}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="chatbubbles-outline" size={48} color={colors.muted} />
            <Text style={styles.emptyText}>
              Talk to Sierra. Messages here sync with your computer's voice session in real time.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={[styles.bubble, item.role === 'user' ? styles.user : styles.sierra]}>
            {item.source === 'voice' && (
              <Ionicons
                name="mic"
                size={11}
                color={colors.muted}
                style={{ marginBottom: 2 }}
              />
            )}
            <Text style={styles.bubbleText}>{item.text}</Text>
          </View>
        )}
      />

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Message Sierra..."
          placeholderTextColor={colors.muted}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          editable={!sending}
        />
        <TouchableOpacity
          style={[styles.sendBtn, { opacity: input.trim() && !sending ? 1 : 0.4 }]}
          onPress={handleSend}
          disabled={!input.trim() || sending}
        >
          <Ionicons name={sending ? 'hourglass' : 'send'} size={20} color="#000" />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  statusBar: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 14, paddingVertical: 8,
    borderBottomColor: colors.border, borderBottomWidth: 1,
  },
  dot: { width: 8, height: 8, borderRadius: 4, marginRight: 8 },
  statusText: { color: colors.textSecondary, fontSize: 12, flex: 1 },
  clearBtn: { paddingHorizontal: 8, paddingVertical: 4 },
  clearText: { color: colors.gold, fontSize: 12, fontWeight: '600' },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 40 },
  emptyText: { color: colors.muted, textAlign: 'center', marginTop: 12, lineHeight: 20 },
  bubble: { maxWidth: '82%', padding: 12, marginVertical: 4, borderRadius: 14 },
  user: { alignSelf: 'flex-end', backgroundColor: colors.goldDark, borderBottomRightRadius: 2 },
  sierra: { alignSelf: 'flex-start', backgroundColor: colors.surfaceAlt, borderBottomLeftRadius: 2 },
  bubbleText: { color: colors.text, fontSize: 15, lineHeight: 21 },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', padding: 10,
    borderTopColor: colors.border, borderTopWidth: 1,
  },
  input: {
    flex: 1, backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1,
    paddingHorizontal: 14, paddingVertical: 10, marginRight: 8, borderRadius: 22, color: colors.text,
  },
  sendBtn: {
    backgroundColor: colors.gold, width: 44, height: 44, borderRadius: 22,
    alignItems: 'center', justifyContent: 'center',
  },
});
