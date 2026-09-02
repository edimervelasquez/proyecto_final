import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, 
  KeyboardAvoidingView, ScrollView, Platform, Alert, Modal 
} from 'react-native';

export default function RegisterScreen({ onNavigate, onRegisterSuccess }) {
  const [formData, setFormData] = useState({
    nombres: '', apellidos: '', tipoDoc: 'Cédula de Ciudadanía (CC)', numDoc: '',
    celular: '', direccion: '', email: '', password: ''
  });

  const [modalVisible, setModalVisible] = useState(false);

  const docOptions = [
    'Cédula de Ciudadanía (CC)',
    'Cédula de Extranjería (CE)',
    'Tarjeta de Identidad (TI)'
  ];

  const updateForm = (key, value) => setFormData(prev => ({ ...prev, [key]: value }));

  const handleRegister = () => {
    const { nombres, numDoc, email, password } = formData;
    if (!nombres.trim() || !numDoc.trim() || !email.trim() || !password.trim()) {
      return Alert.alert('Campos Incompletos', 'Por favor llena los campos obligatorios (*): Nombres, Documento, Correo y Contraseña.');
    }

    Alert.alert('Registro exitoso', 'Tu cuenta ha sido creada. Ahora puedes iniciar sesión.');
    if (onRegisterSuccess) {
      onRegisterSuccess(formData);
    }
    onNavigate('login');
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <View style={styles.topBar}>
        <TouchableOpacity style={styles.backButton} onPress={() => onNavigate('login')}>
          <Text style={styles.backButtonText}>← Volver</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Crear Cuenta</Text>
        <Text style={styles.subtitle}>Ingresa la información requerida</Text>

        <View style={styles.form}>
          <Text style={styles.label}>Nombres *</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej. Yojan Santiago"
            placeholderTextColor="#666"
            value={formData.nombres}
            onChangeText={v => updateForm('nombres', v)}
          />

          <Text style={styles.label}>Apellidos</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej. Castañeda"
            placeholderTextColor="#666"
            value={formData.apellidos}
            onChangeText={v => updateForm('apellidos', v)}
          />

          {/* Desplegable personalizado */}
          <Text style={styles.label}>Tipo de Documento *</Text>
          <TouchableOpacity 
            style={styles.selectButton} 
            onPress={() => setModalVisible(true)}
          >
            <Text style={styles.selectButtonText}>{formData.tipoDoc}</Text>
            <Text style={styles.arrowIcon}>▼</Text>
          </TouchableOpacity>

          <Text style={styles.label}>Número de Documento *</Text>
          <TextInput
            style={styles.input}
            placeholder="1000000000"
            placeholderTextColor="#666"
            keyboardType="numeric"
            value={formData.numDoc}
            onChangeText={v => updateForm('numDoc', v)}
          />

          <Text style={styles.label}>Número de Celular</Text>
          <TextInput
            style={styles.input}
            placeholder="3000000000"
            placeholderTextColor="#666"
            keyboardType="phone-pad"
            value={formData.celular}
            onChangeText={v => updateForm('celular', v)}
          />

          <Text style={styles.label}>Dirección</Text>
          <TextInput
            style={styles.input}
            placeholder="Calle 123 # 45 - 67"
            placeholderTextColor="#666"
            value={formData.direccion}
            onChangeText={v => updateForm('direccion', v)}
          />

          <Text style={styles.label}>Correo Electrónico *</Text>
          <TextInput
            style={styles.input}
            placeholder="ejemplo@sies.com"
            placeholderTextColor="#666"
            keyboardType="email-address"
            autoCapitalize="none"
            value={formData.email}
            onChangeText={v => updateForm('email', v)}
          />

          <Text style={styles.label}>Contraseña *</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            placeholderTextColor="#666"
            secureTextEntry
            value={formData.password}
            onChangeText={v => updateForm('password', v)}
          />

          <TouchableOpacity style={styles.button} onPress={handleRegister}>
            <Text style={styles.buttonText}>Registrarse</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Modal para seleccionar tipo de documento */}
      <Modal visible={modalVisible} transparent animationType="fade">
        <TouchableOpacity style={styles.modalOverlay} activeOpacity={1} onPress={() => setModalVisible(false)}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Selecciona Tipo de Documento</Text>
            {docOptions.map((item, index) => (
              <TouchableOpacity
                key={index}
                style={styles.modalOption}
                onPress={() => {
                  updateForm('tipoDoc', item);
                  setModalVisible(false);
                }}
              >
                <Text style={styles.modalOptionText}>{item}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0A0A' },
  topBar: { paddingTop: 45, paddingHorizontal: 20 },
  backButton: { paddingVertical: 8, paddingHorizontal: 12, alignSelf: 'flex-start' },
  backButtonText: { color: '#D4AF37', fontSize: 16, fontWeight: 'bold' },
  scrollContent: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 32, fontWeight: 'bold', color: '#D4AF37' },
  subtitle: { fontSize: 14, color: '#AAA', marginBottom: 20, marginTop: 4 },
  form: { width: '100%' },
  label: { color: '#FFFFFF', fontSize: 14, marginBottom: 6 },
  input: { backgroundColor: '#1A1A1A', borderWidth: 1, borderColor: '#333', borderRadius: 10, padding: 14, color: '#FFFFFF', fontSize: 16, marginBottom: 16 },
  selectButton: { backgroundColor: '#1A1A1A', borderWidth: 1, borderColor: '#333', borderRadius: 10, padding: 14, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  selectButtonText: { color: '#FFFFFF', fontSize: 16 },
  arrowIcon: { color: '#D4AF37', fontSize: 12 },
  button: { backgroundColor: '#D4AF37', paddingVertical: 16, borderRadius: 10, alignItems: 'center', marginTop: 12, marginBottom: 20 },
  buttonText: { color: '#000000', fontSize: 16, fontWeight: 'bold' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', alignItems: 'center', padding: 20 },
  modalContent: { backgroundColor: '#1A1A1A', width: '100%', borderRadius: 12, padding: 20, borderWidth: 1, borderColor: '#333' },
  modalTitle: { color: '#D4AF37', fontSize: 18, fontWeight: 'bold', marginBottom: 16, textAlign: 'center' },
  modalOption: { paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: '#2A2A2A' },
  modalOptionText: { color: '#FFFFFF', fontSize: 16, textAlign: 'center' }
});