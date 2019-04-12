import numpy as np
from objectClasses import Obstacle

def initialize_fusion_objects(not_assigned_sensor_obj_list):
    """
    :param not_assigned_sensor_obj_list: list of not assigned objects from the sensors
    :return: fusion_list_initialized_objects:
    """
    sensor_specs = not_assigned_sensor_obj_list.sensor_specs
    time = not_assigned_sensor_obj_list.timeStamp
    new_fusion_elements = []
    
    for sensor_obj in not_assigned_sensor_obj_list:
        s_vector = sensor_obj.s_vector
        P = sensor_obj.P
        
        if not all(s_vector[:3] == s_vector[:3]):  # some missing position measurements
            pos_initializers = sensor_specs['pos_initializers']
            pos_nans = np.where(np.isnan(s_vector[:3]))[0]
            for i in pos_nans:
                s_vector[:3][i] = np.random.normal(loc=pos_initializers[i],
                                                   scale=pos_initializers[i] / 10.)
                P[i, :] = 0.
                P[:, i] = 0.
                P[i, i] = 1e18
        
        if not all(s_vector[3:6] == s_vector[3:6]):  # some missing velocity measurements
            vel_initializers = sensor_specs['vel_initializers']
            vel_nans = np.where(np.isnan(s_vector[3:6]))[0]
            for i in vel_nans:
                s_vector[3:6][i] = np.random.normal(loc=vel_initializers[i],
                                                    scale=vel_initializers[i] / 10.)
                P[3+i, :] = 0.
                P[:, 3+i] = 0.
                P[3+i, 3+i] = 1e18

        if not all(s_vector[6:9] == s_vector[6:9]):  # some missing acc measurements
            acc_nans = np.where(np.isnan(s_vector[6:9]))[0]
            s_vector[6:9][acc_nans] = np.random.normal(size=(len(acc_nans)))
            for i in acc_nans:
                P[6+i, :] = 0.
                P[:, 6+i] = 0.
                P[6+i, 6+i] = 1e18
        new_fusion_elements.append(Obstacle(pos_x=s_vector[0], pos_y=s_vector[1],
                                            pos_z=s_vector[2], v_x=s_vector[3],
                                            v_y=s_vector[4], v_z=s_vector[5],
                                            a_x=s_vector[6], a_y=s_vector[7],
                                            a_z=s_vector[8],
                                            yaw=s_vector[9], r_yaw=s_vector[10], P=P,
                                            last_update_time=time, p_existence=1))
    return new_fusion_elements


def drop_objects(fusion_list, last_seen=0.4, distance_to_ego=80):
    """
    :param fusion_list:
    :distance_to_ego: 
    :last_seen
    :return:
    """
    fusion_time = fusion_list.timeStamp
    for fusion_obj in fusion_list:
        last_update = fusion_obj.last_update_time
        D = np.linalg.norm(fusion_obj.s_vector[:3])
        if fusion_time - last_update > last_seen or D > distance_to_ego:  
            fusion_list.remove(fusion_obj)

    return fusion_list