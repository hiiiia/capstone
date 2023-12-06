사용한 패키지 -->
npm install react-native-vision-camera --save

# cd android후 
./gradlew bundleRelease
./gradlew assembleRelease

cap_app\android\app\build\outputs\apk
해당 폴더에 apk 생성됨.


./gradlew assembleDebug


---> 해당 내용으로 release하면 안됌. 아래 내용대로 할것

실제기기 연결
설정 -> 휴대전화 정보 -> 소프트웨어 정보 -> 빌드 번호 (여러번 클릭하면) 개발자 모드로 전환이된다.

전환이 완료가 되면, 옵션에 개발자 옵션이 생긴다. 이때, usb 디버깅을 꼭 켜줘야한다.


<!--이제 안드로이드 Sdk 폴더에서 platform-tools 를 찾아내서 터미널에서 이 폴더로 들어가준다.-->


adb devices 명령어를 사용하면 디바이스가 검색된 것을 알 수 있다.

그후 아래 링크 참조해서 하면 됌
https://jake-seo-dev.tistory.com/267

<!-- ./gradlew bundleRelease -->
