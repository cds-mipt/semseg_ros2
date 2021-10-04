## Создание рабочего пространства

Официальный туториал по созданию рабочего пространства в ROS2: https://docs.ros.org/en/foxy/Tutorials/Workspace/Creating-A-Workspace.html

Исходный код и артефакты сборки принято хранить в рабочем пространстве. В ROS2 принято его называть colcon_ws, а исходный код (в виде набора пакетов/репозиториев) хранить в colcon_ws/src
```bash
mkdir ~/workspace/colcon_ws/src -p
```

Далее можно склонировать исходный код необходимых пакетов:
```bash
cd ~/workspace/colcon_ws/src
git clone https://gitlab.com/sdbcs-nio3/itl_mipt/segm_tracking/alg/2d_segmentation/semseg.git
git clone https://gitlab.com/sdbcs-nio3/itl_mipt/segm_tracking/alg/2d_segmentation/semseg_ros2.git
```


## docker

Офизиальный туториал по docker: https://docs.docker.com/get-started/

Для упрощения развертывания узлов используются docker образы. Такой образ создается по Dockerfile, поэтому сначала необходимо подготовить его. За основу можно взять представленный в данном репозитории в директории docker.

Развертывание узлов может производиться на разных платформах. При этом Dockerfile может отличаться для разных платформ. Для сборки на обычном компьютере название файла должно быть `Dockerfile.x86_64`, для сборки на Jetson - `Dockerfile.aarch64`.

Первая строка Dockerfile:
```dockerfile
FROM nvcr.io/nvidia/cuda:11.1.1-devel-ubuntu20.04
```
обозначает базовый образ. На основе него будет производиться сборка образа для развертывания узлов. Для работы с нейросетевыми моделями нужны такие библиотеки как CUDA, CuDNN и др. А также в контейнере должен быть установлен ROS2. Удобно выбрать базовый образ, в котором установлены необходимые библиотеки для работы с моделями, а ROS2 доустановить, указав инструкции по его установке в Dockerfile. Список образов с предустановленными библиотеками можно найти на https://ngc.nvidia.com/catalog/containers. Для Jetson необходимо использовать образы с L4T (Linux for Tegra) в названии. ROS2 Foxy может быть установлен добавлением в Dockerfile следующих строк:
```dockerfile
# Install ROS2 Foxy
RUN apt-get update \
    && apt-get install -y curl gnupg2 lsb-release \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key  -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt-get update \
    && apt-get install -y \
        ros-foxy-ros-base \
        python3-colcon-common-extensions \
        ros-foxy-cv-bridge \
    && rm -rf /var/lib/apt/lists/*
```

Вторая строка Dockerfile:
```dockerfile
ENV DEBIAN_FRONTEND noninteractive
```
отключает интерактивный режим, который недопустим на этапе сборки. Отсутствие этой строки может привести к зависанию сборки, так как будет ожидаться ввод данных пользователем, что невозможно на этом этапе.

Другим важным элементом является создание нового пользователя внутри контейнера, от имени которого будут производиться все действия:
```dockerfile
RUN useradd -m ${USER} --uid=${UID} && echo "${USER}:${PW}" | chpasswd && adduser ${USER} sudo
WORKDIR /home/${USER}
RUN mkdir -p colcon_ws/src && chown -R ${UID}:${GID} /home/${USER}
USER ${UID}:${GID}
```
Как правило, эти строки можно использовать без изменений и в других репозиториях, изменив лишь имя пользователя в строке:
```dockerfile
ARG USER=docker_semseg
```
на более подходящее.

Также стоит обратить внимание на строчку
```dockerfile
ENV PYTHONPATH=/home/${USER}/colcon_ws/src/semseg:${PYTHONPATH}
```
Она позволяет осуществлять import python-пакета semseg, реализующего библиотеку семантической сегментации. Это наиболее простой путь решить проблему вида: `ImportError: no module named semseg`. Друим возможным решением является добавление инструкций по установке и сама установка пакета semseg. Если используемая библиотека их уже содержит, то можно воспользоваться ими. Иначе придется добавлять самостоятельно, что может существенно зависеть от конкретной библиотеке.

Все остальные строки Dockerfile - это инструкции по установке зависимостей библиотеки semseg и ROS2 обвязки semseg_ros2.

Кроме Dockerfile необходимо также создать набор скриптов для сборки (build.sh), запуска (start.sh) и входа (into.sh) в контейнер. Как правило, эти скрипты можно использовать и в других репозиториях, изменив лишь имя пользователя на указанное в Dockerfile, а имя образа и имя контейнера на более подходящие.

