#PACKAGE_NAME=map_share
PACKAGE_NAME=simulator

#echo "Verificando dependências ..."
#rosdep install -i --from-path src --rosdistro humble -y

echo "Recriando o pacote ${PACKAGE_NAME} ..."
#colcon build
colcon build --packages-select $PACKAGE_NAME

echo
echo "Recarregando o ambiente ..."
source install/setup.bash

# Sobrescrevendo arquivo com classes diversas
cp -f ../astar.py install/${PACKAGE_NAME}/lib/${PACKAGE_NAME}/astar.py
#cp -f map.py install/${PACKAGE_NAME}/lib/${PACKAGE_NAME}/map.py

echo
echo "Rodando programa de nome: $1 ..."
ros2 run $PACKAGE_NAME $1


### Testar serviço
# ros2 service call /get_map_data map_interfaces/srv/GetMapData
### Testar tópico
# ros2 topic echo /map_info
