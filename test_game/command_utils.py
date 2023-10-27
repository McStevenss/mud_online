




def parse_action(server_client,data):
    x,y = server_client.position
    if server_client.game_map[server_client.current_floor][y][x] == ">": #Player is going down one level
            server_client.current_floor = server_client.current_floor + 1
            server_client.position = server_client.game_map_class.Get_spawn_point(current_floor=server_client.current_floor)
            data["move"] = "down"
            data["position"] = server_client.position

            return data
            #server_client.PassOn(data)
    elif server_client.game_map[server_client.current_floor][y][x] == "<": #Player is going up one level
        server_client.current_floor = server_client.current_floor - 1
        server_client.position = server_client.game_map_class.Get_stair_up_point(current_floor=server_client.current_floor)
        data["move"] = "up"
        data["position"] = server_client.position
        return data