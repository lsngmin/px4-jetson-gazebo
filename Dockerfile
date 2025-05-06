#베이스 이미지는 ROS2 Humble 입니다. - Ubuntu 22.04
FROM ros:humble

#필수 패키지 설치
RUN apt-get update && apt-get install -y wget git lsb-release sudo curl gnupg2

#PX4 소스코드 클론 및 서브모듈 포함
RUN git clone https://github.com/PX4/PX4-Autopilot.git --recursive

#PX4 의존성 설치 스크립트 실행
RUN bash PX4-Autopilot/Tools/setup/ubuntu.sh

# Micro XRCE-DDS Agent 설치
RUN git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git && \
	cd Micro-XRCE-DDS-Agent && \
	mkdir build && \
	cd build && \
	cmake .. && \
	make -j$(nproc) && \
	sudo make install && \
	sudo ldconfig /usr/local/lib/

#작업공간 생성 및 MICRO_ROS_SETUP CLONE
WORKDIR /root/micro_ros_ws/src
RUN git clone -b humble https://github.com/micro-ROS/micro_ros_setup.git

#의존성 설치 후 빌드
WORKDIR /root/micro_ros_ws
RUN rosdep update
RUN rosdep install --from-path src --ignore-src -y
RUN . /opt/ros/humble/setup.sh && colcon build
RUN echo "source /root/micro_ros_ws/install/setup.bash" >> /root/.bashrc
