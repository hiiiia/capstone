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
  Alert,
  Modal
} from 'react-native';
import { CameraRoll } from "@react-native-camera-roll/camera-roll";
import { Camera, CameraPermissionStatus, CameraDevice, PhotoFile, useCameraDevice, VideoFile } from 'react-native-vision-camera';

const App = () => {
  const device = useCameraDevice('back');
  const camera = useRef<Camera>(null);
  const [connneting_state, set_connect_state] = useState('None');
  const [camera_state, set_camera_state] = useState('');
  const [capturedPhoto, setCapturedPhoto] = useState<PhotoFile | null>(null);


  const [login_state, set_login_state] = useState(false);
  const [username, setUsername] = useState(''); // 입력받은 사용자명
  const [password, setPassword] = useState(''); // 입력받은 비밀번호

  const [server_address, set_server_address] = useState('192.168.4.70:5000');
  const [inputServerAddress, setInputServerAddress] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  
  const handleUpdateServerAddress = () => {
    set_server_address(inputServerAddress);
    setIsModalVisible(false);
  };

  useEffect(() => {
    async function getPermission() {
      const permission = await Camera.requestCameraPermission();
      set_camera_state(permission);

      if (permission === 'denied') await Linking.openSettings();
    }
    getPermission();
  }, []);

  // 비디오 녹화
  const recodevideo = async () => {
    if (camera.current) {
      try {
        camera.current.startRecording({
          //videoCodec: 'h265',
          //videoBitRate: 'high',
          onRecordingFinished: (video) => { sendVideoToServer(video) },
          onRecordingError: (error) => console.error(error),
        });
      } catch (error) {
        console.error("Error starting video recording:", error);
      }
    }
  };

      // 비디오 녹화
      const recode_predict_video = async () => {
        if (camera.current) {
          try {
            camera.current.startRecording({
              //videoCodec: 'h265',
              //videoBitRate: 'high',
              onRecordingFinished: (video) => { send_predict_VideoToServer(video) },
              onRecordingError: (error) => console.error(error),
            });
          } catch (error) {
            console.error("Error starting video recording:", error);
          }
        }
      };
  
      
  const stop_recodevideo = async () => {
    if (camera.current) {
      const video = await camera.current.stopRecording();
    }
  };




  // 사진 캡처 함수
  const capturePhoto = async () => {
    if (camera.current) {
      const photo = await camera.current.takePhoto({
        qualityPrioritization: 'speed',
        flash: 'off',
        enableShutterSound: false,
      });

      // 이미지를 서버로 전송

      sendImageToServer(photo);
    }
  };

  // 사진 predict 함수
  const capturePhoto_to_predict = async () => {
    if (camera.current) {
      const photo = await camera.current.takePhoto({
        qualityPrioritization: 'speed',
        flash: 'off',
        enableShutterSound: false,
      });

      // 이미지를 서버로 전송

      sendImageTopredict(photo);
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


    // 비디오 서버로 전송하는 함수
    const sendVideoToServer = async (video: VideoFile) => {
      const path = video.path;
    
      try {
        //console.log(`${path}`);
        // Save the video file using CameraRoll
        await CameraRoll.save(`file://${path}`, {
          type: 'video',
        });
    
        const formData = new FormData();
    
        // Append the video file to the formData
        formData.append('video', {
          uri: `file://${path}`,
          type: 'video/mp4',  // Adjust the type based on your video file format
          name: `${getCurrentTimeFormatted()}.mp4`,  // Adjust the extension based on your video file format
        });
    
        const response = await fetch(`http://${server_address}/upload_video`, {
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
    
        set_connect_state("NNNNN");
    
        if (response.ok) {
          // Video successfully sent to the server
          console.log("Send");
          set_connect_state("send");
        } else {
          // Error occurred during the transmission
          console.log("Send Error");
          set_connect_state("Send Error");
        }
      } catch (error) {
        console.log(error);
        set_connect_state(`${error}`);
        // Network error or other exceptions
      }
    };

        // 비디오 서버로 전송하는 함수
        const send_predict_VideoToServer = async (video: VideoFile) => {
          const path = video.path;
        
          try {
            //console.log(`${path}`);
            // Save the video file using CameraRoll
            await CameraRoll.save(`file://${path}`, {
              type: 'video',
            });
        
            const formData = new FormData();
        
            // Append the video file to the formData
            formData.append('video', {
              uri: `file://${path}`,
              type: 'video/mp4',  // Adjust the type based on your video file format
              name: `${getCurrentTimeFormatted()}.mp4`,  // Adjust the extension based on your video file format
            });
        
            const response = await fetch(`http://${server_address}/predict`, {
              method: 'POST',
              body: formData,
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            });
        
            set_connect_state("NNNNN");
        
            if (response.ok) {
              // Video successfully sent to the server
              console.log("Send");
              set_connect_state("send");
            } else {
              // Error occurred during the transmission
              console.log("Send Error");
              set_connect_state("Send Error");
            }
          } catch (error) {
            console.log(error);
            set_connect_state(`${error}`);
            // Network error or other exceptions
          }
        };
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

  const sendImageTopredict = async (image: PhotoFile) => {
    const formData = new FormData();

    formData.append('image', {
      uri: `file://${image.path}`,
      type: 'image/jpeg',
      name: `${getCurrentTimeFormatted()}.jpg`
    });

    try {
      const response = await fetch(`http://${server_address}/predict`, {
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
        const result = await response.json(); // 수정된 부분
        //console.log(result.message); // 서버에서 받은 데이터 출력
        console.log(result.result); // 서버에서 받은 데이터 출력
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
            placeholderTextColor="gray"

            value={username}
            onChangeText={(text) => setUsername(text)}
          />
          <TextInput
            style={styles.login_input}
            placeholder="Password"
            placeholderTextColor="gray"
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
          

          <View>
            <TouchableHighlight
              style={styles.updateServerButton}
              onPress={() => setIsModalVisible(true)}
              disabled={login_state}
            >
              <Text style={styles.updateServerButtonText}>Update Server</Text>
            </TouchableHighlight>
          </View>

          {/* Modal for updating the server address */}
          <Modal
            animationType="slide"
            transparent={true}
            visible={isModalVisible}
            onRequestClose={() => setIsModalVisible(false)}
          >
            <View style={styles.modalContainer}>
              <TextInput
                style={styles.modalInput}
                placeholder="192.168.4.31:5000"
                placeholderTextColor="gray"
                value={inputServerAddress}
                onChangeText={(text) => setInputServerAddress(text)}
              />
              <Button title="Update" onPress={handleUpdateServerAddress} />
              <Button
                title="Cancel"
                onPress={() => setIsModalVisible(false)}
              />
            </View>
          </Modal>

        </View>

        
      ) : (
        // 카메라 및 기타 UI 요소
        <>
          <Camera
            ref={camera}
            style={styles.absoluteFill}
            device={device as CameraDevice}
            isActive={true}
            video={true}
            // photo={true}
          />
          <Text style={styles.sectionTitle}>state: {camera_state}</Text>
          <Button title="Recode Video" onPress={recodevideo} />
          <Button title="Recode Predict Video" onPress={recode_predict_video} />
          <Button title="Stop Recode Video" onPress={stop_recodevideo} color={'lightcoral'} />
          {/* <Button title="Capture Photo" onPress={capturePhoto} />
          <Button title="Capture Photo predict" onPress={capturePhoto_to_predict} /> */}
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
    color : 'black',
    zIndex: 3,
    marginTop: 20,
    paddingHorizontal: 20,
  },
  login_input: {
    color : 'black',
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
    color: 'black',
    fontSize: 18,
  },

  updateServerButton: {
    backgroundColor : "gray",
    position: 'absolute',
    bottom: 0,
    right: 0,
    padding: 10,
    // Styles for the "Update Server" button
  },
  updateServerButtonText: {
    color: 'black',
    // Styles for the text inside the "Update Server" button
  },
  modalContainer: {
    color : 'black',

    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    // Styles for the modal container
  },
  modalInput: {
    // Styles for the text input inside the modal
    color : 'black',

    borderColor: 'gray',
    borderWidth: 1,
    padding: 10,
    marginBottom: 10,
  },
});

export default App;
