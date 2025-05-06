# PX4 Gazebo Simulation with Jetson Nano Integration in Docker
본 프로젝트는 PX4와 Gazebo를 활용하여 드론 시뮬레이션 환경을 구축하고, 이를 Jetson Nano와 ROS 2를 통해 통신하도록 구성하는 시스템입니다.  <br>Docker 환경에서 PX4와 Gazebo 시뮬레이션을 실행하며, Micro XRCE-DDS를 통해 Jetson Nano에서 ROS 2와의 통신을 지원합니다.  <br>이 프로젝트는 드론 제어 및 시뮬레이션을 위한 다양한 구성 요소가 통합되어 있으며, Jetson Nano와의 연동을 통해 실제 드론과 유사한 환경을 시뮬레이션할 수 있습니다.


## 요구사항
- 운영체제: `Ubuntu 20.04` 이상
- PX4 버전: `v1.14` 이상
- Docker: 설치되어 있어야 함
- Jetson Nano: ROS 2를 통한 통신을 위해 사용

## 1. Docker 이미지 빌드

### 1-1 Dockerfile을 통한 환경 구축
>다음 명령어를 사용하여 Docker 이미지를 빌드하고, 컨테이너를 실행합니다.

```
# Docker 이미지 빌드
sudo docker build -t px4-jetson-gazebo .

# Docker 컨테이너 실행
sudo docker run --name pjg -it --network host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --privileged px4-jetson-gazebo
```
### 1-2 Docker 실행 옵션 설명
- `--name pjg`: 컨테이너의 이름을 pjg로 설정
- `-it`: 터미널을 연결하여 상호작용 모드로 실행
- `--network host`: 호스트 네트워크를 사용하여 네트워크 문제를 해결
- `-e DISPLAY=$DISPLAY`: GUI 애플리케이션 실행을 위한 디스플레이 설정
- `-v /tmp/.X11-unix:/tmp/.X11-unix`: 호스트와 컨테이너 간 X11 소켓을 공유하여 GUI 애플리케이션 실행
- `--privileged`: 컨테이너에서 드론 시뮬레이션에 필요한 권한을 부여

## 2. Docker 내에서 명령어 실행
>컨테이너 내에서 각 터미널을 통해 명령어를 실행합니다. 각 명령어는 다른 터미널 또는 별도의 창에서 실행되어야 합니다.
```
sudo docker exec -it pjg bash
```

### 2-1 첫 번째 터미널
>PX4 시뮬레이션을 Gazebo와 함께 실행합니다.
```
make px4_sitl gz_x500
```
PX4 시뮬레이션 환경을 Gazebo에서 실행하도록 설정합니다.

### 2-2. 두 번째 터미널
>MicroXRCEAgent를 실행하여 Jetson Nano와 통신합니다.
```
MicroXRCEAgent udp4 -p 8888
```
이 명령어는 Micro XRCE-DDS 에이전트를 통해 PX4와 ROS 2 간의 데이터 통신을 관리합니다. 8888 포트를 통해 Micro XRCE-DDS 에이전트가 활성화됩니다.

### 2-3. 세 번째 터미널
>ROS 2에서 사용 가능한 토픽 목록을 확인합니다.
```
ros2 topic list
```
만약 ros2 명령어가 인식되지 않는다면, 아래 명령어를 실행하여 ROS 2 환경을 설정하십시오:
```
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```
