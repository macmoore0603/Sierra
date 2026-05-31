import React, { useState } from 'react';
import { View, TextInput, Button, FlatList, Text, StyleSheet } from 'react-native';
import { sendMessage } from '../services/SierraAPI';
import { theme } from '../theme';

export default function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    const response = await sendMessage(input);
    setMessages(prev => [...prev, { role: 'sierra', text: response }]);
    setInput('');
  };

  return (
    <View style={theme.container}>
      <Text style={theme.header}>Sierra</Text>
      <FlatList
        data={messages}
        keyExtractor={(_, i) => i.toString()}
        renderItem={({ item }) => (
          <Text style={[styles.message, item.role === 'user' ? styles.user : styles.sierra]}>
            {item.text}
          </Text>
        )}
      />
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Message Sierra..."
          placeholderTextColor="#888"
        />
        <Button title="Send" onPress={handleSend} color={theme.colors.gold} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  message: { padding: 10, marginVertical: 4, borderRadius: 8 },
  user: { alignSelf: 'flex-end', backgroundColor: '#333' },
  sierra: { alignSelf: 'flex-start', backgroundColor: '#222' },
  inputRow: { flexDirection: 'row', alignItems: 'center' },
  input: { flex: 1, borderWidth: 1, borderColor: '#555', padding: 10, marginRight: 8, borderRadius: 8, color: '#fff' },
});