import React, { useState } from 'react';
import { 
  StyleSheet, Text, View, TextInput, TouchableOpacity, 
  KeyboardAvoidingView, ScrollView, Platform, Alert, ImageBackground 
} from 'react-native';

export default function LoginScreen({ onNavigate, registeredUser }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    if (!email.trim() || !password.trim()) {
      return Alert.alert('Error', 'Por favor ingresa tu correo y contraseña.');
    }

    if (registeredUser && email.toLowerCase() === registeredUser.email.toLowerCase() && password === registeredUser.password) {
      Alert.alert('¡Bienvenido!', `Hola ${registeredUser.nombres}, has iniciado sesión correctamente.`);
    } else if (!registeredUser) {
      Alert.alert('Error de inicio de sesión', 'No hay usuarios registrados aún. Por favor regístrate primero.');
    } else {
      Alert.alert('Credenciales incorrectas', 'El correo o la contraseña no coinciden.');
    }
  };

  const handleForgotPassword = () => {
    Alert.alert('Restablecer contraseña', 'Proceso para crear una nueva contraseña enviado.');
  };

  return (
    <ImageBackground 
      source={require('../assets/background.png')} 
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <View style={styles.overlay}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
          <View style={styles.topBar}>
            <TouchableOpacity style={styles.backButton} onPress={() => onNavigate('welcome')}>
              <Text style={styles.backButtonText}>← Volver</Text>
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
            <Text style={styles.title}>Iniciar Sesión</Text>
            <Text style={styles.subtitle}>Ingresa tus credenciales para continuar</Text>

            <View style={styles.form}>
              <Text style={styles.label}>Correo Electrónico</Text>
              <TextInput
                style={styles.input}
                placeholder="ejemplo@sies.com"
                placeholderTextColor="#888"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />

              <Text style={styles.label}>Contraseña</Text>
              <TextInput
                style={styles.input}
                placeholder="••••••••"
                placeholderTextColor="#888"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
              />

              {/* Enlace para recuperar contraseña */}
              <TouchableOpacity onPress={handleForgotPassword} style={styles.forgotContainer}>
                <Text style={styles.forgotText}>¿Se te olvidó la contraseña? <Text style={styles.linkHighlight}>Crea una nueva.</Text></Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.button} onPress={handleLogin}>
                <Text style={styles.buttonText}>Ingresar</Text>
              </TouchableOpacity>

              <View style={styles.footerContainer}>
                <Text style={styles.footerText}>¿No tienes cuenta? </Text>
                <TouchableOpacity onPress={() => onNavigate('register')}>
                  <Text style={styles.linkText}>Registrate</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.65)', // Capa de opacidad para asegurar la legibilidad del texto
  },
  container: { 
    flex: 1,
  },
  topBar: { 
    paddingTop: 45, 
    paddingHorizontal: 20, 
  },
  backButton: { 
    paddingVertical: 8, 
    paddingHorizontal: 12, 
    alignSelf: 'flex-start' 
  },
  backButtonText: { 
    color: '#D4AF37', 
    fontSize: 16, 
    fontWeight: 'bold' 
  },
  scrollContent: { 
    flexGrow: 1, 
    justifyContent: 'center', 
    padding: 24 
  },
  title: { 
    fontSize: 32, 
    fontWeight: 'bold', 
    color: '#D4AF37' 
  },
  subtitle: { 
    fontSize: 14, 
    color: '#CCC', 
    marginBottom: 32, 
    marginTop: 4 
  },
  form: { 
    width: '100%' 
  },
  label: { 
    color: '#FFFFFF', 
    fontSize: 14, 
    marginBottom: 8 
  },
  input: { 
    backgroundColor: 'rgba(26, 26, 26, 0.85)', 
    borderWidth: 1, 
    borderColor: '#444', 
    borderRadius: 10, 
    padding: 14, 
    color: '#FFFFFF', 
    fontSize: 16, 
    marginBottom: 16 
  },
  forgotContainer: {
    marginBottom: 20,
    alignItems: 'flex-end',
  },
  forgotText: {
    color: '#AAA',
    fontSize: 13,
  },
  linkHighlight: {
    color: '#D4AF37',
    fontWeight: 'bold',
  },
  button: { 
    backgroundColor: '#D4AF37', 
    paddingVertical: 16, 
    borderRadius: 10, 
    alignItems: 'center', 
    marginTop: 10 
  },
  buttonText: { 
    color: '#000000', 
    fontSize: 16, 
    fontWeight: 'bold' 
  },
  footerContainer: { 
    flexDirection: 'row', 
    justifyContent: 'center', 
    marginTop: 24 
  },
  footerText: { 
    color: '#FFFFFF' 
  },
  linkText: { 
    color: '#D4AF37', 
    fontWeight: 'bold' 
  }
});