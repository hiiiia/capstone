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
} from 'react-native';
import { Camera, CameraPermissionStatus, CameraDevice, PhotoFile, useCameraDevice } from 'react-native-vision-camera';

const App = () => {
  const device = useCameraDevice('back');
  const camera = useRef<Camera>(null);
  const [camera_state, set_camera_state] = useState('');
  const [capturedPhoto, setCapturedPhoto] = useState<PhotoFile | null>(null);

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
      const response = await fetch('http://192.168.25.39:5000/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.ok) {
        // 이미지가 성공적으로 서버에 전송됨
        console.log("Send");
      } else {
        // 전송 중에 오류가 발생함
        console.log("Send Error");
      }
    } catch (error) {
      console.log(error);
      // 네트워크 오류 등으로 인한 예외 처리
    }
  };

  return (
    <View style={styles.container}>
      <Camera
        ref={camera}
        style={styles.absoluteFill}
        device={device as CameraDevice}
        isActive={true}
        photo={true}
      />
      <Text style={styles.sectionTitle}>state: {camera_state}</Text>

      {/* 사진을 캡처하는 버튼 */}
      <Button title="Capture Photo" onPress={capturePhoto} />

      {/* 캡처된 사진 표시 */}
      {capturedPhoto && (
        <View>
          <Image source={{ uri: `file://${capturedPhoto.path}` }} style={styles.capturedImage} />
          <Text>Photo: {capturedPhoto.path}</Text>
        </View>
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
});

export default App;