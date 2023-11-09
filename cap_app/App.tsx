/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */


import React, { useEffect, useRef, useState } from 'react';

import {
  Linking,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  Button,
  Image,
  TextInput,
  TouchableHighlight,
  Alert 
} from 'react-native';
import { Camera, CameraPermissionStatus, CameraDevice, PhotoFile, useCameraDevice } from 'react-native-vision-camera';

const App = () => {
  const device = useCameraDevice('back');
  const camera = useRef<Camera>(null);
  const [connneting_state, set_connect_state] = useState('None');
  const [camera_state, set_camera_state] = useState('');
  const [capturedPhoto, setCapturedPhoto] = useState<PhotoFile | null>(null);


  const [login_state, set_login_state] = useState(false);
  const [username, setUsername] = useState(''); // 입력받은 사용자명
  const [password, setPassword] = useState(''); // 입력받은 비밀번호

  const [server_address, set_server_adderss] = useState('192.168.25.39:5000');
  useEffect(() => {
    async function getPermission() {
      const permission = await Camera.requestCameraPermission();
      set_camera_state(permission);

      if (permission === 'denied') await Linking.openSettings();
    }
    getPermission();
  }, []);

  // 사진 캡처 함수
  const capturePhoto = async () => {
    if (camera.current) {
      const photo = await camera.current.takePhoto({
        qualityPrioritization: 'speed',
        flash: 'off',
        enableShutterSound: false,
      });
      setCapturedPhoto(photo);

      // 이미지를 서버로 전송
      
      sendImageToServer(photo);
    }
  };

  function getCurrentTimeFormatted() {
    const currentDate = new Date();
  
    const year = currentDate.getFullYear().toString().slice(-2); // 년도의 끝 두 자리 (YY)
    const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // 월 (MM), 0을 1월로 처리
    const day = String(currentDate.getDate()).padStart(2, '0'); // 일 (DD)
    const hours = String(currentDate.getHours()).padStart(2, '0'); // 시간 (HH)
    const minutes = String(currentDate.getMinutes()).padStart(2, '0'); // 분 (MM)
    const seconds = String(currentDate.getSeconds()).padStart(2, '0'); // 초 (SS)
  
    return `${year}_${month}_${day}_${hours}_${minutes}_${seconds}`;
  }


  // 이미지를 서버로 전송하는 함수
  const sendImageToServer = async (image: PhotoFile) => {
    const formData = new FormData();
    
    formData.append('image', {
      uri: `file://${image.path}`,
      type: 'image/jpeg',
      name: `${getCurrentTimeFormatted()}.jpg`
    });

    try {
      const response = await fetch(`http://${server_address}/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      set_connect_state("NNNNN");
      if (response.ok) {
        // 이미지가 성공적으로 서버에 전송됨
        console.log("Send");
        set_connect_state("send");
      } else {
        // 전송 중에 오류가 발생함
        console.log("Send Error");
        set_connect_state("Send Error");

      }
    } catch (error) {
      console.log(error);
      set_connect_state(`${error}`);

      // 네트워크 오류 등으로 인한 예외 처리
    }
  };


  const handleLogin = () => {
    const userData = {
      user_id: username,
      password: password,
    };
  
    fetch(`http://${server_address}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // 로그인 성공 시, login_state를 true로 변경하여 화면을 전환
          Alert.alert('로그인 성공');
          set_login_state(true);
        } else {
          // 로그인 실패 처리 (예: 오류 메시지 표시)
          Alert.alert('로그인 실패', data.error);

        }
      })
      .catch((error) => {
        // 네트워크 오류 등으로 인한 예외 처리
        Alert.alert('네트워크 오류:', error);
      });
  };
  
  const handleSignup = () => {
    const userData = {
      user_id: username,
      password: password,
    };
  
    fetch(`http://${server_address}/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // 로그인 성공 시, login_state를 true로 변경하여 화면을 전환
          Alert.alert('가입 성공');
        } else {
          // 로그인 실패 처리 (예: 오류 메시지 표시)
          Alert.alert('가입 실패', data.error);

        }
      })
      .catch((error) => {
        // 네트워크 오류 등으로 인한 예외 처리
        Alert.alert('네트워크 오류:', error);
      });
  };

  return (
    <View style={styles.container}>
    {!login_state ? (
      // 로그인 창
      <View style={styles.loginContainer}>
  <TextInput
    style={styles.login_input}
    placeholder="Username"
    value={username}
    onChangeText={(text) => setUsername(text)}
  />
  <TextInput
    style={styles.login_input}
    placeholder="Password"
    secureTextEntry
    value={password}
    onChangeText={(text) => setPassword(text)}
  />
  <TouchableHighlight
    style={styles.login_summit_button}
    onPress={handleLogin}
  >
    <Text style={styles.login_summit_button_text}>Login</Text>
  </TouchableHighlight>
  <TouchableHighlight
    style={styles.signup_button}
    onPress={handleSignup}
  >
    <Text style={styles.signup_button_text}>Sign Up</Text>
  </TouchableHighlight>
</View>
    ) : (
      // 카메라 및 기타 UI 요소
      <>
        <Camera
          ref={camera}
          style={styles.absoluteFill}
          device={device as CameraDevice}
          isActive={true}
          photo={true}
        />
        <Text style={styles.sectionTitle}>state: {camera_state}</Text>
        <Button title="Capture Photo" onPress={capturePhoto} />
        <Text>Server connect : {`${connneting_state}`} Login ID : {`${username}`}</Text>
        {capturedPhoto && (
          <View>
            <Image source={{ uri: `file://${capturedPhoto.path}` }} style={styles.capturedImage} />
          </View>
        )}
      </>
    )}
  </View>
  );
};

const styles = StyleSheet.create({
  absoluteFill: {
    flex: 1,
    position: 'absolute',
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
  },
  container: {
    flex: 1,
    backgroundColor: 'white',
  },
  capturedImage: {
    width: 200,
    height: 200,
    resizeMode: 'cover',
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: 'red',
    position: 'absolute',
    top: 10,
  },

  loginContainer: {
    zIndex : 3,
    marginTop: 20,
    paddingHorizontal: 20,
  },
  login_input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
  login_summit_button: {
    backgroundColor: 'blue',
    color: 'white',
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  login_summit_button_text: {
    color: 'white',
    fontSize: 18,
  },

  signup_button: {
    backgroundColor: 'lightgray',
    color: 'white',
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  signup_button_text: {
    color: 'white',
    fontSize: 18,
  },
});

export default App;