1. user_maps table 생성함
user_name(pk, int), map_id(var)
해당테이블에는 root ,map_id(~~~.osa)로 들어감.
+++ map_id라는 table을 만들고,기존의 map_id에 해당하는 table은 삭제함.
이러한 파이프 라인을 구축해야됨.

2. map_id라는 table에는 predict한 결과(wallet)과 위치가 데이터로 들어가야됨.
즉. columns는 pk(0~N, Default) , x , y, z, predict(wallet or ..) 

