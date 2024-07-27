PACKAGE_NAME=map_share

#echo "Verificando dependências ..."
#rosdep install -i --from-path src --rosdistro humble -y

echo "Recriando o pacote ${PACKAGE_NAME} ..."
#colcon build
colcon build --packages-select $PACKAGE_NAME

echo
echo "Recarregando o ambiente ..."
source install/setup.bash

# Sobrescrevendo arquivo com classes diversas
cp -f ../astar.py install/map_share/lib/map_share/astar.py
cp -f map.py install/map_share/lib/map_share/map.py

echo
echo "Rodando $1 ..."
ros2 run $PACKAGE_NAME $1

