PACKAGE_NAME=map_share

#echo "Verificando dependências ..."
#rosdep install -i --from-path src --rosdistro humble -y

echo "Recriando o pacote ${PACKAGE_NAME} ..."
#colcon build
colcon build --packages-select $PACKAGE_NAME

echo
echo "Recarregando o ambiente ..."
source install/setup.bash

echo
echo "Rodando $1 ..."
ros2 run $PACKAGE_NAME $1
