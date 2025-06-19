# PX4 Gazebo Simulation with Jetson Nano Integration in Docker
이 프로젝트는 PX4와 Gazebo를 사용해 드론 시뮬레이션 환경을 구성하고, Jetson Nano와 ROS 2를 통해 통신하는 시스템을 Docker 기반으로 구축합니다. Micro XRCE-DDS를 이용해 PX4에서 발생한 데이터를 Jetson Nano에서 수신하며, 실제 드론 환경과 유사한 구조를 제공합니다.

## 📦 요구사항
| 구성 요소      | 버전 정보                  |
|----------------|------------------------|
| **OS**             | `Ubuntu 20.04` |
| **Arch**          | `amd64`               |

## 📘 환경
| 구성 요소      | 버전 정보                  |
|----------------|------------------------|
| **OS**             | `Ubuntu 22.04 (Jammy)` |
| **ROS 2**          | `Humble`               |
| **Gazebo**         | `11 Classic`           |
| **PX4**            | `v1.14`                |
| **Jetson Nano**    | `JetPack 4.6.1`        |


## 🛠️ Docker 이미지 빌드

### Dockerfile 기반 이미지 빌드 및 컨테이너 실행
> 사전에 docker를 설치하세요

```
# Docker 이미지 빌드
sudo docker build -t px4-jetson-gazebo .

# Docker 컨테이너 실행
sudo docker run --name pjg -it \
  --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --privileged px4-jetson-gazebo
```

### Docker 내에서 명령어 실행
```
# Docker 컨테이너 진입
sudo docker exec -it pjg bash
```

### 컨테이너 내부 명령 실행
>Docker 컨테이너 내부에 진입한 후, 아래 명령어들을 각기 다른 터미널 또는 새로운 탭에서 실행해야 합니다.
```
# PX4 + Gazebo 실행
cd ../../PX4-autopilot \ make px4_sitl gz_standard_vtol

# Micro XRCE-DDS 에이전트 실행
MicroXRCEAgent udp4 -p 8888

# ROS 2 토픽 확인
ros2 topic list
```

>ros2 명령어가 인식되지 않을 경우
```
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```