В итоге, последовательность работы с docker обвязкой должна получиться следующей:
```bash
bash build.sh
bash start.sh
bash into.sh
```
В результате выполнения этой последовательности команд должен быть создан образ, на его основе запущен контейнер и осуществлен в него вход.

Для дальнейшей работы с пакетом необходимо их выполнить в консоли.


## Работа с готовым пакетом

В настоящем репозитории представлен готовый к использованию ROS2 пакет семантической сегментации. 

К данному моменту предполагается, что собран образ, запущен контейнер и выполнен вход в него. После этого последовательность команд, необходимая для запуска, должна быть максимально простой. 

Сначала необходимо собрать пакет:
```bash
cd ~/colcon_ws
colcon build --packages-select semseg_ros2 --symlink-install
source install/setup.bash
```
Затем запустить launch, который автоматически запустит необходимые компоненты:
```bash
ros2 launch semseg_ros2 semseg_launch.py
```

Нужно стремиться к тому, чтобы последовательность работы с готовым пакетом состояла только из этих четырех строк. Все остальное должно быть перенесено на этап сборки образа, то есть в Dockerfile.

launch файл сконфигурирован для запуска на датасете KITTI. Чтобы запустить проигравание BAG файла, нужно сначала [скачать](https://drive.google.com/file/d/1pfzTmBGHje55STJNKxfkVbQE8ylg-6ds/view?usp=sharing) его. Так как это файл для ROS1, то для проигрывания в ROS2 понадобятся дополнительные пакеты:
```bash
sudo apt install \
    ros-foxy-ros2bag \
    ros-foxy-rosbag2 \
    ros-foxy-ros1-bridge \
    ros-foxy-rosbag2-bag-v2-plugins \
    ros-foxy-rosbag2-converter-default-plugins
```
Для запуска проигрывания нужно сначала активировать окружение ROS1, затем ROS2:
```bash
source /opt/ros/noetic/setup.bash
source /opt/ros/foxy/setup.bash
ros2 bag play -s rosbag_v2 kitti_2011_10_03_drive_0027_synced.bag
```
Визуализировать результаты работы можно либо с помощью rqt
```bash
source /opt/ros/foxy/setup.bash
rqt
# Plugins -> Visualization -> Image View, в выпадающем списке выбрать желаемый топик
```
либо с помощью rviz:
```bash
source /opt/ros/foxy/setup.bash
rviz2
# Add -> By topic, в списке выбрать желаемый топик (Image)
```

## Создание пакета с нуля

Официальные туториалы по созданию пакета: 
1. https://docs.ros.org/en/foxy/Tutorials/Creating-Your-First-ROS2-Package.html
2. https://docs.ros.org/en/foxy/Tutorials/Writing-A-Simple-Py-Publisher-And-Subscriber.html

Официальный туториал по работе с launch: 
1. https://docs.ros.org/en/foxy/Tutorials/Launch-system.html

Далее рассмотрим последовательность действий, которую необходимо выполнить, чтобы создать ROS2 пакет семантической сегментации с нуля, имея код библиотеки семантической сегментации semseg. Но так как код пакета уже представлен в репозитории, его придется сначала удалить из него:
```bash
rm -rf semseg_ros2
```

К данному моменту предполагается, что собран образ, запущен контейнер и выполнен вход в него.

Сначала необходимо создать шаблон пакета, с помощью команды:
```bash
cd ~/colcon_ws/src/semseg_ros2
ros2 pkg create --build-type ament_python semseg_ros2
```
Созданные при этом файлы и их содержимое содержатся в коммите [6ed8ecc](https://github.com/cds-mipt/semseg_ros2/commit/6ed8ecc26626bef38057118f6b533087c3097aab).

Далее нужно создать необходимые узлы, добавив файлы с исходным кодом и дополнителные инструкции в setup.py, как это было сделано в коммитах [d7ed190](https://github.com/cds-mipt/semseg_ros2/commit/d7ed19003f89c39237be72f5cd3b1cf79d44a8e1), [fb0e755](https://github.com/cds-mipt/semseg_ros2/commit/fb0e755a15edddeabbbbaf296f97df7913209f18)

Последним этапом является добавление launch файлов (но можно их добавить и раньше), как это сделано в коммите [6b7065e](https://github.com/cds-mipt/semseg_ros2/commit/6b7065e7db682507177950f3601609f0c12d0156)

Также рекомендуется ознакомиться с [полной историей коммитов](https://gitlab.com/sdbcs-nio3/itl_mipt/segm_tracking/alg/2d_segmentation/semseg_ros2/-/commits/devel/) и актуализировать код в соответствии с ними.

После этого можно перейти к пункту Работа с готовым пакетом для проверки работоспособности.